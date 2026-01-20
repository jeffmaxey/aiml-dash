"""
Logistic Regression (GLM) Page
===============================

Generalized Linear Model for binary classification outcomes.
"""

import dash_mantine_components as dmc
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
)
from utils.data_manager import data_manager


def layout():
    """Create the logistic regression page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Logistic Regression (GLM)",
                "Estimate logistic regression models for binary classification. Model binary outcomes as a function of explanatory variables.",
                icon="carbon:chart-logistic-regression",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList([
                        dmc.TabsTab("Model", value="model"),
                        dmc.TabsTab("Summary", value="summary"),
                        dmc.TabsTab("Predict", value="predict"),
                        dmc.TabsTab("Plot", value="plot"),
                    ]),
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title(
                                                            "Model Configuration",
                                                            order=4,
                                                        ),
                                                        dmc.Select(
                                                            id="logit-dataset",
                                                            label="Dataset",
                                                            data=[],
                                                            placeholder="Select dataset",
                                                        ),
                                                        dmc.Select(
                                                            id="logit-response",
                                                            label="Response variable (binary)",
                                                            data=[],
                                                            placeholder="Select response",
                                                        ),
                                                        dmc.MultiSelect(
                                                            id="logit-explanatory",
                                                            label="Explanatory variables",
                                                            data=[],
                                                            placeholder="Select predictors",
                                                        ),
                                                        dmc.Button(
                                                            "Estimate",
                                                            id="logit-estimate-btn",
                                                            leftSection=DashIconify(
                                                                icon="carbon:play",
                                                                width=20,
                                                            ),
                                                            color="blue",
                                                            fullWidth=True,
                                                        ),
                                                    ],
                                                    gap="md",
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
                                            [html.Div(id="logit-model-info")],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 8},
                                ),
                            ]),
                        ],
                        value="model",
                    ),
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [html.Div(id="logit-summary-output")],
                                withBorder=True,
                                radius="md",
                                p="md",
                            ),
                        ],
                        value="summary",
                    ),
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [html.Div(id="logit-predictions-output")],
                                withBorder=True,
                                radius="md",
                                p="md",
                            ),
                        ],
                        value="predict",
                    ),
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [dcc.Graph(id="logit-plot-output")],
                                withBorder=True,
                                radius="md",
                                p="md",
                            ),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="logit-tabs",
            ),
            dcc.Store(id="logit-model-store"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Similar callbacks as linear regression but adapted for classification
@callback(Output("logit-dataset", "data"), Input("logit-dataset", "id"))
def populate_datasets(_):
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("logit-response", "data"), Output("logit-explanatory", "data")],
    Input("logit-dataset", "value"),
)
def update_variable_lists(dataset_name):
    if not dataset_name:
        return [], []
    try:
        df = data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        return all_cols, all_cols
    except Exception:
        return [], []


@callback(
    [Output("logit-model-store", "data"), Output("logit-model-info", "children")],
    Input("logit-estimate-btn", "n_clicks"),
    [
        State("logit-dataset", "value"),
        State("logit-response", "value"),
        State("logit-explanatory", "value"),
    ],
    prevent_initial_call=True,
)
def estimate_model(n_clicks, dataset_name, response, explanatory):
    if not all([dataset_name, response, explanatory]):
        return None, dmc.Alert("Please select all required fields", color="red")

    try:
        df = data_manager.get_dataset(dataset_name)
        X = df[explanatory]
        y = df[response]

        mask = ~(X.isna().any(axis=1) | y.isna())
        X, y = X[mask], y[mask]

        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)

        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)

        model_data = {
            "model": "logistic_regression",
            "dataset": dataset_name,
            "response": response,
            "explanatory": explanatory,
            "accuracy": accuracy,
            "n_obs": len(y),
        }

        info = dmc.Stack([
            dmc.Badge(f"Accuracy: {accuracy:.4f}", color="green", size="lg"),
            dmc.Text(f"Model trained on {len(y)} observations", size="sm"),
        ])

        return model_data, info
    except Exception as e:
        return None, dmc.Alert(f"Error: {e!s}", color="red")


@callback(
    Output("logit-summary-output", "children"),
    Input("logit-model-store", "data"),
)
def update_summary(model_data):
    if not model_data:
        return dmc.Alert("No model estimated yet", color="yellow")
    return dmc.Stack([
        dmc.Badge(f"Accuracy: {model_data['accuracy']:.4f}", color="green"),
        dmc.Text(f"Observations: {model_data['n_obs']}", size="sm"),
    ])
