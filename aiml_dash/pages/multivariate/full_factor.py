"""
Full Factor Analysis Page
==========================

Perform factor analysis to identify underlying latent factors.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from sklearn.decomposition import FactorAnalysis
import plotly.graph_objects as go
import plotly.express as px

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the full factor analysis page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Factor Analysis",
                "Extract and rotate factors to identify underlying latent structure in your data.",
                icon="carbon:chart-3d",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Factor Settings", order=4),
                                        dmc.Select(
                                            id="factor-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="factor-variables",
                                            label="Variables",
                                            placeholder="Select variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.NumberInput(
                                            id="factor-n-factors",
                                            label="Number of Factors",
                                            value=2,
                                            min=1,
                                            max=10,
                                            step=1,
                                        ),
                                        dmc.Select(
                                            id="factor-rotation",
                                            label="Rotation Method",
                                            data=[
                                                {
                                                    "label": "Varimax",
                                                    "value": "varimax",
                                                },
                                                {"label": "None", "value": "none"},
                                            ],
                                            value="varimax",
                                        ),
                                        dmc.NumberInput(
                                            id="factor-cutoff",
                                            label="Loading Cutoff",
                                            description="Hide loadings below this value",
                                            value=0.5,
                                            min=0.0,
                                            max=1.0,
                                            step=0.1,
                                            decimalScale=2,
                                        ),
                                        dmc.Button(
                                            "Extract Factors",
                                            id="factor-run-btn",
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
                # Right panel
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Loadings",
                                        value="loadings",
                                        leftSection=DashIconify(icon="carbon:table"),
                                    ),
                                    dmc.TabsTab(
                                        "Communalities",
                                        value="communalities",
                                        leftSection=DashIconify(icon="carbon:chart-bar"),
                                    ),
                                    dmc.TabsTab(
                                        "Factor Plot",
                                        value="plot",
                                        leftSection=DashIconify(icon="carbon:chart-scatter"),
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
                                            [
                                                html.Div(id="factor-loadings"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="loadings",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="factor-communalities-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="communalities",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="factor-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="plot",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="factor-summary"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="summary",
                                ),
                            ],
                            value="loadings",
                            id="factor-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="factor-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("factor-dataset", "data"),
    Input("factor-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    Output("factor-variables", "data"),
    Input("factor-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
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
        Output("factor-loadings", "children"),
        Output("factor-communalities-plot", "figure"),
        Output("factor-plot", "figure"),
        Output("factor-summary", "children"),
        Output("factor-notification", "children"),
    ],
    Input("factor-run-btn", "n_clicks"),
    [
        State("factor-dataset", "value"),
        State("factor-variables", "value"),
        State("factor-n-factors", "value"),
        State("factor-rotation", "value"),
        State("factor-cutoff", "value"),
    ],
    prevent_initial_call=True,
)
def run_factor_analysis(n_clicks, dataset_name, variables, n_factors, rotation, cutoff):
    """Run factor analysis."""
    if not all([dataset_name, variables]) or len(variables) < n_factors:
        return (
            dmc.Text("Please select dataset and enough variables.", c="red"),
            {},
            {},
            "",
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
        X = df[variables].dropna()

        # Standardize
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Factor analysis
        fa = FactorAnalysis(n_components=n_factors, rotation=rotation if rotation != "none" else None)
        fa.fit(X_scaled)

        # Get loadings
        loadings = fa.components_.T

        # Communalities
        communalities = np.sum(loadings**2, axis=1)

        # Loadings table
        loadings_df = pd.DataFrame(
            loadings,
            index=variables,
            columns=[f"Factor {i + 1}" for i in range(n_factors)],
        )

        # Apply cutoff for display
        loadings_display = loadings_df.copy()
        for col in loadings_display.columns:
            loadings_display[col] = loadings_display[col].apply(lambda x: f"{x:.3f}" if abs(x) >= cutoff else "")

        loadings_display["Communality"] = [f"{c:.3f}" for c in communalities]
        loadings_display.insert(0, "Variable", loadings_display.index)

        loadings_table = dag.AgGrid(
            rowData=loadings_display.reset_index(drop=True).to_dict("records"),
            columnDefs=[{"field": col, "flex": 1} for col in loadings_display.columns],
            defaultColDef={"sortable": True, "filter": True},
            style={"height": "500px"},
        )

        # Communalities plot
        comm_df = pd.DataFrame({
            "Variable": variables,
            "Communality": communalities,
        }).sort_values("Communality")

        comm_fig = px.bar(
            comm_df,
            x="Communality",
            y="Variable",
            orientation="h",
            title="Communalities",
        )
        comm_fig.add_vline(x=0.5, line_dash="dash", line_color="red")

        # Factor plot (first 2 factors)
        if n_factors >= 2:
            factor_plot_fig = go.Figure()

            # Add variable vectors
            for i, var in enumerate(variables):
                factor_plot_fig.add_trace(
                    go.Scatter(
                        x=[0, loadings[i, 0]],
                        y=[0, loadings[i, 1]],
                        mode="lines+text",
                        name=var,
                        text=["", var],
                        textposition="top center",
                        line=dict(width=2),
                    )
                )

            # Add circle
            theta = np.linspace(0, 2 * np.pi, 100)
            factor_plot_fig.add_trace(
                go.Scatter(
                    x=np.cos(theta),
                    y=np.sin(theta),
                    mode="lines",
                    line=dict(color="gray", dash="dash"),
                    showlegend=False,
                )
            )

            factor_plot_fig.update_layout(
                title="Factor Loadings Plot (First 2 Factors)",
                xaxis_title="Factor 1",
                yaxis_title="Factor 2",
                showlegend=False,
            )
        else:
            factor_plot_fig = {}

        # Summary
        variance_explained = np.var(fa.transform(X_scaled), axis=0)
        total_var = np.sum(variance_explained)
        prop_var = variance_explained / np.sum(np.var(X_scaled, axis=0))

        summary_data = []
        for i in range(n_factors):
            summary_data.append({
                "Factor": f"Factor {i + 1}",
                "Eigenvalue": f"{variance_explained[i]:.3f}",
                "Proportion": f"{prop_var[i]:.3f}",
                "Cumulative": f"{np.sum(prop_var[: i + 1]):.3f}",
            })

        summary = dmc.Stack(
            [
                dmc.Text("Factor Analysis Summary", fw=600, size="xl"),
                dmc.Divider(),
                dmc.Text(f"Number of Factors: {n_factors}"),
                dmc.Text(f"Rotation: {rotation.title()}"),
                dmc.Text(f"Variables: {len(variables)}"),
                dmc.Divider(),
                dag.AgGrid(
                    rowData=summary_data,
                    columnDefs=[{"field": col} for col in summary_data[0].keys()],
                    defaultColDef={"sortable": False},
                    style={"height": "250px"},
                ),
            ],
            gap="md",
        )

        return (
            loadings_table,
            comm_fig,
            factor_plot_fig,
            summary,
            dmc.Notification(
                title="Success",
                message="Factor analysis complete",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {str(e)}", c="red"),
            {},
            {},
            "",
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )
