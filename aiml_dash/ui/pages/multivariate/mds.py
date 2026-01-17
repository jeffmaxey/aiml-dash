"""
Multi-Dimensional Scaling (MDS) Page
=====================================

Perform multi-dimensional scaling to visualize similarity/dissimilarity between objects
in a low-dimensional space.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from sklearn.manifold import MDS as SklearnMDS
from sklearn.metrics import pairwise_distances
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
    """Create the MDS page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Multi-Dimensional Scaling",
                "Visualize similarities or dissimilarities between objects in a low-dimensional space using MDS.",
                icon="carbon:chart-3d",
            ),
            create_two_column_layout(
                # Left panel - configuration
                create_control_card(
                    [
                        dmc.Title("Data Selection", order=4),
                        dmc.Select(
                            id="mds-dataset",
                            label="Dataset",
                            placeholder="Select dataset...",
                            data=[],
                        ),
                        dmc.Select(
                            id="mds-id-var",
                            label="ID Variable (Optional)",
                            description="Variable identifying objects/brands",
                            placeholder="Select ID variable...",
                            data=[],
                            clearable=True,
                        ),
                        dmc.MultiSelect(
                            id="mds-features",
                            label="Feature Variables",
                            description="Variables used to compute distances",
                            placeholder="Select features...",
                            data=[],
                            searchable=True,
                        ),
                        dmc.Divider(
                            label="MDS Options",
                            labelPosition="center",
                        ),
                        dmc.Text("Input Type", size="sm", fw=500),
                        dmc.SegmentedControl(
                            id="mds-input-type",
                            data=[
                                {
                                    "label": "Data Matrix",
                                    "value": "data",
                                },
                                {
                                    "label": "Distance Matrix",
                                    "value": "distance",
                                },
                            ],
                            value="data",
                        ),
                        dmc.Select(
                            id="mds-metric",
                            label="Distance Metric",
                            data=[
                                {
                                    "label": "Euclidean",
                                    "value": "euclidean",
                                },
                                {
                                    "label": "Manhattan",
                                    "value": "manhattan",
                                },
                                {
                                    "label": "Cosine",
                                    "value": "cosine",
                                },
                                {
                                    "label": "Correlation",
                                    "value": "correlation",
                                },
                            ],
                            value="euclidean",
                        ),
                        dmc.NumberInput(
                            id="mds-dimensions",
                            label="Number of Dimensions",
                            description="Target dimensionality",
                            value=2,
                            min=2,
                            max=5,
                            step=1,
                        ),
                        dmc.Switch(
                            id="mds-metric-mds",
                            label="Metric MDS",
                            description="Use metric (vs non-metric) MDS",
                            checked=True,
                        ),
                        dmc.NumberInput(
                            id="mds-random-seed",
                            label="Random Seed",
                            value=1234,
                            min=0,
                            step=1,
                        ),
                        create_action_button(
                            button_id="mds-run-btn",
                            label="Run MDS",
                            icon="carbon:play",
                            size="lg",
                            color="blue",
                        ),
                        dmc.Divider(),
                        dmc.Button(
                            "Export Coordinates (CSV)",
                            id="mds-download-coords",
                            leftSection=DashIconify(icon="carbon:download", width=16),
                            variant="light",
                            fullWidth=True,
                        ),
                    ],
                ),
                # Right panel - results
                dmc.Tabs(
                    [
                        dmc.TabsList([
                            dmc.TabsTab(
                                "MDS Plot",
                                value="plot",
                                leftSection=DashIconify(icon="carbon:chart-scatter"),
                            ),
                            dmc.TabsTab(
                                "Summary",
                                value="summary",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Stress Plot",
                                value="stress",
                                leftSection=DashIconify(icon="carbon:chart-line"),
                            ),
                            dmc.TabsTab(
                                "Distance Matrix",
                                value="distances",
                                leftSection=DashIconify(icon="carbon:table"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        dcc.Graph(
                                            id="mds-plot",
                                            style={"height": "600px"},
                                        ),
                                    ],
                                ),
                            ],
                            value="plot",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="mds-summary"),
                                    ],
                                ),
                            ],
                            value="summary",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        dcc.Graph(id="mds-stress-plot"),
                                    ],
                                ),
                            ],
                            value="stress",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="mds-distances"),
                                    ],
                                ),
                            ],
                            value="distances",
                        ),
                    ],
                    value="plot",
                    id="mds-tabs",
                ),
            ),
            # Hidden storage
            dcc.Store(id="mds-results-store"),
            dcc.Download(id="mds-download-coords-data"),
            html.Div(id="mds-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("mds-dataset", "data"),
    Input("mds-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("mds-id-var", "data"), Output("mds-features", "data")],
    Input("mds-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], []

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        return all_cols, numeric_cols
    except Exception:
        return [], []


@callback(
    [
        Output("mds-plot", "figure"),
        Output("mds-summary", "children"),
        Output("mds-stress-plot", "figure"),
        Output("mds-distances", "children"),
        Output("mds-results-store", "data"),
        Output("mds-notification", "children"),
    ],
    Input("mds-run-btn", "n_clicks"),
    [
        State("mds-dataset", "value"),
        State("mds-id-var", "value"),
        State("mds-features", "value"),
        State("mds-input-type", "value"),
        State("mds-metric", "value"),
        State("mds-dimensions", "value"),
        State("mds-metric-mds", "checked"),
        State("mds-random-seed", "value"),
    ],
    prevent_initial_call=True,
)
def run_mds(
    n_clicks,
    dataset_name,
    id_var,
    features,
    input_type,
    metric,
    n_dims,
    is_metric,
    random_seed,
):
    """Run multi-dimensional scaling analysis."""
    if not all([dataset_name, features]):
        return (
            {},
            dmc.Text("Please select dataset and features.", c="red"),
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message="Missing required inputs",
                color="red",
                action="show",
            ),
        )

    try:
        # Get data
        df = app_manager.data_manager.get_dataset(dataset_name)

        # Get ID labels
        if id_var and id_var in df.columns:
            labels = df[id_var].astype(str).tolist()
        else:
            labels = [f"Obs{i + 1}" for i in range(len(df))]

        # Prepare data
        X = df[features].dropna()
        labels = [labels[i] for i in X.index]

        # Compute distances
        if input_type == "distance":
            # Assume data is already a distance matrix
            distance_matrix = X.values
        else:
            # Compute distance matrix from data
            distance_matrix = pairwise_distances(X, metric=metric)

        # Run MDS
        mds = SklearnMDS(
            n_components=n_dims,
            metric=is_metric,
            dissimilarity="precomputed" if input_type == "distance" else "euclidean",
            random_state=random_seed,
            n_init=10,
            max_iter=300,
        )

        if input_type == "distance":
            coords = mds.fit_transform(distance_matrix)
        else:
            # For data matrix, we need to compute distances first
            coords = mds.fit_transform(distance_matrix)

        # Get stress value
        stress = mds.stress_

        # Create DataFrame with coordinates
        coord_df = pd.DataFrame(coords, columns=[f"Dim{i + 1}" for i in range(n_dims)], index=labels)

        # Create MDS plot (2D)
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=coord_df["Dim1"],
                y=coord_df["Dim2"],
                mode="markers+text",
                marker=dict(size=12, color="blue"),
                text=coord_df.index,
                textposition="top center",
                hovertemplate="<b>%{text}</b><br>Dim1: %{x:.3f}<br>Dim2: %{y:.3f}<extra></extra>",
            )
        )

        # Add origin lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_layout(
            title="Multi-Dimensional Scaling Plot",
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            hovermode="closest",
        )

        # Summary statistics
        summary = dmc.Stack(
            [
                dmc.Text("MDS Summary", fw=600, size="lg"),
                dmc.Divider(),
                dmc.Text(f"Number of Objects: {len(labels)}"),
                dmc.Text(f"Number of Dimensions: {n_dims}"),
                dmc.Text(f"Distance Metric: {metric}"),
                dmc.Text(f"MDS Type: {'Metric' if is_metric else 'Non-metric'}"),
                dmc.Divider(),
                dmc.Text(f"Stress: {stress:.4f}", fw=600, c="blue"),
                dmc.Text("Stress Interpretation:", fw=600, size="sm", mt="md"),
                dmc.List(
                    [
                        dmc.ListItem("< 0.05: Excellent"),
                        dmc.ListItem("0.05 - 0.10: Good"),
                        dmc.ListItem("0.10 - 0.20: Fair"),
                        dmc.ListItem("> 0.20: Poor"),
                    ],
                    size="sm",
                ),
            ],
            gap="xs",
        )

        # Stress plot (Shepard diagram)
        # Compare original distances with distances in reduced space
        original_dists = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]

        # Compute distances in reduced space
        reduced_dists = pairwise_distances(coords)
        reduced_dists = reduced_dists[np.triu_indices_from(reduced_dists, k=1)]

        stress_fig = go.Figure()
        stress_fig.add_trace(
            go.Scatter(
                x=original_dists,
                y=reduced_dists,
                mode="markers",
                marker=dict(size=5, opacity=0.5),
                name="Distances",
            )
        )

        # Add perfect fit line
        min_dist = min(original_dists.min(), reduced_dists.min())
        max_dist = max(original_dists.max(), reduced_dists.max())
        stress_fig.add_trace(
            go.Scatter(
                x=[min_dist, max_dist],
                y=[min_dist, max_dist],
                mode="lines",
                line=dict(color="red", dash="dash"),
                name="Perfect Fit",
            )
        )

        stress_fig.update_layout(
            title=f"Shepard Diagram (Stress = {stress:.4f})",
            xaxis_title="Original Distances",
            yaxis_title="Distances in Reduced Space",
        )

        # Distance matrix heatmap
        dist_fig = px.imshow(
            distance_matrix,
            labels=dict(x="Object", y="Object", color="Distance"),
            x=labels,
            y=labels,
            title="Distance Matrix",
            color_continuous_scale="RdYlBu_r",
        )

        distances = dcc.Graph(figure=dist_fig, style={"height": "600px"})

        # Store results
        results = {
            "coordinates": coord_df.to_dict(),
            "stress": stress,
            "distance_matrix": distance_matrix.tolist(),
            "labels": labels,
        }

        return (
            fig,
            summary,
            stress_fig,
            distances,
            results,
            dmc.Notification(
                title="Success",
                message=f"MDS completed (Stress: {stress:.4f})",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            {},
            dmc.Text(f"Error: {str(e)}", c="red"),
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("mds-download-coords-data", "data"),
    Input("mds-download-coords", "n_clicks"),
    State("mds-results-store", "data"),
    prevent_initial_call=True,
)
def download_coordinates(n_clicks, results):
    """Download MDS coordinates as CSV."""
    if not results:
        return None

    try:
        coords_df = pd.DataFrame.from_dict(results["coordinates"])
        return dcc.send_data_frame(coords_df.to_csv, "mds_coordinates.csv")
    except Exception:
        return None
