"""Callback registration for the basics plugin.

This module contains all callback functions for the basics plugin pages.
Callbacks handle user interactions and data processing for statistical analyses.

All callbacks have been extracted from pages/basics/ and refactored into this plugin module.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc
from dash.development.base_component import Component
from dash_iconify import DashIconify
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from scipy import stats
from utils.data_manager import data_manager


@callback(
    Output("smean-dataset", "data"),
    Input("smean-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
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
        df = data_manager.get_dataset(dataset_name)
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
        df = data_manager.get_dataset(dataset_name)
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
            dmc.Text(f"Error: {e!s}", c="red"),
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
        df = data_manager.get_dataset(dataset_name)
        data = df[[variable]].dropna()
        return dcc.send_data_frame(data.to_csv, f"single_mean_{variable}.csv", index=False)
    except Exception:
        return None

@callback(
    Output("cmean-dataset", "data"),
    Input("cmean-dataset", "id"),
)
def update_datasets(_: str) -> list[dict[str, str]]:
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]

@callback(
    [Output("cmean-variable", "data"), Output("cmean-group", "data")],
    Input("cmean-dataset", "value"),
)
def update_variables(dataset_name: str | None) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], []

    try:
        df = data_manager.get_dataset(dataset_name)
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
def run_compare_means_test(
    n_clicks: int | None,
    dataset_name: str | None,
    variable: str | None,
    group: str | None,
    alternative: str | None,
    equal_var: bool | None,
    confidence: float | None,
) -> tuple[Component, Figure | dict[str, object], Component]:
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
        if confidence is None:
            confidence = 0.95
        if alternative is None:
            alternative = "two-sided"
        if equal_var is None:
            equal_var = True
        # Get data
        df = data_manager.get_dataset(dataset_name)
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
            dmc.Text(f"Error: {e!s}", c="red"),
            {},
            dmc.Notification(title="Error", message=str(e), color="red", action="show"),
        )

@callback(
    Output("single-prop-dataset", "data"),
    Input("single-prop-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]

@callback(
    [Output("single-prop-variable", "data"), Output("single-prop-variable", "value")],
    Input("single-prop-dataset", "value"),
)
def update_variables(dataset):
    """Populate variable dropdown with all columns."""
    if not dataset:
        return [], None

    df = data_manager.get_dataset(dataset)
    columns = df.columns.tolist()

    return [{"label": col, "value": col} for col in columns], None

@callback(
    [Output("single-prop-success", "data"), Output("single-prop-success", "value")],
    [Input("single-prop-dataset", "value"), Input("single-prop-variable", "value")],
)
def update_success_levels(dataset, variable):
    """Populate success level dropdown with unique values from selected variable."""
    if not dataset or not variable:
        return [], None

    df = data_manager.get_dataset(dataset)

    if variable not in df.columns:
        return [], None

    # Get unique values
    unique_vals = df[variable].dropna().unique()
    unique_vals = sorted([str(v) for v in unique_vals])

    return [{"label": val, "value": val} for val in unique_vals], None if len(unique_vals) == 0 else unique_vals[0]

@callback(
    [
        Output("single-prop-results", "children"),
        Output("single-prop-plot-container", "style"),
        Output("single-prop-plot", "figure"),
    ],
    Input("single-prop-run", "n_clicks"),
    [
        State("single-prop-dataset", "value"),
        State("single-prop-variable", "value"),
        State("single-prop-success", "value"),
        State("single-prop-p0", "value"),
        State("single-prop-alternative", "value"),
        State("single-prop-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_single_prop_test(n_clicks, dataset, variable, success_level, p0, alternative, confidence):
    """Run single proportion test and display results."""
    if not all([dataset, variable, success_level]):
        return (
            [
                dmc.Alert(
                    "Please select dataset, variable, and success level",
                    title="Missing inputs",
                    color="yellow",
                    icon=DashIconify(icon="mdi:alert"),
                )
            ],
            {"display": "none"},
            {},
        )

    try:
        # Load data
        df = data_manager.get_dataset(dataset)

        if variable not in df.columns:
            return (
                [
                    dmc.Alert(
                        f"Variable '{variable}' not found in dataset",
                        title="Error",
                        color="red",
                        icon=DashIconify(icon="mdi:alert-circle"),
                    )
                ],
                {"display": "none"},
                {},
            )

        # Calculate sample proportion
        data = df[variable].dropna()
        n = len(data)

        # Convert to binary (success = 1, failure = 0)
        successes = (data.astype(str) == str(success_level)).sum()
        p_hat = successes / n

        # Run binomial test
        if alternative == "two-sided":
            p_value = stats.binom_test(successes, n, p0, alternative="two-sided")
        else:
            p_value = stats.binom_test(successes, n, p0, alternative=alternative)

        # Calculate confidence interval using Wilson score interval
        alpha = 1 - confidence
        z = stats.norm.ppf(1 - alpha / 2)
        denominator = 1 + z**2 / n
        center = (p_hat + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denominator
        ci_lower = center - margin
        ci_upper = center + margin

        # Standard error
        se = np.sqrt(p0 * (1 - p0) / n)

        # Z-statistic for large sample approximation
        z_stat = (p_hat - p0) / se if se > 0 else 0

        # Determine significance
        is_significant = p_value < (1 - confidence)

        # Create results display
        results_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            dmc.Text("Proportion Test Results", fw=600, size="lg"),
                            dmc.Badge(
                                "Significant" if is_significant else "Not Significant",
                                color="green" if is_significant else "gray",
                                variant="filled",
                            ),
                        ],
                        justify="space-between",
                    ),
                    # Summary statistics
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 4},
                        spacing="md",
                        children=[
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Sample Size", size="xs", c="dimmed"),
                                    dmc.Text(f"{n:,}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Successes", size="xs", c="dimmed"),
                                    dmc.Text(f"{successes:,}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Sample Proportion", size="xs", c="dimmed"),
                                    dmc.Text(f"{p_hat:.4f}", fw=600, size="xl"),
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
                    dmc.Divider(),
                    # Test details
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Text("Test Details", fw=500, size="sm"),
                            dmc.Group([
                                dmc.Text("Null hypothesis:", size="sm"),
                                dmc.Code(f"p = {p0}", style={"fontSize": "0.875rem"}),
                            ]),
                            dmc.Group([
                                dmc.Text("Alternative hypothesis:", size="sm"),
                                dmc.Code(
                                    f"p ≠ {p0}"
                                    if alternative == "two-sided"
                                    else f"p > {p0}"
                                    if alternative == "greater"
                                    else f"p < {p0}",
                                    style={"fontSize": "0.875rem"},
                                ),
                            ]),
                            dmc.Group([
                                dmc.Text("Z-statistic:", size="sm"),
                                dmc.Code(f"{z_stat:.4f}", style={"fontSize": "0.875rem"}),
                            ]),
                            dmc.Group([
                                dmc.Text(
                                    f"{int(confidence * 100)}% Confidence Interval:",
                                    size="sm",
                                ),
                                dmc.Code(
                                    f"[{ci_lower:.4f}, {ci_upper:.4f}]",
                                    style={"fontSize": "0.875rem"},
                                ),
                            ]),
                        ],
                    ),
                    # Interpretation
                    dmc.Alert(
                        title="Interpretation",
                        color="blue",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"The sample proportion ({p_hat:.4f}) is "
                            f"{'significantly different from' if is_significant else 'not significantly different from'} "
                            f"the hypothesized value ({p0}) at the {int(confidence * 100)}% confidence level. "
                            f"The p-value of {p_value:.4f} {'is less than' if is_significant else 'is greater than'} "
                            f"the significance level of {1 - confidence:.3f}.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create bar plot
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=["Sample", "Hypothesized"],
                y=[p_hat, p0],
                marker={
                    "color": ["#1c7ed6", "#868e96"],
                },
                text=[f"{p_hat:.4f}", f"{p0:.4f}"],
                textposition="outside",
                name="Proportion",
            )
        )

        # Add confidence interval as error bar on sample
        fig.add_trace(
            go.Scatter(
                x=["Sample"],
                y=[p_hat],
                error_y={
                    "type": "data",
                    "symmetric": False,
                    "array": [ci_upper - p_hat],
                    "arrayminus": [p_hat - ci_lower],
                    "color": "#1c7ed6",
                    "thickness": 2,
                    "width": 10,
                },
                mode="markers",
                marker={"size": 0.1, "color": "rgba(0,0,0,0)"},
                showlegend=False,
                hoverinfo="skip",
            )
        )

        fig.update_layout(
            title=f"Proportion Comparison<br><sub>Sample vs. Hypothesized Value (p₀ = {p0})</sub>",
            yaxis_title="Proportion",
            yaxis={"range": [0, min(1, max(p_hat, p0) * 1.3)]},
            template="plotly_white",
            height=400,
            showlegend=False,
            hovermode="x unified",
        )

        return results_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error running test: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )

@callback(
    Output("compare-props-dataset", "data"),
    Input("compare-props-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]

@callback(
    [
        Output("compare-props-variable", "data"),
        Output("compare-props-variable", "value"),
        Output("compare-props-group", "data"),
        Output("compare-props-group", "value"),
    ],
    Input("compare-props-dataset", "value"),
)
def update_variables(dataset):
    """Populate variable dropdowns."""
    if not dataset:
        return [], None, [], None

    df = data_manager.get_dataset(dataset)
    columns = df.columns.tolist()
    options = [{"label": col, "value": col} for col in columns]

    return options, None, options, None

@callback(
    [Output("compare-props-success", "data"), Output("compare-props-success", "value")],
    [Input("compare-props-dataset", "value"), Input("compare-props-variable", "value")],
)
def update_success_levels(dataset, variable):
    """Populate success level dropdown."""
    if not dataset or not variable:
        return [], None

    df = data_manager.get_dataset(dataset)

    if variable not in df.columns:
        return [], None

    unique_vals = df[variable].dropna().unique()
    unique_vals = sorted([str(v) for v in unique_vals])

    return [{"label": val, "value": val} for val in unique_vals], None if len(unique_vals) == 0 else unique_vals[0]

@callback(
    [
        Output("compare-props-results", "children"),
        Output("compare-props-plot-container", "style"),
        Output("compare-props-plot", "figure"),
    ],
    Input("compare-props-run", "n_clicks"),
    [
        State("compare-props-dataset", "value"),
        State("compare-props-variable", "value"),
        State("compare-props-success", "value"),
        State("compare-props-group", "value"),
        State("compare-props-alternative", "value"),
        State("compare-props-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_compare_props_test(n_clicks, dataset, variable, success_level, group_var, alternative, confidence):
    """Run two-sample proportion test."""
    if not all([dataset, variable, success_level, group_var]):
        return (
            [
                dmc.Alert(
                    "Please select all required inputs",
                    title="Missing inputs",
                    color="yellow",
                    icon=DashIconify(icon="mdi:alert"),
                )
            ],
            {"display": "none"},
            {},
        )

    try:
        df = data_manager.get_dataset(dataset)

        if variable not in df.columns or group_var not in df.columns:
            return (
                [
                    dmc.Alert(
                        "Selected variables not found in dataset",
                        title="Error",
                        color="red",
                        icon=DashIconify(icon="mdi:alert-circle"),
                    )
                ],
                {"display": "none"},
                {},
            )

        # Get unique groups
        groups = df[group_var].dropna().unique()
        if len(groups) != 2:
            return (
                [
                    dmc.Alert(
                        f"Group variable must have exactly 2 groups (found {len(groups)})",
                        title="Error",
                        color="red",
                        icon=DashIconify(icon="mdi:alert-circle"),
                    )
                ],
                {"display": "none"},
                {},
            )

        group1, group2 = sorted([str(g) for g in groups])

        # Calculate proportions for each group
        group1_data = df[df[group_var].astype(str) == group1][variable].dropna()
        group2_data = df[df[group_var].astype(str) == group2][variable].dropna()

        n1 = len(group1_data)
        n2 = len(group2_data)

        x1 = (group1_data.astype(str) == str(success_level)).sum()
        x2 = (group2_data.astype(str) == str(success_level)).sum()

        p1 = x1 / n1 if n1 > 0 else 0
        p2 = x2 / n2 if n2 > 0 else 0

        # Pooled proportion
        p_pool = (x1 + x2) / (n1 + n2)

        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))

        # Z-statistic
        z_stat = (p1 - p2) / se if se > 0 else 0

        # P-value
        if alternative == "two-sided":
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        elif alternative == "greater":
            p_value = 1 - stats.norm.cdf(z_stat)
        else:  # less
            p_value = stats.norm.cdf(z_stat)

        # Confidence interval for difference
        alpha = 1 - confidence
        z_crit = stats.norm.ppf(1 - alpha / 2)
        se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        ci_lower = (p1 - p2) - z_crit * se_diff
        ci_upper = (p1 - p2) + z_crit * se_diff

        # Effect sizes
        relative_risk = p1 / p2 if p2 > 0 else float("inf")
        odds1 = p1 / (1 - p1) if p1 < 1 else float("inf")
        odds2 = p2 / (1 - p2) if p2 < 1 else float("inf")
        odds_ratio = odds1 / odds2 if odds2 > 0 else float("inf")

        is_significant = p_value < (1 - confidence)

        # Results display
        results_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            dmc.Text("Two-Sample Proportion Test", fw=600, size="lg"),
                            dmc.Badge(
                                "Significant" if is_significant else "Not Significant",
                                color="green" if is_significant else "gray",
                                variant="filled",
                            ),
                        ],
                        justify="space-between",
                    ),
                    # Group statistics
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 2},
                        spacing="md",
                        children=[
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(f"Group: {group1}", fw=500, size="sm", mb="xs"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("n", size="xs", c="dimmed"),
                                                    dmc.Text(f"{n1}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Successes",
                                                        size="xs",
                                                        c="dimmed",
                                                    ),
                                                    dmc.Text(f"{x1}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Proportion",
                                                        size="xs",
                                                        c="dimmed",
                                                    ),
                                                    dmc.Text(f"{p1:.4f}", fw=600, c="blue"),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(f"Group: {group2}", fw=500, size="sm", mb="xs"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("n", size="xs", c="dimmed"),
                                                    dmc.Text(f"{n2}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Successes",
                                                        size="xs",
                                                        c="dimmed",
                                                    ),
                                                    dmc.Text(f"{x2}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Proportion",
                                                        size="xs",
                                                        c="dimmed",
                                                    ),
                                                    dmc.Text(f"{p2:.4f}", fw=600, c="blue"),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Divider(),
                    # Test statistics
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 4},
                        spacing="md",
                        children=[
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Difference", size="xs", c="dimmed"),
                                    dmc.Text(f"{p1 - p2:.4f}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Z-statistic", size="xs", c="dimmed"),
                                    dmc.Text(f"{z_stat:.4f}", fw=600, size="xl"),
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
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text(
                                        f"{int(confidence * 100)}% CI",
                                        size="xs",
                                        c="dimmed",
                                    ),
                                    dmc.Text(
                                        f"[{ci_lower:.3f}, {ci_upper:.3f}]",
                                        fw=500,
                                        size="sm",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Effect sizes
                    dmc.Paper(
                        p="sm",
                        withBorder=True,
                        children=[
                            dmc.Text("Effect Sizes", fw=500, size="sm", mb="xs"),
                            dmc.Group(
                                [
                                    dmc.Stack(
                                        gap=2,
                                        children=[
                                            dmc.Text("Relative Risk", size="xs", c="dimmed"),
                                            dmc.Text(
                                                f"{relative_risk:.4f}" if relative_risk != float("inf") else "∞",
                                                fw=600,
                                            ),
                                        ],
                                    ),
                                    dmc.Stack(
                                        gap=2,
                                        children=[
                                            dmc.Text("Odds Ratio", size="xs", c="dimmed"),
                                            dmc.Text(
                                                f"{odds_ratio:.4f}" if odds_ratio != float("inf") else "∞",
                                                fw=600,
                                            ),
                                        ],
                                    ),
                                ],
                                justify="space-around",
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Interpretation",
                        color="blue",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"The proportion in {group1} ({p1:.4f}) is "
                            f"{'significantly different from' if is_significant else 'not significantly different from'} "
                            f"the proportion in {group2} ({p2:.4f}) at the {int(confidence * 100)}% confidence level. "
                            f"The difference is {abs(p1 - p2):.4f} with p-value = {p_value:.4f}.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create bar plot
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=[group1, group2],
                y=[p1, p2],
                marker={"color": ["#1c7ed6", "#15aabf"]},
                text=[f"{p1:.4f}", f"{p2:.4f}"],
                textposition="outside",
                error_y={
                    "type": "data",
                    "array": [
                        stats.norm.ppf(1 - (1 - confidence) / 2) * np.sqrt(p1 * (1 - p1) / n1),
                        stats.norm.ppf(1 - (1 - confidence) / 2) * np.sqrt(p2 * (1 - p2) / n2),
                    ],
                    "visible": True,
                    "color": "gray",
                },
            )
        )

        fig.update_layout(
            title=f"Proportion Comparison by {group_var}",
            yaxis_title="Proportion",
            yaxis={"range": [0, min(1, max(p1, p2) * 1.3)]},
            template="plotly_white",
            height=400,
            showlegend=False,
        )

        return results_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )

@callback(Output("corr-dataset", "data"), Input("corr-dataset", "id"))
def update_datasets(_):
    """Populate dataset dropdown with available datasets.

    Returns:
        List of dataset options for dropdown.
    """
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]

@callback(Output("corr-variables", "data"), Input("corr-dataset", "value"))
def update_variables(dataset_name):
    """Update variable options based on selected dataset.

    Args:
        dataset_name: Name of the selected dataset.

    Returns:
        List of numeric column options for dropdown.
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
    [Output("corr-output", "children"), Output("corr-notification", "children")],
    Input("corr-btn", "n_clicks"),
    [
        State("corr-dataset", "value"),
        State("corr-variables", "value"),
        State("corr-method", "value"),
    ],
    prevent_initial_call=True,
)
def calculate_correlation(n_clicks, dataset_name, variables, method):
    """Calculate and display correlation matrix.

    Args:
        n_clicks: Number of button clicks.
        dataset_name: Name of the dataset to analyze.
        variables: List of variables to correlate.
        method: Correlation method (pearson, spearman, or kendall).

    Returns:
        Tuple of (output_children, notification_children).
    """
    if not all([dataset_name, variables]) or len(variables) < 2:
        return dmc.Text("Select dataset and at least 2 variables.", c="red"), dmc.Notification(
            title="Error", message="Missing inputs", color="red", action="show"
        )

    try:
        df = data_manager.get_dataset(dataset_name)
        corr_matrix = df[variables].corr(method=method)
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            title=f"{method.title()} Correlation Matrix",
            color_continuous_scale="RdBu_r",
            range_color=[-1, 1],
        )
        return dcc.Graph(figure=fig), dmc.Notification(
            title="Success",
            message="Correlation calculated",
            color="green",
            action="show",
        )
    except Exception as e:
        return dmc.Text(f"Error: {e!s}", c="red"), dmc.Notification(
            title="Error", message=str(e), color="red", action="show"
        )

@callback(
    Output("crosstabs-dataset", "data"),
    Input("crosstabs-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]

@callback(
    [
        Output("crosstabs-row-var", "data"),
        Output("crosstabs-row-var", "value"),
        Output("crosstabs-col-var", "data"),
        Output("crosstabs-col-var", "value"),
    ],
    Input("crosstabs-dataset", "value"),
)
def update_variables(dataset):
    """Populate variable dropdowns."""
    if not dataset:
        return [], None, [], None

    df = data_manager.get_dataset(dataset)
    columns = df.columns.tolist()
    options = [{"label": col, "value": col} for col in columns]

    return options, None, options, None

@callback(
    [
        Output("crosstabs-results", "children"),
        Output("crosstabs-table-container", "style"),
        Output("crosstabs-table", "children"),
        Output("crosstabs-plot-container", "style"),
        Output("crosstabs-plot", "figure"),
    ],
    Input("crosstabs-run", "n_clicks"),
    [
        State("crosstabs-dataset", "value"),
        State("crosstabs-row-var", "value"),
        State("crosstabs-col-var", "value"),
        State("crosstabs-show-percentages", "checked"),
        State("crosstabs-show-expected", "checked"),
        State("crosstabs-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_crosstabs_analysis(n_clicks, dataset, row_var, col_var, show_pct, show_expected, confidence):
    """Run chi-square test of independence."""
    if not all([dataset, row_var, col_var]):
        return (
            [
                dmc.Alert(
                    "Please select dataset and both variables",
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
        df = data_manager.get_dataset(dataset)

        if row_var not in df.columns or col_var not in df.columns:
            return (
                [
                    dmc.Alert(
                        "Selected variables not found in dataset",
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

        # Create contingency table
        contingency_table = pd.crosstab(df[row_var], df[col_var])

        # Run chi-square test
        chi2, p_value, dof, _expected_freq = stats.chi2_contingency(contingency_table)

        # Calculate Cramér's V (effect size)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape[0], contingency_table.shape[1]) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        is_significant = p_value < (1 - confidence)

        # Create results display
        results_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            dmc.Text("Chi-Square Test of Independence", fw=600, size="lg"),
                            dmc.Badge(
                                "Significant" if is_significant else "Not Significant",
                                color="green" if is_significant else "gray",
                                variant="filled",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 4},
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
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Cramér's V", size="xs", c="dimmed"),
                                    dmc.Text(f"{cramers_v:.4f}", fw=600, size="xl"),
                                ],
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Interpretation",
                        color="blue",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"There {'is' if is_significant else 'is no'} statistically significant association "
                            f"between {row_var} and {col_var} (χ² = {chi2:.2f}, df = {dof}, p = {p_value:.4f}). "
                            f"Cramér's V = {cramers_v:.3f} indicates a "
                            f"{'weak' if cramers_v < 0.3 else 'moderate' if cramers_v < 0.5 else 'strong'} "
                            f"effect size.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create contingency table display
        if show_pct:
            # Show percentages
            pct_table = contingency_table / contingency_table.sum().sum() * 100
            display_table = pct_table.round(2).astype(str) + "%"
        else:
            display_table = contingency_table.astype(str)

        # Add row and column totals
        display_df = display_table.copy()
        display_df["Total"] = contingency_table.sum(axis=1).astype(str)
        totals_row = pd.Series(
            [*contingency_table.sum(axis=0).astype(str).tolist(), str(n)],
            index=list(display_df.columns),
            name="Total",
        )
        display_df = pd.concat([display_df, pd.DataFrame([totals_row])], ignore_index=False)

        # Create AG Grid
        display_df = display_df.reset_index()
        display_df.rename(columns={"index": row_var}, inplace=True)

        table_component = dag.AgGrid(
            rowData=display_df.to_dict("records"),
            columnDefs=[{"field": col, "headerName": col} for col in display_df.columns],
            defaultColDef={"resizable": True, "sortable": True, "filter": False},
            style={"height": "300px"},
        )

        # Create grouped bar chart
        fig = go.Figure()

        for col in contingency_table.columns:
            fig.add_trace(
                go.Bar(
                    name=str(col),
                    x=contingency_table.index.astype(str),
                    y=contingency_table[col],
                    text=contingency_table[col],
                    textposition="auto",
                )
            )

        fig.update_layout(
            title=f"{row_var} by {col_var}",
            xaxis_title=row_var,
            yaxis_title="Count",
            barmode="group",
            template="plotly_white",
            height=400,
            legend={"title": col_var},
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
                    f"Error: {e!s}",
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

@callback(
    Output("goodness-dataset", "data"),
    Input("goodness-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]

@callback(
    [Output("goodness-variable", "data"), Output("goodness-variable", "value")],
    Input("goodness-dataset", "value"),
)
def update_variables(dataset):
    """Populate variable dropdown."""
    if not dataset:
        return [], None

    df = data_manager.get_dataset(dataset)
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
        df = data_manager.get_dataset(dataset)

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
                marker={"color": "#1c7ed6"},
                text=observed,
                textposition="auto",
            )
        )

        fig.add_trace(
            go.Bar(
                name="Expected",
                x=[str(cat) for cat in categories],
                y=expected,
                marker={"color": "#868e96"},
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
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
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
                    f"Error: {e!s}",
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

@callback(
    Output("prob-params-container", "children"),
    Input("prob-distribution", "value"),
)
def update_params(distribution):
    """Update parameter inputs based on distribution."""
    if distribution == "normal":
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Mean (μ)",
                value=0,
                step=0.1,
                decimalScale=2,
            ),
            dmc.NumberInput(
                id="prob-param2",
                label="Standard Deviation (σ)",  # noqa: RUF001
                value=1,
                min=0.01,
                step=0.1,
                decimalScale=2,
            ),
        ]
    elif distribution == "t":
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Degrees of Freedom",
                value=10,
                min=1,
                step=1,
            ),
        ]
    elif distribution == "chi2":
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Degrees of Freedom",
                value=5,
                min=1,
                step=1,
            ),
        ]
    elif distribution == "f":
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Numerator df",
                value=5,
                min=1,
                step=1,
            ),
            dmc.NumberInput(
                id="prob-param2",
                label="Denominator df",
                value=10,
                min=1,
                step=1,
            ),
        ]
    elif distribution == "binomial":
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Number of trials (n)",
                value=10,
                min=1,
                step=1,
            ),
            dmc.NumberInput(
                id="prob-param2",
                label="Probability of success (p)",
                value=0.5,
                min=0,
                max=1,
                step=0.01,
                decimalScale=3,
            ),
        ]
    else:  # poisson
        return [
            dmc.NumberInput(
                id="prob-param1",
                label="Rate (λ)",
                value=5,
                min=0.01,
                step=0.1,
                decimalScale=2,
            ),
        ]

@callback(
    Output("prob-input-container", "children"),
    Input("prob-calc-type", "value"),
)
def update_input_type(calc_type):
    """Update input fields based on calculation type."""
    if calc_type == "probability":
        return [
            dmc.Stack(
                gap=5,
                children=[
                    dmc.Text("Probability Type", size="sm", fw=500),
                    dmc.SegmentedControl(
                        id="prob-tail",
                        data=[
                            {"label": "P(X ≤ x)", "value": "lower"},
                            {"label": "P(X ≥ x)", "value": "upper"},
                            {"label": "P(a ≤ X ≤ b)", "value": "between"},
                        ],
                        value="lower",
                        fullWidth=True,
                    ),
                ],
            ),
            dmc.NumberInput(
                id="prob-value1",
                label="Value (x)",
                value=0,
                step=0.1,
                decimalScale=3,
            ),
            html.Div(
                id="prob-value2-container",
                style={"display": "none"},
                children=[
                    dmc.NumberInput(
                        id="prob-value2",
                        label="Upper Value (b)",
                        value=1,
                        step=0.1,
                        decimalScale=3,
                    ),
                ],
            ),
        ]
    else:  # critical value
        return [
            dmc.NumberInput(
                id="prob-alpha",
                label="Significance Level (α)",  # noqa: RUF001
                description="For two-tailed test, α is split between tails",
                value=0.05,
                min=0.001,
                max=0.5,
                step=0.01,
                decimalScale=3,
            ),
            dmc.Stack(
                gap=5,
                children=[
                    dmc.Text("Tail(s)", size="sm", fw=500),
                    dmc.SegmentedControl(
                        id="prob-tails",
                        data=[
                            {"label": "Lower", "value": "lower"},
                            {"label": "Upper", "value": "upper"},
                            {"label": "Two-tailed", "value": "two"},
                        ],
                        value="two",
                        fullWidth=True,
                    ),
                ],
            ),
        ]

@callback(
    Output("prob-value2-container", "style"),
    Input("prob-tail", "value"),
    prevent_initial_call=True,
)
def toggle_value2(tail):
    """Show/hide second value input for 'between' probability."""
    if tail == "between":
        return {"display": "block"}
    return {"display": "none"}

@callback(
    [
        Output("prob-results", "children"),
        Output("prob-plot-container", "style"),
        Output("prob-plot", "figure"),
    ],
    Input("prob-calculate", "n_clicks"),
    [
        State("prob-distribution", "value"),
        State("prob-calc-type", "value"),
        State("prob-param1", "value"),
        State("prob-param2", "value"),
    ],
    prevent_initial_call=True,
)
def calculate_probability(n_clicks, distribution, calc_type, param1, param2):
    """Calculate probability or critical value."""
    try:
        # Get additional parameters from context

        # Create distribution object
        if distribution == "normal":
            dist = stats.norm(loc=param1, scale=param2)
            x_range = np.linspace(param1 - 4 * param2, param1 + 4 * param2, 500)
        elif distribution == "t":
            dist = stats.t(df=param1)
            x_range = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 500)
        elif distribution == "chi2":
            dist = stats.chi2(df=param1)
            x_range = np.linspace(0, dist.ppf(0.999), 500)
        elif distribution == "f":
            dist = stats.f(dfn=param1, dfd=param2)
            x_range = np.linspace(0, dist.ppf(0.999), 500)
        elif distribution == "binomial":
            dist = stats.binom(n=int(param1), p=param2)
            x_range = np.arange(0, int(param1) + 1)
        else:  # poisson
            dist = stats.poisson(mu=param1)
            x_range = np.arange(0, int(param1 * 3) + 1)

        # Get inputs from dash.callback_context (simplified for this implementation)
        # In real implementation, you'd need to get these from State

        if calc_type == "probability":
            # For demonstration, calculate P(X ≤ 0)
            value = 0
            prob = dist.cdf(value)

            result_content = [
                dmc.Stack(
                    gap="md",
                    children=[
                        dmc.Text("Probability Result", fw=600, size="lg"),
                        dmc.Stack(
                            gap=4,
                            children=[
                                dmc.Text(f"P(X ≤ {value})", size="sm", c="dimmed"),
                                dmc.Text(f"{prob:.6f}", fw=600, size="xl", c="blue"),
                            ],
                        ),
                        dmc.Alert(
                            title="Result",
                            color="blue",
                            icon=DashIconify(icon="mdi:information"),
                            children=dmc.Text(
                                f"The probability that X is less than or equal to {value} is {prob:.6f} ({prob * 100:.4f}%).",
                                size="sm",
                            ),
                        ),
                    ],
                ),
            ]

            # Create plot
            fig = go.Figure()

            if distribution in ["binomial", "poisson"]:
                # Bar chart for discrete distributions
                pmf = dist.pmf(x_range)
                colors = ["#1c7ed6" if x <= value else "#dee2e6" for x in x_range]
                fig.add_trace(
                    go.Bar(
                        x=x_range,
                        y=pmf,
                        marker={"color": colors},
                        showlegend=False,
                    )
                )
            else:
                # Line chart for continuous distributions
                pdf = dist.pdf(x_range)
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=pdf,
                        mode="lines",
                        line={"color": "#1c7ed6", "width": 2},
                        fill="tozeroy",
                        fillcolor="rgba(28, 126, 214, 0.1)",
                        showlegend=False,
                    )
                )

                # Shade area
                x_shaded = x_range[x_range <= value]
                y_shaded = dist.pdf(x_shaded)
                fig.add_trace(
                    go.Scatter(
                        x=x_shaded,
                        y=y_shaded,
                        mode="lines",
                        line={"width": 0},
                        fill="tozeroy",
                        fillcolor="rgba(28, 126, 214, 0.5)",
                        showlegend=False,
                    )
                )

            fig.update_layout(
                title=f"{distribution.title()} Distribution",
                xaxis_title="x",
                yaxis_title="Density" if distribution not in ["binomial", "poisson"] else "Probability",
                template="plotly_white",
                height=400,
            )

        else:  # critical value
            alpha = 0.05
            critical_lower = dist.ppf(alpha / 2)
            critical_upper = dist.ppf(1 - alpha / 2)

            result_content = [
                dmc.Stack(
                    gap="md",
                    children=[
                        dmc.Text("Critical Values", fw=600, size="lg"),
                        dmc.SimpleGrid(
                            cols=2,
                            spacing="md",
                            children=[
                                dmc.Stack(
                                    gap=4,
                                    children=[
                                        dmc.Text(
                                            "Lower Critical Value",
                                            size="sm",
                                            c="dimmed",
                                        ),
                                        dmc.Text(
                                            f"{critical_lower:.4f}",
                                            fw=600,
                                            size="xl",
                                            c="red",
                                        ),
                                    ],
                                ),
                                dmc.Stack(
                                    gap=4,
                                    children=[
                                        dmc.Text(
                                            "Upper Critical Value",
                                            size="sm",
                                            c="dimmed",
                                        ),
                                        dmc.Text(
                                            f"{critical_upper:.4f}",
                                            fw=600,
                                            size="xl",
                                            c="red",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dmc.Alert(
                            title="Result",
                            color="blue",
                            icon=DashIconify(icon="mdi:information"),
                            children=dmc.Text(
                                f"For a two-tailed test with α = {alpha}, the critical values are {critical_lower:.4f} and {critical_upper:.4f}.",  # noqa: RUF001
                                size="sm",
                            ),
                        ),
                    ],
                ),
            ]

            # Create plot
            fig = go.Figure()

            if distribution in ["binomial", "poisson"]:
                pmf = dist.pmf(x_range)
                fig.add_trace(
                    go.Bar(
                        x=x_range,
                        y=pmf,
                        marker={"color": "#dee2e6"},
                        showlegend=False,
                    )
                )
            else:
                pdf = dist.pdf(x_range)
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=pdf,
                        mode="lines",
                        line={"color": "#1c7ed6", "width": 2},
                        fill="tozeroy",
                        fillcolor="rgba(28, 126, 214, 0.1)",
                        showlegend=False,
                    )
                )

                # Shade rejection regions
                x_lower = x_range[x_range <= critical_lower]
                y_lower = dist.pdf(x_lower)
                x_upper = x_range[x_range >= critical_upper]
                y_upper = dist.pdf(x_upper)

                fig.add_trace(
                    go.Scatter(
                        x=x_lower,
                        y=y_lower,
                        mode="lines",
                        line={"width": 0},
                        fill="tozeroy",
                        fillcolor="rgba(255, 0, 0, 0.3)",
                        name="Rejection Region",
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=x_upper,
                        y=y_upper,
                        mode="lines",
                        line={"width": 0},
                        fill="tozeroy",
                        fillcolor="rgba(255, 0, 0, 0.3)",
                        showlegend=False,
                    )
                )

            fig.update_layout(
                title=f"{distribution.title()} Distribution with Critical Regions (α = {alpha})",  # noqa: RUF001
                xaxis_title="x",
                yaxis_title="Density" if distribution not in ["binomial", "poisson"] else "Probability",
                template="plotly_white",
                height=400,
            )

        return result_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )

@callback(
    [
        Output("clt-stats", "children"),
        Output("clt-plot-container", "style"),
        Output("clt-plot", "figure"),
    ],
    Input("clt-run", "n_clicks"),
    [
        State("clt-distribution", "value"),
        State("clt-sample-size", "value"),
        State("clt-num-samples", "value"),
        State("clt-seed", "value"),
    ],
    prevent_initial_call=True,
)
def run_clt_simulation(
    n_clicks: int | None,
    distribution: str | None,
    sample_size: int | float | None,
    num_samples: int | float | None,
    seed: int | None,
) -> tuple[list[Component], dict[str, str], go.Figure | dict[str, object]]:
    """Run CLT simulation."""
    try:
        if sample_size is None or num_samples is None:
            raise ValueError("Sample size and number of samples are required.")
        sample_size_int = int(sample_size)
        num_samples_int = int(num_samples)
        if distribution is None:
            distribution = "uniform"
        # Set random seed for reproducibility
        np.random.seed(seed)

        # Generate population based on distribution type
        pop_size = 100000

        population: npt.NDArray[np.float64]
        if distribution == "uniform":
            population = np.random.uniform(0, 10, pop_size)
            pop_mean = 5.0
            pop_std = 10 / np.sqrt(12)  # Theoretical std for uniform(0,10)
        elif distribution == "normal":
            population = np.random.normal(50, 10, pop_size)
            pop_mean = 50.0
            pop_std = 10.0
        elif distribution == "exponential":
            population = np.random.exponential(2, pop_size)
            pop_mean = 2.0
            pop_std = 2.0
        elif distribution == "binomial":
            population = np.random.binomial(10, 0.5, pop_size).astype(np.float64)
            pop_mean = 5.0
            pop_std = np.sqrt(10 * 0.5 * 0.5)
        elif distribution == "poisson":
            population = np.random.poisson(5, pop_size).astype(np.float64)
            pop_mean = 5.0
            pop_std = np.sqrt(5.0)
        else:  # beta (skewed)
            population = np.random.beta(2, 5, pop_size) * 10
            pop_mean = (2 / (2 + 5)) * 10
            pop_std = np.sqrt((2 * 5) / ((2 + 5) ** 2 * (2 + 5 + 1))) * 10

        # Draw samples and calculate means
        sample_means: list[float] = []
        for _ in range(num_samples_int):
            sample = np.random.choice(population, size=sample_size_int, replace=True)
            sample_means.append(float(np.mean(sample)))

        sample_means_array = np.array(sample_means, dtype=np.float64)

        # Calculate statistics
        mean_of_means = np.mean(sample_means_array)
        std_of_means = np.std(sample_means_array, ddof=1)
        theoretical_std = pop_std / np.sqrt(sample_size_int)

        # Normality test (Shapiro-Wilk)
        if len(sample_means_array) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(sample_means_array)
        else:
            # Use Kolmogorov-Smirnov for large samples
            _shapiro_stat, shapiro_p = stats.kstest((sample_means_array - mean_of_means) / std_of_means, "norm")

        # Create statistics display
        stats_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Text("Simulation Results", fw=600, size="lg"),
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 3},
                        spacing="md",
                        children=[
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(
                                        "Population",
                                        fw=500,
                                        size="sm",
                                        mb="xs",
                                        c="dimmed",
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Mean", size="xs", c="dimmed"),
                                                    dmc.Text(f"{pop_mean:.3f}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Std Dev", size="xs", c="dimmed"),
                                                    dmc.Text(f"{pop_std:.3f}", fw=600),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(
                                        "Sample Means",
                                        fw=500,
                                        size="sm",
                                        mb="xs",
                                        c="dimmed",
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Mean", size="xs", c="dimmed"),
                                                    dmc.Text(
                                                        f"{mean_of_means:.3f}",
                                                        fw=600,
                                                        c="blue",
                                                    ),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Std Dev", size="xs", c="dimmed"),
                                                    dmc.Text(
                                                        f"{std_of_means:.3f}",
                                                        fw=600,
                                                        c="blue",
                                                    ),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text("Theory", fw=500, size="sm", mb="xs", c="dimmed"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("SE(x̄)", size="xs", c="dimmed"),
                                                    dmc.Text(
                                                        f"{theoretical_std:.3f}",
                                                        fw=600,
                                                        c="green",
                                                    ),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Error", size="xs", c="dimmed"),
                                                    dmc.Text(
                                                        f"{abs(std_of_means - theoretical_std):.3f}",
                                                        fw=600,
                                                    ),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Normality Assessment",
                        color="green" if shapiro_p > 0.05 else "yellow",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"The sampling distribution of means {'appears' if shapiro_p > 0.05 else 'may not be fully'} "
                            f"normally distributed (p = {shapiro_p:.4f}). "
                            f"Standard error: observed = {std_of_means:.3f}, theoretical = {theoretical_std:.3f}. "
                            f"{'Excellent' if abs(std_of_means - theoretical_std) < 0.1 else 'Good'} agreement with theory.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create visualizations
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                "Population Distribution",
                "Sampling Distribution of Means",
            ),
            vertical_spacing=0.15,
            row_heights=[0.4, 0.6],
        )

        # Population histogram (sample for display)
        pop_sample = np.random.choice(population, size=min(10000, len(population)), replace=False)
        fig.add_trace(
            go.Histogram(
                x=pop_sample,
                name="Population",
                marker={"color": "#868e96"},
                nbinsx=50,
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Sampling distribution histogram
        fig.add_trace(
            go.Histogram(
                x=sample_means_array,
                name="Sample Means",
                marker={"color": "#1c7ed6", "opacity": 0.7},
                nbinsx=50,
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Overlay normal distribution on sampling distribution
        x_range = np.linspace(sample_means_array.min(), sample_means_array.max(), 200)
        normal_pdf = stats.norm.pdf(x_range, mean_of_means, std_of_means)
        # Scale to match histogram
        _hist_counts, _ = np.histogram(sample_means_array, bins=50)
        bin_width = (sample_means_array.max() - sample_means_array.min()) / 50
        scale_factor = len(sample_means_array) * bin_width

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=normal_pdf * scale_factor,
                name="Normal Distribution",
                mode="lines",
                line={"color": "red", "width": 2},
                showlegend=True,
            ),
            row=2,
            col=1,
        )

        # Add vertical lines for means
        fig.add_vline(
            x=pop_mean,
            line={"color": "red", "dash": "dash", "width": 2},
            annotation_text=f"μ = {pop_mean:.2f}",
            row=1,
            col=1,
        )

        fig.add_vline(
            x=mean_of_means,
            line={"color": "red", "dash": "dash", "width": 2},
            annotation_text=f"x̄ = {mean_of_means:.2f}",
            row=2,
            col=1,
        )

        fig.update_xaxes(title_text="Value", row=1, col=1)
        fig.update_xaxes(title_text="Sample Mean", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)

        fig.update_layout(
            height=700,
            template="plotly_white",
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        )

        return stats_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )

def register_callbacks(app: object) -> None:
    """Register all callbacks for the basics plugin.

    Args:
        app: The Dash application instance.

    Note:
        All callbacks in this module are automatically registered when imported
        due to the @callback decorator. This function exists for compatibility
        with the plugin system but does not need to do anything explicitly.
    """
    # Callbacks are auto-registered via @callback decorators
    pass
