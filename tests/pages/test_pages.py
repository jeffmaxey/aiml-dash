"""Tests for all page layout() functions and representative page callbacks.

Pages define a layout() function that returns a Dash component tree.
Callback functions within pages can be invoked directly as ordinary Python
functions.
"""

from __future__ import annotations

import importlib

import numpy as np
import pandas as pd
import pytest

from aiml_dash.utils.data_manager import data_manager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _seed_page_datasets():
    """Register datasets needed by page callbacks."""
    rng = np.random.default_rng(0)

    numeric_df = pd.DataFrame(
        {
            "x": rng.normal(5, 1, 60),
            "y": rng.normal(3, 1, 60),
            "z": rng.normal(7, 2, 60),
        }
    )
    two_group_df = pd.DataFrame(
        {
            "value": np.concatenate([rng.normal(5, 1, 30), rng.normal(7, 1, 30)]),
            "group": ["A"] * 30 + ["B"] * 30,
            "outcome": (["yes", "no"] * 30),
        }
    )
    cat_df = pd.DataFrame(
        {"category": ["A", "A", "B", "B", "C"] * 10, "color": ["red", "blue"] * 25}
    )
    data_manager.add_dataset("pg_numeric", numeric_df)
    data_manager.add_dataset("pg_two_groups", two_group_df)
    data_manager.add_dataset("pg_categorical", cat_df)
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_LAYOUT_PAGES = [
    # basics
    "aiml_dash.pages.basics.single_mean",
    "aiml_dash.pages.basics.clt",
    "aiml_dash.pages.basics.compare_means",
    "aiml_dash.pages.basics.compare_props",
    "aiml_dash.pages.basics.correlation",
    "aiml_dash.pages.basics.cross_tabs",
    "aiml_dash.pages.basics.goodness",
    "aiml_dash.pages.basics.prob_calc",
    "aiml_dash.pages.basics.single_prop",
    # data
    "aiml_dash.pages.data.combine",
    "aiml_dash.pages.data.explore",
    "aiml_dash.pages.data.manage",
    "aiml_dash.pages.data.pivot",
    "aiml_dash.pages.data.report",
    "aiml_dash.pages.data.sql_query",
    "aiml_dash.pages.data.transform",
    "aiml_dash.pages.data.view",
    "aiml_dash.pages.data.visualize",
    # design
    "aiml_dash.pages.design.doe",
    "aiml_dash.pages.design.randomizer",
    "aiml_dash.pages.design.sample_size",
    "aiml_dash.pages.design.sample_size_comp",
    "aiml_dash.pages.design.sampling",
    # model
    "aiml_dash.pages.model.collaborative_filtering",
    "aiml_dash.pages.model.decision_analysis",
    "aiml_dash.pages.model.decision_tree",
    "aiml_dash.pages.model.evaluate_classification",
    "aiml_dash.pages.model.evaluate_regression",
    "aiml_dash.pages.model.gradient_boosting",
    "aiml_dash.pages.model.linear_regression",
    "aiml_dash.pages.model.logistic",
    "aiml_dash.pages.model.logistic_regression",
    "aiml_dash.pages.model.multinomial_logit",
    "aiml_dash.pages.model.naive_bayes",
    "aiml_dash.pages.model.neural_network",
    "aiml_dash.pages.model.random_forest",
    "aiml_dash.pages.model.simulator",
    # multivariate
    "aiml_dash.pages.multivariate.conjoint",
    "aiml_dash.pages.multivariate.full_factor",
    "aiml_dash.pages.multivariate.hierarchical_cluster",
    "aiml_dash.pages.multivariate.kmeans_cluster",
    "aiml_dash.pages.multivariate.mds",
    "aiml_dash.pages.multivariate.perceptual_map",
    "aiml_dash.pages.multivariate.pre_factor",
]


# ---------------------------------------------------------------------------
# Layout smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module_path", ALL_LAYOUT_PAGES)
def test_layout_returns_component(module_path):
    """Every page's layout() should return a Dash component without error."""
    import dash_mantine_components as dmc

    mod = importlib.import_module(module_path)
    result = mod.layout()
    # All pages currently return a dmc.Container
    assert isinstance(result, dmc.Container)


# ---------------------------------------------------------------------------
# data/combine callbacks
# ---------------------------------------------------------------------------


class TestCombineCallbacks:
    def test_update_combine_selectors_returns_tuple(self):
        from aiml_dash.pages.data.combine import update_combine_selectors

        result = update_combine_selectors(0)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_update_join_columns_empty_for_none(self):
        from aiml_dash.pages.data.combine import update_join_columns

        result = update_join_columns(None, None)
        assert result == []

    def test_update_join_columns_returns_common_cols(self):
        from aiml_dash.pages.data.combine import update_join_columns

        result = update_join_columns("pg_two_groups", "pg_two_groups")
        labels = [i["label"] for i in result]
        assert "value" in labels or "group" in labels

    def test_combine_datasets_missing_returns_error(self):
        from aiml_dash.pages.data.combine import combine_datasets

        result = combine_datasets(1, None, None, "inner", None, None)
        assert result is not None

    def test_combine_datasets_inner_join(self):
        from aiml_dash.pages.data.combine import combine_datasets

        result = combine_datasets(1, "pg_numeric", "pg_numeric", "inner", ["x"], "merged")
        assert result is not None


# ---------------------------------------------------------------------------
# data/explore callbacks
# ---------------------------------------------------------------------------


class TestExploreCallbacks:
    def test_update_explore_selectors_returns_tuple(self):
        from aiml_dash.pages.data.explore import update_explore_selectors

        result = update_explore_selectors("pg_numeric")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_update_explore_selectors_empty_for_none(self):
        from aiml_dash.pages.data.explore import update_explore_selectors

        result = update_explore_selectors(None)
        assert result[0] == [] and result[1] == []

    def test_calculate_statistics_missing_returns_error(self):
        from aiml_dash.pages.data.explore import calculate_statistics

        result = calculate_statistics(1, None, None, None, None, None)
        assert result is not None

    def test_calculate_statistics_valid(self):
        from aiml_dash.pages.data.explore import calculate_statistics

        result = calculate_statistics(1, "pg_numeric", ["x", "y"], None, ["mean", "sd"], None)
        assert result is not None

    def test_export_statistics_no_inputs(self):
        from aiml_dash.pages.data.explore import export_statistics
        from dash import no_update

        result = export_statistics(1, None, None, None, None, None)
        assert result is None or result is no_update


# ---------------------------------------------------------------------------
# data/view callbacks
# ---------------------------------------------------------------------------


class TestViewCallbacks:
    def test_update_view_table_returns_component(self):
        from aiml_dash.pages.data.view import update_view_table

        result = update_view_table("pg_numeric", None, None, None)
        assert result is not None

    def test_update_view_table_with_filter(self):
        from aiml_dash.pages.data.view import update_view_table

        result = update_view_table("pg_numeric", "x > 4", None, None)
        assert result is not None

    def test_export_csv_no_inputs(self):
        from aiml_dash.pages.data.view import export_csv
        from dash import no_update

        result = export_csv(1, None, None, None, None)
        assert result is None or result is no_update


# ---------------------------------------------------------------------------
# data/transform callbacks
# ---------------------------------------------------------------------------


class TestTransformCallbacks:
    def test_update_transform_selectors_empty_for_none(self):
        from aiml_dash.pages.data.transform import update_transform_selectors

        result = update_transform_selectors(None)
        assert isinstance(result, tuple)

    def test_update_transform_selectors_valid(self):
        from aiml_dash.pages.data.transform import update_transform_selectors

        result = update_transform_selectors("pg_numeric")
        assert isinstance(result, tuple)

    def test_create_new_variable_missing_inputs(self):
        from aiml_dash.pages.data.transform import create_new_variable

        result = create_new_variable(1, None, None, None)
        assert result is not None

    def test_apply_transformation_missing(self):
        from aiml_dash.pages.data.transform import apply_transformation

        result = apply_transformation(1, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# data/pivot callbacks
# ---------------------------------------------------------------------------


class TestPivotCallbacks:
    def test_update_pivot_selectors_empty_for_none(self):
        from aiml_dash.pages.data.pivot import update_pivot_selectors

        result = update_pivot_selectors(None)
        assert isinstance(result, tuple)

    def test_update_pivot_selectors_valid(self):
        from aiml_dash.pages.data.pivot import update_pivot_selectors

        result = update_pivot_selectors("pg_two_groups")
        assert isinstance(result, tuple)

    def test_create_pivot_table_missing_inputs(self):
        from aiml_dash.pages.data.pivot import create_pivot_table

        result = create_pivot_table(1, None, None, None, None, "mean", False, False, None)
        assert result is not None


# ---------------------------------------------------------------------------
# data/report callbacks
# ---------------------------------------------------------------------------


class TestReportCallbacks:
    def test_generate_code_missing(self):
        from aiml_dash.pages.data.report import generate_code

        result = generate_code(1, None)
        assert result is not None

    def test_generate_code_valid(self):
        from aiml_dash.pages.data.report import generate_code

        result = generate_code(1, "pg_numeric")
        assert result is not None

    def test_copy_code(self):
        from aiml_dash.pages.data.report import copy_code

        result = copy_code(1, "some code here")
        assert result is not None

    def test_download_script_missing(self):
        from aiml_dash.pages.data.report import download_script

        result = download_script(1, None, None)
        # Returns None or a dict with content=None when no code/dataset
        assert result is None or (isinstance(result, dict) and result.get("content") is None)


# ---------------------------------------------------------------------------
# data/visualize callbacks
# ---------------------------------------------------------------------------


class TestVisualizeCallbacks:
    def test_update_viz_selectors_empty_for_none(self):
        from aiml_dash.pages.data.visualize import update_viz_selectors

        result = update_viz_selectors(None)
        assert isinstance(result, tuple)

    def test_update_viz_selectors_valid(self):
        from aiml_dash.pages.data.visualize import update_viz_selectors

        result = update_viz_selectors("pg_numeric")
        assert isinstance(result, tuple)


# ---------------------------------------------------------------------------
# design/sample_size callbacks
# ---------------------------------------------------------------------------


class TestSampleSizeCallbacks:
    def test_missing_inputs(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size

        result = calculate_sample_size(1, None, None, None, None, None)
        assert result is not None

    def test_one_sample_t(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size

        result = calculate_sample_size(1, "one_sample_t", 0.5, 0.8, 0.05, "two-sided")
        assert result is not None

    def test_two_sample_t(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size

        result = calculate_sample_size(1, "two_sample_t", 0.5, 0.8, 0.05, "two-sided")
        assert result is not None

    def test_one_sample_prop(self):
        from aiml_dash.pages.design.sample_size import calculate_sample_size

        result = calculate_sample_size(1, "one_proportion", 0.5, 0.8, 0.05, "two-sided")
        assert result is not None


# ---------------------------------------------------------------------------
# design/randomizer callbacks
# ---------------------------------------------------------------------------


class TestRandomizerCallbacks:
    def test_missing_inputs(self):
        from aiml_dash.pages.design.randomizer import generate_randomization

        result = generate_randomization(1, None, None, None, None, None)
        assert result is not None

    def test_valid_simple_randomization(self):
        from aiml_dash.pages.design.randomizer import generate_randomization

        result = generate_randomization(1, 20, 4, "A,B,C,D", "simple", 42)
        assert result is not None

    def test_valid_block_randomization(self):
        from aiml_dash.pages.design.randomizer import generate_randomization

        result = generate_randomization(1, 20, 4, "A,B,C,D", "block", 42)
        assert result is not None


# ---------------------------------------------------------------------------
# design/sampling callbacks
# ---------------------------------------------------------------------------


class TestSamplingCallbacks:
    def test_update_strata_options_random(self):
        from aiml_dash.pages.design.sampling import update_strata_options

        result = update_strata_options("random")
        assert result is not None

    def test_update_strata_options_stratified(self):
        from aiml_dash.pages.design.sampling import update_strata_options

        result = update_strata_options("stratified")
        assert result is not None

    def test_generate_sample_missing(self):
        from aiml_dash.pages.design.sampling import generate_sample

        result = generate_sample(1, None, None, None, None)
        assert result is not None


# ---------------------------------------------------------------------------
# multivariate/pre_factor standalone functions
# ---------------------------------------------------------------------------


class TestPreFactorFunctions:
    def test_calculate_bartlett_returns_tuple(self):
        from aiml_dash.pages.multivariate.pre_factor import calculate_bartlett_sphericity

        X = pd.DataFrame(np.random.randn(50, 3), columns=["a", "b", "c"])
        chi_sq, p_val = calculate_bartlett_sphericity(X)
        assert isinstance(float(chi_sq), float)
        assert 0.0 <= float(p_val) <= 1.0

    def test_calculate_kmo_returns_float(self):
        from aiml_dash.pages.multivariate.pre_factor import calculate_kmo

        X = pd.DataFrame(np.random.randn(50, 3), columns=["a", "b", "c"])
        kmo = calculate_kmo(X)
        assert isinstance(float(kmo), float)
        assert 0.0 <= float(kmo) <= 1.0


# ---------------------------------------------------------------------------
# model/decision_analysis standalone functions
# ---------------------------------------------------------------------------


class TestDecisionAnalysisFunctions:
    def test_calculate_ev_payoff_node(self):
        from aiml_dash.pages.model.decision_analysis import calculate_ev

        node = {"payoff": 100}
        assert calculate_ev(node) == 100

    def test_calculate_ev_chance_node(self):
        from aiml_dash.pages.model.decision_analysis import calculate_ev

        node = {
            "type": "chance",
            "branches": [
                {"prob": 0.5, "payoff": 100},
                {"prob": 0.5, "payoff": 0},
            ],
        }
        result = calculate_ev(node)
        assert result == pytest.approx(50.0)

    def test_calculate_ev_decision_node_empty(self):
        from aiml_dash.pages.model.decision_analysis import calculate_ev

        node = {"type": "decision", "branches": []}
        assert calculate_ev(node) == 0

    def test_calculate_ev_with_cost(self):
        from aiml_dash.pages.model.decision_analysis import calculate_ev

        node = {
            "type": "chance",
            "cost": 20,
            "branches": [
                {"prob": 1.0, "payoff": 100},
            ],
        }
        assert calculate_ev(node) == pytest.approx(80.0)

    def test_find_optimal_path_payoff_node(self):
        from aiml_dash.pages.model.decision_analysis import find_optimal_path

        node = {"payoff": 50, "name": "end"}
        result = find_optimal_path(node, "root")
        assert isinstance(result, list)
        assert result[0][1] == 50

    def test_find_optimal_path_empty_decision(self):
        from aiml_dash.pages.model.decision_analysis import find_optimal_path

        node = {"type": "decision", "branches": []}
        result = find_optimal_path(node)
        assert result == []
