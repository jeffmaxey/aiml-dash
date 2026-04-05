"""
Unsupervised Learning – Cluster Analysis
=========================================

Provides:

* :class:`HierarchicalClustering` – agglomerative hierarchical clustering via
  ``scipy`` linkage.
* :class:`KMeans` – k-means clustering via scikit-learn.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.cluster import KMeans as _SKKMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from aiml.base import BaseModel


class HierarchicalClustering(BaseModel):
    """Agglomerative (hierarchical) clustering.

    Uses :func:`scipy.cluster.hierarchy.linkage` to build a dendrogram and
    :func:`scipy.cluster.hierarchy.fcluster` to cut the tree into flat
    clusters.

    Parameters
    ----------
    n_clusters:
        Number of clusters to extract when calling :meth:`predict`. Default
        ``2``.
    method:
        Linkage method (``"ward"``, ``"complete"``, ``"average"``,
        ``"single"``). Default ``"ward"``.
    metric:
        Distance metric passed to :func:`scipy.cluster.hierarchy.linkage`.
        Default ``"euclidean"``.
    standardize:
        Standardise the data before clustering. Default ``True``.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.unsupervised.clustering import HierarchicalClustering
    >>> rng = np.random.default_rng(0)
    >>> X = rng.standard_normal((20, 3))
    >>> model = HierarchicalClustering(n_clusters=3)
    >>> model.fit(X)
    HierarchicalClustering(...)
    >>> labels = model.predict(X)
    >>> len(set(labels)) == 3
    True
    """

    def __init__(
        self,
        *,
        n_clusters: int = 2,
        method: str = "ward",
        metric: str = "euclidean",
        standardize: bool = True,
    ) -> None:
        self.n_clusters = n_clusters
        self.method = method
        self.metric = metric
        self.standardize = standardize
        self._scaler = StandardScaler() if standardize else None
        self._linkage_matrix: np.ndarray | None = None
        self._is_fitted = False
        # No single sklearn estimator; use a thin wrapper for get_params
        self._estimator = _HierarchicalEstimator(
            n_clusters=n_clusters,
            method=method,
            metric=metric,
            standardize=standardize,
        )

    # ------------------------------------------------------------------ #

    def _prepare(self, X: Any, fit: bool = False) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(include=[np.number]).to_numpy()
        else:
            X = np.asarray(X, dtype=float)
        if self._scaler is not None:
            if fit:
                X = self._scaler.fit_transform(X)
            else:
                X = self._scaler.transform(X)
        return X

    def fit(self, X: Any, y: Any = None) -> "HierarchicalClustering":
        """Build the linkage matrix.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Ignored.

        Returns
        -------
        self
        """
        X_prep = self._prepare(X, fit=True)
        self._linkage_matrix = linkage(X_prep, method=self.method, metric=self.metric)
        self._X_fit = X_prep
        self._is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Assign cluster labels by cutting the dendrogram.

        Parameters
        ----------
        X:
            Feature matrix (must be the same data used for :meth:`fit` for
            hierarchical clustering).

        Returns
        -------
        labels : np.ndarray of int, shape (n_samples,)
        """
        return fcluster(self._linkage_matrix, self.n_clusters, criterion="maxclust")

    def evaluate(self, X: Any, y: Any = None) -> dict[str, Any]:
        """Compute cluster quality metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Ignored.

        Returns
        -------
        metrics : dict
            ``{"silhouette_score": float, "n_clusters": int}``
        """
        X_prep = self._prepare(X)
        labels = self.predict(X_prep)
        result: dict[str, Any] = {"n_clusters": self.n_clusters}
        if len(set(labels)) > 1:
            result["silhouette_score"] = float(silhouette_score(X_prep, labels))
        return result

    def linkage_matrix(self) -> np.ndarray:
        """Return the linkage matrix produced by :meth:`fit`.

        Returns
        -------
        Z : np.ndarray, shape (n_samples - 1, 4)
        """
        if self._linkage_matrix is None:
            msg = "Model has not been fitted yet."
            raise RuntimeError(msg)
        return self._linkage_matrix

    def summary(self) -> dict[str, Any]:
        """Return model summary.

        Returns
        -------
        info : dict
        """
        return {
            "model": type(self).__name__,
            "params": self.get_params(),
        }


# --------------------------------------------------------------------------- #


class KMeans(BaseModel):
    """K-means clustering.

    Wraps :class:`sklearn.cluster.KMeans`.

    Parameters
    ----------
    n_clusters:
        Number of clusters. Default ``8``.
    init:
        Initialisation method (``"k-means++"``, ``"random"``). Default
        ``"k-means++"``.
    max_iter:
        Maximum number of iterations. Default ``300``.
    random_state:
        Seed for reproducibility.
    standardize:
        Standardise the data before clustering. Default ``True``.
    **kwargs:
        Additional keyword arguments forwarded to the underlying estimator.

    Examples
    --------
    >>> import numpy as np
    >>> from aiml.unsupervised.clustering import KMeans
    >>> rng = np.random.default_rng(0)
    >>> X = rng.standard_normal((30, 3))
    >>> model = KMeans(n_clusters=3, random_state=0)
    >>> model.fit(X)
    KMeans(...)
    >>> labels = model.predict(X)
    >>> len(labels) == 30
    True
    """

    def __init__(
        self,
        *,
        n_clusters: int = 8,
        init: str = "k-means++",
        max_iter: int = 300,
        random_state: int | None = None,
        standardize: bool = True,
        **kwargs: Any,
    ) -> None:
        self._estimator = _SKKMeans(
            n_clusters=n_clusters,
            init=init,
            max_iter=max_iter,
            random_state=random_state,
            **kwargs,
        )
        self._scaler = StandardScaler() if standardize else None
        self._standardize = standardize
        self._is_fitted = False

    # ------------------------------------------------------------------ #

    def _prepare(self, X: Any, fit: bool = False) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(include=[np.number]).to_numpy()
        else:
            X = np.asarray(X, dtype=float)
        if self._scaler is not None:
            if fit:
                X = self._scaler.fit_transform(X)
            else:
                X = self._scaler.transform(X)
        return X

    def fit(self, X: Any, y: Any = None) -> "KMeans":
        """Fit k-means to *X*.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Ignored.

        Returns
        -------
        self
        """
        X_prep = self._prepare(X, fit=True)
        self._estimator.fit(X_prep)
        self._is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Assign cluster labels.

        Parameters
        ----------
        X:
            Feature matrix.

        Returns
        -------
        labels : np.ndarray of int
        """
        return self._estimator.predict(self._prepare(X))

    def evaluate(self, X: Any, y: Any = None) -> dict[str, Any]:
        """Compute cluster quality metrics.

        Parameters
        ----------
        X:
            Feature matrix.
        y:
            Ignored.

        Returns
        -------
        metrics : dict
            ``{"inertia": float, "silhouette_score": float, "n_clusters": int}``
        """
        X_prep = self._prepare(X)
        labels = self.predict(X)
        result: dict[str, Any] = {
            "inertia": float(self._estimator.inertia_),
            "n_clusters": int(self._estimator.n_clusters),
        }
        if len(set(labels)) > 1:
            result["silhouette_score"] = float(silhouette_score(X_prep, labels))
        return result

    def summary(self) -> dict[str, Any]:
        """Return model summary.

        Returns
        -------
        info : dict
        """
        return {
            "model": type(self).__name__,
            "params": self.get_params(),
        }


# --------------------------------------------------------------------------- #
# Internal thin wrapper so get_params works for HierarchicalClustering        #
# --------------------------------------------------------------------------- #


class _HierarchicalEstimator:
    """Minimal stand-in providing :meth:`get_params`."""

    def __init__(self, **params: Any) -> None:
        self._params = params

    def get_params(self, deep: bool = True) -> dict[str, Any]:  # noqa: ARG002
        return dict(self._params)

    def set_params(self, **params: Any) -> "_HierarchicalEstimator":
        self._params.update(params)
        return self
