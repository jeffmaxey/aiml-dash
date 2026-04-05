"""
Supervised Learning – Generalised Linear Models
=================================================

Provides regularised regression models:

* :class:`Ridge` – L2-penalised regression
* :class:`Lasso` – L1-penalised regression
* :class:`ElasticNet` – L1+L2 mixed penalty
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import (
    ElasticNet as _SKElasticNet,
    Lasso as _SKLasso,
    Ridge as _SKRidge,
)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from aiml.base import BaseModel


class _RegularisedRegressor(BaseModel):
    """Shared implementation for Ridge, Lasso, and ElasticNet."""

    _estimator: Any

    def fit(self, X: Any, y: Any = None) -> "_RegularisedRegressor":
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
        if getattr(self, "_is_fitted", False):
            info["coef"] = self._estimator.coef_.tolist()
            info["intercept"] = float(self._estimator.intercept_)
        return info


# --------------------------------------------------------------------------- #


class Ridge(_RegularisedRegressor):
    """Ridge regression (L2 regularisation).

    Wraps :class:`sklearn.linear_model.Ridge`.

    Parameters
    ----------
    alpha:
        Regularisation strength. Larger values enforce stronger
        regularisation. Default ``1.0``.
    fit_intercept:
        Whether to fit an intercept. Default ``True``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.glm import Ridge
    >>> X = np.array([[1], [2], [3], [4]])
    >>> y = np.array([2.0, 4.0, 6.0, 8.0])
    >>> model = Ridge(alpha=0.5)
    >>> model.fit(X, y)
    Ridge(...)
    >>> model.evaluate(X, y)["r2"] > 0.99
    True
    """

    def __init__(self, *, alpha: float = 1.0, fit_intercept: bool = True, **kwargs: Any) -> None:
        self._estimator = _SKRidge(alpha=alpha, fit_intercept=fit_intercept, **kwargs)
        self._is_fitted = False


class Lasso(_RegularisedRegressor):
    """Lasso regression (L1 regularisation).

    Wraps :class:`sklearn.linear_model.Lasso`.

    Parameters
    ----------
    alpha:
        Regularisation strength. Default ``1.0``.
    fit_intercept:
        Whether to fit an intercept. Default ``True``.
    max_iter:
        Maximum number of iterations. Default ``1000``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.glm import Lasso
    >>> X = np.array([[1], [2], [3], [4]])
    >>> y = np.array([2.0, 4.0, 6.0, 8.0])
    >>> model = Lasso(alpha=0.01)
    >>> model.fit(X, y)
    Lasso(...)
    """

    def __init__(
        self,
        *,
        alpha: float = 1.0,
        fit_intercept: bool = True,
        max_iter: int = 1000,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKLasso(
            alpha=alpha,
            fit_intercept=fit_intercept,
            max_iter=max_iter,
            **kwargs,
        )
        self._is_fitted = False


class ElasticNet(_RegularisedRegressor):
    """Elastic-net regression (L1 + L2 regularisation).

    Wraps :class:`sklearn.linear_model.ElasticNet`.

    Parameters
    ----------
    alpha:
        Regularisation strength. Default ``1.0``.
    l1_ratio:
        Mix ratio between L1 and L2 (``0`` → ridge, ``1`` → lasso).
        Default ``0.5``.
    fit_intercept:
        Whether to fit an intercept. Default ``True``.
    max_iter:
        Maximum number of iterations. Default ``1000``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.glm import ElasticNet
    >>> X = np.array([[1], [2], [3], [4]])
    >>> y = np.array([2.0, 4.0, 6.0, 8.0])
    >>> model = ElasticNet(alpha=0.01, l1_ratio=0.5)
    >>> model.fit(X, y)
    ElasticNet(...)
    """

    def __init__(
        self,
        *,
        alpha: float = 1.0,
        l1_ratio: float = 0.5,
        fit_intercept: bool = True,
        max_iter: int = 1000,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKElasticNet(
            alpha=alpha,
            l1_ratio=l1_ratio,
            fit_intercept=fit_intercept,
            max_iter=max_iter,
            **kwargs,
        )
        self._is_fitted = False
