"""Correlation Analysis Page"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
import plotly.express as px
from components.common import (
    create_action_button,
    create_control_card,
    create_dataset_selector,
    create_page_header,
    create_results_card,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    return dmc.Container(
        [
            create_page_header(
                "Correlation",
                "Correlation matrix and significance tests",
                icon="carbon:connection-signal",
            ),
            create_two_column_layout(
                create_control_card(
                    [
                        create_dataset_selector(
                            selector_id="corr-dataset",
                            label="Dataset",
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
                        create_action_button(
                            button_id="corr-btn",
                            label="Calculate",
                            icon="carbon:play",
                        ),
                    ],
                    title="Settings",
                ),
                create_results_card(
                    [html.Div(id="corr-output")],
                ),
            ),
            html.Div(id="corr-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("corr-dataset", "data"), Input("corr-dataset", "id"))
def update_datasets(_):
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(Output("corr-variables", "data"), Input("corr-dataset", "value"))
def update_variables(dataset_name):
    if not dataset_name:
        return []
    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
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
    if not all([dataset_name, variables]) or len(variables) < 2:
        return dmc.Text("Select dataset and at least 2 variables.", c="red"), dmc.Notification(
            title="Error", message="Missing inputs", color="red", action="show"
        )

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
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
        return dmc.Text(f"Error: {str(e)}", c="red"), dmc.Notification(
            title="Error", message=str(e), color="red", action="show"
        )
