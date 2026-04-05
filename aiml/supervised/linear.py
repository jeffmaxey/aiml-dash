"""
Supervised Learning – Linear Models
====================================

Provides :class:`LinearRegression` and :class:`LogisticRegression`.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import (
    LinearRegression as _SKLinearRegression,
    LogisticRegression as _SKLogisticRegression,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)

from aiml.base import BaseModel


class LinearRegression(BaseModel):
    """Ordinary least squares linear regression.

    Wraps :class:`sklearn.linear_model.LinearRegression`.

    Parameters
    ----------
    fit_intercept:
        Whether to fit an intercept term. Default ``True``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.linear import LinearRegression
    >>> X = np.array([[1], [2], [3], [4]])
    >>> y = np.array([2, 4, 6, 8])
    >>> model = LinearRegression()
    >>> model.fit(X, y)
    LinearRegression(...)
    >>> model.predict(np.array([[5]]))
    array([10.])
    """

    def __init__(self, *, fit_intercept: bool = True, **kwargs: Any) -> None:
        self._estimator = _SKLinearRegression(fit_intercept=fit_intercept, **kwargs)
        self._is_fitted = False
        self._coef_: np.ndarray | None = None
        self._intercept_: float | None = None

    # ------------------------------------------------------------------ #

    def fit(self, X: Any, y: Any = None) -> "LinearRegression":
        """Fit the model.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Target vector (required).

        Returns
        -------
        self
        """
        self._estimator.fit(X, y)
        self._is_fitted = True
        self._coef_ = self._estimator.coef_
        self._intercept_ = float(self._estimator.intercept_)
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Return predicted values.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        y_pred : np.ndarray
        """
        return self._estimator.predict(X)

    def evaluate(self, X: Any, y: Any) -> dict[str, float]:
        """Compute regression metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            True target values.

        Returns
        -------
        metrics : dict
            ``{"r2": float, "mse": float, "rmse": float, "mae": float}``
        """
        y_pred = self.predict(X)
        mse = mean_squared_error(y, y_pred)
        return {
            "r2": float(r2_score(y, y_pred)),
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "mae": float(mean_absolute_error(y, y_pred)),
        }

    def summary(self) -> dict[str, Any]:
        """Return model summary including coefficients.

        Returns
        -------
        info : dict
        """
        info: dict[str, Any] = {
            "model": type(self).__name__,
            "params": self.get_params(),
        }
        if self._is_fitted:
            info["coef"] = self._coef_.tolist() if self._coef_ is not None else None
            info["intercept"] = self._intercept_
        return info


# --------------------------------------------------------------------------- #


class LogisticRegression(BaseModel):
    """Logistic regression classifier.

    Wraps :class:`sklearn.linear_model.LogisticRegression`.

    Parameters
    ----------
    C:
        Inverse regularisation strength. Smaller values enforce stronger
        regularisation. Default ``1.0``.
    l1_ratio:
        Mix ratio between L1 and L2. ``0`` → L2 (ridge), ``1`` → L1 (lasso).
        When ``None`` the solver uses L2 regularisation. Default ``None``.
    max_iter:
        Maximum number of solver iterations. Default ``1000``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.linear import LogisticRegression
    >>> X = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    >>> y = np.array([0, 0, 1, 1])
    >>> model = LogisticRegression()
    >>> model.fit(X, y)
    LogisticRegression(...)
    >>> model.predict(np.array([[1.5, 1.5]]))
    array([...])
    """

    def __init__(
        self,
        *,
        C: float = 1.0,
        l1_ratio: float | None = None,
        max_iter: int = 1000,
        **kwargs: Any,
    ) -> None:
        if l1_ratio is not None:
            kwargs["l1_ratio"] = l1_ratio
        self._estimator = _SKLogisticRegression(
            C=C,
            max_iter=max_iter,
            **kwargs,
        )
        self._is_fitted = False

    # ------------------------------------------------------------------ #

    def fit(self, X: Any, y: Any = None) -> "LogisticRegression":
        """Fit the classifier.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Target class labels (required).

        Returns
        -------
        self
        """
        self._estimator.fit(X, y)
        self._is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict class labels.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        y_pred : np.ndarray
        """
        return self._estimator.predict(X)

    def predict_proba(self, X: Any) -> np.ndarray:
        """Predict class probabilities.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        proba : np.ndarray, shape (n_samples, n_classes)
        """
        return self._estimator.predict_proba(X)

    def evaluate(self, X: Any, y: Any) -> dict[str, Any]:
        """Compute classification metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            True class labels.

        Returns
        -------
        metrics : dict
            ``{"accuracy": float, "f1": float, "confusion_matrix": list, ...}``
        """
        y_pred = self.predict(X)
        classes = self._estimator.classes_
        metrics: dict[str, Any] = {
            "accuracy": float(accuracy_score(y, y_pred)),
            "f1": float(f1_score(y, y_pred, average="weighted", zero_division=0)),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "classification_report": classification_report(y, y_pred, output_dict=True),
        }
        if len(classes) == 2:
            proba = self.predict_proba(X)[:, 1]
            metrics["roc_auc"] = float(roc_auc_score(y, proba))
        return metrics

    def summary(self) -> dict[str, Any]:
        """Return model summary.

        Returns
        -------
        info : dict
        """
        info: dict[str, Any] = {
            "model": type(self).__name__,
            "params": self.get_params(),
        }
        if self._is_fitted:
            info["classes"] = self._estimator.classes_.tolist()
            info["coef"] = self._estimator.coef_.tolist()
            info["intercept"] = self._estimator.intercept_.tolist()
        return info
