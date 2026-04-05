"""Tests for aiml.supervised.glm – Ridge, Lasso, ElasticNet."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.supervised.glm import ElasticNet, Lasso, Ridge


@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(7)
    X = rng.standard_normal((80, 4))
    y = 1.5 * X[:, 0] - 2 * X[:, 1] + rng.normal(0, 0.3, 80)
    return X, y


class TestRidge:
    def test_fit_returns_self(self, regression_data):
        X, y = regression_data
        model = Ridge()
        assert model.fit(X, y) is model

    def test_predict_shape(self, regression_data):
        X, y = regression_data
        model = Ridge().fit(X, y)
        assert model.predict(X).shape == (80,)

    def test_evaluate_keys(self, regression_data):
        X, y = regression_data
        model = Ridge().fit(X, y)
        assert set(model.evaluate(X, y)) == {"r2", "mse", "rmse", "mae"}

    def test_good_r2(self, regression_data):
        X, y = regression_data
        model = Ridge(alpha=0.01).fit(X, y)
        assert model.evaluate(X, y)["r2"] > 0.9

    def test_summary_coef(self, regression_data):
        X, y = regression_data
        model = Ridge().fit(X, y)
        s = model.summary()
        assert "coef" in s
        assert len(s["coef"]) == 4

    def test_alpha_param(self):
        model = Ridge(alpha=2.0)
        assert model.get_params()["alpha"] == 2.0


class TestLasso:
    def test_fit_predict(self, regression_data):
        X, y = regression_data
        model = Lasso(alpha=0.01).fit(X, y)
        assert model.predict(X).shape == (80,)

    def test_evaluate_r2(self, regression_data):
        X, y = regression_data
        model = Lasso(alpha=0.001).fit(X, y)
        assert model.evaluate(X, y)["r2"] > 0.85

    def test_sparsity(self, regression_data):
        X, y = regression_data
        # High alpha should drive some coefficients to zero
        model = Lasso(alpha=10.0).fit(X, y)
        coef = np.array(model._estimator.coef_)
        assert np.any(coef == 0)

    def test_summary(self, regression_data):
        X, y = regression_data
        s = Lasso(alpha=0.01).fit(X, y).summary()
        assert s["model"] == "Lasso"


class TestElasticNet:
    def test_fit_predict(self, regression_data):
        X, y = regression_data
        model = ElasticNet(alpha=0.01, l1_ratio=0.5).fit(X, y)
        assert model.predict(X).shape == (80,)

    def test_evaluate_keys(self, regression_data):
        X, y = regression_data
        model = ElasticNet(alpha=0.01).fit(X, y)
        metrics = model.evaluate(X, y)
        assert "r2" in metrics and "mae" in metrics

    def test_l1_ratio_param(self):
        model = ElasticNet(l1_ratio=0.3)
        assert model.get_params()["l1_ratio"] == 0.3

    def test_summary_model_name(self, regression_data):
        X, y = regression_data
        s = ElasticNet(alpha=0.01).fit(X, y).summary()
        assert s["model"] == "ElasticNet"
