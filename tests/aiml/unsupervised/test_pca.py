"""Tests for aiml.unsupervised.pca – PCA."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aiml.unsupervised.pca import PCA


@pytest.fixture()
def data():
    rng = np.random.default_rng(21)
    return rng.standard_normal((60, 6))


class TestPCA:
    def test_fit_returns_self(self, data):
        model = PCA(n_components=3)
        assert model.fit(data) is model

    def test_predict_shape(self, data):
        model = PCA(n_components=3).fit(data)
        scores = model.predict(data)
        assert scores.shape == (60, 3)

    def test_evaluate_keys(self, data):
        model = PCA(n_components=3).fit(data)
        metrics = model.evaluate(data)
        assert "explained_variance_ratio" in metrics
        assert "cumulative_variance" in metrics
        assert "n_components" in metrics

    def test_n_components_respected(self, data):
        model = PCA(n_components=2).fit(data)
        assert model.evaluate(data)["n_components"] == 2

    def test_cumulative_variance_monotone(self, data):
        model = PCA(n_components=4).fit(data)
        cv = model.evaluate(data)["cumulative_variance"]
        assert all(cv[i] <= cv[i + 1] for i in range(len(cv) - 1))

    def test_explained_variance_sums_to_cumulative(self, data):
        model = PCA(n_components=4).fit(data)
        evr = np.array(model.evaluate(data)["explained_variance_ratio"])
        cv = np.array(model.evaluate(data)["cumulative_variance"])
        np.testing.assert_allclose(np.cumsum(evr), cv, atol=1e-10)

    def test_loadings_shape(self, data):
        model = PCA(n_components=3).fit(data)
        loadings = model.loadings()
        assert loadings.shape == (3, 6)

    def test_dataframe_input(self, data):
        df = pd.DataFrame(data, columns=[f"v{i}" for i in range(6)])
        model = PCA(n_components=2).fit(df)
        scores = model.predict(df)
        assert scores.shape == (60, 2)

    def test_no_standardize(self, data):
        model = PCA(n_components=2, standardize=False).fit(data)
        assert model.predict(data).shape == (60, 2)

    def test_summary_contains_n_components(self, data):
        model = PCA(n_components=2).fit(data)
        s = model.summary()
        assert "n_components" in s

    def test_get_params(self):
        model = PCA(n_components=3)
        params = model.get_params()
        assert params["n_components"] == 3
