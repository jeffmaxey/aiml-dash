"""
Supervised Learning – Tree-Based Models
=========================================

Provides the following estimators:

* :class:`DecisionTreeRegressor`
* :class:`DecisionTreeClassifier`
* :class:`RandomForestRegressor`
* :class:`RandomForestClassifier`
* :class:`GradientBoostingRegressor`
* :class:`GradientBoostingClassifier`
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import (
    GradientBoostingClassifier as _SKGBClassifier,
    GradientBoostingRegressor as _SKGBRegressor,
    RandomForestClassifier as _SKRFClassifier,
    RandomForestRegressor as _SKRFRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.tree import (
    DecisionTreeClassifier as _SKDTClassifier,
    DecisionTreeRegressor as _SKDTRegressor,
)

from aiml.base import BaseModel


# --------------------------------------------------------------------------- #
# Internal mixins                                                              #
# --------------------------------------------------------------------------- #


class _RegressorMixin:
    """Shared evaluation logic for tree regressors."""

    _estimator: Any

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
        y_pred = self.predict(X)  # type: ignore[attr-defined]
        mse = mean_squared_error(y, y_pred)
        return {
            "r2": float(r2_score(y, y_pred)),
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "mae": float(mean_absolute_error(y, y_pred)),
        }


class _ClassifierMixin:
    """Shared evaluation logic for tree classifiers."""

    _estimator: Any

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
        y_pred = self.predict(X)  # type: ignore[attr-defined]
        return {
            "accuracy": float(accuracy_score(y, y_pred)),
            "f1": float(f1_score(y, y_pred, average="weighted", zero_division=0)),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "classification_report": classification_report(y, y_pred, output_dict=True),
        }

    def predict_proba(self, X: Any) -> np.ndarray:
        """Predict class probabilities.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        proba : np.ndarray
        """
        return self._estimator.predict_proba(X)


class _TreeBase(BaseModel):
    """Base for all tree models – provides fit/predict/summary."""

    _estimator: Any
    _is_fitted: bool = False

    def fit(self, X: Any, y: Any = None) -> "_TreeBase":
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
        """Return predictions.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        y_pred : np.ndarray
        """
        return self._estimator.predict(X)

    def summary(self) -> dict[str, Any]:
        """Return model summary including feature importances.

        Returns
        -------
        info : dict
        """
        info: dict[str, Any] = {
            "model": type(self).__name__,
            "params": self.get_params(),
        }
        if self._is_fitted and hasattr(self._estimator, "feature_importances_"):
            info["feature_importances"] = self._estimator.feature_importances_.tolist()
        return info


# --------------------------------------------------------------------------- #
# Decision Trees                                                               #
# --------------------------------------------------------------------------- #


class DecisionTreeRegressor(_RegressorMixin, _TreeBase):
    """Decision tree regressor (CART).

    Wraps :class:`sklearn.tree.DecisionTreeRegressor`.

    Parameters
    ----------
    max_depth:
        Maximum tree depth. ``None`` expands until leaves are pure.
    min_samples_leaf:
        Minimum samples required at a leaf node. Default ``1``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.trees import DecisionTreeRegressor
    >>> X = np.array([[1], [2], [3], [4]])
    >>> y = np.array([2.0, 4.0, 6.0, 8.0])
    >>> model = DecisionTreeRegressor(max_depth=3)
    >>> model.fit(X, y)
    DecisionTreeRegressor(...)
    """

    def __init__(
        self,
        *,
        max_depth: int | None = None,
        min_samples_leaf: int = 1,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKDTRegressor(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            **kwargs,
        )
        self._is_fitted = False


class DecisionTreeClassifier(_ClassifierMixin, _TreeBase):
    """Decision tree classifier (CART).

    Wraps :class:`sklearn.tree.DecisionTreeClassifier`.

    Parameters
    ----------
    max_depth:
        Maximum tree depth.
    min_samples_leaf:
        Minimum samples required at a leaf node. Default ``1``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.supervised.trees import DecisionTreeClassifier
    >>> X = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    >>> y = np.array([0, 0, 1, 1])
    >>> model = DecisionTreeClassifier(max_depth=3)
    >>> model.fit(X, y)
    DecisionTreeClassifier(...)
    """

    def __init__(
        self,
        *,
        max_depth: int | None = None,
        min_samples_leaf: int = 1,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKDTClassifier(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            **kwargs,
        )
        self._is_fitted = False


# --------------------------------------------------------------------------- #
# Random Forests                                                               #
# --------------------------------------------------------------------------- #


class RandomForestRegressor(_RegressorMixin, _TreeBase):
    """Random forest regressor.

    Wraps :class:`sklearn.ensemble.RandomForestRegressor`.

    Parameters
    ----------
    n_estimators:
        Number of trees. Default ``100``.
    max_depth:
        Maximum tree depth. ``None`` expands until leaves are pure.
    random_state:
        Seed for reproducibility.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        max_depth: int | None = None,
        random_state: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKRFRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            **kwargs,
        )
        self._is_fitted = False


class RandomForestClassifier(_ClassifierMixin, _TreeBase):
    """Random forest classifier.

    Wraps :class:`sklearn.ensemble.RandomForestClassifier`.

    Parameters
    ----------
    n_estimators:
        Number of trees. Default ``100``.
    max_depth:
        Maximum tree depth.
    random_state:
        Seed for reproducibility.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        max_depth: int | None = None,
        random_state: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKRFClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            **kwargs,
        )
        self._is_fitted = False


# --------------------------------------------------------------------------- #
# Gradient Boosting                                                            #
# --------------------------------------------------------------------------- #


class GradientBoostingRegressor(_RegressorMixin, _TreeBase):
    """Gradient boosting regressor.

    Wraps :class:`sklearn.ensemble.GradientBoostingRegressor`.

    Parameters
    ----------
    n_estimators:
        Number of boosting stages. Default ``100``.
    learning_rate:
        Shrinkage applied to each tree. Default ``0.1``.
    max_depth:
        Maximum individual tree depth. Default ``3``.
    random_state:
        Seed for reproducibility.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        random_state: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
            **kwargs,
        )
        self._is_fitted = False


class GradientBoostingClassifier(_ClassifierMixin, _TreeBase):
    """Gradient boosting classifier.

    Wraps :class:`sklearn.ensemble.GradientBoostingClassifier`.

    Parameters
    ----------
    n_estimators:
        Number of boosting stages. Default ``100``.
    learning_rate:
        Shrinkage applied to each tree. Default ``0.1``.
    max_depth:
        Maximum individual tree depth. Default ``3``.
    random_state:
        Seed for reproducibility.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        random_state: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKGBClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
            **kwargs,
        )
        self._is_fitted = False
