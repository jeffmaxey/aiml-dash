"""Tests for aiml.model_selection."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.model_selection import compare_models, cross_validate, grid_search, random_search
from aiml.supervised.linear import LinearRegression, LogisticRegression
from aiml.supervised.trees import RandomForestRegressor


@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(3)
    X = rng.standard_normal((80, 3))
    y = 2 * X[:, 0] - X[:, 1] + rng.normal(0, 0.3, 80)
    return X, y


@pytest.fixture()
def classification_data():
    rng = np.random.default_rng(3)
    X = rng.standard_normal((80, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


class TestCrossValidate:
    def test_returns_dict_with_expected_keys(self, regression_data):
        X, y = regression_data
        model = LinearRegression()
        result = cross_validate(model, X, y, cv=5, scoring="r2")
        assert set(result) == {"scores", "mean", "std", "cv", "scoring"}

    def test_scores_length_equals_cv(self, regression_data):
        X, y = regression_data
        model = LinearRegression()
        result = cross_validate(model, X, y, cv=4)
        assert len(result["scores"]) == 4

    def test_mean_within_scores_range(self, regression_data):
        X, y = regression_data
        model = LinearRegression()
        result = cross_validate(model, X, y, cv=5, scoring="r2")
        assert min(result["scores"]) <= result["mean"] <= max(result["scores"])

    def test_classification_cross_validate(self, classification_data):
        X, y = classification_data
        model = LogisticRegression()
        result = cross_validate(model, X, y, cv=3, scoring="accuracy")
        assert result["mean"] > 0.5


class TestGridSearch:
    def test_returns_best_params(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Ridge
        model = Ridge()
        result = grid_search(model, X, y, {"alpha": [0.01, 0.1, 1.0]}, cv=3)
        assert "best_params" in result
        assert result["best_params"]["alpha"] in [0.01, 0.1, 1.0]

    def test_best_score_is_float(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Ridge
        model = Ridge()
        result = grid_search(model, X, y, {"alpha": [0.1, 1.0]}, cv=3)
        assert isinstance(result["best_score"], float)

    def test_refit_updates_estimator(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Ridge
        model = Ridge()
        grid_search(model, X, y, {"alpha": [0.01, 1.0]}, cv=3, refit=True)
        # After refit, the estimator should be the best one
        assert model._estimator.alpha in [0.01, 1.0]


class TestRandomSearch:
    def test_returns_expected_keys(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Ridge
        model = Ridge()
        result = random_search(
            model, X, y, {"alpha": [0.001, 0.01, 0.1, 1.0]}, n_iter=3, cv=3, random_state=0
        )
        assert "best_params" in result
        assert "best_score" in result


class TestCompareModels:
    def test_returns_sorted_by_mean(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Lasso, Ridge
        models = [LinearRegression(), Ridge(alpha=0.1), Lasso(alpha=0.01)]
        results = compare_models(models, X, y, cv=3, scoring="r2")
        means = [r["mean"] for r in results]
        assert means == sorted(means, reverse=True)

    def test_result_contains_model_name(self, regression_data):
        X, y = regression_data
        results = compare_models([LinearRegression()], X, y, cv=3, scoring="r2")
        assert results[0]["model"] == "LinearRegression"

    def test_all_models_present(self, regression_data):
        X, y = regression_data
        from aiml.supervised.glm import Ridge
        models = [LinearRegression(), Ridge()]
        results = compare_models(models, X, y, cv=3)
        names = {r["model"] for r in results}
        assert names == {"LinearRegression", "Ridge"}
