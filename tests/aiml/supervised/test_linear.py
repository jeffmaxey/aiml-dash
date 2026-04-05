"""Tests for aiml.supervised.linear – LinearRegression and LogisticRegression."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.supervised.linear import LinearRegression, LogisticRegression


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((100, 3))
    y = 2 * X[:, 0] - 3 * X[:, 1] + 0.5 * X[:, 2] + rng.normal(0, 0.2, 100)
    return X, y


@pytest.fixture()
def classification_data():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((100, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


# ---------------------------------------------------------------------------
# LinearRegression tests
# ---------------------------------------------------------------------------

class TestLinearRegression:
    def test_fit_returns_self(self, regression_data):
        X, y = regression_data
        model = LinearRegression()
        result = model.fit(X, y)
        assert result is model

    def test_predict_shape(self, regression_data):
        X, y = regression_data
        model = LinearRegression()
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (100,)

    def test_evaluate_keys(self, regression_data):
        X, y = regression_data
        model = LinearRegression().fit(X, y)
        metrics = model.evaluate(X, y)
        assert set(metrics) == {"r2", "mse", "rmse", "mae"}

    def test_high_r2_on_linear_data(self, regression_data):
        X, y = regression_data
        model = LinearRegression().fit(X, y)
        assert model.evaluate(X, y)["r2"] > 0.95

    def test_summary_includes_coef(self, regression_data):
        X, y = regression_data
        model = LinearRegression().fit(X, y)
        s = model.summary()
        assert "coef" in s
        assert "intercept" in s

    def test_get_params(self):
        model = LinearRegression(fit_intercept=False)
        params = model.get_params()
        assert params["fit_intercept"] is False

    def test_set_params(self):
        model = LinearRegression()
        model.set_params(fit_intercept=False)
        assert model.get_params()["fit_intercept"] is False

    def test_repr(self):
        model = LinearRegression()
        assert "LinearRegression" in repr(model)

    def test_rmse_non_negative(self, regression_data):
        X, y = regression_data
        model = LinearRegression().fit(X, y)
        assert model.evaluate(X, y)["rmse"] >= 0


# ---------------------------------------------------------------------------
# LogisticRegression tests
# ---------------------------------------------------------------------------

class TestLogisticRegression:
    def test_fit_returns_self(self, classification_data):
        X, y = classification_data
        model = LogisticRegression()
        assert model.fit(X, y) is model

    def test_predict_classes(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        preds = model.predict(X)
        assert set(preds).issubset({0, 1})

    def test_predict_proba_shape(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (100, 2)

    def test_predict_proba_sums_to_one(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        proba = model.predict_proba(X)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-6)

    def test_evaluate_keys(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        metrics = model.evaluate(X, y)
        assert "accuracy" in metrics
        assert "f1" in metrics
        assert "confusion_matrix" in metrics
        assert "roc_auc" in metrics

    def test_high_accuracy_on_separable_data(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        assert model.evaluate(X, y)["accuracy"] > 0.85

    def test_summary_includes_classes(self, classification_data):
        X, y = classification_data
        model = LogisticRegression().fit(X, y)
        s = model.summary()
        assert "classes" in s

    def test_get_params_contains_c(self):
        model = LogisticRegression(C=0.5)
        assert model.get_params()["C"] == 0.5
