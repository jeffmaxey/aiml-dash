"""
Hierarchical Clustering Page
=============================

Perform hierarchical clustering with dendrograms.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage
import plotly.figure_factory as ff

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    return dmc.Container(
        [
            create_page_header(
                "Hierarchical Clustering",
                "Build hierarchical cluster dendrograms using various linkage methods.",
                icon="carbon:tree-view-alt",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Clustering Settings", order=4),
                                        dmc.Select(
                                            id="hclus-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="hclus-variables",
                                            label="Variables",
                                            placeholder="Select variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="hclus-method",
                                            label="Linkage Method",
                                            data=[
                                                {"label": "Ward", "value": "ward"},
                                                {
                                                    "label": "Complete",
                                                    "value": "complete",
                                                },
                                                {
                                                    "label": "Average",
                                                    "value": "average",
                                                },
                                                {
                                                    "label": "Single",
                                                    "value": "single",
                                                },
                                            ],
                                            value="ward",
                                        ),
                                        dmc.Select(
                                            id="hclus-metric",
                                            label="Distance Metric",
                                            data=[
                                                {
                                                    "label": "Euclidean",
                                                    "value": "euclidean",
                                                },
                                                {
                                                    "label": "Manhattan",
                                                    "value": "cityblock",
                                                },
                                                {
                                                    "label": "Cosine",
                                                    "value": "cosine",
                                                },
                                            ],
                                            value="euclidean",
                                        ),
                                        dmc.Button(
                                            "Build Dendrogram",
                                            id="hclus-run-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
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
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Dendrogram",
                                        value="dendrogram",
                                        leftSection=DashIconify(icon="carbon:tree-view"),
                                    ),
                                    dmc.TabsTab(
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [dcc.Graph(id="hclus-dendrogram")],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        )
                                    ],
                                    value="dendrogram",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [html.Div(id="hclus-summary")],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        )
                                    ],
                                    value="summary",
                                ),
                            ],
                            value="dendrogram",
                            id="hclus-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="hclus-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("hclus-dataset", "data"), Input("hclus-dataset", "id"))
def update_datasets(_):
    return [{"label": name, "value": name} for name in data_manager.get_dataset_names()]


@callback(Output("hclus-variables", "data"), Input("hclus-dataset", "value"))
def update_variables(dataset_name):
    if not dataset_name:
        return []
    try:
        df = data_manager.get_dataset(dataset_name)
        return [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
    except Exception:
        return []


@callback(
    [
        Output("hclus-dendrogram", "figure"),
        Output("hclus-summary", "children"),
        Output("hclus-notification", "children"),
    ],
    Input("hclus-run-btn", "n_clicks"),
    [
        State("hclus-dataset", "value"),
        State("hclus-variables", "value"),
        State("hclus-method", "value"),
        State("hclus-metric", "value"),
    ],
    prevent_initial_call=True,
)
def run_hierarchical(n_clicks, dataset_name, variables, method, metric):
    if not all([dataset_name, variables]):
        return (
            {},
            dmc.Text("Please select dataset and variables.", c="red"),
            dmc.Notification(title="Error", message="Missing inputs", color="red", action="show"),
        )

    try:
        df = data_manager.get_dataset(dataset_name)
        X = df[variables].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        Z = linkage(X_scaled, method=method, metric=metric)

        fig = ff.create_dendrogram(X_scaled, linkagefun=lambda x: linkage(x, method=method, metric=metric))
        fig.update_layout(
            title=f"Dendrogram ({method.title()} linkage, {metric} distance)",
            xaxis_title="Sample Index",
            yaxis_title="Distance",
        )

        summary = dmc.Stack(
            [
                dmc.Text("Hierarchical Clustering Summary", fw=600, size="xl"),
                dmc.Text(f"Linkage Method: {method.title()}"),
                dmc.Text(f"Distance Metric: {metric.title()}"),
                dmc.Text(f"Observations: {len(X)}"),
                dmc.Text(f"Variables: {len(variables)}"),
            ],
            gap="xs",
        )

        return (
            fig,
            summary,
            dmc.Notification(
                title="Success",
                message="Dendrogram complete",
                color="green",
                action="show",
            ),
        )
    except Exception as e:
        return (
            {},
            dmc.Text(f"Error: {str(e)}", c="red"),
            dmc.Notification(title="Error", message=str(e), color="red", action="show"),
        )
