"""
K-Means Clustering Page
========================

Perform K-means clustering to segment data into groups.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import plotly.graph_objects as go
import plotly.express as px

from aiml_dash.components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the K-means clustering page layout."""
    return dmc.Container(
        [
            create_page_header(
                "K-Means Clustering",
                "Segment observations into K clusters using iterative partitioning. Determine optimal number of clusters.",
                icon="carbon:cluster",
            ),
            create_two_column_layout(
                # Left panel
                create_control_card(
                    [
                        dmc.Title("Clustering Settings", order=4),
                        dmc.Select(
                            id="kmeans-dataset",
                            label="Dataset",
                            placeholder="Select dataset...",
                            data=[],
                        ),
                        dmc.MultiSelect(
                            id="kmeans-variables",
                            label="Variables",
                            placeholder="Select variables...",
                            data=[],
                            searchable=True,
                        ),
                        dmc.NumberInput(
                            id="kmeans-k",
                            label="Number of Clusters (K)",
                            value=3,
                            min=2,
                            max=20,
                            step=1,
                        ),
                        dmc.NumberInput(
                            id="kmeans-seed",
                            label="Random Seed",
                            value=1234,
                            min=0,
                            step=1,
                        ),
                        create_action_button(
                            button_id="kmeans-run-btn",
                            label="Run Clustering",
                            icon="carbon:play",
                            size="lg",
                            color="blue",
                        ),
                    ],
                ),
                # Right panel
                dmc.Tabs(
                    [
                        dmc.TabsList([
                            dmc.TabsTab(
                                "Cluster Plot",
                                value="plot",
                                leftSection=DashIconify(icon="carbon:chart-scatter"),
                            ),
                            dmc.TabsTab(
                                "Summary",
                                value="summary",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Elbow Plot",
                                value="elbow",
                                leftSection=DashIconify(icon="carbon:chart-line"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [dcc.Graph(id="kmeans-cluster-plot")],
                                )
                            ],
                            value="plot",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [html.Div(id="kmeans-summary")],
                                )
                            ],
                            value="summary",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [dcc.Graph(id="kmeans-elbow-plot")],
                                )
                            ],
                            value="elbow",
                        ),
                    ],
                    value="plot",
                    id="kmeans-tabs",
                ),
            ),
            html.Div(id="kmeans-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("kmeans-dataset", "data"), Input("kmeans-dataset", "id"))
def update_datasets(_):
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(Output("kmeans-variables", "data"), Input("kmeans-dataset", "value"))
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
    [
        Output("kmeans-cluster-plot", "figure"),
        Output("kmeans-summary", "children"),
        Output("kmeans-elbow-plot", "figure"),
        Output("kmeans-notification", "children"),
    ],
    Input("kmeans-run-btn", "n_clicks"),
    [
        State("kmeans-dataset", "value"),
        State("kmeans-variables", "value"),
        State("kmeans-k", "value"),
        State("kmeans-seed", "value"),
    ],
    prevent_initial_call=True,
)
def run_kmeans(n_clicks, dataset_name, variables, k, seed):
    if not all([dataset_name, variables]) or len(variables) < 2:
        return (
            {},
            dmc.Text("Please select dataset and at least 2 variables.", c="red"),
            {},
            dmc.Notification(title="Error", message="Missing inputs", color="red", action="show"),
        )

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        X = df[variables].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        # Cluster plot (PCA for visualization if more than 2 vars)
        if len(variables) == 2:
            plot_df = pd.DataFrame(X_scaled, columns=variables)
            plot_df["Cluster"] = [f"Cluster {c + 1}" for c in clusters]
            fig = px.scatter(
                plot_df,
                x=variables[0],
                y=variables[1],
                color="Cluster",
                title="K-Means Clustering",
            )
        else:
            from sklearn.decomposition import PCA

            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            plot_df = pd.DataFrame(X_pca, columns=["PC1", "PC2"])
            plot_df["Cluster"] = [f"Cluster {c + 1}" for c in clusters]
            fig = px.scatter(
                plot_df,
                x="PC1",
                y="PC2",
                color="Cluster",
                title="K-Means Clustering (PCA)",
            )

        # Summary
        silhouette = silhouette_score(X_scaled, clusters)
        inertia = kmeans.inertia_
        cluster_sizes = pd.Series(clusters).value_counts().sort_index()

        summary = dmc.Stack(
            [
                dmc.Text(f"Number of Clusters: {k}", fw=600, size="lg"),
                dmc.Text(f"Silhouette Score: {silhouette:.3f}"),
                dmc.Text(f"Within-cluster Sum of Squares: {inertia:.2f}"),
                dmc.Divider(),
                dmc.Text("Cluster Sizes:", fw=600),
                *[dmc.Text(f"Cluster {i + 1}: {size} observations") for i, size in enumerate(cluster_sizes)],
            ],
            gap="xs",
        )

        # Elbow plot
        k_range = range(2, min(11, len(X)))
        inertias = []
        for k_test in k_range:
            km = KMeans(n_clusters=k_test, random_state=seed, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)

        elbow_fig = go.Figure()
        elbow_fig.add_trace(go.Scatter(x=list(k_range), y=inertias, mode="lines+markers"))
        elbow_fig.update_layout(
            title="Elbow Plot",
            xaxis_title="Number of Clusters",
            yaxis_title="Within-Cluster Sum of Squares",
        )

        return (
            fig,
            summary,
            elbow_fig,
            dmc.Notification(
                title="Success",
                message="Clustering complete",
                color="green",
                action="show",
            ),
        )
    except Exception as e:
        return (
            {},
            dmc.Text(f"Error: {str(e)}", c="red"),
            {},
            dmc.Notification(title="Error", message=str(e), color="red", action="show"),
        )
