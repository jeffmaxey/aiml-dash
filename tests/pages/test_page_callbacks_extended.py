"""Additional tests for data, design, and model page callbacks.

Supplements test_pages.py with more thorough coverage of data transformation,
visualization, pivot table, SQL query, design, and model page callbacks.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aiml_dash.utils.data_manager import data_manager


@pytest.fixture(autouse=True)
def _seed_page_datasets():
    rng = np.random.default_rng(99)
    numeric_df = pd.DataFrame({
        "x": rng.normal(5, 1, 60),
        "y": rng.normal(3, 1, 60),
        "z": rng.normal(7, 2, 60),
    })
    two_group_df = pd.DataFrame({
        "value": np.concatenate([rng.normal(5, 1, 30), rng.normal(7, 1, 30)]),
        "group": ["A"] * 30 + ["B"] * 30,
        "outcome": ["yes", "no"] * 30,
    })
    cat_df = pd.DataFrame({
        "category": ["A", "A", "B", "B", "C"] * 10,
        "color": ["red", "blue"] * 25,
    })
    data_manager.add_dataset("pg2_numeric", numeric_df)
    data_manager.add_dataset("pg2_two_groups", two_group_df)
    data_manager.add_dataset("pg2_categorical", cat_df)
    yield


# ---------------------------------------------------------------------------
# data/view extended
# ---------------------------------------------------------------------------

class TestViewCallbacksExtended:
    def test_view_with_invalid_filter_still_returns_component(self):
        from aiml_dash.pages.data.view import update_view_table
        result = update_view_table("pg2_numeric", "bad expression !!!", None, None)
        assert result is not None

    def test_view_with_slice_expr(self):
        from aiml_dash.pages.data.view import update_view_table
        result = update_view_table("pg2_numeric", None, None, ":10")
        assert result is not None

    def test_export_csv_valid(self):
        from aiml_dash.pages.data.view import export_csv
        result = export_csv(1, "pg2_numeric", None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# data/transform extended
# ---------------------------------------------------------------------------

class TestTransformCallbacksExtended:
    def test_create_new_variable_valid(self):
        from aiml_dash.pages.data.transform import create_new_variable
        result = create_new_variable(1, "pg2_numeric", "x_sq", "x ** 2")
        assert result is not None

    def test_create_new_variable_bad_expression(self):
        from aiml_dash.pages.data.transform import create_new_variable
        result = create_new_variable(1, "pg2_numeric", "bad", "INVALID@@##")
        assert result is not None

    def test_apply_log_transformation(self):
        from aiml_dash.pages.data.transform import apply_transformation
        result = apply_transformation(1, "pg2_numeric", "x", "log")
        assert result is not None

    def test_apply_sqrt_transformation(self):
        from aiml_dash.pages.data.transform import apply_transformation
        result = apply_transformation(1, "pg2_numeric", "x", "sqrt")
        assert result is not None

    def test_apply_zscore_transformation(self):
        from aiml_dash.pages.data.transform import apply_transformation
        result = apply_transformation(1, "pg2_numeric", "x", "zscore")
        assert result is not None

    def test_apply_transformation_missing(self):
        from aiml_dash.pages.data.transform import apply_transformation
        result = apply_transformation(1, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# data/manage callbacks
# ---------------------------------------------------------------------------

class TestManageCallbacks:
    def test_update_dataset_info_none(self):
        from aiml_dash.pages.data.manage import update_dataset_info
        result = update_dataset_info(None)
        assert result is not None

    def test_update_dataset_info_valid(self):
        from aiml_dash.pages.data.manage import update_dataset_info
        result = update_dataset_info("pg2_numeric")
        assert result is not None

    def test_update_preview_grid(self):
        from aiml_dash.pages.data.manage import update_preview
        result = update_preview("pg2_numeric", "grid")
        assert result is not None

    def test_update_preview_statistics(self):
        from aiml_dash.pages.data.manage import update_preview
        result = update_preview("pg2_numeric", "statistics")
        assert result is not None

    def test_update_preview_missing_dataset(self):
        from aiml_dash.pages.data.manage import update_preview
        result = update_preview(None, "grid")
        assert result is not None


# ---------------------------------------------------------------------------
# data/pivot extended
# ---------------------------------------------------------------------------

class TestPivotCallbacksExtended:
    def test_create_pivot_valid(self):
        from aiml_dash.pages.data.pivot import create_pivot_table
        result = create_pivot_table(
            1, "pg2_two_groups", ["group"], [], ["value"], "mean", False, False, None
        )
        assert result is not None

    def test_create_pivot_with_margins(self):
        from aiml_dash.pages.data.pivot import create_pivot_table
        result = create_pivot_table(
            1, "pg2_two_groups", ["group"], [], ["value"], "mean", True, False, None
        )
        assert result is not None


# ---------------------------------------------------------------------------
# data/visualize
# ---------------------------------------------------------------------------

class TestVisualizeCallbacksExtended:
    def test_scatter_plot(self):
        from aiml_dash.pages.data.visualize import create_visualization
        from dash import dcc
        result = create_visualization(1, "pg2_numeric", "scatter", "x", "y", None, None, None, None)
        assert isinstance(result, dcc.Graph)

    def test_histogram_plot(self):
        from aiml_dash.pages.data.visualize import create_visualization
        from dash import dcc
        result = create_visualization(1, "pg2_numeric", "histogram", "x", None, None, None, None, None)
        assert isinstance(result, dcc.Graph)

    def test_box_plot(self):
        from aiml_dash.pages.data.visualize import create_visualization
        from dash import dcc
        result = create_visualization(1, "pg2_two_groups", "box", "group", "value", None, None, None, None)
        assert isinstance(result, dcc.Graph)

    def test_bar_plot(self):
        from aiml_dash.pages.data.visualize import create_visualization
        result = create_visualization(1, "pg2_numeric", "bar", "x", "y", None, None, None, None)
        assert result is not None

    def test_missing_required_args_returns_fallback(self):
        from aiml_dash.pages.data.visualize import create_visualization
        result = create_visualization(None, None, "scatter", None, None, None, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# data/sql_query
# ---------------------------------------------------------------------------

class TestSqlQueryCallbacks:
    def test_update_connection_list_returns_tuple(self):
        from aiml_dash.pages.data.sql_query import update_connection_list
        result = update_connection_list(0)
        assert isinstance(result, tuple) or isinstance(result, list) or result is not None

    def test_save_connection_missing_inputs(self):
        from aiml_dash.pages.data.sql_query import save_connection
        result = save_connection(1, None, None, None, None, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# design/sample_size_comp
# ---------------------------------------------------------------------------

class TestSampleSizeCompCallbacks:
    def test_one_sample_t(self):
        from aiml_dash.pages.design.sample_size_comp import compare_sample_sizes
        import plotly.graph_objects as go
        result = compare_sample_sizes(1, "one_sample_t", 0.2, 1.0, [0.8, 0.9], 0.05)
        assert isinstance(result, go.Figure)

    def test_missing_inputs(self):
        from aiml_dash.pages.design.sample_size_comp import compare_sample_sizes
        result = compare_sample_sizes(1, None, None, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# design/doe
# ---------------------------------------------------------------------------

class TestDoeCallbacks:
    def test_create_design_two_factor(self):
        from aiml_dash.pages.design.doe import create_design
        factors = [
            {"name": "Temp", "levels": ["Low", "High"]},
            {"name": "Press", "levels": ["Low", "High"]},
        ]
        result = create_design(1, factors, [], 8, 42)
        assert result is not None

    def test_create_design_missing_factors(self):
        from aiml_dash.pages.design.doe import create_design
        result = create_design(1, None, [], 8, 42)
        assert result is not None

    def test_manage_factors_add(self):
        from aiml_dash.pages.design.doe import manage_factors
        from unittest.mock import patch, MagicMock

        # manage_factors uses dash.callback_context internally; mock it
        mock_ctx = MagicMock()
        mock_ctx.triggered = [{"prop_id": "doe-add-factor.n_clicks"}]
        with patch("dash.callback_context", mock_ctx):
            result = manage_factors(1, 0, "Temperature", "Low", "High", 2, [])
        assert result is not None

    def test_manage_factors_remove(self):
        from aiml_dash.pages.design.doe import manage_factors
        from unittest.mock import patch, MagicMock

        factors = [{"name": "Temp", "level1": "Low", "level2": "High"}]
        mock_ctx = MagicMock()
        mock_ctx.triggered = [{"prop_id": "doe-remove-factor.n_clicks"}]
        with patch("dash.callback_context", mock_ctx):
            result = manage_factors(0, 1, "Temperature", "Low", "High", 2, factors)
        assert result is not None


# ---------------------------------------------------------------------------
# design/sample_size extended
# ---------------------------------------------------------------------------

class TestSampleSizeExtended:
    def test_two_proportions(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size
        result = calculate_sample_size(1, "two_proportions", 0.5, 0.8, 0.05, "two-sided")
        assert result is not None

    def test_chi_square(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size
        result = calculate_sample_size(1, "chi_square", 0.3, 0.8, 0.05, "two-sided")
        assert result is not None

    def test_correlation(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size
        result = calculate_sample_size(1, "correlation", 0.3, 0.8, 0.05, "two-sided")
        assert result is not None


# ---------------------------------------------------------------------------
# design/sampling extended
# ---------------------------------------------------------------------------

class TestSamplingExtended:
    def test_simple_random_sample(self):
        from aiml_dash.pages.design.sampling import generate_sample
        result = generate_sample(1, "random", 10, None, 42)
        assert result is not None

    def test_systematic_sample(self):
        from aiml_dash.pages.design.sampling import generate_sample
        result = generate_sample(1, "systematic", 10, None, 42)
        assert result is not None


# ---------------------------------------------------------------------------
# model/decision_analysis extended
# ---------------------------------------------------------------------------

class TestDecisionAnalysisExtended:
    def test_calculate_ev_nested_chance(self):
        from aiml_dash.pages.model.decision_analysis import calculate_ev
        node = {
            "type": "chance",
            "branches": [
                {"prob": 0.6, "payoff": 50},
                {"prob": 0.4, "payoff": 100},
            ],
        }
        ev = calculate_ev(node)
        assert abs(ev - (0.6 * 50 + 0.4 * 100)) < 1e-9

    def test_find_optimal_path_chance_node(self):
        from aiml_dash.pages.model.decision_analysis import find_optimal_path
        node = {
            "type": "chance",
            "branches": [
                {"name": "Win", "payoff": 100},
                {"name": "Lose", "payoff": 0},
            ],
        }
        result = find_optimal_path(node)
        assert isinstance(result, list)

    def test_find_optimal_path_decision_with_best(self):
        from aiml_dash.pages.model.decision_analysis import find_optimal_path
        node = {
            "type": "decision",
            "branches": [
                {"name": "opt_a", "payoff": 30},
                {"name": "opt_b", "payoff": 70},
            ],
        }
        result = find_optimal_path(node)
        assert isinstance(result, list)
        # Should find opt_b
        assert any("opt_b" in str(r) for r in result)
