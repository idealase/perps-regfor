"""Test feature engineering."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from perps_forecaster.features.engine import (build_features, cyclic_encoding,
                                              ema, get_feature_columns,
                                              realized_volatility)


def create_synthetic_dataframe(n: int = 200) -> pd.DataFrame:
    """Create synthetic dataframe for testing."""
    dates = pd.date_range("2024-01-01", periods=n, freq="H")

    df = pd.DataFrame(
        {
            "timestamp": dates,
            "perp_close": 50000 + np.cumsum(np.random.randn(n) * 100),
            "spot_close": 50000 + np.cumsum(np.random.randn(n) * 100),
            "openInterest": 1e9 + np.cumsum(np.random.randn(n) * 1e7),
            "fundingRate": np.random.randn(n) * 0.0001,
        }
    )

    return df


def test_ema():
    """Test EMA calculation."""
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    result = ema(series, span=3)

    assert len(result) == len(series)
    assert not result.isna().all()
    assert result.iloc[-1] > result.iloc[0]  # Upward trend


def test_realized_volatility():
    """Test realized volatility calculation."""
    returns = pd.Series(np.random.randn(100) * 0.01)
    rv = realized_volatility(returns, window=24)

    assert len(rv) == len(returns)
    assert rv.isna().sum() == 23  # First 23 values should be NaN


def test_cyclic_encoding():
    """Test cyclic encoding."""
    hours = pd.Series([0, 6, 12, 18, 23])
    sin_vals, cos_vals = cyclic_encoding(hours, max_val=24)

    assert len(sin_vals) == len(hours)
    assert len(cos_vals) == len(hours)

    # Check 0 and 12 hour encoding
    assert abs(sin_vals.iloc[0]) < 0.01  # sin(0) ≈ 0
    assert abs(cos_vals.iloc[0] - 1) < 0.01  # cos(0) ≈ 1


def test_build_features():
    """Test full feature building pipeline."""
    df = create_synthetic_dataframe(n=200)

    config = {
        "ema_fast_funding": 8,
        "ema_slow_funding": 24,
        "ema_fast_price": 12,
        "ema_slow_price": 48,
        "rv_window": 24,
        "jump_sigma_window": 24,
        "jump_threshold": 3.0,
        "oi_clip_min": -0.2,
        "oi_clip_max": 0.2,
    }

    result = build_features(df, config)

    # Check expected columns exist
    expected_cols = [
        "rv24",
        "oi_pct_chg",
        "basis_proxy",
        "funding_ema8",
        "funding_ema24",
        "funding_slope",
        "jump_3sigma",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
    ]

    for col in expected_cols:
        assert col in result.columns, f"Missing column: {col}"

    # Check no infinite values
    assert not np.isinf(result.select_dtypes(include=[np.number]).values).any()


def test_get_feature_columns():
    """Test feature column list."""
    cols = get_feature_columns()

    assert isinstance(cols, list)
    assert len(cols) > 0
    assert "rv24" in cols
    assert "oi_pct_chg" in cols
    assert "basis_proxy" in cols


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
