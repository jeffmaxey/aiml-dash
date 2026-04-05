"""Tests for aiml.deep_learning.neural_network – NeuralNetwork."""

from __future__ import annotations

import numpy as np
import pytest

from aiml.deep_learning.neural_network import NeuralNetwork


@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(11)
    X = rng.standard_normal((100, 4))
    y = X[:, 0] + 2 * X[:, 1] + rng.normal(0, 0.1, 100)
    return X, y


@pytest.fixture()
def classification_data():
    rng = np.random.default_rng(11)
    X = rng.standard_normal((100, 3))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


class TestNeuralNetworkRegression:
    def test_fit_returns_self(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(task="regression", max_iter=200, random_state=0)
        assert model.fit(X, y) is model

    def test_predict_shape(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(task="regression", max_iter=200, random_state=0).fit(X, y)
        assert model.predict(X).shape == (100,)

    def test_evaluate_keys(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(task="regression", max_iter=200, random_state=0).fit(X, y)
        metrics = model.evaluate(X, y)
        assert {"r2", "mse", "rmse", "mae"} == set(metrics)

    def test_r2_positive(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(
            task="regression",
            hidden_layer_sizes=(50, 25),
            max_iter=500,
            random_state=0,
        ).fit(X, y)
        assert model.evaluate(X, y)["r2"] > 0.8

    def test_predict_proba_raises_for_regression(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(task="regression", max_iter=50, random_state=0).fit(X, y)
        with pytest.raises(AttributeError):
            model.predict_proba(X)

    def test_summary_contains_task(self, regression_data):
        X, y = regression_data
        model = NeuralNetwork(task="regression", max_iter=50, random_state=0).fit(X, y)
        s = model.summary()
        assert s["task"] == "regression"
        assert "n_iter" in s
        assert "loss" in s


class TestNeuralNetworkClassification:
    def test_fit_predict(self, classification_data):
        X, y = classification_data
        model = NeuralNetwork(task="classification", max_iter=300, random_state=0).fit(X, y)
        preds = model.predict(X)
        assert set(preds).issubset({0, 1})

    def test_predict_proba_shape(self, classification_data):
        X, y = classification_data
        model = NeuralNetwork(task="classification", max_iter=300, random_state=0).fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (100, 2)

    def test_predict_proba_sum_to_one(self, classification_data):
        X, y = classification_data
        model = NeuralNetwork(task="classification", max_iter=300, random_state=0).fit(X, y)
        proba = model.predict_proba(X)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-6)

    def test_evaluate_classification_keys(self, classification_data):
        X, y = classification_data
        model = NeuralNetwork(task="classification", max_iter=300, random_state=0).fit(X, y)
        metrics = model.evaluate(X, y)
        assert "accuracy" in metrics
        assert "confusion_matrix" in metrics

    def test_summary_task_classification(self, classification_data):
        X, y = classification_data
        model = NeuralNetwork(task="classification", max_iter=50, random_state=0).fit(X, y)
        assert model.summary()["task"] == "classification"


class TestNeuralNetworkInvalidTask:
    def test_invalid_task_raises(self):
        with pytest.raises(ValueError, match="task"):
            NeuralNetwork(task="clustering")
