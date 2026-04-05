"""Tests for basics_plugin/callbacks_goodness.py."""

from __future__ import annotations

import pytest

from aiml_dash.plugins.basics_plugin.callbacks_goodness import (
    calculate_probability,
    run_goodness_test,
    toggle_custom_input,
    toggle_value2,
    update_input_type,
    update_params,
    update_prob_calc_datasets,
    update_prob_calc_variables,
)


class TestUpdateProbCalcDatasets:
    def test_returns_list(self):
        assert isinstance(update_prob_calc_datasets("id"), list)


class TestUpdateProbCalcVariables:
    def test_returns_empty_for_none(self):
        opts, val = update_prob_calc_variables(None)
        assert opts == [] and val is None

    def test_returns_all_columns(self):
        opts, _ = update_prob_calc_variables("cb_categorical")
        assert len(opts) > 0


class TestToggleCustomInput:
    def test_custom_shows_block(self):
        style = toggle_custom_input("custom")
        assert style.get("display") == "block"

    def test_non_custom_hides(self):
        style = toggle_custom_input("uniform")
        assert style.get("display") == "none"

    def test_normal_hides(self):
        style = toggle_custom_input("normal")
        assert style.get("display") == "none"


class TestUpdateParams:
    def test_normal_returns_two_inputs(self):
        result = update_params("normal")
        assert len(result) == 2

    def test_t_returns_one_input(self):
        assert len(update_params("t")) == 1

    def test_chi2_returns_one_input(self):
        assert len(update_params("chi2")) == 1

    def test_f_returns_two_inputs(self):
        assert len(update_params("f")) == 2

    def test_binomial_returns_two_inputs(self):
        assert len(update_params("binomial")) == 2

    def test_poisson_returns_one_input(self):
        assert len(update_params("poisson")) == 1


class TestUpdateInputType:
    def test_probability_type_returns_list(self):
        result = update_input_type("probability")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_critical_value_type_returns_list(self):
        result = update_input_type("critical_value")
        assert isinstance(result, list)
        assert len(result) > 0


class TestToggleValue2:
    def test_between_shows_block(self):
        style = toggle_value2("between")
        assert style.get("display") == "block"

    def test_lower_hides(self):
        style = toggle_value2("lower")
        assert style.get("display") == "none"

    def test_upper_hides(self):
        style = toggle_value2("upper")
        assert style.get("display") == "none"


class TestCalculateProbability:
    def test_returns_three_elements(self):
        result = calculate_probability(1, "normal", "probability", 0, 1)
        assert len(result) == 3

    def test_normal_distribution(self):
        result, style, fig = calculate_probability(1, "normal", "probability", 0, 1)
        assert result is not None

    def test_t_distribution(self):
        result, style, fig = calculate_probability(1, "t", "probability", 10, None)
        assert result is not None

    def test_chi2_distribution(self):
        result, style, fig = calculate_probability(1, "chi2", "probability", 5, None)
        assert result is not None

    def test_f_distribution(self):
        result, style, fig = calculate_probability(1, "f", "probability", 5, 10)
        assert result is not None

    def test_binomial_distribution(self):
        result, style, fig = calculate_probability(1, "binomial", "probability", 10, 0.5)
        assert result is not None

    def test_poisson_distribution(self):
        result, style, fig = calculate_probability(1, "poisson", "probability", 5, None)
        assert result is not None


class TestRunGoodnessTest:
    def test_missing_inputs_returns_result(self):
        result = run_goodness_test(1, None, None, "uniform", None, 0.95)
        assert result is not None
        assert len(result) == 5

    def test_valid_uniform_test(self):
        results, t_style, table, p_style, fig = run_goodness_test(
            1, "cb_categorical", "category", "uniform", None, 0.95
        )
        assert results is not None

    def test_valid_custom_test(self):
        """Custom expected values test."""
        results, t_style, table, p_style, fig = run_goodness_test(
            1, "cb_categorical", "category", "custom", "0.4, 0.4, 0.2", 0.95
        )
        assert results is not None
