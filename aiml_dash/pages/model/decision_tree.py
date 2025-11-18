"""
Decision Tree (CART) Page
==========================

Classification and Regression Trees.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import accuracy_score, r2_score
import plotly.graph_objects as go

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    return dmc.Container(
        [
            create_page_header(
                "Decision Tree (CART)",
                "Classification and Regression Trees. Interpretable tree-based models for prediction.",
                icon="carbon:tree-view",
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
                            leftSection=DashIconify(icon="carbon:tree-view", width=16),
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
                                                            id="cart-dataset",
                                                            label="Dataset",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="cart-response",
                                                            label="Response",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.MultiSelect(
                                                            id="cart-explanatory",
                                                            label="Explanatory variables",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="cart-type",
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
                                                            id="cart-max-depth",
                                                            label="Max depth",
                                                            value=5,
                                                            min=1,
                                                            max=20,
                                                        ),
                                                        dmc.NumberInput(
                                                            id="cart-min-samples",
                                                            label="Min samples per leaf",
                                                            value=5,
                                                            min=1,
                                                        ),
                                                        dmc.Button(
                                                            "Build Tree",
                                                            id="cart-build-btn",
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
                                            [html.Div(id="cart-status")],
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
                            dmc.Card([html.Div(id="cart-summary")], withBorder=True, p="md"),
                        ],
                        value="summary",
                    ),
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [
                                    dcc.Graph(id="cart-plot", style={"height": "700px"}),
                                ],
                                withBorder=True,
                                p="md",
                            ),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="cart-tabs",
            ),
            dcc.Store(id="cart-model-store"),
            dcc.Store(id="cart-results-store"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("cart-dataset", "data"), Input("cart-tabs", "value"))
def update_datasets(_):
    return [{"label": n, "value": n} for n in data_manager.get_dataset_names()]


@callback(
    Output("cart-response", "data"),
    Output("cart-explanatory", "data"),
    Input("cart-dataset", "value"),
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
    Output("cart-model-store", "data"),
    Output("cart-results-store", "data"),
    Output("cart-status", "children"),
    Input("cart-build-btn", "n_clicks"),
    State("cart-dataset", "value"),
    State("cart-response", "value"),
    State("cart-explanatory", "value"),
    State("cart-type", "value"),
    State("cart-max-depth", "value"),
    State("cart-min-samples", "value"),
    prevent_initial_call=True,
)
def build_tree(n, dataset, response, explanatory, tree_type, max_depth, min_samples):
    if not all([dataset, response, explanatory]):
        return None, None, dmc.Alert("Select all fields", color="red")

    try:
        df = data_manager.get_dataset(dataset)
        X = df[explanatory].select_dtypes(include=[np.number]).fillna(0)
        y = df[response]

        if tree_type == "classification":
            model = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=min_samples)
            model.fit(X, y)
            score = accuracy_score(y, model.predict(X))
            metric = "Accuracy"
        else:
            model = DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples)
            model.fit(X, y)
            score = r2_score(y, model.predict(X))
            metric = "R²"

        results = {
            "score": score,
            "metric": metric,
            "n_leaves": model.get_n_leaves(),
            "depth": model.get_depth(),
        }

        status = dmc.Stack([
            dmc.Alert("Tree built successfully!", color="green"),
            dmc.Text(f"{metric}: {score:.3f}"),
            dmc.Text(f"Depth: {model.get_depth()}, Leaves: {model.get_n_leaves()}"),
        ])

        return (
            {"dataset": dataset, "response": response, "explanatory": explanatory},
            results,
            status,
        )

    except Exception as e:
        return None, None, dmc.Alert(f"Error: {str(e)}", color="red")


@callback(
    Output("cart-summary", "children"),
    Input("cart-results-store", "data"),
)
def update_summary(results):
    if not results:
        return dmc.Text("No tree built yet.", c="dimmed")

    return dmc.Stack(
        [
            dmc.Title("Decision Tree", order=4),
            dmc.Text(f"{results['metric']}: {results['score']:.3f}", fw=700, size="xl"),
            dmc.Text(f"Tree depth: {results['depth']}"),
            dmc.Text(f"Number of leaves: {results['n_leaves']}"),
        ],
        gap="md",
    )


@callback(
    Output("cart-plot", "figure"),
    Input("cart-results-store", "data"),
)
def update_plot(results):
    if not results:
        return go.Figure().add_annotation(
            text="No tree built yet",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    # Placeholder for tree visualization
    return go.Figure().add_annotation(
        text="Tree visualization coming soon",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
