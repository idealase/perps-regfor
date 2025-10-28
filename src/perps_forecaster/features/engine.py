"""Feature engineering for regime forecasting."""

import numpy as np
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate exponential moving average.

    Args:
        series: Input series
        span: EMA span (number of periods)

    Returns:
        EMA series
    """
    return series.ewm(span=span, adjust=False).mean()


def realized_volatility(returns: pd.Series, window: int = 24) -> pd.Series:
    """Calculate realized volatility from returns.

    Args:
        returns: Log returns series
        window: Rolling window size

    Returns:
        Realized volatility series
    """
    return returns.rolling(window=window).std()


def cyclic_encoding(values: pd.Series, max_val: int) -> tuple[pd.Series, pd.Series]:
    """Encode cyclic features using sin/cos transformation.

    Args:
        values: Values to encode (e.g., hour of day)
        max_val: Maximum value in the cycle

    Returns:
        Tuple of (sin_encoded, cos_encoded)
    """
    angle = 2 * np.pi * values / max_val
    return np.sin(angle), np.cos(angle)


def build_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Build all features for regime forecasting.

    Args:
        df: DataFrame with columns: timestamp, perp_close, spot_close,
            openInterest, fundingRate
        config: Configuration dictionary with feature parameters

    Returns:
        DataFrame with engineered features
    """
    df = df.copy()

    # Log returns
    df["log_return"] = np.log(df["perp_close"] / df["perp_close"].shift(1))

    # Funding rate features
    df["funding_ema8"] = ema(df["fundingRate"], config.get("ema_fast_funding", 8))
    df["funding_ema24"] = ema(df["fundingRate"], config.get("ema_slow_funding", 24))
    df["funding_slope"] = df["funding_ema8"] - df["funding_ema24"]

    # Open interest percentage change
    df["oi_pct_chg"] = df["openInterest"].pct_change()
    df["oi_pct_chg"] = df["oi_pct_chg"].clip(
        config.get("oi_clip_min", -0.2), config.get("oi_clip_max", 0.2)
    )

    # Basis proxy (perp - spot)
    df["basis_proxy"] = df["perp_close"] - df["spot_close"]

    # Realized volatility
    rv_window = config.get("rv_window", 24)
    df["rv24"] = realized_volatility(df["log_return"], window=rv_window)

    # Jump detection (3-sigma events)
    jump_window = config.get("jump_sigma_window", 24)
    jump_threshold = config.get("jump_threshold", 3.0)
    rolling_std = df["log_return"].rolling(window=jump_window).std()
    df["jump_3sigma"] = (np.abs(df["log_return"]) > jump_threshold * rolling_std).astype(int)

    # Price EMAs for trend
    df["price_ema12"] = ema(df["perp_close"], config.get("ema_fast_price", 12))
    df["price_ema48"] = ema(df["perp_close"], config.get("ema_slow_price", 48))

    # Cyclic time encodings
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["hour_sin"], df["hour_cos"] = cyclic_encoding(df["hour"], 24)
    df["dow_sin"], df["dow_cos"] = cyclic_encoding(df["day_of_week"], 7)

    return df


def create_regime_labels(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Create regime labels: bull, bear, or chop.

    Logic:
    1. Calculate future return (horizon bars ahead)
    2. Determine trend: EMA(12) vs EMA(48)
    3. Volatility gate: above median rv24 keeps bull/bear, else chop
    4. Assign regime based on future return sign and trend

    Args:
        df: DataFrame with features (must include price_ema12, price_ema48, rv24)
        horizon: Number of bars ahead to predict

    Returns:
        DataFrame with 'regime' column added
    """
    df = df.copy()

    # Future return
    df["future_return"] = df["log_return"].shift(-horizon)

    # Trend: uptrend if fast EMA > slow EMA
    df["uptrend"] = (df["price_ema12"] > df["price_ema48"]).astype(int)

    # Volatility gate: above median
    rv_median = df["rv24"].median()
    df["high_vol"] = (df["rv24"] > rv_median).astype(int)

    # Initialize regime as 'chop'
    df["regime"] = "chop"

    # Bull: positive future return, uptrend, high vol
    bull_mask = (df["future_return"] > 0) & (df["uptrend"] == 1) & (df["high_vol"] == 1)
    df.loc[bull_mask, "regime"] = "bull"

    # Bear: negative future return, downtrend, high vol
    bear_mask = (df["future_return"] < 0) & (df["uptrend"] == 0) & (df["high_vol"] == 1)
    df.loc[bear_mask, "regime"] = "bear"

    # Drop helper columns
    df = df.drop(columns=["future_return", "uptrend", "high_vol"])

    return df


def get_feature_columns() -> list[str]:
    """Return list of feature column names for modeling.

    Returns:
        List of feature column names
    """
    return [
        "fundingRate",
        "funding_ema8",
        "funding_ema24",
        "funding_slope",
        "oi_pct_chg",
        "basis_proxy",
        "rv24",
        "jump_3sigma",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
    ]
