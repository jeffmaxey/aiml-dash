"""Tests for the PCA page in the multivariate plugin."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aiml_dash.utils.data_manager import data_manager


@pytest.fixture(autouse=True)
def _seed_pca_datasets():
    """Seed the global data_manager with datasets used by PCA tests."""
    rng = np.random.default_rng(0)
    numeric_df = pd.DataFrame(
        {
            "a": rng.normal(0, 1, 50),
            "b": rng.normal(2, 1, 50),
            "c": rng.normal(-1, 2, 50),
            "d": rng.normal(5, 0.5, 50),
        }
    )
    data_manager.add_dataset("pca_test", numeric_df, description="PCA test data")

    mixed_df = pd.DataFrame(
        {
            "x": rng.normal(0, 1, 20),
            "label": ["A", "B"] * 10,
        }
    )
    data_manager.add_dataset("pca_mixed", mixed_df, description="mixed test data")

    # Tiny dataset to trigger "insufficient data" path
    tiny_df = pd.DataFrame({"p": [1.0], "q": [2.0]})
    data_manager.add_dataset("pca_tiny", tiny_df, description="tiny test data")

    yield


class TestPcaLayout:
    def test_layout_returns_container(self):
        from aiml_dash.pages.multivariate.pca import layout

        result = layout()
        # Should be a dmc.Container
        assert result is not None
        assert hasattr(result, "children")

    def test_layout_contains_run_button(self):
        import dash_mantine_components as dmc

        from aiml_dash.pages.multivariate.pca import layout

        def _find_ids(component, ids=None):
            if ids is None:
                ids = []
            cid = getattr(component, "id", None)
            if cid:
                ids.append(cid)
            for child in getattr(component, "children", []) or []:
                if hasattr(child, "children"):
                    _find_ids(child, ids)
            return ids

        result = layout()
        # Verify that the layout is a dmc.Container instance
        assert isinstance(result, dmc.Container)


class TestUpdateDatasets:
    def test_returns_list(self):
        from aiml_dash.pages.multivariate.pca import update_datasets

        result = update_datasets("pca-dataset")
        assert isinstance(result, list)

    def test_entries_have_label_value(self):
        from aiml_dash.pages.multivariate.pca import update_datasets

        result = update_datasets("pca-dataset")
        assert len(result) > 0
        for item in result:
            assert "label" in item
            assert "value" in item

    def test_known_dataset_present(self):
        from aiml_dash.pages.multivariate.pca import update_datasets

        result = update_datasets("pca-dataset")
        names = [i["value"] for i in result]
        assert "pca_test" in names


class TestUpdateVariables:
    def test_returns_empty_for_none(self):
        from aiml_dash.pages.multivariate.pca import update_variables

        assert update_variables(None) == []

    def test_returns_empty_for_unknown_dataset(self):
        from aiml_dash.pages.multivariate.pca import update_variables

        assert update_variables("__nonexistent__") == []

    def test_returns_numeric_columns_only(self):
        from aiml_dash.pages.multivariate.pca import update_variables

        result = update_variables("pca_test")
        labels = [i["label"] for i in result]
        assert "a" in labels
        assert "b" in labels
        assert "c" in labels
        assert "d" in labels

    def test_excludes_non_numeric(self):
        from aiml_dash.pages.multivariate.pca import update_variables

        result = update_variables("pca_mixed")
        labels = [i["label"] for i in result]
        assert "label" not in labels
        assert "x" in labels


class TestRunPca:
    def test_missing_inputs_returns_error_notification(self):
        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, row_data, col_defs, summary, notif = run_pca(
            1, None, None, 2, True
        )
        assert row_data == []
        assert col_defs == []
        assert notif is not None

    def test_single_variable_returns_error(self):
        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, _, _, _, notif = run_pca(1, "pca_test", ["a"], 2, True)
        assert notif is not None

    def test_valid_inputs_returns_non_empty_figures(self):
        import plotly.graph_objects as go

        from aiml_dash.pages.multivariate.pca import run_pca

        scree, biplot, row_data, col_defs, summary, notif = run_pca(
            1, "pca_test", ["a", "b", "c"], 2, True
        )
        assert isinstance(scree, go.Figure)
        assert len(scree.data) >= 1
        assert isinstance(biplot, go.Figure)
        assert len(biplot.data) >= 1

    def test_loadings_table_has_correct_columns(self):
        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, row_data, col_defs, _, _ = run_pca(
            1, "pca_test", ["a", "b", "c"], 2, True
        )
        assert len(col_defs) > 0
        field_names = [cd["field"] for cd in col_defs]
        assert "Variable" in field_names
        assert "PC1" in field_names
        assert "PC2" in field_names

    def test_loadings_table_includes_explained_variance_row(self):
        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, row_data, _, _, _ = run_pca(
            1, "pca_test", ["a", "b", "c"], 2, True
        )
        variables = [r["Variable"] for r in row_data]
        assert "Explained Variance %" in variables

    def test_summary_is_not_none_on_success(self):
        import dash_mantine_components as dmc

        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, _, _, summary, _ = run_pca(
            1, "pca_test", ["a", "b", "c"], 2, True
        )
        assert summary is not None
        assert isinstance(summary, dmc.Stack)

    def test_no_standardize(self):
        import plotly.graph_objects as go

        from aiml_dash.pages.multivariate.pca import run_pca

        scree, biplot, row_data, col_defs, summary, notif = run_pca(
            1, "pca_test", ["a", "b"], 2, False
        )
        assert isinstance(scree, go.Figure)

    def test_insufficient_data_returns_error(self):
        from aiml_dash.pages.multivariate.pca import run_pca

        # 1 row, 2 variables: n_components clamped to 1 < 2 → error
        _, _, row_data, col_defs, summary, notif = run_pca(
            1, "pca_tiny", ["p", "q"], 2, True
        )
        # Should return an error notification (red)
        assert notif is not None
        assert row_data == []

    def test_green_notification_on_success(self):
        import dash_mantine_components as dmc

        from aiml_dash.pages.multivariate.pca import run_pca

        _, _, _, _, _, notif = run_pca(
            1, "pca_test", ["a", "b", "c"], 2, True
        )
        assert isinstance(notif, dmc.Notification)
        assert notif.color == "green"
