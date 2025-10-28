"""Test data fetching and alignment."""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from perps_forecaster.data.binance import (align_hourly, fetch_funding_rate,
                                           fetch_open_interest,
                                           fetch_perp_klines,
                                           fetch_spot_klines)


def test_fetch_funding_rate():
    """Test fetching funding rate data."""
    df = fetch_funding_rate(symbol="BTCUSDT", limit=100)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10, "Should fetch at least 10 records"
    assert "fundingTime" in df.columns
    assert "fundingRate" in df.columns
    assert df["fundingRate"].dtype == float


def test_fetch_open_interest():
    """Test fetching open interest data."""
    df = fetch_open_interest(symbol="BTCUSDT", period="1h", limit=100)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10, "Should fetch at least 10 records"
    assert "timestamp" in df.columns
    assert "sumOpenInterest" in df.columns
    assert df["sumOpenInterest"].dtype == float


def test_fetch_perp_klines():
    """Test fetching perpetual klines."""
    df = fetch_perp_klines(pair="BTCUSDT", interval="1h", limit=100)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10, "Should fetch at least 10 records"
    assert "open_time" in df.columns
    assert "perp_close" in df.columns
    assert df["perp_close"].dtype == float


def test_fetch_spot_klines():
    """Test fetching spot klines."""
    df = fetch_spot_klines(symbol="BTCUSDT", interval="1h", limit=100)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10, "Should fetch at least 10 records"
    assert "open_time" in df.columns
    assert "spot_close" in df.columns
    assert df["spot_close"].dtype == float


def test_align_hourly():
    """Test alignment of all data sources."""
    # Fetch data
    funding = fetch_funding_rate(symbol="BTCUSDT", limit=100)
    oi = fetch_open_interest(symbol="BTCUSDT", period="1h", limit=100)
    perp = fetch_perp_klines(pair="BTCUSDT", interval="1h", limit=100)
    spot = fetch_spot_klines(symbol="BTCUSDT", interval="1h", limit=100)

    # Align
    df = align_hourly(funding, oi, perp, spot)

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10, "Should have at least 10 aligned records"
    assert "timestamp" in df.columns
    assert "perp_close" in df.columns
    assert "spot_close" in df.columns
    assert "openInterest" in df.columns
    assert "fundingRate" in df.columns

    # Check no NaNs
    assert df.isna().sum().sum() == 0, "Should have no NaN values after alignment"

    # Check sorted
    assert df["timestamp"].is_monotonic_increasing, "Timestamps should be sorted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
