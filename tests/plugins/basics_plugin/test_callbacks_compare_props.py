"""Tests for basics_plugin/callbacks_compare_props.py."""

from __future__ import annotations

import pytest

from aiml_dash.plugins.basics_plugin.callbacks_compare_props import (
    run_compare_props_test,
    update_compare_props_datasets,
    update_compare_props_success_levels,
    update_compare_props_variables,
)


class TestUpdateComparePropsDatasetsAndVars:
    def test_datasets_returns_list(self):
        assert isinstance(update_compare_props_datasets("id"), list)

    def test_variables_empty_for_none(self):
        a, b, c, d = update_compare_props_variables(None)
        assert a == [] and b is None and c == [] and d is None

    def test_variables_returns_columns(self):
        a, _, c, _ = update_compare_props_variables("cb_two_groups")
        assert len(a) > 0 and len(c) > 0

    def test_success_levels_empty_for_none(self):
        opts, val = update_compare_props_success_levels(None, None)
        assert opts == [] and val is None

    def test_success_levels_returns_unique_values(self):
        opts, val = update_compare_props_success_levels("cb_two_groups", "outcome")
        labels = [i["label"] for i in opts]
        assert "yes" in labels

    def test_success_levels_missing_column(self):
        opts, val = update_compare_props_success_levels("cb_two_groups", "bad_col")
        assert opts == [] and val is None


class TestRunComparePropTest:
    def test_missing_inputs_returns_result(self):
        result = run_compare_props_test(1, None, None, None, None, None, None)
        assert result is not None
        assert len(result) == 3

    def test_valid_two_sided(self):
        results, style, fig = run_compare_props_test(
            1, "cb_two_groups", "outcome", "yes", "group", "two-sided", 0.95
        )
        assert results is not None

    def test_valid_greater(self):
        results, style, fig = run_compare_props_test(
            1, "cb_two_groups", "outcome", "yes", "group", "greater", 0.95
        )
        assert results is not None

    def test_valid_less(self):
        results, style, fig = run_compare_props_test(
            1, "cb_two_groups", "outcome", "yes", "group", "less", 0.95
        )
        assert results is not None
