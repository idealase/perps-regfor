"""Point and volatility forecasting models."""

from typing import Tuple

import numpy as np
import pandas as pd


def forecast_point_and_vol(returns: pd.Series, horizon: int = 1) -> Tuple[float, float]:
    """Forecast mean and volatility using ARIMA and GARCH.

    Args:
        returns: Historical log returns
        horizon: Forecast horizon (number of periods ahead)

    Returns:
        Tuple of (mu_hat, sigma_hat)
    """
    # Remove NaN values
    returns_clean = returns.dropna()

    if len(returns_clean) < 50:
        # Not enough data, return naive estimates
        return returns_clean.mean(), returns_clean.std()

    try:
        # ARIMA(1,0,1) for mean forecast
        from statsmodels.tsa.arima.model import ARIMA

        arima_model = ARIMA(returns_clean, order=(1, 0, 1))
        arima_fit = arima_model.fit(method_kwargs={"warn_convergence": False})
        mu_forecast = arima_fit.forecast(steps=horizon)
        mu_hat = mu_forecast.iloc[-1] if hasattr(mu_forecast, "iloc") else mu_forecast[-1]

    except Exception:
        # Fallback to simple mean
        mu_hat = returns_clean.mean()

    try:
        # GARCH(1,1) for volatility forecast
        from arch import arch_model

        # Scale returns to percentage for better GARCH convergence
        returns_pct = returns_clean * 100

        garch_model = arch_model(returns_pct, vol="Garch", p=1, q=1, rescale=False)
        garch_fit = garch_model.fit(disp="off", show_warning=False)
        vol_forecast = garch_fit.forecast(horizon=horizon)
        sigma_hat = np.sqrt(vol_forecast.variance.values[-1, -1]) / 100  # Scale back

    except Exception:
        # Fallback to simple std
        sigma_hat = returns_clean.std()

    return float(mu_hat), float(sigma_hat)


def forecast_next_bar(df: pd.DataFrame, horizon: int = 1) -> Tuple[float, float]:
    """Forecast next bar mean return and volatility.

    Args:
        df: DataFrame with 'log_return' column
        horizon: Forecast horizon

    Returns:
        Tuple of (mu_hat, sigma_hat)
    """
    if "log_return" not in df.columns:
        raise ValueError("DataFrame must contain 'log_return' column")

    returns = df["log_return"]
    return forecast_point_and_vol(returns, horizon=horizon)
