"""Streamlit app for crypto regime forecasting."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st
from plotly.subplots import make_subplots

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from perps_forecaster.config import default_config
from perps_forecaster.data.binance import (align_hourly, fetch_funding_rate,
                                           fetch_open_interest,
                                           fetch_perp_klines,
                                           fetch_spot_klines)
from perps_forecaster.eval.metrics import qlike, rmse, smape
from perps_forecaster.features.engine import (build_features,
                                              create_regime_labels,
                                              get_feature_columns)
from perps_forecaster.insights.analyzer import generate_regime_insights
from perps_forecaster.models.point_vol import forecast_next_bar
from perps_forecaster.models.regime import (predict_regime_proba,
                                            train_regime_classifier)
from perps_forecaster.utils.cache import (get_cache_path, load_parquet,
                                          save_parquet)

# Page config
st.set_page_config(page_title="Crypto Regime Forecaster", layout="wide", page_icon="📈")

# Banner
st.warning("⚠️ **Research Demo**: This is a research demonstration. Not financial advice.")

st.title("🔮 Crypto Regime Forecaster")
st.markdown("*Short-term regime forecasting using public Binance Futures APIs*")

# Config
config = default_config


@st.cache_data(ttl=1800)  # 30 min TTL
def load_and_process_data(symbol: str, lookback: int, horizon: int):
    """Load and process all data with caching."""
    cache_dir = config.cache_dir

    try:
        # Try loading from cache first
        cache_file = get_cache_path(cache_dir, symbol, "aligned")
        cached_df = load_parquet(cache_file)

        if cached_df is not None and len(cached_df) >= lookback:
            st.info("📦 Loaded data from cache")
            df = cached_df.tail(lookback).copy()
        else:
            # Fetch fresh data
            with st.spinner("🌐 Fetching data from Binance..."):
                funding = fetch_funding_rate(symbol, limit=1000)
                oi = fetch_open_interest(symbol, period="1h", limit=500)
                perp = fetch_perp_klines(symbol, interval="1h", limit=min(lookback + 100, 1500))
                spot = fetch_spot_klines(symbol, interval="1h", limit=min(lookback + 100, 1000))

                # Align
                df = align_hourly(funding, oi, perp, spot)

                # Save to cache
                save_parquet(df, cache_file)
                st.success(f"✅ Fetched {len(df)} bars")

                df = df.tail(lookback).copy()

        # Build features
        with st.spinner("⚙️ Engineering features..."):
            config_dict = {
                "ema_fast_funding": config.ema_fast_funding,
                "ema_slow_funding": config.ema_slow_funding,
                "ema_fast_price": config.ema_fast_price,
                "ema_slow_price": config.ema_slow_price,
                "rv_window": config.rv_window,
                "jump_sigma_window": config.jump_sigma_window,
                "jump_threshold": config.jump_threshold,
                "oi_clip_min": config.oi_clip_min,
                "oi_clip_max": config.oi_clip_max,
            }
            df = build_features(df, config_dict)

        # Create labels
        with st.spinner("🏷️ Creating regime labels..."):
            df = create_regime_labels(df, horizon=horizon)

        # Drop NaN rows
        df = df.dropna().reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None


# Sidebar
st.sidebar.header("⚙️ Configuration")

symbol = st.sidebar.text_input("Symbol", value=config.symbol)
interval = st.sidebar.selectbox("Interval", ["1h"], index=0)
lookback = st.sidebar.slider("Lookback (bars)", 200, 1400, config.default_lookback, step=50)
horizon = st.sidebar.slider("Horizon (bars ahead)", 1, 6, config.default_horizon)
model_choice = st.sidebar.selectbox("Model", ["Logistic Regression", "LightGBM"])

model_type = "lightgbm" if model_choice == "LightGBM" else "logistic"

# Load data
df = load_and_process_data(symbol, lookback, horizon)

if df is None or len(df) < 100:
    st.error("❌ Insufficient data. Please adjust parameters.")
    st.stop()

# Convert to display timezone
tz = pytz.timezone(config.display_tz)
df["timestamp_local"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(tz)

# Ensure timestamp_local is timezone-naive for Plotly (Plotly doesn't handle tz-aware timestamps well)
df["timestamp_local"] = df["timestamp_local"].dt.tz_localize(None)

# Debug info in expander
with st.expander("🔍 Debug Info", expanded=False):
    st.write(f"**Data Shape:** {df.shape}")
    st.write(f"**Date Range:** {df['timestamp_local'].min()} to {df['timestamp_local'].max()}")
    st.write(f"**Regime Counts:** {df['regime'].value_counts().to_dict()}")
    st.write(f"**Sample Data:**")
    st.dataframe(df.head(3))

# Split train/test (80/20)
split_idx = int(len(df) * 0.8)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

feature_cols = get_feature_columns()

# Train model
with st.spinner("🤖 Training regime classifier..."):
    X_train = train_df[feature_cols]
    y_train = train_df["regime"]

    model, scaler = train_regime_classifier(X_train, y_train, model_type=model_type)

# Predict on test set
X_test = test_df[feature_cols]
y_test = test_df["regime"]

y_proba, classes = predict_regime_proba(model, scaler, X_test)

# Get last prediction (next bar forecast)
last_row = df.iloc[[-1]][feature_cols]
last_proba, _ = predict_regime_proba(model, scaler, last_row)

# Forecast μ and σ
with st.spinner("📊 Forecasting point and volatility..."):
    mu_hat, sigma_hat = forecast_next_bar(df, horizon=horizon)

# Display main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Price Chart with Regime Ribbon")

    try:
        # Create figure with regime coloring
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=("Price", "Funding Rate"),
        )

        # Regime ribbon (color background by regime) - add BEFORE the line
        regime_colors = {"bull": "rgba(0, 255, 0, 0.2)", "bear": "rgba(255, 0, 0, 0.2)", "chop": "rgba(128, 128, 128, 0.1)"}

        for i in range(len(df) - 1):
            regime = df.iloc[i]["regime"]
            fig.add_vrect(
                x0=df.iloc[i]["timestamp_local"],
                x1=df.iloc[i + 1]["timestamp_local"],
                fillcolor=regime_colors.get(regime, "rgba(128, 128, 128, 0.1)"),
                layer="below",
                line_width=0,
                row=1,
                col=1,
            )

        # Price line
        fig.add_trace(
            go.Scatter(
                x=df["timestamp_local"],
                y=df["perp_close"],
                mode="lines",
                name="Price",
                line=dict(color="blue", width=1.5),
            ),
            row=1,
            col=1,
        )

        # Funding rate
        fig.add_trace(
            go.Scatter(
                x=df["timestamp_local"],
                y=df["fundingRate"],
                mode="lines",
                name="Funding Rate",
                line=dict(color="purple", width=1.5),
            ),
            row=2,
            col=1,
        )

        fig.update_xaxes(title_text="Time (Australia/Perth)", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Funding Rate", row=2, col=1)

        fig.update_layout(
            height=600,
            showlegend=True,
            hovermode="x unified",
            template="plotly_dark",
        )

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error rendering chart: {e}")
        # Fallback: simple single chart
        st.line_chart(df.set_index("timestamp_local")[["perp_close"]])

with col2:
    st.subheader("🔮 Next Bar Forecast")

    # Regime probabilities
    st.markdown("**Regime Probabilities:**")
    prob_df = pd.DataFrame(
        {"Regime": classes, "Probability": last_proba[0]},
    )
    prob_df["Probability"] = prob_df["Probability"].apply(lambda x: f"{x:.1%}")

    st.dataframe(prob_df, hide_index=True, use_container_width=True)

    # Bar chart
    try:
        fig_prob = go.Figure(
            data=[
                go.Bar(
                    x=classes,
                    y=last_proba[0],
                    marker_color=["green", "red", "gray"],
                )
            ]
        )
        fig_prob.update_layout(
            yaxis_title="Probability",
            xaxis_title="Regime",
            height=250,
            showlegend=False,
            template="plotly_dark",
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render probability chart: {e}")

    # μ and σ forecast
    st.markdown("**Point & Volatility Forecast:**")
    st.metric("μ (mean return)", f"{mu_hat:.4%}")
    st.metric("σ (volatility)", f"{sigma_hat:.4%}")

# Generate comprehensive insights
predicted_regime = classes[last_proba[0].argmax()]
regime_proba_dict = {cls: prob for cls, prob in zip(classes, last_proba[0])}

insights = generate_regime_insights(
    df=df,
    predicted_regime=predicted_regime,
    regime_proba=regime_proba_dict,
    mu_forecast=mu_hat,
    sigma_forecast=sigma_hat,
    feature_cols=feature_cols,
    y_test=y_test,
    y_pred=y_pred_classes,
)

# Display insights in expandable sections
st.markdown("---")
st.subheader("💡 Insights & Decision Pathways")

# Confidence Score
confidence_color = "green" if insights.confidence_score > 70 else "orange" if insights.confidence_score > 40 else "red"
st.markdown(f"### Confidence Score: :{confidence_color}[{insights.confidence_score:.0f}/100]")

# Warnings (if any)
if insights.warnings:
    for warning in insights.warnings:
        st.warning(warning)

# Regime Interpretation
with st.expander("🎯 Regime Interpretation", expanded=True):
    st.markdown(insights.regime_description)
    st.markdown(f"**Market Conditions:** {insights.market_conditions}")
    st.markdown(f"**Risk Level:** {insights.risk_level}")

# Trading Suggestions
with st.expander("📋 Trading Suggestions", expanded=True):
    st.markdown("**Suggested Actions:**")
    for action in insights.suggested_actions:
        st.markdown(f"- {action}")
    
    st.markdown("---")
    st.markdown(f"**Position Sizing:** {insights.position_sizing}")

# Feature Drivers
with st.expander("🔍 What's Driving This Forecast?", expanded=False):
    if insights.key_drivers:
        st.markdown("**Key Market Drivers (by percentile):**")
        driver_df = pd.DataFrame(insights.key_drivers, columns=["Feature", "Percentile"])
        driver_df["Percentile"] = driver_df["Percentile"].apply(lambda x: f"{x:.0f}th")
        st.dataframe(driver_df, hide_index=True, use_container_width=True)
    
    if insights.supporting_signals:
        st.markdown("**Supporting Signals:**")
        for signal in insights.supporting_signals:
            st.markdown(f"✅ {signal}")
    
    if insights.contradicting_signals:
        st.markdown("**Contradicting Signals:**")
        for signal in insights.contradicting_signals:
            st.markdown(f"❌ {signal}")

# Historical Performance
with st.expander("📊 Historical Model Performance", expanded=False):
    if insights.historical_accuracy:
        st.markdown("**Accuracy by Regime:**")
        acc_df = pd.DataFrame(
            [
                {"Regime": regime, "Accuracy": f"{acc:.1%}"}
                for regime, acc in insights.historical_accuracy.items()
            ]
        )
        st.dataframe(acc_df, hide_index=True, use_container_width=True)
    
    if insights.regime_statistics.get("regime_distribution"):
        st.markdown("**Regime Distribution (Historical):**")
        regime_dist = insights.regime_statistics["regime_distribution"]
        dist_df = pd.DataFrame(
            [
                {"Regime": regime, "Count": count, "Percentage": f"{count / sum(regime_dist.values()):.1%}"}
                for regime, count in regime_dist.items()
            ]
        )
        st.dataframe(dist_df, hide_index=True, use_container_width=True)

# Diagnostics table
st.subheader("🔍 Diagnostics: Last 10 Bars")

diag_cols = [
    "timestamp_local",
    "perp_close",
    "fundingRate",
    "oi_pct_chg",
    "basis_proxy",
    "rv24",
    "regime",
]
diag_df = df[diag_cols].tail(10).copy()
diag_df["timestamp_local"] = diag_df["timestamp_local"].dt.strftime("%Y-%m-%d %H:%M")

st.dataframe(diag_df, hide_index=True, use_container_width=True)

# Model evaluation metrics
st.subheader("📊 Model Evaluation (Test Set)")

col1, col2, col3 = st.columns(3)

# Accuracy
y_pred_classes = [classes[i] for i in y_proba.argmax(axis=1)]
accuracy = (pd.Series(y_pred_classes) == y_test.values).mean()

with col1:
    st.metric("Accuracy", f"{accuracy:.2%}")

with col2:
    # Brier scores (average)
    brier_scores = []
    for i, cls in enumerate(classes):
        y_binary = (y_test == cls).astype(int)
        from sklearn.metrics import brier_score_loss

        brier = brier_score_loss(y_binary, y_proba[:, i])
        brier_scores.append(brier)
    avg_brier = np.mean(brier_scores)
    st.metric("Avg Brier Score", f"{avg_brier:.4f}")

with col3:
    st.metric("Test Samples", len(y_test))

# Footer
st.markdown("---")
st.caption(f"Data source: Binance Public APIs | Display timezone: {config.display_tz}")
st.caption("Built with ❤️ using Streamlit")
