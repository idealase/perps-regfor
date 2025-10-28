"""Configuration dataclass for the regime forecaster."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration for the perps regime forecaster."""

    # Trading pair
    symbol: str = "BTCUSDT"
    interval: str = "1h"

    # Display timezone
    display_tz: str = "Australia/Perth"

    # Data cache
    cache_dir: Path = Path("data")

    # Safety caps
    max_rows: int = 2000
    default_lookback: int = 500
    default_horizon: int = 1

    # API settings
    http_timeout: int = 30
    max_retries: int = 3

    # Feature windows
    ema_fast_funding: int = 8
    ema_slow_funding: int = 24
    ema_fast_price: int = 12
    ema_slow_price: int = 48
    rv_window: int = 24
    jump_sigma_window: int = 24
    jump_threshold: float = 3.0

    # OI clipping
    oi_clip_min: float = -0.2
    oi_clip_max: float = 0.2


# Global default instance
default_config = Config()
