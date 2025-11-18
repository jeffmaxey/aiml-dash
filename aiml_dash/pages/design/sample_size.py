"""
Sample Size Page
================

Calculate required sample size for different types of tests.
"""

from dash import html, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
from scipy import stats

from components.common import create_page_header


def layout():
    """Create the Sample Size page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Sample Size Calculation",
                "Calculate the required sample size for your study based on statistical power, effect size, and significance level.",
                icon="carbon:calculator",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Select(
                                            id="ss-test-type",
                                            label="Test type",
                                            value="mean",
                                            data=[
                                                {
                                                    "label": "Mean (t-test)",
                                                    "value": "mean",
                                                },
                                                {
                                                    "label": "Proportion (z-test)",
                                                    "value": "proportion",
                                                },
                                                {
                                                    "label": "Comparison of means",
                                                    "value": "compare_means",
                                                },
                                                {
                                                    "label": "Comparison of proportions",
                                                    "value": "compare_props",
                                                },
                                            ],
                                        ),
                                        dmc.NumberInput(
                                            id="ss-effect-size",
                                            label="Effect size",
                                            description="Cohen's d for means, difference for proportions",
                                            value=0.5,
                                            min=0.01,
                                            step=0.01,
                                            precision=2,
                                        ),
                                        dmc.NumberInput(
                                            id="ss-power",
                                            label="Statistical power (1 - β)",
                                            value=0.80,
                                            min=0.5,
                                            max=0.99,
                                            step=0.01,
                                            decimalScale=2,
                                        ),
                                        dmc.NumberInput(
                                            id="ss-alpha",
                                            label="Significance level (α)",
                                            value=0.5,
                                            min=0.01,
                                            max=2.0,
                                            step=0.1,
                                            decimalScale=3,
                                        ),
                                        dmc.Select(
                                            id="ss-alternative",
                                            label="Alternative hypothesis",
                                            value="two-sided",
                                            data=[
                                                {
                                                    "label": "Two-sided",
                                                    "value": "two-sided",
                                                },
                                                {
                                                    "label": "Greater than",
                                                    "value": "greater",
                                                },
                                                {
                                                    "label": "Less than",
                                                    "value": "less",
                                                },
                                            ],
                                        ),
                                        dmc.Button(
                                            "Calculate",
                                            id="ss-calculate",
                                            leftSection=DashIconify(icon="carbon:calculator", width=20),
                                            fullWidth=True,
                                            color="blue",
                                        ),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Sample Size Results", order=4),
                                        html.Div(id="ss-results"),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
        ],
        fluid=True,
    )


# Callbacks


@callback(
    Output("ss-results", "children"),
    Input("ss-calculate", "n_clicks"),
    State("ss-test-type", "value"),
    State("ss-effect-size", "value"),
    State("ss-power", "value"),
    State("ss-alpha", "value"),
    State("ss-alternative", "value"),
    prevent_initial_call=True,
)
def calculate_sample_size(n_clicks, test_type, effect_size, power, alpha, alternative):
    """Calculate required sample size."""
    try:
        # Determine test type and calculate sample size
        if test_type == "mean":
            # t-test for one mean
            # Using power analysis formula for t-test
            z_alpha = stats.norm.ppf(1 - alpha / 2 if alternative == "two-sided" else 1 - alpha)
            z_beta = stats.norm.ppf(power)
            n = ((z_alpha + z_beta) / effect_size) ** 2
            n = int(np.ceil(n))
            test_name = "One-sample t-test"

        elif test_type == "proportion":
            # z-test for one proportion
            # Assume p0=0.5 for generic calculation
            p0 = 0.5
            p1 = p0 + effect_size
            z_alpha = stats.norm.ppf(1 - alpha / 2 if alternative == "two-sided" else 1 - alpha)
            z_beta = stats.norm.ppf(power)
            n = ((z_alpha * np.sqrt(p0 * (1 - p0)) + z_beta * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2
            n = int(np.ceil(n))
            test_name = "One-sample proportion test"

        elif test_type == "compare_means":
            # Two-sample t-test
            z_alpha = stats.norm.ppf(1 - alpha / 2 if alternative == "two-sided" else 1 - alpha)
            z_beta = stats.norm.ppf(power)
            n_per_group = 2 * ((z_alpha + z_beta) / effect_size) ** 2
            n_per_group = int(np.ceil(n_per_group))
            n = n_per_group * 2
            test_name = "Two-sample t-test"

        elif test_type == "compare_props":
            # Two-sample proportion test
            p0 = 0.5
            p1 = p0 + effect_size
            p_avg = (p0 + p1) / 2
            z_alpha = stats.norm.ppf(1 - alpha / 2 if alternative == "two-sided" else 1 - alpha)
            z_beta = stats.norm.ppf(power)
            n_per_group = (
                2
                * (
                    (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + z_beta * np.sqrt(p0 * (1 - p0) + p1 * (1 - p1)))
                    / (p1 - p0)
                )
                ** 2
            )
            n_per_group = int(np.ceil(n_per_group))
            n = n_per_group * 2
            test_name = "Two-sample proportion test"

        else:
            return dmc.Alert(
                "Unknown test type",
                color="red",
                icon=DashIconify(icon="carbon:warning"),
            )

        # Create results display
        results = dmc.Stack(
            [
                dmc.Alert(
                    "Sample size calculation complete",
                    color="green",
                    icon=DashIconify(icon="carbon:checkmark"),
                ),
                dmc.Card(
                    [
                        dmc.Stack(
                            [
                                dmc.Title("Required Sample Size", order=2),
                                dmc.Text(
                                    f"{n} observations",
                                    size="xl",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "var(--mantine-color-blue-6)",
                                    },
                                ),
                            ],
                            gap="xs",
                            align="center",
                        )
                    ],
                    withBorder=True,
                    p="lg",
                    radius="md",
                    style={"background": "var(--mantine-color-blue-0)"},
                ),
                dmc.SimpleGrid(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "Test type",
                                            size="sm",
                                            style={"color": "gray"},
                                        ),
                                        dmc.Text(test_name),
                                    ],
                                    gap=0,
                                )
                            ],
                            withBorder=True,
                            p="sm",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "Effect size",
                                            size="sm",
                                            style={"color": "gray"},
                                        ),
                                        dmc.Text(f"{effect_size:.3f}"),
                                    ],
                                    gap=0,
                                )
                            ],
                            withBorder=True,
                            p="sm",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "Statistical power",
                                            size="sm",
                                            style={"color": "gray"},
                                        ),
                                        dmc.Text(f"{power:.2f}"),
                                    ],
                                    gap=0,
                                )
                            ],
                            withBorder=True,
                            p="sm",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "Significance level",
                                            size="sm",
                                            style={"color": "gray"},
                                        ),
                                        dmc.Text(f"{alpha:.3f}"),
                                    ],
                                    gap=0,
                                )
                            ],
                            withBorder=True,
                            p="sm",
                        ),
                    ],
                    cols=4,
                ),
                dmc.Alert(
                    dmc.Stack(
                        [
                            dmc.Text("Interpretation:", style={"fontWeight": "bold"}),
                            dmc.Text(
                                f"To detect an effect size of {effect_size:.2f} with {power * 100:.0f}% power at α={alpha:.3f}, you need a sample size of {n} observations."
                            ),
                        ],
                        gap="xs",
                    ),
                    title="Sample Size Interpretation",
                    color="blue",
                    icon=DashIconify(icon="carbon:information"),
                ),
            ],
            gap="md",
        )

        return results

    except Exception as e:
        return dmc.Alert(
            f"Error calculating sample size: {str(e)}",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
