"""Regime classification models."""

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, confusion_matrix
from sklearn.preprocessing import StandardScaler


def train_regime_classifier(
    X: pd.DataFrame, y: pd.Series, model_type: str = "logistic"
) -> Tuple[Any, StandardScaler]:
    """Train a regime classifier with feature scaling.

    Args:
        X: Feature matrix
        y: Target labels (bull, bear, chop)
        model_type: Type of model ('logistic' or 'lightgbm')

    Returns:
        Tuple of (trained_model, fitted_scaler)
    """
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if model_type == "lightgbm":
        try:
            from lightgbm import LGBMClassifier

            model = LGBMClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
                verbose=-1,
            )
        except ImportError:
            # Fallback to logistic regression
            model = LogisticRegression(max_iter=1000, random_state=42, multi_class="multinomial")
    else:
        model = LogisticRegression(max_iter=1000, random_state=42, multi_class="multinomial")

    model.fit(X_scaled, y)

    return model, scaler


def predict_regime_proba(
    model: Any, scaler: StandardScaler, X: pd.DataFrame
) -> Tuple[np.ndarray, list[str]]:
    """Predict regime probabilities.

    Args:
        model: Trained classifier
        scaler: Fitted StandardScaler
        X: Feature matrix

    Returns:
        Tuple of (probability_matrix, class_names)
    """
    X_scaled = scaler.transform(X)
    proba = model.predict_proba(X_scaled)
    classes = model.classes_.tolist()

    return proba, classes


def calculate_brier_scores(y_true: pd.Series, y_proba: np.ndarray, classes: list[str]) -> Dict[str, float]:
    """Calculate Brier score for each class.

    Args:
        y_true: True labels
        y_proba: Predicted probabilities (n_samples, n_classes)
        classes: Class names

    Returns:
        Dictionary mapping class name to Brier score
    """
    brier_scores = {}

    for i, cls in enumerate(classes):
        # Create binary indicator for this class
        y_binary = (y_true == cls).astype(int)
        y_prob_cls = y_proba[:, i]

        brier = brier_score_loss(y_binary, y_prob_cls)
        brier_scores[cls] = brier

    return brier_scores


def get_confusion_matrix(y_true: pd.Series, y_pred: pd.Series, classes: list[str]) -> pd.DataFrame:
    """Generate confusion matrix as DataFrame.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        classes: Class names

    Returns:
        Confusion matrix as DataFrame
    """
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    return pd.DataFrame(cm, index=classes, columns=classes)


def evaluate_classifier(
    model: Any,
    scaler: StandardScaler,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Dict[str, Any]:
    """Evaluate classifier performance.

    Args:
        model: Trained classifier
        scaler: Fitted StandardScaler
        X_test: Test feature matrix
        y_test: Test labels

    Returns:
        Dictionary with evaluation metrics
    """
    # Predictions
    y_proba, classes = predict_regime_proba(model, scaler, X_test)
    y_pred = pd.Series([classes[i] for i in y_proba.argmax(axis=1)], index=X_test.index)

    # Metrics
    brier_scores = calculate_brier_scores(y_test, y_proba, classes)
    cm = get_confusion_matrix(y_test, y_pred, classes)

    # Accuracy
    accuracy = (y_pred == y_test).mean()

    return {
        "accuracy": accuracy,
        "brier_scores": brier_scores,
        "confusion_matrix": cm,
        "classes": classes,
    }
