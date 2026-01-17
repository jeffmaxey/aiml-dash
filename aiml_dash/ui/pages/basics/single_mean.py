"""
Single Mean Test Page
=====================

One-sample t-test to compare sample mean against a population value.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import numpy as np
from scipy import stats
import plotly.graph_objects as go

from components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_dataset_selector,
    create_numeric_input,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the single mean test page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Single Mean",
                "One-sample t-test to compare a sample mean against a hypothesized population value.",
                icon="carbon:chart-average",
            ),
            create_two_column_layout(
                # Left panel - Controls
                create_control_card(
                    [
                        create_dataset_selector(selector_id="smean-dataset"),
                        dmc.Select(
                            id="smean-variable",
                            label="Variable",
                            placeholder="Select variable...",
                            data=[],
                        ),
                        create_numeric_input(
                            input_id="smean-comparison",
                            label="Comparison Value",
                            description="Hypothesized population mean",
                            value=0,
                            step=0.1,
                        ),
                        dmc.Select(
                            id="smean-alternative",
                            label="Alternative Hypothesis",
                            value="two-sided",
                            data=[
                                {
                                    "label": "Two-sided (≠)",
                                    "value": "two-sided",
                                },
                                {
                                    "label": "Greater than (>)",
                                    "value": "greater",
                                },
                                {
                                    "label": "Less than (<)",
                                    "value": "less",
                                },
                            ],
                        ),
                        create_numeric_input(
                            input_id="smean-confidence",
                            label="Confidence Level",
                            value=0.95,
                            min_val=0.5,
                            max_val=0.99,
                            step=0.01,
                        ),
                        create_action_button(
                            button_id="smean-run-btn",
                            label="Run Test",
                            size="lg",
                        ),
                        dmc.Divider(),
                        create_action_button(
                            button_id="smean-export-btn",
                            label="Export Results (CSV)",
                            icon="carbon:download",
                            variant="light",
                        ),
                    ],
                    title="Test Settings",
                ),
                # Right panel - Results
                dmc.Tabs(
                    [
                        dmc.TabsList([
                            dmc.TabsTab(
                                "Summary",
                                value="summary",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Plot",
                                value="plot",
                                leftSection=DashIconify(icon="carbon:chart-histogram"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(html.Div(id="smean-summary")),
                            ],
                            value="summary",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(dcc.Graph(id="smean-plot")),
                            ],
                            value="plot",
                        ),
                    ],
                    value="summary",
                    id="smean-tabs",
                ),
            ),
            # Hidden components
            dcc.Store(id="smean-results-store"),
            dcc.Download(id="smean-download"),
            html.Div(id="smean-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("smean-dataset", "data"),
    Input("smean-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    Output("smean-variable", "data"),
    Input("smean-dataset", "value"),
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
        Output("smean-summary", "children"),
        Output("smean-plot", "figure"),
        Output("smean-results-store", "data"),
        Output("smean-notification", "children"),
    ],
    Input("smean-run-btn", "n_clicks"),
    [
        State("smean-dataset", "value"),
        State("smean-variable", "value"),
        State("smean-comparison", "value"),
        State("smean-alternative", "value"),
        State("smean-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_single_mean_test(n_clicks, dataset_name, variable, comparison, alternative, confidence):
    """Run single mean t-test."""
    if not all([dataset_name, variable]):
        return (
            dmc.Text("Please select dataset and variable.", c="red"),
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
        df = app_manager.data_manager.get_dataset(dataset_name)
        data = df[variable].dropna()

        if len(data) < 2:
            raise ValueError("Need at least 2 observations")

        # Run t-test
        result = stats.ttest_1samp(data, comparison, alternative=alternative)

        # Calculate statistics
        n = len(data)
        mean = data.mean()
        std = data.std(ddof=1)
        se = std / np.sqrt(n)
        diff = mean - comparison

        # Confidence interval
        alpha = 1 - confidence
        if alternative == "two-sided":
            ci = stats.t.interval(confidence, n - 1, loc=mean, scale=se)
            ci_lower, ci_upper = ci
        elif alternative == "greater":
            ci_lower = stats.t.ppf(alpha, n - 1, loc=mean, scale=se)
            ci_upper = np.inf
        else:  # less
            ci_lower = -np.inf
            ci_upper = stats.t.ppf(1 - alpha, n - 1, loc=mean, scale=se)

        # Format p-value
        if result.pvalue < 0.001:
            p_value_str = "< .001"
            sig_stars = "***"
        elif result.pvalue < 0.01:
            p_value_str = f"{result.pvalue:.3f}"
            sig_stars = "**"
        elif result.pvalue < 0.05:
            p_value_str = f"{result.pvalue:.3f}"
            sig_stars = "*"
        else:
            p_value_str = f"{result.pvalue:.3f}"
            sig_stars = ""

        # Determine conclusion
        reject_null = result.pvalue < (1 - confidence)

        # Summary output
        summary = dmc.Stack(
            [
                dmc.Text("Hypothesis", fw=600, size="lg"),
                dmc.Text(f"H₀: μ = {comparison}"),
                dmc.Text(
                    f"Hₐ: μ {alternative.replace('two-sided', '≠').replace('greater', '>').replace('less', '<')} {comparison}"
                ),
                dmc.Divider(),
                dmc.Text("Descriptive Statistics", fw=600, size="lg"),
                dag.AgGrid(
                    rowData=[
                        {
                            "n": n,
                            "mean": f"{mean:.3f}",
                            "sd": f"{std:.3f}",
                            "se": f"{se:.3f}",
                            "min": f"{data.min():.3f}",
                            "max": f"{data.max():.3f}",
                        }
                    ],
                    columnDefs=[
                        {"field": "n", "headerName": "n"},
                        {"field": "mean", "headerName": "Mean"},
                        {"field": "sd", "headerName": "SD"},
                        {"field": "se", "headerName": "SE"},
                        {"field": "min", "headerName": "Min"},
                        {"field": "max", "headerName": "Max"},
                    ],
                    defaultColDef={"sortable": False, "flex": 1},
                    style={"height": "100px"},
                ),
                dmc.Divider(),
                dmc.Text("Test Results", fw=600, size="lg"),
                dag.AgGrid(
                    rowData=[
                        {
                            "diff": f"{diff:.3f}",
                            "se": f"{se:.3f}",
                            "t-value": f"{result.statistic:.3f}",
                            "p-value": f"{p_value_str} {sig_stars}",
                            "df": n - 1,
                            "CI": f"[{ci_lower:.3f}, {ci_upper if ci_upper != np.inf else '∞'}]",
                        }
                    ],
                    columnDefs=[
                        {"field": "diff", "headerName": "Difference"},
                        {"field": "se", "headerName": "SE"},
                        {"field": "t-value", "headerName": "t-value"},
                        {"field": "p-value", "headerName": "p-value"},
                        {"field": "df", "headerName": "df"},
                        {"field": "CI", "headerName": f"{int(confidence * 100)}% CI"},
                    ],
                    defaultColDef={"sortable": False, "flex": 1},
                    style={"height": "100px"},
                ),
                dmc.Divider(),
                dmc.Text("Conclusion", fw=600, size="lg"),
                dmc.Text(
                    f"{'Reject' if reject_null else 'Fail to reject'} H₀ at α = {1 - confidence:.2f} level.",
                    c="green" if reject_null else "orange",
                    fw=600,
                ),
                dmc.Text(
                    f"The sample mean ({mean:.3f}) is {'significantly' if reject_null else 'not significantly'} "
                    f"different from {comparison}.",
                ),
            ],
            gap="md",
        )

        # Plot - histogram with mean and comparison value
        fig = go.Figure()

        # Histogram
        fig.add_trace(
            go.Histogram(
                x=data,
                name="Data",
                nbinsx=30,
                opacity=0.7,
            )
        )

        # Sample mean (solid black line)
        fig.add_vline(
            x=mean,
            line_dash="solid",
            line_color="black",
            line_width=2,
            annotation_text=f"Sample Mean ({mean:.2f})",
            annotation_position="top",
        )

        # Confidence interval (dashed black lines)
        if ci_lower != -np.inf:
            fig.add_vline(x=ci_lower, line_dash="dash", line_color="black", line_width=1)
        if ci_upper != np.inf:
            fig.add_vline(x=ci_upper, line_dash="dash", line_color="black", line_width=1)

        # Comparison value (red line)
        fig.add_vline(
            x=comparison,
            line_dash="solid",
            line_color="red",
            line_width=2,
            annotation_text=f"H₀ Value ({comparison})",
            annotation_position="bottom",
        )

        fig.update_layout(
            title=f"Distribution of {variable}",
            xaxis_title=variable,
            yaxis_title="Frequency",
            showlegend=False,
        )

        return (
            summary,
            fig,
            {"result": "success"},
            dmc.Notification(
                title="Success",
                message="Test completed successfully",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {str(e)}", c="red"),
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
    Output("smean-download", "data"),
    Input("smean-export-btn", "n_clicks"),
    [State("smean-dataset", "value"), State("smean-variable", "value")],
    prevent_initial_call=True,
)
def export_results(n_clicks, dataset_name, variable):
    """Export test results."""
    if not all([dataset_name, variable]):
        return None

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        data = df[[variable]].dropna()
        return dcc.send_data_frame(data.to_csv, f"single_mean_{variable}.csv", index=False)
    except Exception:
        return None
