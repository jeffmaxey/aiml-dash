"""Tests for basics_plugin/callbacks_correlation.py."""

from __future__ import annotations

import pytest

from aiml_dash.plugins.basics_plugin.callbacks_correlation import (
    calculate_correlation,
    update_correlation_datasets,
    update_correlation_variables,
)


class TestUpdateCorrelationDatasets:
    def test_returns_list(self):
        result = update_correlation_datasets("id")
        assert isinstance(result, list)

    def test_entries_have_label_value(self):
        result = update_correlation_datasets("id")
        for item in result:
            assert "label" in item and "value" in item

    def test_known_dataset_present(self):
        result = update_correlation_datasets("id")
        names = [i["value"] for i in result]
        assert "cb_numeric" in names


class TestUpdateCorrelationVariables:
    def test_returns_empty_for_none(self):
        assert update_correlation_variables(None) == []

    def test_returns_empty_for_unknown(self):
        assert update_correlation_variables("_nope_") == []

    def test_returns_numeric_columns(self):
        result = update_correlation_variables("cb_numeric")
        labels = [i["label"] for i in result]
        assert "x" in labels
        assert "y" in labels

    def test_excludes_non_numeric(self):
        result = update_correlation_variables("cb_two_groups")
        labels = [i["label"] for i in result]
        assert "group" not in labels


class TestCalculateCorrelation:
    def test_missing_inputs_returns_error(self):
        summary, notif = calculate_correlation(1, None, None, "pearson")
        assert summary is not None

    def test_only_one_variable_returns_error(self):
        summary, notif = calculate_correlation(1, "cb_numeric", ["x"], "pearson")
        assert summary is not None

    def test_valid_pearson(self):
        from dash import dcc
        result, notif = calculate_correlation(1, "cb_numeric", ["x", "y"], "pearson")
        assert isinstance(result, dcc.Graph)

    def test_valid_spearman(self):
        from dash import dcc
        result, notif = calculate_correlation(1, "cb_numeric", ["x", "y", "z"], "spearman")
        assert isinstance(result, dcc.Graph)

    def test_returns_two_elements(self):
        result = calculate_correlation(1, "cb_numeric", ["x", "y"], "pearson")
        assert len(result) == 2
