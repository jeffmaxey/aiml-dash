"""
Logistic Regression (GLM) Page
===============================

Generalized Linear Model for binary classification outcomes.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
)

from components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


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
                            create_two_column_layout(
                                create_control_card(
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
                                        create_action_button(
                                            button_id="logit-estimate-btn",
                                            label="Estimate",
                                            icon="carbon:play",
                                            color="blue",
                                        ),
                                    ],
                                ),
                                create_results_card(
                                    [html.Div(id="logit-model-info")],
                                ),
                            ),
                        ],
                        value="model",
                    ),
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [html.Div(id="logit-summary-output")],
                            ),
                        ],
                        value="summary",
                    ),
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [html.Div(id="logit-predictions-output")],
                            ),
                        ],
                        value="predict",
                    ),
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [dcc.Graph(id="logit-plot-output")],
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
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("logit-response", "data"), Output("logit-explanatory", "data")],
    Input("logit-dataset", "value"),
)
def update_variable_lists(dataset_name):
    if not dataset_name:
        return [], []
    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
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
        df = app_manager.data_manager.get_dataset(dataset_name)
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
        return None, dmc.Alert(f"Error: {str(e)}", color="red")


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
