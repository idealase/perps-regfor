"""Evaluation metrics for forecasts."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error


def smape(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Calculate symmetric Mean Absolute Percentage Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        sMAPE value (0-100 scale)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    diff = np.abs(y_true - y_pred)

    # Avoid division by zero
    mask = denominator != 0
    smape_values = np.zeros_like(diff)
    smape_values[mask] = diff[mask] / denominator[mask]

    return float(np.mean(smape_values) * 100)


def qlike(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Calculate QLIKE (Quasi-Likelihood) loss for volatility forecasts.

    QLIKE = log(σ²_pred) + σ²_true / σ²_pred

    Args:
        y_true: True volatility values (standard deviation)
        y_pred: Predicted volatility values (standard deviation)

    Returns:
        Mean QLIKE loss
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Convert to variance (σ²)
    var_true = y_true**2
    var_pred = y_pred**2

    # Avoid division by zero or log of zero
    var_pred = np.maximum(var_pred, 1e-10)

    qlike_values = np.log(var_pred) + var_true / var_pred

    return float(np.mean(qlike_values))


def rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Calculate Root Mean Squared Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        RMSE value
    """
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))
