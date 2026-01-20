"""Correlation Analysis Page"""

import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from utils.data_manager import data_manager


def layout():
    """Create the correlation analysis page layout.

    Returns:
        Container with correlation settings and output area.
    """
    return dmc.Container(
        [
            create_page_header(
                "Correlation",
                "Correlation matrix and significance tests",
                icon="carbon:connection-signal",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Settings", order=4),
                                        dmc.Select(
                                            id="corr-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="corr-variables",
                                            label="Variables",
                                            placeholder="Select variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="corr-method",
                                            label="Method",
                                            value="pearson",
                                            data=[
                                                {
                                                    "label": "Pearson",
                                                    "value": "pearson",
                                                },
                                                {
                                                    "label": "Spearman",
                                                    "value": "spearman",
                                                },
                                                {
                                                    "label": "Kendall",
                                                    "value": "kendall",
                                                },
                                            ],
                                        ),
                                        dmc.Button(
                                            "Calculate",
                                            id="corr-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            color="blue",
                                        ),
                                    ],
                                    gap="sm",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                dmc.GridCol(
                    [
                        dmc.Card(
                            [html.Div(id="corr-output")],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="corr-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("corr-dataset", "data"), Input("corr-dataset", "id"))
def update_datasets(_):
    """Populate dataset dropdown with available datasets.

    Returns:
        List of dataset options for dropdown.
    """
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(Output("corr-variables", "data"), Input("corr-dataset", "value"))
def update_variables(dataset_name):
    """Update variable options based on selected dataset.

    Args:
        dataset_name: Name of the selected dataset.

    Returns:
        List of numeric column options for dropdown.
    """
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

    Args:
        n_clicks: Number of button clicks.
        dataset_name: Name of the dataset to analyze.
        variables: List of variables to correlate.
        method: Correlation method (pearson, spearman, or kendall).

    Returns:
        Tuple of (output_children, notification_children).
    """
    if not all([dataset_name, variables]) or len(variables) < 2:
        return dmc.Text("Select dataset and at least 2 variables.", c="red"), dmc.Notification(
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
