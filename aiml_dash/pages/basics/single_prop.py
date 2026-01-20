"""
Single Proportion Test Page
Tests whether a sample proportion is significantly different from a hypothesized value.
"""

import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc
from dash_iconify import DashIconify
from scipy import stats
from utils.data_manager import data_manager

# ==============================================================================
# LAYOUT
# ==============================================================================


def layout():
    """Create layout for single proportion test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:percent", width=32),
                            dmc.Title("Single Proportion Test", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Test whether a sample proportion differs significantly from a hypothesized value",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Data Selection", fw=500, size="lg"),
                                            # Dataset selector
                                            dmc.Select(
                                                id="single-prop-dataset",
                                                label="Select Dataset",
                                                placeholder="Choose dataset...",
                                                data=[],
                                                searchable=True,
                                                clearable=False,
                                            ),
                                            # Variable selector
                                            dmc.Select(
                                                id="single-prop-variable",
                                                label="Variable",
                                                placeholder="Choose variable...",
                                                description="Select binary variable (0/1, TRUE/FALSE, Yes/No, etc.)",
                                                data=[],
                                                searchable=True,
                                            ),
                                            # Success level selector
                                            dmc.Select(
                                                id="single-prop-success",
                                                label="Success Level",
                                                placeholder="Choose success level...",
                                                description="Level representing 'success'",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Test Parameters", fw=500, size="lg"),
                                            # Comparison proportion
                                            dmc.NumberInput(
                                                id="single-prop-p0",
                                                label="Comparison Proportion (p₀)",
                                                description="Hypothesized population proportion",
                                                value=0.5,
                                                min=0,
                                                max=1,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            # Alternative hypothesis
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text(
                                                        "Alternative Hypothesis",
                                                        size="sm",
                                                        fw=500,
                                                    ),
                                                    dmc.SegmentedControl(
                                                        id="single-prop-alternative",
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
                                            # Confidence level
                                            dmc.NumberInput(
                                                id="single-prop-confidence",
                                                label="Confidence Level",
                                                description="For confidence interval",
                                                value=0.95,
                                                min=0.5,
                                                max=0.999,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            # Run test button
                                            dmc.Button(
                                                "Run Test",
                                                id="single-prop-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    # Results summary
                                    dmc.Paper(
                                        id="single-prop-results",
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
                                    # Visualization
                                    dmc.Paper(
                                        id="single-prop-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="single-prop-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================


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
