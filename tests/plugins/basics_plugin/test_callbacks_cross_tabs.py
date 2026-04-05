"""Tests for basics_plugin/callbacks_cross_tabs.py."""

from __future__ import annotations

import pytest

from aiml_dash.plugins.basics_plugin.callbacks_cross_tabs import (
    run_crosstabs_analysis,
    update_cross_tabs_datasets,
    update_cross_tabs_variables,
)


class TestUpdateCrossTabsDatasets:
    def test_returns_list(self):
        assert isinstance(update_cross_tabs_datasets("id"), list)

    def test_entries_have_label_value(self):
        for item in update_cross_tabs_datasets("id"):
            assert "label" in item and "value" in item


class TestUpdateCrossTabsVariables:
    def test_returns_empties_for_none(self):
        a, va, b, vb = update_cross_tabs_variables(None)
        assert a == [] and va is None and b == [] and vb is None

    def test_returns_all_columns(self):
        a, _, b, _ = update_cross_tabs_variables("cb_categorical")
        labels = [i["label"] for i in a]
        assert "category" in labels and "color" in labels


class TestRunCrosstabsAnalysis:
    def test_missing_inputs_returns_alert(self):
        result = run_crosstabs_analysis(1, None, None, None, False, False, 0.95)
        assert result is not None
        assert len(result) == 5

    def test_same_variable_for_row_and_col(self):
        """Using the same variable for row and col should produce a result (or error gracefully)."""
        result = run_crosstabs_analysis(1, "cb_categorical", "category", "category", False, False, 0.95)
        assert result is not None

    def test_valid_crosstabs(self):
        results, table_style, table, plot_style, fig = run_crosstabs_analysis(
            1, "cb_categorical", "category", "color", False, False, 0.95
        )
        assert results is not None

    def test_with_percentages(self):
        results, table_style, table, plot_style, fig = run_crosstabs_analysis(
            1, "cb_categorical", "category", "color", True, False, 0.95
        )
        assert results is not None

    def test_with_expected_counts(self):
        results, table_style, table, plot_style, fig = run_crosstabs_analysis(
            1, "cb_categorical", "category", "color", False, True, 0.95
        )
        assert results is not None

    def test_missing_column_handled(self):
        result = run_crosstabs_analysis(
            1, "cb_categorical", "category", "nonexistent", False, False, 0.95
        )
        assert result is not None
