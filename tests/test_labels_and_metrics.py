"""Test label creation and metrics."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from perps_forecaster.eval.metrics import qlike, rmse, smape
from perps_forecaster.features.engine import (build_features,
                                              create_regime_labels)


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


def test_create_regime_labels():
    """Test regime label creation."""
    df = create_synthetic_dataframe(n=200)

    # Build features first
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

    df = build_features(df, config)

    # Create labels
    result = create_regime_labels(df, horizon=1)

    # Check regime column exists
    assert "regime" in result.columns

    # Check regime values are valid
    valid_regimes = {"bull", "bear", "chop"}
    unique_regimes = set(result["regime"].dropna().unique())
    assert unique_regimes.issubset(valid_regimes), f"Invalid regimes: {unique_regimes}"

    # Check at least some labels exist
    assert len(result["regime"].dropna()) > 0


def test_smape():
    """Test sMAPE calculation."""
    y_true = pd.Series([100, 200, 300, 400])
    y_pred = pd.Series([110, 190, 310, 390])

    result = smape(y_true, y_pred)

    assert isinstance(result, float)
    assert 0 <= result <= 100
    assert result > 0  # Should have some error


def test_smape_perfect():
    """Test sMAPE with perfect predictions."""
    y_true = pd.Series([100, 200, 300, 400])
    y_pred = pd.Series([100, 200, 300, 400])

    result = smape(y_true, y_pred)

    assert result == 0.0


def test_qlike():
    """Test QLIKE calculation."""
    y_true = pd.Series([0.01, 0.02, 0.015, 0.025])
    y_pred = pd.Series([0.011, 0.019, 0.016, 0.024])

    result = qlike(y_true, y_pred)

    assert isinstance(result, float)
    assert not np.isnan(result)
    assert not np.isinf(result)


def test_rmse():
    """Test RMSE calculation."""
    y_true = pd.Series([1.0, 2.0, 3.0, 4.0])
    y_pred = pd.Series([1.1, 2.1, 2.9, 3.9])

    result = rmse(y_true, y_pred)

    assert isinstance(result, float)
    assert result > 0
    assert result < 1  # Should be small for close predictions


def test_rmse_perfect():
    """Test RMSE with perfect predictions."""
    y_true = pd.Series([1.0, 2.0, 3.0, 4.0])
    y_pred = pd.Series([1.0, 2.0, 3.0, 4.0])

    result = rmse(y_true, y_pred)

    assert result == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
