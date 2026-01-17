"""
Compare Proportions Test Page
Two-sample test for comparing proportions between independent groups.
"""

from dash import dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from aiml_dash.managers.app_manager import app_manager
from aiml_dash.components.common import (
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
    """Create layout for compare proportions test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            create_page_header(
                "Compare Proportions Test",
                "Test whether proportions differ significantly between two independent groups.",
                icon="mdi:percent-box-outline",
            ),
            dmc.Divider(),
            # Main Content
            create_two_column_layout(
                # Left Column - Controls
                create_control_card(
                    [
                        dmc.Text("Data Selection", fw=500, size="lg"),
                        create_dataset_selector(
                            selector_id="compare-props-dataset",
                            label="Select Dataset",
                        ),
                        dmc.Select(
                            id="compare-props-variable",
                            label="Variable",
                            placeholder="Choose variable...",
                            description="Binary variable to test",
                            data=[],
                            searchable=True,
                        ),
                        dmc.Select(
                            id="compare-props-success",
                            label="Success Level",
                            placeholder="Choose success level...",
                            description="Level representing 'success'",
                            data=[],
                            searchable=True,
                        ),
                        dmc.Select(
                            id="compare-props-group",
                            label="Group Variable",
                            placeholder="Choose grouping variable...",
                            description="Variable with exactly 2 groups",
                            data=[],
                            searchable=True,
                        ),
                        dmc.Divider(),
                        dmc.Text("Test Parameters", fw=500, size="lg"),
                        dmc.Stack(
                            gap=5,
                            children=[
                                dmc.Text(
                                    "Alternative Hypothesis",
                                    size="sm",
                                    fw=500,
                                ),
                                dmc.SegmentedControl(
                                    id="compare-props-alternative",
                                    data=[
                                        {
                                            "label": "Two-sided",
                                            "value": "two-sided",
                                        },
                                        {
                                            "label": "Greater",
                                            "value": "greater",
                                        },
                                        {
                                            "label": "Less",
                                            "value": "less",
                                        },
                                    ],
                                    value="two-sided",
                                    fullWidth=True,
                                ),
                            ],
                        ),
                        dmc.NumberInput(
                            id="compare-props-confidence",
                            label="Confidence Level",
                            description="For confidence interval",
                            value=0.95,
                            min=0.5,
                            max=0.999,
                            step=0.01,
                            decimalScale=3,
                        ),
                        create_action_button(
                            button_id="compare-props-run",
                            label="Run Test",
                            icon="mdi:play",
                        ),
                    ],
                ),
                # Right Column - Results
                dmc.Stack(
                    gap="md",
                    children=[
                        dmc.Paper(
                            id="compare-props-results",
                            p="md",
                            withBorder=True,
                            children=[
                                dmc.Text(
                                    "Configure test parameters and click 'Run Test' to see results",
                                    c="dimmed",
                                    ta="center",
                                    py="xl",
                                ),
                            ],
                        ),
                        dmc.Paper(
                            id="compare-props-plot-container",
                            p="md",
                            withBorder=True,
                            style={"display": "none"},
                            children=[
                                dcc.Graph(
                                    id="compare-props-plot",
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
    Output("compare-props-dataset", "data"),
    Input("compare-props-dataset", "id"),
)
def update_datasets(_):
    """Populate dataset dropdown."""
    datasets = app_manager.data_manager.get_dataset_names()
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

    df = app_manager.data_manager.get_dataset(dataset)
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

    df = app_manager.data_manager.get_dataset(dataset)

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
        df = app_manager.data_manager.get_dataset(dataset)

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
                marker=dict(color=["#1c7ed6", "#15aabf"]),
                text=[f"{p1:.4f}", f"{p2:.4f}"],
                textposition="outside",
                error_y=dict(
                    type="data",
                    array=[
                        stats.norm.ppf(1 - (1 - confidence) / 2) * np.sqrt(p1 * (1 - p1) / n1),
                        stats.norm.ppf(1 - (1 - confidence) / 2) * np.sqrt(p2 * (1 - p2) / n2),
                    ],
                    visible=True,
                    color="gray",
                ),
            )
        )

        fig.update_layout(
            title=f"Proportion Comparison by {group_var}",
            yaxis_title="Proportion",
            yaxis=dict(range=[0, min(1, max(p1, p2) * 1.3)]),
            template="plotly_white",
            height=400,
            showlegend=False,
        )

        return results_content, {"display": "block"}, fig

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
            {},
        )
