"""Tests for aiml.unsupervised.clustering – HierarchicalClustering, KMeans."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.unsupervised.clustering import HierarchicalClustering, KMeans


@pytest.fixture()
def blobs():
    """Three well-separated Gaussian clusters."""
    rng = np.random.default_rng(5)
    X1 = rng.standard_normal((20, 3)) + np.array([0, 0, 0])
    X2 = rng.standard_normal((20, 3)) + np.array([10, 0, 0])
    X3 = rng.standard_normal((20, 3)) + np.array([0, 10, 0])
    return np.vstack([X1, X2, X3])


class TestHierarchicalClustering:
    def test_fit_returns_self(self, blobs):
        model = HierarchicalClustering(n_clusters=3)
        assert model.fit(blobs) is model

    def test_predict_n_unique_labels(self, blobs):
        model = HierarchicalClustering(n_clusters=3).fit(blobs)
        labels = model.predict(blobs)
        assert len(set(labels)) == 3

    def test_predict_length(self, blobs):
        model = HierarchicalClustering(n_clusters=3).fit(blobs)
        assert len(model.predict(blobs)) == 60

    def test_evaluate_has_silhouette(self, blobs):
        model = HierarchicalClustering(n_clusters=3).fit(blobs)
        metrics = model.evaluate(blobs)
        assert "silhouette_score" in metrics
        assert metrics["silhouette_score"] > 0.5

    def test_linkage_matrix_available(self, blobs):
        model = HierarchicalClustering(n_clusters=3).fit(blobs)
        Z = model.linkage_matrix()
        assert Z.shape == (59, 4)

    def test_linkage_matrix_before_fit_raises(self):
        model = HierarchicalClustering(n_clusters=3)
        with pytest.raises(RuntimeError):
            model.linkage_matrix()

    def test_get_params(self):
        model = HierarchicalClustering(n_clusters=4, method="complete")
        params = model.get_params()
        assert params["n_clusters"] == 4
        assert params["method"] == "complete"

    def test_summary(self, blobs):
        s = HierarchicalClustering(n_clusters=3).fit(blobs).summary()
        assert s["model"] == "HierarchicalClustering"

    def test_no_standardize(self, blobs):
        model = HierarchicalClustering(n_clusters=3, standardize=False).fit(blobs)
        labels = model.predict(blobs)
        assert len(labels) == 60


class TestKMeans:
    def test_fit_returns_self(self, blobs):
        model = KMeans(n_clusters=3, random_state=0)
        assert model.fit(blobs) is model

    def test_predict_labels(self, blobs):
        model = KMeans(n_clusters=3, random_state=0).fit(blobs)
        labels = model.predict(blobs)
        assert len(labels) == 60
        assert len(set(labels)) == 3

    def test_evaluate_keys(self, blobs):
        model = KMeans(n_clusters=3, random_state=0).fit(blobs)
        metrics = model.evaluate(blobs)
        assert "inertia" in metrics
        assert "silhouette_score" in metrics

    def test_good_silhouette(self, blobs):
        model = KMeans(n_clusters=3, random_state=0).fit(blobs)
        assert model.evaluate(blobs)["silhouette_score"] > 0.5

    def test_get_params(self):
        model = KMeans(n_clusters=5)
        assert model.get_params()["n_clusters"] == 5

    def test_summary_model_name(self, blobs):
        s = KMeans(n_clusters=3, random_state=0).fit(blobs).summary()
        assert s["model"] == "KMeans"
