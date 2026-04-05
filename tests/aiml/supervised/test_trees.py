"""Tests for aiml.supervised.trees."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.supervised.trees import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)


@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(99)
    X = rng.standard_normal((120, 4))
    y = X[:, 0] ** 2 + X[:, 1] - 0.5 * X[:, 2] + rng.normal(0, 0.3, 120)
    return X, y


@pytest.fixture()
def classification_data():
    rng = np.random.default_rng(99)
    X = rng.standard_normal((120, 3))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


# ---------------------------------------------------------------------------
# DecisionTreeRegressor
# ---------------------------------------------------------------------------

class TestDecisionTreeRegressor:
    def test_fit_predict(self, regression_data):
        X, y = regression_data
        model = DecisionTreeRegressor(max_depth=5).fit(X, y)
        assert model.predict(X).shape == (120,)

    def test_evaluate_keys(self, regression_data):
        X, y = regression_data
        model = DecisionTreeRegressor(max_depth=5).fit(X, y)
        assert {"r2", "mse", "rmse", "mae"} == set(model.evaluate(X, y))

    def test_feature_importances_in_summary(self, regression_data):
        X, y = regression_data
        model = DecisionTreeRegressor().fit(X, y)
        s = model.summary()
        assert "feature_importances" in s
        assert len(s["feature_importances"]) == 4


# ---------------------------------------------------------------------------
# DecisionTreeClassifier
# ---------------------------------------------------------------------------

class TestDecisionTreeClassifier:
    def test_fit_predict(self, classification_data):
        X, y = classification_data
        model = DecisionTreeClassifier(max_depth=5).fit(X, y)
        preds = model.predict(X)
        assert set(preds).issubset({0, 1})

    def test_evaluate_accuracy(self, classification_data):
        X, y = classification_data
        model = DecisionTreeClassifier(max_depth=5).fit(X, y)
        metrics = model.evaluate(X, y)
        assert metrics["accuracy"] > 0.8

    def test_predict_proba(self, classification_data):
        X, y = classification_data
        model = DecisionTreeClassifier().fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (120, 2)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-6)


# ---------------------------------------------------------------------------
# RandomForestRegressor
# ---------------------------------------------------------------------------

class TestRandomForestRegressor:
    def test_fit_predict(self, regression_data):
        X, y = regression_data
        model = RandomForestRegressor(n_estimators=10, random_state=0).fit(X, y)
        assert model.predict(X).shape == (120,)

    def test_r2_positive(self, regression_data):
        X, y = regression_data
        model = RandomForestRegressor(n_estimators=50, random_state=0).fit(X, y)
        assert model.evaluate(X, y)["r2"] > 0.85


# ---------------------------------------------------------------------------
# RandomForestClassifier
# ---------------------------------------------------------------------------

class TestRandomForestClassifier:
    def test_fit_predict(self, classification_data):
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
        assert len(model.predict(X)) == 120

    def test_accuracy(self, classification_data):
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=50, random_state=0).fit(X, y)
        assert model.evaluate(X, y)["accuracy"] > 0.85

    def test_predict_proba(self, classification_data):
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (120, 2)


# ---------------------------------------------------------------------------
# GradientBoostingRegressor
# ---------------------------------------------------------------------------

class TestGradientBoostingRegressor:
    def test_fit_predict(self, regression_data):
        X, y = regression_data
        model = GradientBoostingRegressor(n_estimators=20, random_state=0).fit(X, y)
        assert model.predict(X).shape == (120,)

    def test_rmse_positive(self, regression_data):
        X, y = regression_data
        model = GradientBoostingRegressor(n_estimators=20, random_state=0).fit(X, y)
        assert model.evaluate(X, y)["rmse"] >= 0


# ---------------------------------------------------------------------------
# GradientBoostingClassifier
# ---------------------------------------------------------------------------

class TestGradientBoostingClassifier:
    def test_fit_predict(self, classification_data):
        X, y = classification_data
        model = GradientBoostingClassifier(n_estimators=20, random_state=0).fit(X, y)
        preds = model.predict(X)
        assert set(preds).issubset({0, 1})

    def test_accuracy(self, classification_data):
        X, y = classification_data
        model = GradientBoostingClassifier(n_estimators=50, random_state=0).fit(X, y)
        assert model.evaluate(X, y)["accuracy"] > 0.85

    def test_predict_proba(self, classification_data):
        X, y = classification_data
        model = GradientBoostingClassifier(n_estimators=20, random_state=0).fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (120, 2)
