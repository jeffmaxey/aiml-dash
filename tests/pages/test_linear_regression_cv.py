"""Tests for the Cross-Validation feature in the linear regression page."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from aiml_dash.utils.data_manager import data_manager


@pytest.fixture(autouse=True)
def _seed_lr_datasets():
    """Seed the global data_manager with datasets used by LR CV tests."""
    rng = np.random.default_rng(1)
    n = 80
    X1 = rng.normal(0, 1, n)
    X2 = rng.normal(2, 1, n)
    y = 3 * X1 - 2 * X2 + rng.normal(0, 0.5, n)

    lr_df = pd.DataFrame({"x1": X1, "x2": X2, "y": y})
    data_manager.add_dataset("lr_cv_test", lr_df, description="LR CV test data")
    yield


class TestRunLrCv:
    def test_returns_two_elements(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        result = run_lr_cv(1, "lr_cv_test", "y", ["x1", "x2"], 5, "r2", [])
        assert len(result) == 2

    def test_valid_inputs_returns_figure(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", "y", ["x1", "x2"], 5, "r2", []
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_valid_inputs_returns_summary(self):
        import dash_mantine_components as dmc

        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", "y", ["x1", "x2"], 5, "r2", []
        )
        assert summary is not None

    def test_rmse_scoring(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1,
            "lr_cv_test",
            "y",
            ["x1", "x2"],
            5,
            "neg_root_mean_squared_error",
            [],
        )
        assert isinstance(fig, go.Figure)

    def test_mae_scoring(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1,
            "lr_cv_test",
            "y",
            ["x1", "x2"],
            5,
            "neg_mean_absolute_error",
            [],
        )
        assert isinstance(fig, go.Figure)

    def test_standardize_option(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", "y", ["x1", "x2"], 5, "r2", ["standardize"]
        )
        assert isinstance(fig, go.Figure)

    def test_missing_dataset_returns_empty_figure(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, None, None, None, 5, "r2", []
        )
        assert isinstance(fig, go.Figure)
        # Empty figure has no data traces
        assert len(fig.data) == 0

    def test_missing_response_returns_empty_figure(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", None, ["x1", "x2"], 5, "r2", []
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_missing_explanatory_returns_empty_figure(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", "y", None, 5, "r2", []
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_three_fold_cv(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, summary = run_lr_cv(
            1, "lr_cv_test", "y", ["x1", "x2"], 3, "r2", []
        )
        assert isinstance(fig, go.Figure)

    def test_box_plot_trace_type(self):
        from aiml_dash.pages.model.linear_regression import run_lr_cv

        fig, _ = run_lr_cv(
            1, "lr_cv_test", "y", ["x1", "x2"], 5, "r2", []
        )
        assert any(isinstance(t, go.Box) for t in fig.data)
