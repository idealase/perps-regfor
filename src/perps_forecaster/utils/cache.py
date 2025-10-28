"""Parquet cache utilities for data persistence."""

from pathlib import Path
from typing import Optional

import pandas as pd


def ensure_cache_dir(cache_dir: Path) -> None:
    """Create cache directory if it doesn't exist.

    Args:
        cache_dir: Path to cache directory
    """
    cache_dir.mkdir(parents=True, exist_ok=True)


def save_parquet(df: pd.DataFrame, file_path: Path) -> None:
    """Save DataFrame to parquet with directory creation.

    Args:
        df: DataFrame to save
        file_path: Path to output parquet file
    """
    ensure_cache_dir(file_path.parent)
    df.to_parquet(file_path, index=False, engine="pyarrow")


def load_parquet(file_path: Path) -> Optional[pd.DataFrame]:
    """Load DataFrame from parquet if it exists.

    Args:
        file_path: Path to parquet file

    Returns:
        DataFrame if file exists, None otherwise
    """
    if not file_path.exists():
        return None
    try:
        return pd.read_parquet(file_path, engine="pyarrow")
    except Exception:
        return None


def get_cache_path(cache_dir: Path, symbol: str, data_type: str) -> Path:
    """Generate cache file path for a given symbol and data type.

    Args:
        cache_dir: Base cache directory
        symbol: Trading symbol
        data_type: Type of data (e.g., 'funding', 'oi', 'perp_klines')

    Returns:
        Path to cache file
    """
    return cache_dir / f"{symbol}_{data_type}.parquet"
