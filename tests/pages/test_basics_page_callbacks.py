"""Tests for page-level callbacks in pages/basics/.

These are separate implementations from the plugin-level callbacks in
plugins/basics_plugin/. All functions are pure Python and can be called
directly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from aiml_dash.utils.data_manager import data_manager


# ---------------------------------------------------------------------------
# Fixture: seed datasets
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _seed_basics_page_datasets():
    """Ensure known datasets are available for all basics-page callback tests."""
    rng = np.random.default_rng(1234)

    numeric_df = pd.DataFrame(
        {
            "x": rng.normal(5.0, 1.5, 60),
            "y": rng.normal(3.0, 1.0, 60),
            "z": rng.normal(7.0, 2.0, 60),
        }
    )
    two_group_df = pd.DataFrame(
        {
            "value": np.concatenate(
                [rng.normal(5.0, 1.0, 30), rng.normal(7.0, 1.0, 30)]
            ),
            "group": ["A"] * 30 + ["B"] * 30,
            "outcome": (["yes", "no"] * 30),
        }
    )
    cat_df = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B", "C"] * 10,
            "color": ["red", "blue"] * 25,
        }
    )

    data_manager.add_dataset("bpg_numeric", numeric_df)
    data_manager.add_dataset("bpg_two_groups", two_group_df)
    data_manager.add_dataset("bpg_categorical", cat_df)
    yield


# ---------------------------------------------------------------------------
# pages/basics/single_mean
# ---------------------------------------------------------------------------


class TestPageSingleMeanCallbacks:
    def test_update_datasets_returns_list(self):
        from aiml_dash.pages.basics.single_mean import update_datasets
        result = update_datasets("id")
        assert isinstance(result, list)
        assert any(i["value"] == "bpg_numeric" for i in result)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.single_mean import update_variables
        assert update_variables(None) == []

    def test_update_variables_numeric_only(self):
        from aiml_dash.pages.basics.single_mean import update_variables
        labels = [i["label"] for i in update_variables("bpg_numeric")]
        assert "x" in labels

    def test_run_test_missing_returns_4_tuple(self):
        from aiml_dash.pages.basics.single_mean import run_single_mean_test
        result = run_single_mean_test(1, None, None, 0, "two-sided", 0.95)
        assert len(result) == 4 and result[2] is None

    def test_run_test_valid_two_sided(self):
        from aiml_dash.pages.basics.single_mean import run_single_mean_test
        _, fig, store, _ = run_single_mean_test(1, "bpg_numeric", "x", 0.0, "two-sided", 0.95)
        assert isinstance(fig, go.Figure)
        assert store == {"result": "success"}

    def test_run_test_valid_greater(self):
        from aiml_dash.pages.basics.single_mean import run_single_mean_test
        _, fig, store, _ = run_single_mean_test(1, "bpg_numeric", "x", 0.0, "greater", 0.95)
        assert isinstance(fig, go.Figure)

    def test_run_test_valid_less(self):
        from aiml_dash.pages.basics.single_mean import run_single_mean_test
        _, fig, store, _ = run_single_mean_test(1, "bpg_numeric", "x", 10.0, "less", 0.95)
        assert isinstance(fig, go.Figure)

    def test_export_results_valid(self):
        from aiml_dash.pages.basics.single_mean import export_results
        result = export_results(1, "bpg_numeric", "x")
        assert result is not None

    def test_export_results_missing(self):
        from aiml_dash.pages.basics.single_mean import export_results
        result = export_results(1, None, None)
        assert result is None


# ---------------------------------------------------------------------------
# pages/basics/clt
# ---------------------------------------------------------------------------


class TestPageCltCallbacks:
    def test_run_clt_missing_args_returns_error(self):
        from aiml_dash.pages.basics.clt import run_clt_simulation
        stats, style, fig = run_clt_simulation(1, "normal", None, None, None)
        assert isinstance(stats, list)

    def test_run_clt_normal(self):
        from aiml_dash.pages.basics.clt import run_clt_simulation
        _, style, fig = run_clt_simulation(1, "normal", 30, 100, 42)
        assert isinstance(fig, go.Figure)
        assert style.get("display") == "block"

    def test_run_clt_uniform(self):
        from aiml_dash.pages.basics.clt import run_clt_simulation
        _, style, fig = run_clt_simulation(1, "uniform", 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_run_clt_exponential(self):
        from aiml_dash.pages.basics.clt import run_clt_simulation
        _, style, fig = run_clt_simulation(1, "exponential", 30, 100, 42)
        assert isinstance(fig, go.Figure)


# ---------------------------------------------------------------------------
# pages/basics/correlation
# ---------------------------------------------------------------------------


class TestPageCorrelationCallbacks:
    def test_update_datasets(self):
        from aiml_dash.pages.basics.correlation import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.correlation import update_variables
        assert update_variables(None) == []

    def test_update_variables_numeric(self):
        from aiml_dash.pages.basics.correlation import update_variables
        labels = [i["label"] for i in update_variables("bpg_numeric")]
        assert "x" in labels

    def test_calculate_correlation_missing(self):
        from aiml_dash.pages.basics.correlation import calculate_correlation
        result, notif = calculate_correlation(1, None, None, "pearson")
        assert result is not None

    def test_calculate_correlation_valid(self):
        from aiml_dash.pages.basics.correlation import calculate_correlation
        from dash import dcc
        result, notif = calculate_correlation(1, "bpg_numeric", ["x", "y"], "pearson")
        assert isinstance(result, dcc.Graph)

    def test_calculate_correlation_spearman(self):
        from aiml_dash.pages.basics.correlation import calculate_correlation
        from dash import dcc
        result, notif = calculate_correlation(1, "bpg_numeric", ["x", "y", "z"], "spearman")
        assert isinstance(result, dcc.Graph)


# ---------------------------------------------------------------------------
# pages/basics/compare_means
# ---------------------------------------------------------------------------


class TestPageCompareMeansCallbacks:
    def test_update_datasets(self):
        from aiml_dash.pages.basics.compare_means import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.compare_means import update_variables
        a, b = update_variables(None)
        assert a == [] and b == []

    def test_update_variables_valid(self):
        from aiml_dash.pages.basics.compare_means import update_variables
        numeric, all_cols = update_variables("bpg_two_groups")
        assert len(numeric) > 0 and len(all_cols) > 0

    def test_run_missing_returns_error(self):
        from aiml_dash.pages.basics.compare_means import run_compare_means_test
        result = run_compare_means_test(1, None, None, None, None, None, None)
        assert len(result) == 3

    def test_run_valid_two_sided(self):
        from aiml_dash.pages.basics.compare_means import run_compare_means_test
        summary, fig, notif = run_compare_means_test(
            1, "bpg_two_groups", "value", "group", "two-sided", True, 0.95
        )
        assert isinstance(fig, go.Figure)


# ---------------------------------------------------------------------------
# pages/basics/single_prop
# ---------------------------------------------------------------------------


class TestPageSinglePropCallbacks:
    def test_update_datasets(self):
        from aiml_dash.pages.basics.single_prop import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.single_prop import update_variables
        opts, val = update_variables(None)
        assert opts == [] and val is None

    def test_update_success_levels_empty_for_none(self):
        from aiml_dash.pages.basics.single_prop import update_success_levels
        opts, val = update_success_levels(None, None)
        assert opts == [] and val is None

    def test_update_success_levels_valid(self):
        from aiml_dash.pages.basics.single_prop import update_success_levels
        opts, _ = update_success_levels("bpg_two_groups", "outcome")
        labels = [i["label"] for i in opts]
        assert "yes" in labels

    def test_run_test_valid(self):
        from aiml_dash.pages.basics.single_prop import run_single_prop_test
        result = run_single_prop_test(1, "bpg_two_groups", "outcome", "yes", 0.5, "two-sided", 0.95)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# pages/basics/compare_props
# ---------------------------------------------------------------------------


class TestPageComparePropCallbacks:
    def test_update_datasets(self):
        from aiml_dash.pages.basics.compare_props import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.compare_props import update_variables
        a, b, c, d = update_variables(None)
        assert a == [] and b is None

    def test_update_success_levels_empty_for_none(self):
        from aiml_dash.pages.basics.compare_props import update_success_levels
        opts, val = update_success_levels(None, None)
        assert opts == [] and val is None

    def test_run_test_missing(self):
        from aiml_dash.pages.basics.compare_props import run_compare_props_test
        result = run_compare_props_test(1, None, None, None, None, None, None)
        assert len(result) == 3

    def test_run_test_valid(self):
        from aiml_dash.pages.basics.compare_props import run_compare_props_test
        result = run_compare_props_test(
            1, "bpg_two_groups", "outcome", "yes", "group", "two-sided", 0.95
        )
        assert len(result) == 3


# ---------------------------------------------------------------------------
# pages/basics/cross_tabs
# ---------------------------------------------------------------------------


class TestPageCrossTabsCallbacks:
    def test_update_datasets(self):
        from aiml_dash.pages.basics.cross_tabs import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_empty_for_none(self):
        from aiml_dash.pages.basics.cross_tabs import update_variables
        a, va, b, vb = update_variables(None)
        assert a == [] and va is None

    def test_run_crosstabs_missing(self):
        from aiml_dash.pages.basics.cross_tabs import run_crosstabs_analysis
        result = run_crosstabs_analysis(1, None, None, None, False, False, 0.95)
        assert len(result) == 5

    def test_run_crosstabs_valid(self):
        from aiml_dash.pages.basics.cross_tabs import run_crosstabs_analysis
        result = run_crosstabs_analysis(
            1, "bpg_categorical", "category", "color", False, False, 0.95
        )
        assert result is not None


# ---------------------------------------------------------------------------
# pages/basics/goodness
# ---------------------------------------------------------------------------


class TestPageGoodnessCallbacks:
    def test_toggle_custom_input_custom(self):
        from aiml_dash.pages.basics.goodness import toggle_custom_input
        assert toggle_custom_input("custom").get("display") == "block"

    def test_toggle_custom_input_other(self):
        from aiml_dash.pages.basics.goodness import toggle_custom_input
        assert toggle_custom_input("uniform").get("display") == "none"

    def test_update_datasets(self):
        from aiml_dash.pages.basics.goodness import update_datasets
        assert isinstance(update_datasets("id"), list)

    def test_update_variables_valid(self):
        from aiml_dash.pages.basics.goodness import update_variables
        opts, _ = update_variables("bpg_categorical")
        assert len(opts) > 0

    def test_run_goodness_missing(self):
        from aiml_dash.pages.basics.goodness import run_goodness_test
        result = run_goodness_test(1, None, None, "uniform", None, 0.95)
        assert len(result) == 5

    def test_run_goodness_uniform_valid(self):
        from aiml_dash.pages.basics.goodness import run_goodness_test
        result = run_goodness_test(1, "bpg_categorical", "category", "uniform", None, 0.95)
        assert len(result) == 5


# ---------------------------------------------------------------------------
# pages/basics/prob_calc
# ---------------------------------------------------------------------------


class TestPageProbCalcCallbacks:
    def test_update_params_normal(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("normal")) == 2

    def test_update_params_t(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("t")) == 1

    def test_update_params_chi2(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("chi2")) == 1

    def test_update_params_f(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("f")) == 2

    def test_update_params_binomial(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("binomial")) == 2

    def test_update_params_poisson(self):
        from aiml_dash.pages.basics.prob_calc import update_params
        assert len(update_params("poisson")) == 1

    def test_update_input_type_probability(self):
        from aiml_dash.pages.basics.prob_calc import update_input_type
        result = update_input_type("probability")
        assert isinstance(result, list) and len(result) > 0

    def test_update_input_type_critical(self):
        from aiml_dash.pages.basics.prob_calc import update_input_type
        result = update_input_type("critical_value")
        assert isinstance(result, list) and len(result) > 0

    def test_toggle_value2_between(self):
        from aiml_dash.pages.basics.prob_calc import toggle_value2
        assert toggle_value2("between").get("display") == "block"

    def test_toggle_value2_lower(self):
        from aiml_dash.pages.basics.prob_calc import toggle_value2
        assert toggle_value2("lower").get("display") == "none"

    def test_calculate_probability_normal(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "normal", "probability", 0, 1)
        assert len(result) == 3

    def test_calculate_probability_t(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "t", "probability", 10, None)
        assert result[0] is not None

    def test_calculate_probability_chi2(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "chi2", "probability", 5, None)
        assert result[0] is not None

    def test_calculate_probability_f(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "f", "probability", 5, 10)
        assert result[0] is not None

    def test_calculate_probability_binomial(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "binomial", "probability", 10, 0.5)
        assert result[0] is not None

    def test_calculate_probability_poisson(self):
        from aiml_dash.pages.basics.prob_calc import calculate_probability
        result = calculate_probability(1, "poisson", "probability", 5, None)
        assert result[0] is not None
