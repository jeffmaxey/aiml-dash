"""Tests for basics_plugin/callbacks_single_mean.py.

Callbacks are pure Python functions that can be invoked directly without a
running Dash application.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from aiml_dash.plugins.basics_plugin.callbacks_single_mean import (
    export_results,
    run_single_mean_test,
    update_datasets,
    update_variables,
)
from aiml_dash.utils.data_manager import data_manager


# ---------------------------------------------------------------------------
# update_datasets
# ---------------------------------------------------------------------------


class TestUpdateDatasets:
    """Tests for update_datasets()."""

    def test_returns_list(self):
        """update_datasets() should return a list."""
        result = update_datasets("dummy-id")
        assert isinstance(result, list)

    def test_entries_have_label_and_value(self):
        """Each entry should have 'label' and 'value' keys."""
        result = update_datasets("dummy-id")
        for item in result:
            assert "label" in item
            assert "value" in item

    def test_known_dataset_included(self):
        """A dataset already registered should appear in the list."""
        result = update_datasets("dummy-id")
        names = [item["value"] for item in result]
        assert "cb_numeric" in names


# ---------------------------------------------------------------------------
# update_variables
# ---------------------------------------------------------------------------


class TestUpdateVariables:
    """Tests for update_variables()."""

    def test_returns_empty_for_none_dataset(self):
        """update_variables(None) should return []."""
        assert update_variables(None) == []

    def test_returns_empty_for_unknown_dataset(self):
        """update_variables() should return [] for an unregistered name."""
        assert update_variables("does_not_exist_xyz") == []

    def test_returns_only_numeric_columns(self):
        """update_variables() should list only numeric columns."""
        result = update_variables("cb_numeric")
        assert isinstance(result, list)
        labels = [item["label"] for item in result]
        assert "x" in labels
        assert "y" in labels
        assert "z" in labels

    def test_non_numeric_columns_excluded(self):
        """Categorical columns should not appear in the variable list."""
        result = update_variables("cb_two_groups")
        labels = [item["label"] for item in result]
        assert "group" not in labels
        assert "outcome" not in labels


# ---------------------------------------------------------------------------
# run_single_mean_test
# ---------------------------------------------------------------------------


class TestRunSingleMeanTest:
    """Tests for run_single_mean_test()."""

    def test_missing_inputs_returns_error_component(self):
        """Missing dataset/variable should produce an error Text component."""
        summary, fig, store, notif = run_single_mean_test(
            1, None, None, 0, "two-sided", 0.95
        )
        assert hasattr(summary, "children") or summary is not None
        assert store is None

    def test_returns_four_elements(self):
        """The callback should always return a 4-tuple."""
        result = run_single_mean_test(1, None, None, 0, "two-sided", 0.95)
        assert len(result) == 4

    def test_successful_two_sided_test(self):
        """A valid two-sided test should return a figure and a success store."""
        summary, fig, store, notif = run_single_mean_test(
            1, "cb_numeric", "x", 0.0, "two-sided", 0.95
        )
        assert isinstance(fig, go.Figure)
        assert store == {"result": "success"}

    def test_successful_greater_test(self):
        """A greater-than alternative should run without error."""
        summary, fig, store, notif = run_single_mean_test(
            1, "cb_numeric", "x", 0.0, "greater", 0.95
        )
        assert isinstance(fig, go.Figure)

    def test_successful_less_test(self):
        """A less-than alternative should run without error."""
        summary, fig, store, notif = run_single_mean_test(
            1, "cb_numeric", "x", 10.0, "less", 0.95
        )
        assert isinstance(fig, go.Figure)

    def test_invalid_variable_returns_error(self):
        """A variable not present in the dataset should result in an error."""
        summary, fig, store, notif = run_single_mean_test(
            1, "cb_numeric", "nonexistent_col", 0.0, "two-sided", 0.95
        )
        assert store is None

    def test_notification_returned(self):
        """A notification component should always be returned."""
        _, _, _, notif = run_single_mean_test(1, "cb_numeric", "x", 0.0, "two-sided", 0.95)
        assert notif is not None


# ---------------------------------------------------------------------------
# export_results
# ---------------------------------------------------------------------------


class TestExportResults:
    """Tests for export_results()."""

    def test_missing_inputs_returns_none(self):
        """Missing dataset/variable should return None."""
        result = export_results(1, None, None)
        assert result is None

    def test_returns_none_for_unknown_dataset(self):
        """An unregistered dataset should return None gracefully."""
        result = export_results(1, "no_such_dataset", "x")
        assert result is None

    def test_returns_send_data_result_for_valid_inputs(self):
        """Valid inputs should return a dcc.send_data_frame result."""
        result = export_results(1, "cb_numeric", "x")
        assert result is not None
