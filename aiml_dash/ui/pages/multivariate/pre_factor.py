"""
Pre-Factor Analysis Page
=========================

Explore data for factor analysis. Test assumptions and determine optimal number of factors.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import numpy as np
from scipy.stats import chi2
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


def calculate_bartlett_sphericity(X):
    """
    Calculate Bartlett's test of sphericity.
    Tests if the correlation matrix is an identity matrix.
    """
    n, p = X.shape
    corr = np.corrcoef(X.T)
    det_corr = np.linalg.det(corr)

    # Test statistic
    chi_square = -1 * (n - 1 - (2 * p + 5) / 6) * np.log(det_corr)
    df = p * (p - 1) / 2
    p_value = 1 - chi2.cdf(chi_square, df)

    return chi_square, p_value


def calculate_kmo(X):
    """
    Calculate Kaiser-Meyer-Olkin (KMO) measure of sampling adequacy.
    """
    corr = np.corrcoef(X.T)
    inv_corr = np.linalg.inv(corr)

    # Partial correlation matrix
    n_vars = corr.shape[0]
    partial_corr = np.zeros((n_vars, n_vars))
    for i in range(n_vars):
        for j in range(n_vars):
            if i != j:
                partial_corr[i, j] = -inv_corr[i, j] / np.sqrt(inv_corr[i, i] * inv_corr[j, j])

    # KMO calculation
    sum_sq_corr = np.sum(corr**2) - n_vars  # Exclude diagonal
    sum_sq_partial = np.sum(partial_corr**2)

    kmo_overall = sum_sq_corr / (sum_sq_corr + sum_sq_partial)

    return kmo_overall


def layout():
    """Create the pre-factor analysis page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Pre-Factor Analysis",
                "Explore data for factor analysis. Test assumptions including KMO and Bartlett's test, and determine the optimal number of factors.",
                icon="carbon:search",
            ),
            create_two_column_layout(
                # Left panel
                create_control_card(
                    [
                        dmc.Title("Analysis Settings", order=4),
                        dmc.Select(
                            id="prefactor-dataset",
                            label="Dataset",
                            placeholder="Select dataset...",
                            data=[],
                        ),
                        dmc.MultiSelect(
                            id="prefactor-variables",
                            label="Variables",
                            placeholder="Select variables...",
                            data=[],
                            searchable=True,
                        ),
                        dmc.NumberInput(
                            id="prefactor-max-factors",
                            label="Maximum Factors to Test",
                            value=10,
                            min=2,
                            max=20,
                            step=1,
                        ),
                        create_action_button(
                            button_id="prefactor-run-btn",
                            label="Run Analysis",
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
                                "Summary",
                                value="summary",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Scree Plot",
                                value="scree",
                                leftSection=DashIconify(icon="carbon:chart-line"),
                            ),
                            dmc.TabsTab(
                                "Correlation Matrix",
                                value="correlation",
                                leftSection=DashIconify(icon="carbon:grid"),
                            ),
                            dmc.TabsTab(
                                "KMO",
                                value="kmo",
                                leftSection=DashIconify(icon="carbon:table"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="prefactor-summary"),
                                    ],
                                ),
                            ],
                            value="summary",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        dcc.Graph(id="prefactor-scree-plot"),
                                    ],
                                ),
                            ],
                            value="scree",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        dcc.Graph(id="prefactor-correlation-plot"),
                                    ],
                                ),
                            ],
                            value="correlation",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="prefactor-kmo-table"),
                                    ],
                                ),
                            ],
                            value="kmo",
                        ),
                    ],
                    value="summary",
                    id="prefactor-tabs",
                ),
            ),
            html.Div(id="prefactor-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("prefactor-dataset", "data"),
    Input("prefactor-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    Output("prefactor-variables", "data"),
    Input("prefactor-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
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
        Output("prefactor-summary", "children"),
        Output("prefactor-scree-plot", "figure"),
        Output("prefactor-correlation-plot", "figure"),
        Output("prefactor-kmo-table", "children"),
        Output("prefactor-notification", "children"),
    ],
    Input("prefactor-run-btn", "n_clicks"),
    [
        State("prefactor-dataset", "value"),
        State("prefactor-variables", "value"),
        State("prefactor-max-factors", "value"),
    ],
    prevent_initial_call=True,
)
def run_prefactor_analysis(n_clicks, dataset_name, variables, max_factors):
    """Run pre-factor analysis."""
    if not all([dataset_name, variables]) or len(variables) < 2:
        return (
            dmc.Text("Please select dataset and at least 2 variables.", c="red"),
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
        df = app_manager.data_manager.get_dataset(dataset_name)
        X = df[variables].dropna()

        if len(X) < 3:
            raise ValueError("Need at least 3 observations")

        # Correlation matrix
        corr_matrix = X.corr()

        # KMO test
        kmo_all, kmo_model = calculate_kmo(X)

        # Bartlett's test
        chi_square_value, p_value = calculate_bartlett_sphericity(X)

        # Eigenvalues from correlation matrix
        eigenvalues = np.linalg.eigvals(corr_matrix)
        eigenvalues = np.sort(eigenvalues)[::-1]

        # Summary
        n_factors_kaiser = np.sum(eigenvalues > 1)  # Kaiser criterion

        summary = dmc.Stack(
            [
                dmc.Text("Pre-Factor Analysis Results", fw=600, size="xl"),
                dmc.Divider(),
                dmc.Text(f"Variables: {len(variables)}", size="lg"),
                dmc.Text(f"Observations: {len(X)}"),
                dmc.Divider(),
                dmc.Text("Bartlett's Test of Sphericity:", fw=600),
                dmc.Text(f"Chi-square: {chi_square_value:.2f}"),
                dmc.Text(f"P-value: {p_value:.4f}", c="green" if p_value < 0.05 else "red"),
                dmc.Text(
                    "✓ Significant - suitable for factor analysis"
                    if p_value < 0.05
                    else "✗ Not significant - may not be suitable",
                    c="green" if p_value < 0.05 else "red",
                ),
                dmc.Divider(),
                dmc.Text("Kaiser-Meyer-Olkin (KMO) Measure:", fw=600),
                dmc.Text(f"Overall KMO: {kmo_model:.3f}"),
                dmc.Text(
                    "Interpretation: "
                    + (
                        "Excellent"
                        if kmo_model >= 0.9
                        else "Good"
                        if kmo_model >= 0.8
                        else "Middling"
                        if kmo_model >= 0.7
                        else "Mediocre"
                        if kmo_model >= 0.6
                        else "Miserable"
                        if kmo_model >= 0.5
                        else "Unacceptable"
                    ),
                    c="green" if kmo_model >= 0.6 else "orange" if kmo_model >= 0.5 else "red",
                ),
                dmc.Divider(),
                dmc.Text(
                    f"Suggested factors (Kaiser criterion): {n_factors_kaiser}",
                    fw=600,
                    size="lg",
                ),
            ],
            gap="xs",
        )

        # Scree plot
        scree_fig = go.Figure()
        scree_fig.add_trace(
            go.Scatter(
                x=list(range(1, len(eigenvalues) + 1)),
                y=eigenvalues,
                mode="lines+markers",
                name="Eigenvalues",
                line=dict(width=2),
                marker=dict(size=8),
            )
        )
        scree_fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Kaiser criterion")
        scree_fig.update_layout(
            title="Scree Plot",
            xaxis_title="Factor Number",
            yaxis_title="Eigenvalue",
        )

        # Correlation heatmap
        corr_fig = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            title="Correlation Matrix",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
        )

        # KMO by variable table
        kmo_data = [{"Variable": var, "KMO": f"{kmo_all[i]:.3f}"} for i, var in enumerate(variables)]

        kmo_table = dmc.Stack(
            [
                dmc.Text(f"Overall KMO: {kmo_model:.3f}", fw=600, size="lg"),
                dag.AgGrid(
                    rowData=kmo_data,
                    columnDefs=[
                        {"field": "Variable", "flex": 1},
                        {"field": "KMO", "flex": 1},
                    ],
                    defaultColDef={"sortable": True},
                    style={"height": "400px"},
                ),
            ],
            gap="md",
        )

        return (
            summary,
            scree_fig,
            corr_fig,
            kmo_table,
            dmc.Notification(
                title="Success",
                message="Analysis complete",
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
