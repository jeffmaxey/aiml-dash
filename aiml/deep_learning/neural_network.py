"""
Deep Learning – Neural Network
================================

Provides :class:`NeuralNetwork`, a multi-layer perceptron (MLP) that supports
both classification and regression tasks.

Built on top of scikit-learn's :class:`sklearn.neural_network.MLPClassifier`
and :class:`sklearn.neural_network.MLPRegressor`.
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler

from aiml.base import BaseModel


class NeuralNetwork(BaseModel):
    """Multi-layer perceptron (MLP) neural network.

    Supports both **regression** and **classification** tasks via a
    ``task`` parameter.  The underlying estimator is either
    :class:`sklearn.neural_network.MLPRegressor` or
    :class:`sklearn.neural_network.MLPClassifier`.

    Parameters
    ----------
    task:
        ``"regression"`` or ``"classification"``. Default ``"regression"``.
    hidden_layer_sizes:
        Tuple specifying the number of neurons in each hidden layer.
        Default ``(100,)`` (one hidden layer with 100 neurons).
    activation:
        Activation function (``"relu"``, ``"tanh"``, ``"logistic"``).
        Default ``"relu"``.
    solver:
        Weight optimisation solver (``"adam"``, ``"sgd"``, ``"lbfgs"``).
        Default ``"adam"``.
    alpha:
        L2 regularisation term. Default ``1e-4``.
    max_iter:
        Maximum number of training iterations. Default ``200``.
    random_state:
        Seed for reproducibility.
    standardize:
        Standardise inputs before training/inference. Default ``True``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.deep_learning.neural_network import NeuralNetwork
    >>> rng = np.random.default_rng(0)
    >>> X = rng.standard_normal((50, 4))
    >>> y = (X[:, 0] + X[:, 1] > 0).astype(int)
    >>> model = NeuralNetwork(task="classification", max_iter=500, random_state=0)
    >>> model.fit(X, y)
    NeuralNetwork(...)
    >>> preds = model.predict(X)
    >>> len(preds) == 50
    True
    """

    def __init__(
        self,
        *,
        task: Literal["regression", "classification"] = "regression",
        hidden_layer_sizes: tuple[int, ...] = (100,),
        activation: str = "relu",
        solver: str = "adam",
        alpha: float = 1e-4,
        max_iter: int = 200,
        random_state: int | None = None,
        standardize: bool = True,
        **kwargs: Any,
    ) -> None:
        if task not in {"regression", "classification"}:
            msg = "task must be 'regression' or 'classification'"
            raise ValueError(msg)

        self._task = task
        self._standardize = standardize
        self._scaler = StandardScaler() if standardize else None
        self._is_fitted = False

        shared = {
            "hidden_layer_sizes": hidden_layer_sizes,
            "activation": activation,
            "solver": solver,
            "alpha": alpha,
            "max_iter": max_iter,
            "random_state": random_state,
            **kwargs,
        }

        if task == "regression":
            self._estimator: MLPRegressor | MLPClassifier = MLPRegressor(**shared)
        else:
            self._estimator = MLPClassifier(**shared)

    # ------------------------------------------------------------------ #

    def _prepare(self, X: Any, fit: bool = False) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if self._scaler is not None:
            if fit:
                X = self._scaler.fit_transform(X)
            else:
                X = self._scaler.transform(X)
        return X

    def fit(self, X: Any, y: Any = None) -> "NeuralNetwork":
        """Train the neural network.

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
        X_prep = self._prepare(X, fit=True)
        self._estimator.fit(X_prep, y)
        self._is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Generate predictions.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        y_pred : np.ndarray
        """
        return self._estimator.predict(self._prepare(X))

    def predict_proba(self, X: Any) -> np.ndarray:
        """Predict class probabilities (classification only).

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        proba : np.ndarray, shape (n_samples, n_classes)

        Raises
        ------
        AttributeError
            When called on a regression network.
        """
        if self._task != "classification":
            msg = "predict_proba is only available for classification tasks."
            raise AttributeError(msg)
        return self._estimator.predict_proba(self._prepare(X))  # type: ignore[union-attr]

    def evaluate(self, X: Any, y: Any) -> dict[str, Any]:
        """Compute task-specific evaluation metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            True target values.

        Returns
        -------
        metrics : dict
            Regression: ``{"r2", "mse", "rmse", "mae"}``
            Classification: ``{"accuracy", "f1", "confusion_matrix", ...}``
        """
        y_pred = self.predict(X)
        if self._task == "regression":
            mse = mean_squared_error(y, y_pred)
            return {
                "r2": float(r2_score(y, y_pred)),
                "mse": float(mse),
                "rmse": float(np.sqrt(mse)),
                "mae": float(mean_absolute_error(y, y_pred)),
            }
        return {
            "accuracy": float(accuracy_score(y, y_pred)),
            "f1": float(f1_score(y, y_pred, average="weighted", zero_division=0)),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "classification_report": classification_report(y, y_pred, output_dict=True),
        }

    def summary(self) -> dict[str, Any]:
        """Return model summary.

        Returns
        -------
        info : dict
        """
        info: dict[str, Any] = {
            "model": type(self).__name__,
            "task": self._task,
            "params": self.get_params(),
        }
        if self._is_fitted:
            info["n_iter"] = int(self._estimator.n_iter_)
            info["loss"] = float(self._estimator.loss_)
        return info
