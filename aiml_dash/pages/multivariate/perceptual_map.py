"""
Perceptual Map (Correspondence Analysis) Page
==============================================

Create perceptual maps using correspondence analysis to visualize brand positioning
and relationships between categorical variables.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the perceptual map page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Perceptual Map",
                "Create perceptual maps using correspondence analysis to visualize relationships between brands and attributes.",
                icon="carbon:chart-bubble-packed",
            ),
            dmc.Grid([
                # Left panel - configuration
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Data Selection", order=4),
                                        dmc.Select(
                                            id="prmap-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="prmap-row-var",
                                            label="Row Variable",
                                            description="Variable for rows (e.g., brands)",
                                            placeholder="Select row variable...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="prmap-col-var",
                                            label="Column Variable",
                                            description="Variable for columns (e.g., attributes)",
                                            placeholder="Select column variable...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="prmap-value-var",
                                            label="Value Variable (Optional)",
                                            description="Numeric values for cell counts/frequencies",
                                            placeholder="Select value variable...",
                                            data=[],
                                            clearable=True,
                                        ),
                                        dmc.Divider(
                                            label="Analysis Options",
                                            labelPosition="center",
                                        ),
                                        dmc.NumberInput(
                                            id="prmap-dimensions",
                                            label="Number of Dimensions",
                                            description="Dimensions to extract",
                                            value=2,
                                            min=2,
                                            max=5,
                                            step=1,
                                        ),
                                        dmc.Switch(
                                            id="prmap-normalize",
                                            label="Normalize data",
                                            description="Apply chi-square normalization",
                                            checked=True,
                                        ),
                                        dmc.Button(
                                            "Create Map",
                                            id="prmap-create-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
                                        ),
                                        dmc.Divider(),
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Export Options",
                                                    size="sm",
                                                    fw=500,
                                                ),
                                                dmc.Button(
                                                    "Download Plot (PNG)",
                                                    id="prmap-download-plot",
                                                    leftSection=DashIconify(
                                                        icon="carbon:download",
                                                        width=16,
                                                    ),
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm",
                                                ),
                                                dmc.Button(
                                                    "Export Coordinates (CSV)",
                                                    id="prmap-download-coords",
                                                    leftSection=DashIconify(
                                                        icon="carbon:download",
                                                        width=16,
                                                    ),
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm",
                                                ),
                                            ],
                                            gap="xs",
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
                # Right panel - results
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Perceptual Map",
                                        value="map",
                                        leftSection=DashIconify(icon="carbon:chart-bubble"),
                                    ),
                                    dmc.TabsTab(
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Coordinates",
                                        value="coordinates",
                                        leftSection=DashIconify(icon="carbon:table"),
                                    ),
                                    dmc.TabsTab(
                                        "Scree Plot",
                                        value="scree",
                                        leftSection=DashIconify(icon="carbon:chart-line"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(
                                                    id="prmap-plot",
                                                    style={"height": "600px"},
                                                ),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="map",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="prmap-summary"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="prmap-coordinates"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="coordinates",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="prmap-scree-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="scree",
                                ),
                            ],
                            value="map",
                            id="prmap-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="prmap-results-store"),
            dcc.Download(id="prmap-download-plot-data"),
            dcc.Download(id="prmap-download-coords-data"),
            html.Div(id="prmap-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("prmap-dataset", "data"),
    Input("prmap-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("prmap-row-var", "data"),
        Output("prmap-col-var", "data"),
        Output("prmap-value-var", "data"),
    ],
    Input("prmap-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        return all_cols, all_cols, numeric_cols
    except Exception:
        return [], [], []


@callback(
    [
        Output("prmap-plot", "figure"),
        Output("prmap-summary", "children"),
        Output("prmap-coordinates", "children"),
        Output("prmap-scree-plot", "figure"),
        Output("prmap-results-store", "data"),
        Output("prmap-notification", "children"),
    ],
    Input("prmap-create-btn", "n_clicks"),
    [
        State("prmap-dataset", "value"),
        State("prmap-row-var", "value"),
        State("prmap-col-var", "value"),
        State("prmap-value-var", "value"),
        State("prmap-dimensions", "value"),
        State("prmap-normalize", "checked"),
    ],
    prevent_initial_call=True,
)
def create_perceptual_map(n_clicks, dataset_name, row_var, col_var, value_var, n_dims, normalize):
    """Create perceptual map using correspondence analysis."""
    if not all([dataset_name, row_var, col_var]):
        return (
            {},
            dmc.Text("Please select dataset, row variable, and column variable.", c="red"),
            "",
            {},
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
        df = data_manager.get_dataset(dataset_name)

        # Create contingency table
        if value_var and value_var in df.columns:
            contingency = df.pivot_table(
                values=value_var,
                index=row_var,
                columns=col_var,
                aggfunc="sum",
                fill_value=0,
            )
        else:
            contingency = pd.crosstab(df[row_var], df[col_var])

        # Store original for later
        original_table = contingency.copy()

        # Correspondence analysis using SVD
        # Step 1: Calculate proportions
        N = contingency.sum().sum()
        P = contingency / N

        # Step 2: Row and column masses
        row_masses = P.sum(axis=1)
        col_masses = P.sum(axis=0)

        # Step 3: Expected frequencies under independence
        expected = np.outer(row_masses, col_masses)

        # Step 4: Standardized residuals (if normalize)
        if normalize:
            residuals = (P - expected) / np.sqrt(expected)
        else:
            residuals = P - expected

        # Step 5: SVD
        U, s, Vt = np.linalg.svd(residuals, full_matrices=False)

        # Calculate explained variance (inertia)
        total_inertia = np.sum(s**2)
        explained_variance = (s**2) / total_inertia * 100

        # Get coordinates for rows and columns (using first n_dims dimensions)
        row_coords = U[:, :n_dims] * s[:n_dims]
        col_coords = Vt[:n_dims, :].T * s[:n_dims]

        # Create row coordinates DataFrame
        row_coord_df = pd.DataFrame(
            row_coords,
            index=contingency.index,
            columns=[f"Dim{i + 1}" for i in range(n_dims)],
        )

        # Create column coordinates DataFrame
        col_coord_df = pd.DataFrame(
            col_coords,
            index=contingency.columns,
            columns=[f"Dim{i + 1}" for i in range(n_dims)],
        )

        # Create perceptual map (2D plot)
        fig = go.Figure()

        # Add row points (brands)
        fig.add_trace(
            go.Scatter(
                x=row_coord_df["Dim1"],
                y=row_coord_df["Dim2"],
                mode="markers+text",
                marker=dict(size=12, color="blue", symbol="circle"),
                text=row_coord_df.index,
                textposition="top center",
                name=row_var,
                hovertemplate="<b>%{text}</b><br>Dim1: %{x:.3f}<br>Dim2: %{y:.3f}<extra></extra>",
            )
        )

        # Add column points (attributes)
        fig.add_trace(
            go.Scatter(
                x=col_coord_df["Dim1"],
                y=col_coord_df["Dim2"],
                mode="markers+text",
                marker=dict(size=10, color="red", symbol="diamond"),
                text=col_coord_df.index,
                textposition="bottom center",
                name=col_var,
                hovertemplate="<b>%{text}</b><br>Dim1: %{x:.3f}<br>Dim2: %{y:.3f}<extra></extra>",
            )
        )

        # Add origin lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_layout(
            title=f"Perceptual Map: {row_var} vs {col_var}",
            xaxis_title=f"Dimension 1 ({explained_variance[0]:.1f}%)",
            yaxis_title=f"Dimension 2 ({explained_variance[1]:.1f}%)",
            hovermode="closest",
            showlegend=True,
        )

        # Summary statistics
        summary = dmc.Stack(
            [
                dmc.Text("Correspondence Analysis Summary", fw=600, size="lg"),
                dmc.Divider(),
                dmc.Text(f"Total Inertia: {total_inertia:.4f}"),
                dmc.Text(f"Number of Dimensions: {min(n_dims, len(s))}"),
                dmc.Divider(),
                dmc.Text("Explained Variance by Dimension:", fw=600),
                *[dmc.Text(f"Dimension {i + 1}: {var:.2f}%") for i, var in enumerate(explained_variance[:n_dims])],
                dmc.Text(
                    f"Cumulative: {explained_variance[:n_dims].sum():.2f}%",
                    c="blue",
                    fw=600,
                ),
                dmc.Divider(),
                dmc.Text(f"Number of {row_var} categories: {len(contingency.index)}"),
                dmc.Text(f"Number of {col_var} categories: {len(contingency.columns)}"),
                dmc.Text(f"Total observations: {int(N)}"),
            ],
            gap="xs",
        )

        # Coordinates table
        coords_tabs = dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.TabsTab("Row Coordinates", value="rows"),
                    dmc.TabsTab("Column Coordinates", value="cols"),
                ]),
                dmc.TabsPanel(
                    [
                        dag.AgGrid(
                            rowData=row_coord_df.reset_index().to_dict("records"),
                            columnDefs=[{"field": col, "flex": 1} for col in row_coord_df.reset_index().columns],
                            defaultColDef={
                                "sortable": True,
                                "filter": True,
                                "resizable": True,
                            },
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 20,
                            },
                            style={"height": "400px"},
                        ),
                    ],
                    value="rows",
                ),
                dmc.TabsPanel(
                    [
                        dag.AgGrid(
                            rowData=col_coord_df.reset_index().to_dict("records"),
                            columnDefs=[{"field": col, "flex": 1} for col in col_coord_df.reset_index().columns],
                            defaultColDef={
                                "sortable": True,
                                "filter": True,
                                "resizable": True,
                            },
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 20,
                            },
                            style={"height": "400px"},
                        ),
                    ],
                    value="cols",
                ),
            ],
            value="rows",
        )

        # Scree plot
        scree_fig = go.Figure()
        dims_to_plot = min(10, len(explained_variance))
        scree_fig.add_trace(
            go.Bar(
                x=[f"Dim{i + 1}" for i in range(dims_to_plot)],
                y=explained_variance[:dims_to_plot],
                name="Explained Variance",
            )
        )
        scree_fig.add_trace(
            go.Scatter(
                x=[f"Dim{i + 1}" for i in range(dims_to_plot)],
                y=np.cumsum(explained_variance[:dims_to_plot]),
                mode="lines+markers",
                name="Cumulative",
                yaxis="y2",
            )
        )
        scree_fig.update_layout(
            title="Scree Plot: Explained Variance by Dimension",
            xaxis_title="Dimension",
            yaxis_title="Explained Variance (%)",
            yaxis2=dict(title="Cumulative (%)", overlaying="y", side="right"),
            hovermode="x unified",
        )

        # Store results
        results = {
            "row_coords": row_coord_df.to_dict(),
            "col_coords": col_coord_df.to_dict(),
            "explained_variance": explained_variance.tolist(),
            "total_inertia": total_inertia,
        }

        return (
            fig,
            summary,
            coords_tabs,
            scree_fig,
            results,
            dmc.Notification(
                title="Success",
                message="Perceptual map created successfully",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            {},
            dmc.Text(f"Error: {str(e)}", c="red"),
            "",
            {},
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("prmap-download-coords-data", "data"),
    Input("prmap-download-coords", "n_clicks"),
    State("prmap-results-store", "data"),
    prevent_initial_call=True,
)
def download_coordinates(n_clicks, results):
    """Download coordinates as CSV."""
    if not results:
        return None

    try:
        row_coords = pd.DataFrame.from_dict(results["row_coords"])
        col_coords = pd.DataFrame.from_dict(results["col_coords"])

        # Combine into one DataFrame
        row_coords["Type"] = "Row"
        col_coords["Type"] = "Column"

        combined = pd.concat([row_coords, col_coords])

        return dcc.send_data_frame(combined.to_csv, "perceptual_map_coordinates.csv")
    except Exception:
        return None
