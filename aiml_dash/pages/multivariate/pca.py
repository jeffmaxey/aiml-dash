"""
Principal Component Analysis (PCA) Page
=========================================

Reduce dimensionality and explore structure in multivariate data using PCA.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from aiml_dash.components.common import create_page_header
from aiml_dash.utils.data_manager import data_manager


def layout():
    """Create the PCA page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Principal Component Analysis",
                "Reduce dimensionality and uncover latent structure. Visualize data variance through scree plots, biplots and component loadings.",
                icon="carbon:chart-scatter",
            ),
            dmc.Grid([
                # Left panel – controls
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("PCA Settings", order=4),
                                        dmc.Select(
                                            id="pca-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="pca-variables",
                                            label="Numeric Variables",
                                            placeholder="Select variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.NumberInput(
                                            id="pca-n-components",
                                            label="Number of Components",
                                            value=2,
                                            min=2,
                                            max=10,
                                            step=1,
                                        ),
                                        dmc.Switch(
                                            id="pca-standardize",
                                            label="Standardize Variables",
                                            checked=True,
                                        ),
                                        dmc.Button(
                                            "Run PCA",
                                            id="pca-run-btn",
                                            leftSection=DashIconify(
                                                icon="carbon:play", width=20
                                            ),
                                            fullWidth=True,
                                            size="lg",
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
                # Right panel – results
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Scree Plot",
                                        value="scree",
                                        leftSection=DashIconify(
                                            icon="carbon:chart-bar", width=16
                                        ),
                                    ),
                                    dmc.TabsTab(
                                        "Biplot",
                                        value="biplot",
                                        leftSection=DashIconify(
                                            icon="carbon:chart-scatter", width=16
                                        ),
                                    ),
                                    dmc.TabsTab(
                                        "Loadings",
                                        value="loadings",
                                        leftSection=DashIconify(
                                            icon="carbon:data-table", width=16
                                        ),
                                    ),
                                    dmc.TabsTab(
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(
                                            icon="carbon:report", width=16
                                        ),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    dmc.Card(
                                        [dcc.Graph(id="pca-scree-plot")],
                                        withBorder=True,
                                        radius="md",
                                        p="md",
                                        mt="md",
                                    ),
                                    value="scree",
                                ),
                                dmc.TabsPanel(
                                    dmc.Card(
                                        [dcc.Graph(id="pca-biplot")],
                                        withBorder=True,
                                        radius="md",
                                        p="md",
                                        mt="md",
                                    ),
                                    value="biplot",
                                ),
                                dmc.TabsPanel(
                                    dmc.Card(
                                        [
                                            dag.AgGrid(
                                                id="pca-loadings-grid",
                                                rowData=[],
                                                columnDefs=[],
                                                defaultColDef={
                                                    "sortable": True,
                                                    "filter": True,
                                                    "resizable": True,
                                                },
                                                style={"height": "400px"},
                                            )
                                        ],
                                        withBorder=True,
                                        radius="md",
                                        p="md",
                                        mt="md",
                                    ),
                                    value="loadings",
                                ),
                                dmc.TabsPanel(
                                    dmc.Card(
                                        [html.Div(id="pca-summary")],
                                        withBorder=True,
                                        radius="md",
                                        p="md",
                                        mt="md",
                                    ),
                                    value="summary",
                                ),
                            ],
                            value="scree",
                            id="pca-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="pca-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------


@callback(Output("pca-dataset", "data"), Input("pca-dataset", "id"))
def update_datasets(_):
    """Populate dataset dropdown with available datasets.

    Returns:
        List of dataset options for the dropdown.
    """
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(Output("pca-variables", "data"), Input("pca-dataset", "value"))
def update_variables(dataset_name):
    """Update numeric variable options based on the selected dataset.

    Args:
        dataset_name: Name of the selected dataset.

    Returns:
        List of numeric column options.
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
    [
        Output("pca-scree-plot", "figure"),
        Output("pca-biplot", "figure"),
        Output("pca-loadings-grid", "rowData"),
        Output("pca-loadings-grid", "columnDefs"),
        Output("pca-summary", "children"),
        Output("pca-notification", "children"),
    ],
    Input("pca-run-btn", "n_clicks"),
    [
        State("pca-dataset", "value"),
        State("pca-variables", "value"),
        State("pca-n-components", "value"),
        State("pca-standardize", "checked"),
    ],
    prevent_initial_call=True,
)
def run_pca(n_clicks, dataset_name, variables, n_components, standardize):
    """Run Principal Component Analysis and return all result panels.

    Args:
        n_clicks: Button click counter (trigger only).
        dataset_name: Name of the dataset to analyse.
        variables: List of numeric variable names to include.
        n_components: Number of principal components to extract.
        standardize: Whether to standardize variables before PCA.

    Returns:
        Tuple of (scree_figure, biplot_figure, loadings_row_data,
                  loadings_col_defs, summary_children, notification).
    """
    if not all([dataset_name, variables]) or len(variables) < 2:
        return (
            {},
            {},
            [],
            [],
            dmc.Text("Please select a dataset and at least 2 variables.", c="red"),
            dmc.Notification(
                title="Missing inputs",
                message="Select a dataset and at least 2 numeric variables.",
                color="red",
                action="show",
            ),
        )

    try:
        df = data_manager.get_dataset(dataset_name)
        X = df[variables].dropna()

        n_obs, n_vars = X.shape
        # Clamp n_components to what is feasible
        n_components = int(min(n_components, n_vars, n_obs))
        if n_components < 2:
            raise ValueError(
                f"Need at least 2 components but only {n_components} feasible "
                f"given {n_obs} observations and {n_vars} variables."
            )

        # Optional standardization
        if standardize:
            scaler = StandardScaler()
            X_arr = scaler.fit_transform(X)
        else:
            X_arr = X.values

        pca = PCA(n_components=n_components)
        scores = pca.fit_transform(X_arr)
        loadings = pca.components_  # shape (n_components, n_vars)
        explained = pca.explained_variance_ratio_ * 100  # percent
        cumulative = np.cumsum(explained)

        pc_labels = [f"PC{i + 1}" for i in range(n_components)]

        # ------------------------------------------------------------------ #
        # Scree plot – bar for individual + line for cumulative variance
        # ------------------------------------------------------------------ #
        scree_fig = go.Figure()
        scree_fig.add_trace(
            go.Bar(
                x=pc_labels,
                y=explained,
                name="Explained Variance %",
                marker_color="steelblue",
            )
        )
        scree_fig.add_trace(
            go.Scatter(
                x=pc_labels,
                y=cumulative,
                name="Cumulative %",
                mode="lines+markers",
                line={"color": "crimson", "dash": "dot"},
                yaxis="y2",
            )
        )
        scree_fig.update_layout(
            title="Scree Plot",
            xaxis_title="Principal Component",
            yaxis={"title": "Explained Variance (%)"},
            yaxis2={
                "title": "Cumulative Explained Variance (%)",
                "overlaying": "y",
                "side": "right",
                "range": [0, 105],
            },
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
            template="plotly_white",
        )

        # ------------------------------------------------------------------ #
        # Biplot – scores + loading vectors
        # ------------------------------------------------------------------ #
        biplot_fig = go.Figure()

        # Scores scatter (coloured by row index)
        biplot_fig.add_trace(
            go.Scatter(
                x=scores[:, 0],
                y=scores[:, 1],
                mode="markers",
                marker={
                    "color": list(range(n_obs)),
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": "Row"},
                    "opacity": 0.7,
                    "size": 6,
                },
                name="Observations",
                showlegend=True,
            )
        )

        # Loading vectors – scale to fit on the same axes as scores
        scale = max(float(np.abs(scores[:, :2]).max()), 1e-9)
        loading_scale = scale * 0.8

        for i, var in enumerate(variables):
            lx = float(loadings[0, i]) * loading_scale
            ly = float(loadings[1, i]) * loading_scale
            biplot_fig.add_trace(
                go.Scatter(
                    x=[0, lx],
                    y=[0, ly],
                    mode="lines+text",
                    line={"color": "firebrick", "width": 2},
                    text=["", var],
                    textposition="top center",
                    showlegend=False,
                )
            )

        biplot_fig.update_layout(
            title="Biplot (PC1 vs PC2)",
            xaxis_title=f"PC1 ({explained[0]:.1f}%)",
            yaxis_title=f"PC2 ({explained[1]:.1f}%)",
            template="plotly_white",
        )

        # ------------------------------------------------------------------ #
        # Loadings table
        # ------------------------------------------------------------------ #
        loadings_df = pd.DataFrame(
            loadings.T.round(3),
            columns=pc_labels,
        )
        loadings_df.insert(0, "Variable", variables)

        # Append explained variance row
        ev_row = {"Variable": "Explained Variance %"}
        for j, pc in enumerate(pc_labels):
            ev_row[pc] = round(float(explained[j]), 3)
        row_data = loadings_df.to_dict("records") + [ev_row]
        col_defs = [{"field": "Variable"}] + [{"field": pc} for pc in pc_labels]

        # ------------------------------------------------------------------ #
        # Summary panel
        # ------------------------------------------------------------------ #
        summary = dmc.Stack(
            [
                dmc.Text("PCA Summary", fw=700, size="lg"),
                dmc.Divider(),
                dmc.Text(f"Number of Components: {n_components}", fw=500),
                dmc.Text(f"Number of Variables: {n_vars}"),
                dmc.Text(f"Number of Observations: {n_obs}"),
                dmc.Text(
                    f"Total Explained Variance: {cumulative[-1]:.2f}%",
                    fw=500,
                ),
                dmc.Divider(),
                dmc.Text("Per-Component Explained Variance:", fw=500),
                *[
                    dmc.Text(f"  {pc}: {ev:.2f}%")
                    for pc, ev in zip(pc_labels, explained)
                ],
            ],
            gap="xs",
        )

        notification = dmc.Notification(
            title="PCA Complete",
            message=(
                f"Extracted {n_components} components explaining "
                f"{cumulative[-1]:.1f}% of variance."
            ),
            color="green",
            action="show",
            autoClose=3000,
        )

        return scree_fig, biplot_fig, row_data, col_defs, summary, notification

    except Exception as exc:
        error_msg = str(exc)
        return (
            {},
            {},
            [],
            [],
            dmc.Text(f"Error: {error_msg}", c="red"),
            dmc.Notification(
                title="Error",
                message=error_msg,
                color="red",
                action="show",
            ),
        )
