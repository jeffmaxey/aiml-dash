"""Tests for basics_plugin/callbacks_single_prop.py."""

from __future__ import annotations

import pytest

from aiml_dash.plugins.basics_plugin.callbacks_single_prop import (
    run_single_prop_test,
    update_single_prop_datasets,
    update_single_prop_success_levels,
    update_single_prop_variables,
)


class TestUpdateSinglePropDatasets:
    def test_returns_list(self):
        result = update_single_prop_datasets("id")
        assert isinstance(result, list)

    def test_known_dataset_present(self):
        names = [i["value"] for i in update_single_prop_datasets("id")]
        assert "cb_two_groups" in names


class TestUpdateSinglePropVariables:
    def test_returns_empty_for_none(self):
        cols, val = update_single_prop_variables(None)
        assert cols == [] and val is None

    def test_returns_all_columns(self):
        cols, val = update_single_prop_variables("cb_two_groups")
        labels = [i["label"] for i in cols]
        assert "group" in labels
        assert "outcome" in labels

    def test_second_element_is_none(self):
        _, val = update_single_prop_variables("cb_two_groups")
        assert val is None


class TestUpdateSinglePropSuccessLevels:
    def test_returns_empty_for_none_inputs(self):
        opts, val = update_single_prop_success_levels(None, None)
        assert opts == [] and val is None

    def test_returns_unique_values(self):
        opts, val = update_single_prop_success_levels("cb_two_groups", "outcome")
        labels = [i["label"] for i in opts]
        assert "yes" in labels
        assert "no" in labels

    def test_missing_column_returns_empty(self):
        opts, val = update_single_prop_success_levels("cb_two_groups", "nonexistent_col")
        assert opts == [] and val is None


class TestRunSinglePropTest:
    def test_missing_inputs_returns_list(self):
        result = run_single_prop_test(1, None, None, None, 0.5, "two-sided", 0.95)
        # Should return some output (error state)
        assert result is not None

    def test_returns_three_elements(self):
        result = run_single_prop_test(1, None, None, None, 0.5, "two-sided", 0.95)
        assert len(result) == 3

    def test_valid_two_sided_test(self):
        results, style, fig = run_single_prop_test(
            1, "cb_two_groups", "outcome", "yes", 0.5, "two-sided", 0.95
        )
        assert results is not None

    def test_valid_greater_test(self):
        results, style, fig = run_single_prop_test(
            1, "cb_two_groups", "outcome", "yes", 0.3, "greater", 0.95
        )
        assert results is not None

    def test_valid_less_test(self):
        results, style, fig = run_single_prop_test(
            1, "cb_two_groups", "outcome", "yes", 0.8, "less", 0.95
        )
        assert results is not None
