"""Tests for insights and decision pathway analysis."""

import numpy as np
import pandas as pd
import pytest

from perps_forecaster.insights.analyzer import (
    RegimeInsights,
    analyze_feature_drivers,
    calculate_confidence_score,
    generate_regime_insights,
    get_regime_interpretation,
    get_trading_suggestions,
)


def test_get_regime_interpretation():
    """Test regime interpretation for all regimes."""
    # Bull regime
    desc, cond, risk = get_regime_interpretation("bull", 0.7)
    assert "Bullish" in desc
    assert "uptrend" in cond.lower() or "upward" in cond.lower()
    assert risk in ["Low", "Moderate", "High"]

    # Bear regime
    desc, cond, risk = get_regime_interpretation("bear", 0.7)
    assert "Bearish" in desc
    assert "downtrend" in cond.lower() or "downward" in cond.lower()
    assert risk == "High"

    # Chop regime
    desc, cond, risk = get_regime_interpretation("chop", 0.7)
    assert "Chop" in desc
    assert "volatility" in cond.lower()
    assert risk in ["Low", "Moderate"]


def test_get_trading_suggestions():
    """Test trading suggestions generation."""
    # High confidence bull
    suggestions, position = get_trading_suggestions("bull", 0.75, 0.02, 0.03, 70)
    assert len(suggestions) > 0
    assert any("long" in s.lower() for s in suggestions)
    assert "position" in position.lower()

    # Bear regime
    suggestions, position = get_trading_suggestions("bear", 0.65, -0.02, 0.04, 60)
    assert len(suggestions) > 0
    assert any("short" in s.lower() or "exit" in s.lower() for s in suggestions)

    # Chop regime
    suggestions, position = get_trading_suggestions("chop", 0.70, 0.001, 0.01, 50)
    assert len(suggestions) > 0
    assert any("no clear" in s.lower() or "avoid" in s.lower() for s in suggestions)


def test_calculate_confidence_score():
    """Test confidence score calculation."""
    # High confidence scenario
    proba = np.array([0.1, 0.8, 0.1])
    score = calculate_confidence_score(proba)
    assert 0 <= score <= 100
    assert score > 60  # Should be relatively high

    # Low confidence scenario
    proba = np.array([0.33, 0.34, 0.33])
    score = calculate_confidence_score(proba)
    assert 0 <= score <= 100
    assert score < 60  # Should be relatively low

    # With historical accuracy
    proba = np.array([0.7, 0.2, 0.1])
    score = calculate_confidence_score(proba, historical_accuracy=0.8)
    assert score > calculate_confidence_score(proba, historical_accuracy=0.5)

    # With high volatility
    proba = np.array([0.7, 0.2, 0.1])
    score_high_vol = calculate_confidence_score(proba, vol_forecast=0.10)
    score_low_vol = calculate_confidence_score(proba, vol_forecast=0.02)
    assert score_low_vol > score_high_vol  # High vol should reduce confidence


def test_analyze_feature_drivers():
    """Test feature driver analysis."""
    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "fundingRate": [0.0001, 0.0002, 0.0005, 0.001],
            "funding_slope": [0.0001, 0.0002, 0.0003, 0.0004],
            "oi_pct_chg": [0.01, 0.02, 0.03, 0.08],
            "rv24": [0.02, 0.03, 0.04, 0.05],
            "basis_proxy": [10, 15, 20, 25],
        }
    )

    feature_cols = ["fundingRate", "funding_slope", "oi_pct_chg", "rv24", "basis_proxy"]

    drivers, supporting, contradicting = analyze_feature_drivers(df, feature_cols)

    # Should return lists
    assert isinstance(drivers, list)
    assert isinstance(supporting, list)
    assert isinstance(contradicting, list)

    # Drivers should have (name, percentile) tuples
    if len(drivers) > 0:
        assert isinstance(drivers[0], tuple)
        assert len(drivers[0]) == 2
        assert isinstance(drivers[0][0], str)
        assert isinstance(drivers[0][1], (int, float))


def test_generate_regime_insights():
    """Test comprehensive insights generation."""
    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="1H"),
            "perp_close": np.random.randn(100).cumsum() + 50000,
            "fundingRate": np.random.randn(100) * 0.0001,
            "funding_ema8": np.random.randn(100) * 0.0001,
            "funding_ema24": np.random.randn(100) * 0.0001,
            "funding_slope": np.random.randn(100) * 0.0001,
            "oi_pct_chg": np.random.randn(100) * 0.02,
            "basis_proxy": np.random.randn(100) * 10,
            "rv24": np.random.rand(100) * 0.05,
            "jump_3sigma": np.random.randint(0, 2, 100),
            "regime": np.random.choice(["bull", "bear", "chop"], 100),
        }
    )

    feature_cols = [
        "fundingRate",
        "funding_ema8",
        "funding_ema24",
        "funding_slope",
        "oi_pct_chg",
        "basis_proxy",
        "rv24",
        "jump_3sigma",
    ]

    regime_proba = {"bull": 0.6, "bear": 0.2, "chop": 0.2}

    insights = generate_regime_insights(
        df=df,
        predicted_regime="bull",
        regime_proba=regime_proba,
        mu_forecast=0.02,
        sigma_forecast=0.03,
        feature_cols=feature_cols,
    )

    # Check all fields are populated
    assert isinstance(insights, RegimeInsights)
    assert insights.predicted_regime == "bull"
    assert insights.regime_probabilities == regime_proba
    assert 0 <= insights.confidence_score <= 100
    assert len(insights.regime_description) > 0
    assert len(insights.market_conditions) > 0
    assert len(insights.suggested_actions) > 0
    assert len(insights.risk_level) > 0
    assert len(insights.position_sizing) > 0
    assert isinstance(insights.key_drivers, list)
    assert isinstance(insights.supporting_signals, list)
    assert isinstance(insights.contradicting_signals, list)
    assert isinstance(insights.warnings, list)
    assert isinstance(insights.historical_accuracy, dict)
    assert isinstance(insights.regime_statistics, dict)


def test_generate_regime_insights_with_historical():
    """Test insights generation with historical accuracy data."""
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=50, freq="1H"),
            "fundingRate": np.random.randn(50) * 0.0001,
            "oi_pct_chg": np.random.randn(50) * 0.02,
            "rv24": np.random.rand(50) * 0.05,
            "regime": np.random.choice(["bull", "bear", "chop"], 50),
        }
    )

    feature_cols = ["fundingRate", "oi_pct_chg", "rv24"]
    regime_proba = {"bull": 0.5, "bear": 0.3, "chop": 0.2}

    y_test = pd.Series(["bull", "bear", "bull", "chop", "bull"])
    y_pred = ["bull", "bear", "bull", "bull", "bull"]

    insights = generate_regime_insights(
        df=df,
        predicted_regime="bull",
        regime_proba=regime_proba,
        mu_forecast=0.015,
        sigma_forecast=0.025,
        feature_cols=feature_cols,
        y_test=y_test,
        y_pred=y_pred,
    )

    # Should include historical accuracy
    assert len(insights.historical_accuracy) > 0
    assert all(0 <= acc <= 1 for acc in insights.historical_accuracy.values())
