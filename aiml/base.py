"""
Base Model
==========

Abstract base class providing a unified interface for all ``aiml`` models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    """Abstract base class for all ``aiml`` models.

    All models expose the same interface:

    * :meth:`fit` – fit the model to training data.
    * :meth:`predict` – generate predictions.
    * :meth:`evaluate` – compute evaluation metrics.
    * :meth:`summary` – return a human-readable summary dict.
    * :meth:`get_params` / :meth:`set_params` – hyperparameter access.
    """

    # Sub-classes must set ``_estimator`` to the wrapped scikit-learn estimator.
    _estimator: Any = None

    # ------------------------------------------------------------------ #
    # Abstract interface                                                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def fit(self, X: Any, y: Any = None) -> "BaseModel":
        """Fit the model to training data.

        Parameters
        ----------
        X:
            Feature matrix (array-like or :class:`pandas.DataFrame`).
        y:
            Target vector. ``None`` for unsupervised models.

        Returns
        -------
        self
        """

    @abstractmethod
    def predict(self, X: Any) -> Any:
        """Generate predictions for *X*.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        predictions : array-like
        """

    @abstractmethod
    def evaluate(self, X: Any, y: Any) -> dict[str, Any]:
        """Evaluate the model and return a metrics dictionary.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            True target values.

        Returns
        -------
        metrics : dict
            Mapping of metric name → value.
        """

    # ------------------------------------------------------------------ #
    # Concrete helpers                                                     #
    # ------------------------------------------------------------------ #

    def summary(self) -> dict[str, Any]:
        """Return a summary of the model configuration.

        Returns
        -------
        info : dict
            Model class name and current hyperparameters.
        """
        return {
            "model": type(self).__name__,
            "params": self.get_params(),
        }

    def get_params(self) -> dict[str, Any]:
        """Return the model's hyperparameters.

        Returns
        -------
        params : dict
        """
        if self._estimator is None:
            return {}
        return self._estimator.get_params()

    def set_params(self, **params: Any) -> "BaseModel":
        """Update hyperparameters.

        Parameters
        ----------
        **params:
            Keyword arguments forwarded to the underlying estimator.

        Returns
        -------
        self
        """
        if self._estimator is not None:
            self._estimator.set_params(**params)
        return self

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.get_params()})"
