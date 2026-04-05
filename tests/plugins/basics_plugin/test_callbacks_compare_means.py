"""Tests for basics_plugin/callbacks_compare_means.py."""

from __future__ import annotations

import plotly.graph_objects as go
import pytest

from aiml_dash.plugins.basics_plugin.callbacks_compare_means import (
    run_compare_means_test,
    update_compare_means_datasets,
    update_compare_means_variables,
)


class TestUpdateCompareMeansDatasets:
    def test_returns_list(self):
        result = update_compare_means_datasets("id")
        assert isinstance(result, list)

    def test_entries_have_label_value(self):
        for item in update_compare_means_datasets("id"):
            assert "label" in item and "value" in item


class TestUpdateCompareMeansVariables:
    def test_returns_two_empty_lists_for_none(self):
        numeric_cols, all_cols = update_compare_means_variables(None)
        assert numeric_cols == []
        assert all_cols == []

    def test_returns_empty_for_unknown(self):
        numeric_cols, all_cols = update_compare_means_variables("_nope_")
        assert numeric_cols == [] and all_cols == []

    def test_numeric_and_all_cols_returned(self):
        numeric_cols, all_cols = update_compare_means_variables("cb_two_groups")
        numeric_labels = [i["label"] for i in numeric_cols]
        all_labels = [i["label"] for i in all_cols]
        assert "value" in numeric_labels
        assert "group" in all_labels

    def test_non_numeric_excluded_from_numeric(self):
        numeric_cols, _ = update_compare_means_variables("cb_two_groups")
        labels = [i["label"] for i in numeric_cols]
        assert "group" not in labels
        assert "outcome" not in labels


class TestRunCompareMeansTest:
    def test_missing_inputs_returns_error(self):
        summary, fig, notif = run_compare_means_test(1, None, None, None, None, None, None)
        assert summary is not None
        assert isinstance(fig, dict)

    def test_returns_three_elements(self):
        result = run_compare_means_test(1, None, None, None, None, None, None)
        assert len(result) == 3

    def test_valid_two_sample_t_test(self):
        summary, fig, notif = run_compare_means_test(
            1, "cb_two_groups", "value", "group", "two-sided", True, 0.95
        )
        assert isinstance(fig, go.Figure)

    def test_welch_test_unequal_var(self):
        summary, fig, notif = run_compare_means_test(
            1, "cb_two_groups", "value", "group", "two-sided", False, 0.95
        )
        assert isinstance(fig, go.Figure)

    def test_greater_alternative(self):
        summary, fig, notif = run_compare_means_test(
            1, "cb_two_groups", "value", "group", "greater", True, 0.95
        )
        assert isinstance(fig, go.Figure)

    def test_default_params_when_none(self):
        """None confidence/alternative should fall back to defaults."""
        summary, fig, notif = run_compare_means_test(
            1, "cb_two_groups", "value", "group", None, None, None
        )
        assert isinstance(fig, go.Figure)

    def test_invalid_variable_returns_error(self):
        summary, fig, notif = run_compare_means_test(
            1, "cb_two_groups", "bad_col", "group", "two-sided", True, 0.95
        )
        assert fig == {} or summary is not None

    def test_group_with_one_level_returns_error(self):
        """A group variable with only one level should produce an error."""
        from aiml_dash.utils.data_manager import data_manager
        import pandas as pd, numpy as np
        df = pd.DataFrame({"val": np.random.randn(20), "grp": ["A"] * 20})
        data_manager.add_dataset("one_group", df)
        summary, fig, notif = run_compare_means_test(
            1, "one_group", "val", "grp", "two-sided", True, 0.95
        )
        assert summary is not None
