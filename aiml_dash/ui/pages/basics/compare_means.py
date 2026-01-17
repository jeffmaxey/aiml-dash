"""
Compare Means Test Page
========================

Two-sample t-test to compare means between two groups.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px

from aiml_dash.components.common import (
    create_action_button,
    create_control_card,
    create_dataset_selector,
    create_numeric_input,
    create_page_header,
    create_results_card,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the compare means test page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Compare Means",
                "Two-sample t-test to compare means between two independent groups.",
                icon="carbon:compare",
            ),
            create_two_column_layout(
                # Left panel
                create_control_card(
                    [
                        create_dataset_selector(
                            selector_id="cmean-dataset",
                            label="Dataset",
                        ),
                        dmc.Select(
                            id="cmean-variable",
                            label="Numeric Variable",
                            placeholder="Select variable...",
                            data=[],
                        ),
                        dmc.Select(
                            id="cmean-group",
                            label="Grouping Variable",
                            placeholder="Select group variable...",
                            data=[],
                        ),
                        dmc.Select(
                            id="cmean-alternative",
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
                        dmc.Switch(
                            id="cmean-equal-var",
                            label="Assume Equal Variances",
                            description="Use pooled variance estimate",
                            checked=True,
                        ),
                        create_numeric_input(
                            input_id="cmean-confidence",
                            label="Confidence Level",
                            value=0.95,
                            min_val=0.5,
                            max_val=0.99,
                            step=0.01,
                        ),
                        create_action_button(
                            button_id="cmean-run-btn",
                            label="Run Test",
                            icon="carbon:play",
                            size="lg",
                        ),
                    ],
                    title="Test Settings",
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
                                "Plot",
                                value="plot",
                                leftSection=DashIconify(icon="carbon:chart-box-plot"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="cmean-summary"),
                                    ],
                                ),
                            ],
                            value="summary",
                        ),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        dcc.Graph(id="cmean-plot"),
                                    ],
                                ),
                            ],
                            value="plot",
                        ),
                    ],
                    value="summary",
                    id="cmean-tabs",
                ),
            ),
            html.Div(id="cmean-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("cmean-dataset", "data"),
    Input("cmean-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("cmean-variable", "data"), Output("cmean-group", "data")],
    Input("cmean-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], []

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        all_cols = [{"label": col, "value": col} for col in df.columns]
        return numeric_cols, all_cols
    except Exception:
        return [], []


@callback(
    [
        Output("cmean-summary", "children"),
        Output("cmean-plot", "figure"),
        Output("cmean-notification", "children"),
    ],
    Input("cmean-run-btn", "n_clicks"),
    [
        State("cmean-dataset", "value"),
        State("cmean-variable", "value"),
        State("cmean-group", "value"),
        State("cmean-alternative", "value"),
        State("cmean-equal-var", "checked"),
        State("cmean-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_compare_means_test(n_clicks, dataset_name, variable, group, alternative, equal_var, confidence):
    """Run two-sample t-test."""
    if not all([dataset_name, variable, group]):
        return (
            dmc.Text("Please select dataset, variable, and group.", c="red"),
            {},
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
        df_clean = df[[variable, group]].dropna()

        groups = df_clean[group].unique()
        if len(groups) != 2:
            raise ValueError(f"Grouping variable must have exactly 2 levels, found {len(groups)}")

        group1_data = df_clean[df_clean[group] == groups[0]][variable]
        group2_data = df_clean[df_clean[group] == groups[1]][variable]

        # Run t-test
        result = stats.ttest_ind(group1_data, group2_data, equal_var=equal_var, alternative=alternative)

        # Calculate statistics
        n1, n2 = len(group1_data), len(group2_data)
        mean1, mean2 = group1_data.mean(), group2_data.mean()
        std1, std2 = group1_data.std(ddof=1), group2_data.std(ddof=1)
        se1, se2 = std1 / np.sqrt(n1), std2 / np.sqrt(n2)
        diff = mean1 - mean2

        # Standard error of difference
        if equal_var:
            pooled_var = ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
            se_diff = np.sqrt(pooled_var * (1 / n1 + 1 / n2))
        else:
            se_diff = np.sqrt(se1**2 + se2**2)

        # Confidence interval
        df_val = n1 + n2 - 2 if equal_var else min(n1 - 1, n2 - 1)
        alpha = 1 - confidence
        if alternative == "two-sided":
            ci = stats.t.interval(confidence, df_val, loc=diff, scale=se_diff)
            ci_lower, ci_upper = ci
        elif alternative == "greater":
            ci_lower = stats.t.ppf(alpha, df_val, loc=diff, scale=se_diff)
            ci_upper = np.inf
        else:  # less
            ci_lower = -np.inf
            ci_upper = stats.t.ppf(1 - alpha, df_val, loc=diff, scale=se_diff)

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

        reject_null = result.pvalue < (1 - confidence)

        # Summary
        summary = dmc.Stack(
            [
                dmc.Text("Hypothesis", fw=600, size="lg"),
                dmc.Text("H₀: μ₁ = μ₂"),
                dmc.Text(
                    f"Hₐ: μ₁ {alternative.replace('two-sided', '≠').replace('greater', '>').replace('less', '<')} μ₂"
                ),
                dmc.Divider(),
                dmc.Text("Descriptive Statistics", fw=600, size="lg"),
                dag.AgGrid(
                    rowData=[
                        {
                            "group": str(groups[0]),
                            "n": n1,
                            "mean": f"{mean1:.3f}",
                            "sd": f"{std1:.3f}",
                            "se": f"{se1:.3f}",
                        },
                        {
                            "group": str(groups[1]),
                            "n": n2,
                            "mean": f"{mean2:.3f}",
                            "sd": f"{std2:.3f}",
                            "se": f"{se2:.3f}",
                        },
                    ],
                    columnDefs=[
                        {"field": "group", "headerName": "Group"},
                        {"field": "n", "headerName": "n"},
                        {"field": "mean", "headerName": "Mean"},
                        {"field": "sd", "headerName": "SD"},
                        {"field": "se", "headerName": "SE"},
                    ],
                    defaultColDef={"sortable": False, "flex": 1},
                    style={"height": "150px"},
                ),
                dmc.Divider(),
                dmc.Text("Test Results", fw=600, size="lg"),
                dag.AgGrid(
                    rowData=[
                        {
                            "diff": f"{diff:.3f}",
                            "se": f"{se_diff:.3f}",
                            "t-value": f"{result.statistic:.3f}",
                            "p-value": f"{p_value_str} {sig_stars}",
                            "df": df_val,
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
            ],
            gap="md",
        )

        # Plot - box plot
        plot_df = pd.DataFrame({
            variable: pd.concat([group1_data, group2_data]),
            group: [str(groups[0])] * len(group1_data) + [str(groups[1])] * len(group2_data),
        })

        fig = px.box(plot_df, x=group, y=variable, points="all", title=f"{variable} by {group}")

        return (
            summary,
            fig,
            dmc.Notification(title="Success", message="Test completed", color="green", action="show"),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {str(e)}", c="red"),
            {},
            dmc.Notification(title="Error", message=str(e), color="red", action="show"),
        )
