"""
Goodness of Fit Test Page
Chi-square test to compare observed frequencies with expected frequencies.
"""

from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from aiml_dash.managers.app_manager import app_manager
from components.common import (
    create_action_button,
    create_control_card,
    create_dataset_selector,
    create_numeric_input,
    create_page_header,
    create_results_card,
    create_segmented_control,
    create_two_column_layout,
)


def layout():
    """Create layout for goodness of fit test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            create_page_header(
                "Goodness of Fit Test",
                "Test whether observed frequencies match an expected distribution",
                icon="mdi:chart-bell-curve",
            ),
            dmc.Divider(),
            # Main Content
            create_two_column_layout(
                # Left Column - Controls
                dmc.Paper(
                    p="md",
                    withBorder=True,
                    children=[
                        dmc.Stack(
                            gap="md",
                            children=[
                                dmc.Text("Data Selection", fw=500, size="lg"),
                                dmc.Select(
                                    id="goodness-dataset",
                                    label="Select Dataset",
                                    placeholder="Choose dataset...",
                                    data=[],
                                    searchable=True,
                                    clearable=False,
                                ),
                                dmc.Select(
                                    id="goodness-variable",
                                    label="Variable",
                                    placeholder="Choose categorical variable...",
                                    data=[],
                                    searchable=True,
                                ),
                                dmc.Divider(),
                                dmc.Text(
                                    "Expected Distribution",
                                    fw=500,
                                    size="lg",
                                ),
                                dmc.Stack(
                                    gap=5,
                                    children=[
                                        dmc.Text(
                                            "Distribution Type",
                                            size="sm",
                                            fw=500,
                                        ),
                                        dmc.SegmentedControl(
                                            id="goodness-dist-type",
                                            data=[
                                                {
                                                    "label": "Uniform",
                                                    "value": "uniform",
                                                },
                                                {
                                                    "label": "Custom",
                                                    "value": "custom",
                                                },
                                            ],
                                            value="uniform",
                                            fullWidth=True,
                                        ),
                                    ],
                                ),
                                dmc.Textarea(
                                    id="goodness-expected-input",
                                    label="Custom Expected Proportions",
                                    description="Enter comma-separated proportions (e.g., 0.25,0.25,0.5)",
                                    placeholder="0.25,0.25,0.5",
                                    minRows=2,
                                    style={"display": "none"},
                                ),
                                dmc.NumberInput(
                                    id="goodness-confidence",
                                    label="Confidence Level",
                                    value=0.95,
                                    min=0.5,
                                    max=0.999,
                                    step=0.01,
                                    decimalScale=3,
                                ),
                                create_action_button(
                                    button_id="goodness-run",
                                    label="Run Test",
                                    icon="mdi:play",
                                ),
                            ],
                        ),
                    ],
                ),
                # Right Column - Results
                dmc.Stack(
                    gap="md",
                    children=[
                        dmc.Paper(
                            id="goodness-results",
                            p="md",
                            withBorder=True,
                            children=[
                                dmc.Text(
                                    "Select variable and click 'Run Test' to see results",
                                    c="dimmed",
                                    ta="center",
                                    py="xl",
                                ),
                            ],
                        ),
                        dmc.Paper(
                            id="goodness-table-container",
                            p="md",
                            withBorder=True,
                            style={"display": "none"},
                            children=[
                                dmc.Text(
                                    "Observed vs Expected Frequencies",
                                    fw=500,
                                    mb="sm",
                                ),
                                html.Div(id="goodness-table"),
                            ],
                        ),
                        dmc.Paper(
                            id="goodness-plot-container",
                            p="md",
                            withBorder=True,
                            style={"display": "none"},
                            children=[
                                dcc.Graph(
                                    id="goodness-plot",
                                    config={"displayModeBar": False},
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================


@callback(
    Output("goodness-dataset", "data"),
    Input("goodness-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]


@callback(
    [Output("goodness-variable", "data"), Output("goodness-variable", "value")],
    Input("goodness-dataset", "value"),
)
def update_variables(dataset):
    """Populate variable dropdown."""
    if not dataset:
        return [], None

    df = app_manager.data_manager.get_dataset(dataset)
    columns = df.columns.tolist()

    return [{"label": col, "value": col} for col in columns], None


@callback(
    Output("goodness-expected-input", "style"),
    Input("goodness-dist-type", "value"),
)
def toggle_custom_input(dist_type):
    """Show/hide custom expected input based on distribution type."""
    if dist_type == "custom":
        return {"display": "block"}
    return {"display": "none"}


@callback(
    [
        Output("goodness-results", "children"),
        Output("goodness-table-container", "style"),
        Output("goodness-table", "children"),
        Output("goodness-plot-container", "style"),
        Output("goodness-plot", "figure"),
    ],
    Input("goodness-run", "n_clicks"),
    [
        State("goodness-dataset", "value"),
        State("goodness-variable", "value"),
        State("goodness-dist-type", "value"),
        State("goodness-expected-input", "value"),
        State("goodness-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_goodness_test(n_clicks, dataset, variable, dist_type, custom_expected, confidence):
    """Run chi-square goodness of fit test."""
    if not all([dataset, variable]):
        return (
            [
                dmc.Alert(
                    "Please select dataset and variable",
                    title="Missing inputs",
                    color="yellow",
                    icon=DashIconify(icon="mdi:alert"),
                )
            ],
            {"display": "none"},
            None,
            {"display": "none"},
            {},
        )

    try:
        df = app_manager.data_manager.get_dataset(dataset)

        if variable not in df.columns:
            return (
                [
                    dmc.Alert(
                        "Variable not found in dataset",
                        title="Error",
                        color="red",
                        icon=DashIconify(icon="mdi:alert-circle"),
                    )
                ],
                {"display": "none"},
                None,
                {"display": "none"},
                {},
            )

        # Get observed frequencies
        observed_counts = df[variable].value_counts().sort_index()
        categories = observed_counts.index.tolist()
        observed = observed_counts.values
        n_categories = len(categories)
        total = observed.sum()

        # Calculate expected frequencies
        if dist_type == "uniform":
            expected = np.ones(n_categories) * (total / n_categories)
        else:  # custom
            if not custom_expected:
                return (
                    [
                        dmc.Alert(
                            "Please enter custom expected proportions",
                            title="Missing input",
                            color="yellow",
                            icon=DashIconify(icon="mdi:alert"),
                        )
                    ],
                    {"display": "none"},
                    None,
                    {"display": "none"},
                    {},
                )

            try:
                proportions = [float(x.strip()) for x in custom_expected.split(",")]
                if len(proportions) != n_categories:
                    return (
                        [
                            dmc.Alert(
                                f"Number of proportions ({len(proportions)}) doesn't match number of categories ({n_categories})",
                                title="Error",
                                color="red",
                                icon=DashIconify(icon="mdi:alert-circle"),
                            )
                        ],
                        {"display": "none"},
                        None,
                        {"display": "none"},
                        {},
                    )

                if not np.isclose(sum(proportions), 1.0):
                    return (
                        [
                            dmc.Alert(
                                f"Proportions must sum to 1.0 (currently {sum(proportions):.4f})",
                                title="Error",
                                color="red",
                                icon=DashIconify(icon="mdi:alert-circle"),
                            )
                        ],
                        {"display": "none"},
                        None,
                        {"display": "none"},
                        {},
                    )

                expected = np.array(proportions) * total
            except ValueError:
                return (
                    [
                        dmc.Alert(
                            "Invalid format for expected proportions",
                            title="Error",
                            color="red",
                            icon=DashIconify(icon="mdi:alert-circle"),
                        )
                    ],
                    {"display": "none"},
                    None,
                    {"display": "none"},
                    {},
                )

        # Run chi-square goodness of fit test
        chi2, p_value = stats.chisquare(observed, expected)
        dof = n_categories - 1

        # Calculate residuals
        residuals = observed - expected
        std_residuals = residuals / np.sqrt(expected)

        is_significant = p_value < (1 - confidence)

        # Create results display
        results_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            dmc.Text("Chi-Square Goodness of Fit Test", fw=600, size="lg"),
                            dmc.Badge(
                                "Significant" if is_significant else "Not Significant",
                                color="green" if is_significant else "gray",
                                variant="filled",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 3},
                        spacing="md",
                        children=[
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("χ² Statistic", size="xs", c="dimmed"),
                                    dmc.Text(f"{chi2:.4f}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("df", size="xs", c="dimmed"),
                                    dmc.Text(f"{dof}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("P-value", size="xs", c="dimmed"),
                                    dmc.Text(
                                        f"{p_value:.4f}",
                                        fw=600,
                                        size="xl",
                                        c="green" if is_significant else "gray",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Interpretation",
                        color="blue",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"The observed distribution {'does' if is_significant else 'does not'} "
                            f"significantly differ from the expected {'uniform' if dist_type == 'uniform' else 'custom'} "
                            f"distribution (χ² = {chi2:.2f}, df = {dof}, p = {p_value:.4f}).",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create frequency table
        freq_df = pd.DataFrame({
            "Category": [str(cat) for cat in categories],
            "Observed": observed,
            "Expected": expected.round(2),
            "Residual": residuals.round(2),
            "Std. Residual": std_residuals.round(2),
        })

        table_component = dag.AgGrid(
            rowData=freq_df.to_dict("records"),
            columnDefs=[
                {"field": "Category", "headerName": variable},
                {"field": "Observed", "headerName": "Observed"},
                {"field": "Expected", "headerName": "Expected"},
                {"field": "Residual", "headerName": "Residual"},
                {"field": "Std. Residual", "headerName": "Std. Residual"},
            ],
            defaultColDef={"resizable": True, "sortable": True, "filter": False},
            style={"height": "300px"},
        )

        # Create grouped bar chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Observed",
                x=[str(cat) for cat in categories],
                y=observed,
                marker=dict(color="#1c7ed6"),
                text=observed,
                textposition="auto",
            )
        )

        fig.add_trace(
            go.Bar(
                name="Expected",
                x=[str(cat) for cat in categories],
                y=expected,
                marker=dict(color="#868e96"),
                text=expected.round(2),
                textposition="auto",
            )
        )

        fig.update_layout(
            title=f"Observed vs Expected Frequencies: {variable}",
            xaxis_title=variable,
            yaxis_title="Frequency",
            barmode="group",
            template="plotly_white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        return (
            results_content,
            {"display": "block"},
            table_component,
            {"display": "block"},
            fig,
        )

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {str(e)}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            None,
            {"display": "none"},
            {},
        )
