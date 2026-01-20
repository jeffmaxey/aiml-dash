"""
Random Forest Page
==================

Ensemble of decision trees for robust prediction.
"""

import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score
from utils.data_manager import data_manager


def layout():
    return dmc.Container(
        [
            create_page_header(
                "Random Forest",
                "Ensemble of decision trees. Robust and accurate predictions with feature importance.",
                icon="carbon:cloud-satellite",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList([
                        dmc.TabsTab(
                            "Model",
                            value="model",
                            leftSection=DashIconify(icon="carbon:model", width=16),
                        ),
                        dmc.TabsTab(
                            "Summary",
                            value="summary",
                            leftSection=DashIconify(icon="carbon:document", width=16),
                        ),
                        dmc.TabsTab(
                            "Plot",
                            value="plot",
                            leftSection=DashIconify(icon="carbon:chart-bar", width=16),
                        ),
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
                                                        dmc.Title("Configuration", order=4),
                                                        dmc.Select(
                                                            id="rf-dataset",
                                                            label="Dataset",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="rf-response",
                                                            label="Response",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.MultiSelect(
                                                            id="rf-explanatory",
                                                            label="Explanatory variables",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="rf-type",
                                                            label="Type",
                                                            data=[
                                                                {
                                                                    "label": "Classification",
                                                                    "value": "classification",
                                                                },
                                                                {
                                                                    "label": "Regression",
                                                                    "value": "regression",
                                                                },
                                                            ],
                                                            value="classification",
                                                        ),
                                                        dmc.NumberInput(
                                                            id="rf-n-trees",
                                                            label="Number of trees",
                                                            value=100,
                                                            min=10,
                                                            max=500,
                                                            step=10,
                                                        ),
                                                        dmc.NumberInput(
                                                            id="rf-max-depth",
                                                            label="Max depth",
                                                            value=10,
                                                            min=1,
                                                            max=30,
                                                        ),
                                                        dmc.NumberInput(
                                                            id="rf-seed",
                                                            label="Random seed",
                                                            value=1234,
                                                            min=0,
                                                        ),
                                                        dmc.Button(
                                                            "Train Forest",
                                                            id="rf-train-btn",
                                                            fullWidth=True,
                                                            color="blue",
                                                        ),
                                                    ],
                                                    gap="sm",
                                                )
                                            ],
                                            withBorder=True,
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 4},
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [html.Div(id="rf-status")],
                                            withBorder=True,
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
                            dmc.Card([html.Div(id="rf-summary")], withBorder=True, p="md"),
                        ],
                        value="summary",
                    ),
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [
                                    dcc.Graph(id="rf-plot", style={"height": "600px"}),
                                ],
                                withBorder=True,
                                p="md",
                            ),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="rf-tabs",
            ),
            dcc.Store(id="rf-model-store"),
            dcc.Store(id="rf-results-store"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("rf-dataset", "data"), Input("rf-tabs", "value"))
def update_datasets(_):
    return [{"label": n, "value": n} for n in data_manager.get_dataset_names()]


@callback(
    Output("rf-response", "data"),
    Output("rf-explanatory", "data"),
    Input("rf-dataset", "value"),
)
def update_variables(dataset):
    if not dataset:
        return [], []
    df = data_manager.get_dataset(dataset)
    if df is None:
        return [], []
    vars_list = [{"label": col, "value": col} for col in df.columns]
    return vars_list, vars_list


@callback(
    Output("rf-model-store", "data"),
    Output("rf-results-store", "data"),
    Output("rf-status", "children"),
    Input("rf-train-btn", "n_clicks"),
    State("rf-dataset", "value"),
    State("rf-response", "value"),
    State("rf-explanatory", "value"),
    State("rf-type", "value"),
    State("rf-n-trees", "value"),
    State("rf-max-depth", "value"),
    State("rf-seed", "value"),
    prevent_initial_call=True,
)
def train_forest(n, dataset, response, explanatory, rf_type, n_trees, max_depth, seed):
    if not all([dataset, response, explanatory]):
        return None, None, dmc.Alert("Select all fields", color="red")

    try:
        df = data_manager.get_dataset(dataset)
        X = df[explanatory].select_dtypes(include=[np.number]).fillna(0)
        y = df[response]

        if rf_type == "classification":
            model = RandomForestClassifier(n_estimators=n_trees, max_depth=max_depth, random_state=seed)
            model.fit(X, y)
            score = accuracy_score(y, model.predict(X))
            metric = "Accuracy"
        else:
            model = RandomForestRegressor(n_estimators=n_trees, max_depth=max_depth, random_state=seed)
            model.fit(X, y)
            score = r2_score(y, model.predict(X))
            metric = "R²"

        importance = dict(zip(explanatory, model.feature_importances_))

        results = {
            "score": score,
            "metric": metric,
            "importance": importance,
        }

        status = dmc.Stack([
            dmc.Alert("Forest trained successfully!", color="green"),
            dmc.Text(f"{metric}: {score:.3f}"),
            dmc.Text(f"Trees: {n_trees}"),
        ])

        return (
            {"dataset": dataset, "response": response, "explanatory": explanatory},
            results,
            status,
        )

    except Exception as e:
        return None, None, dmc.Alert(f"Error: {e!s}", color="red")


@callback(
    Output("rf-summary", "children"),
    Input("rf-results-store", "data"),
)
def update_summary(results):
    if not results:
        return dmc.Text("No forest trained yet.", c="dimmed")

    return dmc.Stack(
        [
            dmc.Title("Random Forest", order=4),
            dmc.Text(f"{results['metric']}: {results['score']:.3f}", fw=700, size="xl"),
        ],
        gap="md",
    )


@callback(
    Output("rf-plot", "figure"),
    Input("rf-results-store", "data"),
)
def update_plot(results):
    if not results or not results.get("importance"):
        return go.Figure().add_annotation(
            text="No model trained yet",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    importance = results["importance"]
    fig = go.Figure(go.Bar(x=list(importance.values()), y=list(importance.keys()), orientation="h"))
    fig.update_layout(
        title="Feature Importance",
        xaxis_title="Importance",
        yaxis_title="Feature",
        height=600,
    )
    return fig
