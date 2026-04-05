"""Correlation analysis callbacks.

This module is part of the basics plugin callback suite.
Callbacks are registered automatically via ``@callback`` decorators on import.
"""

import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
from dash import Input, Output, State, callback, dcc

from aiml_dash.utils.data_manager import data_manager


@callback(Output("corr-dataset", "data"), Input("corr-dataset", "id"))
def update_correlation_datasets(_):
    """Populate dataset dropdown with available datasets.

    Parameters
    ----------
    _ : Any
        Value provided for this parameter."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(Output("corr-variables", "data"), Input("corr-dataset", "value"))
def update_correlation_variables(dataset_name):
    """Update variable options based on selected dataset.

    Parameters
    ----------
    dataset_name : Any
        Value provided for this parameter."""
    if not dataset_name:
        return []
    try:
        df = data_manager.get_dataset(dataset_name)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return [{"label": col, "value": col} for col in numeric_cols]
    except Exception:
        return []


@callback(
    [Output("corr-output", "children"), Output("corr-notification", "children")],
    Input("corr-btn", "n_clicks"),
    [
        State("corr-dataset", "value"),
        State("corr-variables", "value"),
        State("corr-method", "value"),
    ],
    prevent_initial_call=True,
)
def calculate_correlation(n_clicks, dataset_name, variables, method):
    """Calculate and display correlation matrix.

    Parameters
    ----------
    n_clicks : Any
        Input value for ``n_clicks``.
    dataset_name : Any
        Input value for ``dataset_name``.
    variables : Any
        Input value for ``variables``.
    method : Any
        Value provided for this parameter."""
    if not all([dataset_name, variables]) or len(variables) < 2:
        return dmc.Text(
            "Select dataset and at least 2 variables.", c="red"
        ), dmc.Notification(
            title="Error", message="Missing inputs", color="red", action="show"
        )

    try:
        df = data_manager.get_dataset(dataset_name)
        corr_matrix = df[variables].corr(method=method)
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            title=f"{method.title()} Correlation Matrix",
            color_continuous_scale="RdBu_r",
            range_color=[-1, 1],
        )
        return dcc.Graph(figure=fig), dmc.Notification(
            title="Success",
            message="Correlation calculated",
            color="green",
            action="show",
        )
    except Exception as e:
        return dmc.Text(f"Error: {e!s}", c="red"), dmc.Notification(
            title="Error", message=str(e), color="red", action="show"
        )


