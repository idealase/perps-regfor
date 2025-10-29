"""Insight generation and decision pathway analysis."""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class RegimeInsights:
    """Container for regime forecast insights."""

    # Primary forecast
    predicted_regime: str
    regime_probabilities: Dict[str, float]
    confidence_score: float

    # Interpretation
    regime_description: str
    market_conditions: str

    # Trading suggestions
    suggested_actions: List[str]
    risk_level: str
    position_sizing: str

    # Feature drivers
    key_drivers: List[Tuple[str, float]]
    supporting_signals: List[str]
    contradicting_signals: List[str]

    # Risk warnings
    warnings: List[str]

    # Context
    historical_accuracy: Dict[str, float]
    regime_statistics: Dict[str, Any]


def get_regime_interpretation(regime: str, proba: float) -> Tuple[str, str, str]:
    """Get human-readable interpretation of a regime forecast.

    Args:
        regime: Predicted regime (bull, bear, chop)
        proba: Probability of the regime

    Returns:
        Tuple of (description, market_conditions, risk_level)
    """
    interpretations = {
        "bull": {
            "description": "🟢 **Bullish Regime** - Market showing upward momentum with high volatility",
            "conditions": "Strong uptrend with fast EMA > slow EMA, positive funding rates suggest long bias, high volatility creates opportunities",
            "risk": "Moderate" if proba > 0.6 else "High",
        },
        "bear": {
            "description": "🔴 **Bearish Regime** - Market showing downward pressure with high volatility",
            "conditions": "Downtrend with fast EMA < slow EMA, negative funding may indicate short squeeze risk, high volatility increases danger",
            "risk": "High",
        },
        "chop": {
            "description": "⚪ **Choppy Regime** - Market consolidating with low directional conviction",
            "conditions": "Low volatility environment, unclear trend direction, range-bound price action expected",
            "risk": "Low" if proba > 0.6 else "Moderate",
        },
    }

    info = interpretations.get(regime, interpretations["chop"])
    return info["description"], info["conditions"], info["risk"]


def get_trading_suggestions(
    regime: str,
    proba: float,
    mu_forecast: float,
    sigma_forecast: float,
    confidence: float,
) -> Tuple[List[str], str]:
    """Generate actionable trading suggestions based on forecast.

    Args:
        regime: Predicted regime
        proba: Regime probability
        mu_forecast: Mean return forecast
        sigma_forecast: Volatility forecast
        confidence: Confidence score (0-100)

    Returns:
        Tuple of (list of suggestions, position sizing recommendation)
    """
    suggestions = []
    position_sizing = ""

    # High confidence bull
    if regime == "bull" and proba > 0.6 and confidence > 60:
        suggestions.extend(
            [
                "✅ Consider long positions in alignment with trend",
                f"🎯 Expected return: {mu_forecast:.2%} with volatility {sigma_forecast:.2%}",
                "⏰ Use tight stop losses due to high volatility",
                "📊 Monitor funding rate - high rates may signal over-leverage",
            ]
        )
        position_sizing = "**Moderate to Large** (60-80% of normal position)" if proba > 0.7 else "**Moderate** (40-60% of normal position)"

    # Low confidence bull
    elif regime == "bull" and proba > 0.4:
        suggestions.extend(
            [
                "⚠️ Weak bullish signal - proceed with caution",
                f"🎯 Expected return: {mu_forecast:.2%} with volatility {sigma_forecast:.2%}",
                "🔍 Wait for confirmation before entering positions",
                "📉 Consider smaller position sizes due to uncertainty",
            ]
        )
        position_sizing = "**Small** (20-40% of normal position)"

    # High confidence bear
    elif regime == "bear" and proba > 0.6 and confidence > 60:
        suggestions.extend(
            [
                "🔻 Consider short positions or exit longs",
                f"🎯 Expected return: {mu_forecast:.2%} with volatility {sigma_forecast:.2%}",
                "🛡️ Use wider stops due to short squeeze risk",
                "⚡ Monitor for capitulation signals or reversal patterns",
            ]
        )
        position_sizing = "**Moderate** (40-60% of normal position)" if proba > 0.7 else "**Small to Moderate** (30-50% of normal position)"

    # Low confidence bear
    elif regime == "bear" and proba > 0.4:
        suggestions.extend(
            [
                "⚠️ Weak bearish signal - high risk environment",
                f"🎯 Expected return: {mu_forecast:.2%} with volatility {sigma_forecast:.2%}",
                "💰 Consider taking profits on existing longs",
                "🚫 Avoid new long entries until clarity emerges",
            ]
        )
        position_sizing = "**Very Small** (10-30% of normal position)"

    # Choppy market
    else:
        suggestions.extend(
            [
                "🚫 **No clear directional edge** - avoid new positions",
                f"📊 Expected return: {mu_forecast:.2%} with low volatility {sigma_forecast:.2%}",
                "💰 Consider taking profits on existing positions",
                "⏸️ Wait for better setup with clearer regime",
                "🎯 Range-bound strategies may work (mean reversion)",
            ]
        )
        position_sizing = "**Minimal** (0-20% of normal position) or stay flat"

    return suggestions, position_sizing


def calculate_confidence_score(
    regime_proba: np.ndarray,
    historical_accuracy: float = None,
    vol_forecast: float = None,
) -> float:
    """Calculate confidence score for the forecast.

    Args:
        regime_proba: Probability distribution over regimes
        historical_accuracy: Historical accuracy of model (optional)
        vol_forecast: Volatility forecast (optional)

    Returns:
        Confidence score (0-100)
    """
    # Base confidence from max probability
    max_proba = regime_proba.max()
    base_confidence = max_proba * 100

    # Adjust for probability spread (higher spread = more confident)
    sorted_proba = np.sort(regime_proba)[::-1]
    if len(sorted_proba) > 1:
        spread = sorted_proba[0] - sorted_proba[1]
        spread_factor = spread * 50  # 0-50 bonus points
        base_confidence += spread_factor

    # Adjust for historical accuracy if available
    if historical_accuracy is not None:
        accuracy_factor = (historical_accuracy - 0.5) * 50  # -25 to +25 points
        base_confidence += accuracy_factor

    # Penalize high volatility (uncertainty)
    if vol_forecast is not None and vol_forecast > 0.05:  # > 5% vol
        vol_penalty = min(20, (vol_forecast - 0.05) * 200)
        base_confidence -= vol_penalty

    # Clamp to 0-100
    return max(0, min(100, base_confidence))


def analyze_feature_drivers(
    df: pd.DataFrame, feature_cols: List[str], last_row_idx: int = -1
) -> Tuple[List[Tuple[str, float]], List[str], List[str]]:
    """Analyze which features are driving the current forecast.

    Args:
        df: DataFrame with features
        feature_cols: List of feature column names
        last_row_idx: Index of the row to analyze (default: last row)

    Returns:
        Tuple of (key_drivers, supporting_signals, contradicting_signals)
    """
    if len(df) == 0:
        return [], [], []

    last_row = df.iloc[last_row_idx]

    # Analyze key features
    drivers = []
    supporting = []
    contradicting = []

    # Funding rate analysis
    if "fundingRate" in df.columns:
        funding = last_row["fundingRate"]
        funding_percentile = (df["fundingRate"] < funding).mean() * 100

        if abs(funding) > 0.0005:  # Significant funding
            drivers.append(("Funding Rate", funding_percentile))
            if funding > 0.0005:
                supporting.append(f"📈 High positive funding rate ({funding:.4%}) indicates long bias")
            elif funding < -0.0005:
                contradicting.append(
                    f"📉 Negative funding rate ({funding:.4%}) suggests short interest"
                )

    # Funding slope
    if "funding_slope" in df.columns:
        slope = last_row["funding_slope"]
        if abs(slope) > 0.0002:
            slope_percentile = (df["funding_slope"] < slope).mean() * 100
            drivers.append(("Funding Slope", slope_percentile))
            if slope > 0:
                supporting.append(
                    "📊 Funding rate increasing - growing long conviction"
                )
            else:
                contradicting.append(
                    "📊 Funding rate decreasing - weakening long sentiment"
                )

    # Open interest change
    if "oi_pct_chg" in df.columns:
        oi_chg = last_row["oi_pct_chg"]
        if abs(oi_chg) > 0.02:  # >2% change
            oi_percentile = (df["oi_pct_chg"] < oi_chg).mean() * 100
            drivers.append(("Open Interest Change", oi_percentile))
            if oi_chg > 0.05:
                supporting.append(
                    f"🔥 Large OI increase ({oi_chg:.1%}) - strong new positioning"
                )
            elif oi_chg < -0.05:
                contradicting.append(
                    f"💨 Large OI decrease ({oi_chg:.1%}) - position unwinding"
                )

    # Realized volatility
    if "rv24" in df.columns:
        rv = last_row["rv24"]
        rv_percentile = (df["rv24"] < rv).mean() * 100
        drivers.append(("Realized Volatility", rv_percentile))
        if rv > df["rv24"].quantile(0.75):
            supporting.append(
                f"⚡ High volatility ({rv:.2%}) - regime clarity increases"
            )
        elif rv < df["rv24"].quantile(0.25):
            contradicting.append(f"😴 Low volatility ({rv:.2%}) - choppy conditions likely")

    # Basis proxy
    if "basis_proxy" in df.columns:
        basis = last_row["basis_proxy"]
        if abs(basis) > df["basis_proxy"].std():
            basis_percentile = (df["basis_proxy"] < basis).mean() * 100
            drivers.append(("Basis (Perp-Spot)", basis_percentile))
            if basis > 0:
                supporting.append("💰 Positive basis - perp premium suggests bullish sentiment")
            else:
                contradicting.append("💸 Negative basis - perp discount suggests bearish sentiment")

    # Sort drivers by extremity (distance from 50th percentile)
    drivers.sort(key=lambda x: abs(x[1] - 50), reverse=True)
    drivers = drivers[:5]  # Top 5 drivers

    return drivers, supporting, contradicting


def generate_regime_insights(
    df: pd.DataFrame,
    predicted_regime: str,
    regime_proba: Dict[str, float],
    mu_forecast: float,
    sigma_forecast: float,
    feature_cols: List[str],
    y_test: pd.Series = None,
    y_pred: List[str] = None,
) -> RegimeInsights:
    """Generate comprehensive insights for the regime forecast.

    Args:
        df: Full DataFrame with features
        predicted_regime: Predicted regime class
        regime_proba: Dictionary of regime probabilities
        mu_forecast: Mean return forecast
        sigma_forecast: Volatility forecast
        feature_cols: List of feature column names
        y_test: Test labels (optional, for historical accuracy)
        y_pred: Predicted labels (optional, for historical accuracy)

    Returns:
        RegimeInsights object with all analysis
    """
    # Convert proba dict to array
    regimes = ["bear", "bull", "chop"]
    proba_array = np.array([regime_proba.get(r, 0.0) for r in regimes])

    # Calculate confidence
    historical_acc = None
    if y_test is not None and y_pred is not None:
        historical_acc = (pd.Series(y_pred) == y_test.values).mean()

    confidence = calculate_confidence_score(proba_array, historical_acc, sigma_forecast)

    # Get interpretation
    description, conditions, risk_level = get_regime_interpretation(
        predicted_regime, regime_proba[predicted_regime]
    )

    # Get trading suggestions
    suggestions, position_sizing = get_trading_suggestions(
        predicted_regime,
        regime_proba[predicted_regime],
        mu_forecast,
        sigma_forecast,
        confidence,
    )

    # Analyze feature drivers
    key_drivers, supporting, contradicting = analyze_feature_drivers(
        df, feature_cols, last_row_idx=-1
    )

    # Generate warnings
    warnings = []
    if confidence < 40:
        warnings.append("⚠️ LOW CONFIDENCE: Model uncertainty is high - avoid large positions")

    if sigma_forecast > 0.05:
        warnings.append(
            f"⚡ HIGH VOLATILITY ALERT: Expected volatility {sigma_forecast:.2%} - use wider stops"
        )

    if regime_proba[predicted_regime] < 0.5:
        warnings.append(
            "🤔 MIXED SIGNALS: No clear regime dominance - wait for confirmation"
        )

    if len(contradicting) > len(supporting):
        warnings.append(
            "⚔️ CONFLICTING INDICATORS: Multiple contradicting signals present"
        )

    # Calculate historical accuracy by regime
    regime_accuracy = {}
    if y_test is not None and y_pred is not None:
        for regime in regimes:
            regime_mask = y_test == regime
            if regime_mask.sum() > 0:
                regime_acc = (
                    pd.Series(y_pred)[regime_mask] == y_test[regime_mask]
                ).mean()
                regime_accuracy[regime] = regime_acc

    # Regime statistics
    regime_stats = {
        "total_bars": len(df),
        "regime_distribution": df["regime"].value_counts().to_dict()
        if "regime" in df.columns
        else {},
        "avg_regime_duration": None,  # Could calculate regime persistence
    }

    return RegimeInsights(
        predicted_regime=predicted_regime,
        regime_probabilities=regime_proba,
        confidence_score=confidence,
        regime_description=description,
        market_conditions=conditions,
        suggested_actions=suggestions,
        risk_level=risk_level,
        position_sizing=position_sizing,
        key_drivers=key_drivers,
        supporting_signals=supporting,
        contradicting_signals=contradicting,
        warnings=warnings,
        historical_accuracy=regime_accuracy,
        regime_statistics=regime_stats,
    )
