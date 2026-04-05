"""
Unsupervised Learning – Principal Component Analysis
=====================================================

Provides :class:`PCA` wrapping scikit-learn's implementation with a
unified :class:`~aiml.base.BaseModel` interface.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA as _SKPCA
from sklearn.preprocessing import StandardScaler

from aiml.base import BaseModel


class PCA(BaseModel):
    """Principal Component Analysis.

    Wraps :class:`sklearn.decomposition.PCA` and optionally applies
    standard scaling before fitting.

    Parameters
    ----------
    n_components:
        Number of components to retain. Accepts an integer, a float in
        ``(0, 1)`` (fraction of variance explained), or ``None`` (keep
        all). Default ``None``.
    standardize:
        When ``True`` the data are mean-centred and scaled to unit variance
        prior to decomposition. Default ``True``.
    **kwargs:
        Additional keyword arguments forwarded to
        :class:`sklearn.decomposition.PCA`.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.unsupervised.pca import PCA
    >>> rng = np.random.default_rng(0)
    >>> X = rng.standard_normal((50, 4))
    >>> model = PCA(n_components=2)
    >>> model.fit(X)
    PCA(...)
    >>> scores = model.predict(X)
    >>> scores.shape
    (50, 2)
    """

    def __init__(
        self,
        *,
        n_components: int | float | None = None,
        standardize: bool = True,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKPCA(n_components=n_components, **kwargs)
        self._scaler = StandardScaler() if standardize else None
        self._standardize = standardize
        self._is_fitted = False

    # ------------------------------------------------------------------ #

    def _transform_input(self, X: Any) -> np.ndarray:
        """Convert *X* to a numpy array and optionally scale it."""
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(include=[np.number]).to_numpy()
        else:
            X = np.asarray(X)
        if self._scaler is not None and self._is_fitted:
            X = self._scaler.transform(X)
        return X

    def fit(self, X: Any, y: Any = None) -> "PCA":
        """Fit PCA to *X*.

        Parameters
        ----------
        X:
            Numeric feature matrix (rows = observations, columns = variables).
        y:
            Ignored. Present for API consistency.

        Returns
        -------
        self
        """
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(include=[np.number]).to_numpy()
        else:
            X = np.asarray(X)

        if self._scaler is not None:
            X = self._scaler.fit_transform(X)

        self._estimator.fit(X)
        self._is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Project *X* onto the principal components.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        scores : np.ndarray, shape (n_samples, n_components)
            Component scores (also known as the transformed data).
        """
        return self._estimator.transform(self._transform_input(X))

    def evaluate(self, X: Any, y: Any = None) -> dict[str, Any]:
        """Compute variance-explained metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Ignored.

        Returns
        -------
        metrics : dict
            ``{"explained_variance_ratio": list, "cumulative_variance": list,
            "n_components": int}``
        """
        evr = self._estimator.explained_variance_ratio_
        return {
            "explained_variance_ratio": evr.tolist(),
            "cumulative_variance": np.cumsum(evr).tolist(),
            "n_components": int(self._estimator.n_components_),
        }

    def loadings(self) -> np.ndarray:
        """Return the component loadings (principal axes).

        Returns
        -------
        loadings : np.ndarray, shape (n_components, n_features)
        """
        return self._estimator.components_

    def summary(self) -> dict[str, Any]:
        """Return a summary of the PCA model.

        Returns
        -------
        info : dict
        """
        info: dict[str, Any] = {
            "model": type(self).__name__,
            "params": self.get_params(),
        }
        if self._is_fitted:
            evr = self._estimator.explained_variance_ratio_
            info["explained_variance_ratio"] = evr.tolist()
            info["cumulative_variance"] = np.cumsum(evr).tolist()
            info["n_components"] = int(self._estimator.n_components_)
        return info
