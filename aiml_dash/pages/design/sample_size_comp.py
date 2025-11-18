"""
Sample Size Comparison Page
===========================

Compare sample sizes across different scenarios and parameters.
"""

from dash import dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import numpy as np

from components.common import create_page_header


def layout():
    """Create the Sample Size Comparison page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Sample Size Comparison",
                "Compare required sample sizes across different effect sizes, power levels, and significance levels.",
                icon="carbon:comparison",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Select(
                                            id="ssc-test-type",
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
                                            ],
                                        ),
                                        dmc.Text("Effect size range", size="sm", fw=500),
                                        dmc.Group(
                                            [
                                                dmc.NumberInput(
                                                    id="ssc-effect-min",
                                                    label="Min",
                                                    value=0.2,
                                                    min=0.01,
                                                    step=0.1,
                                                    style={"flex": 1},
                                                ),
                                                dmc.NumberInput(
                                                    id="ssc-effect-max",
                                                    label="Max",
                                                    value=0.8,
                                                    min=0.01,
                                                    step=0.1,
                                                    style={"flex": 1},
                                                ),
                                            ],
                                            grow=True,
                                        ),
                                        dmc.MultiSelect(
                                            id="ssc-power-levels",
                                            label="Power levels to compare",
                                            value=["0.80", "0.90"],
                                            data=[
                                                {"label": "0.70", "value": "0.70"},
                                                {"label": "0.80", "value": "0.80"},
                                                {"label": "0.90", "value": "0.90"},
                                                {"label": "0.95", "value": "0.95"},
                                            ],
                                        ),
                                        dmc.NumberInput(
                                            id="ssc-alpha",
                                            label="Significance level (α)",
                                            value=2.0,
                                            min=0.1,
                                            max=5.0,
                                            step=0.1,
                                            decimalScale=3,
                                        ),
                                        dmc.Button(
                                            "Compare",
                                            id="ssc-compare",
                                            leftSection=DashIconify(icon="carbon:chart-line", width=20),
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
                                        dmc.Title("Sample Size Comparison Chart", order=4),
                                        dcc.Graph(
                                            id="ssc-chart",
                                            style={"height": "500px"},
                                        ),
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
    Output("ssc-chart", "figure"),
    Input("ssc-compare", "n_clicks"),
    State("ssc-test-type", "value"),
    State("ssc-effect-min", "value"),
    State("ssc-effect-max", "value"),
    State("ssc-power-levels", "value"),
    State("ssc-alpha", "value"),
    prevent_initial_call=True,
)
def compare_sample_sizes(n_clicks, test_type, effect_min, effect_max, power_levels, alpha):
    """Compare sample sizes across different scenarios."""
    try:
        # Generate effect size range
        effect_sizes = np.linspace(effect_min, effect_max, 20)

        # Create figure
        fig = go.Figure()

        # Calculate sample sizes for each power level
        for power_str in power_levels:
            power = float(power_str)
            sample_sizes = []

            for effect in effect_sizes:
                # Calculate sample size
                if test_type == "mean":
                    # t-test for one mean
                    from scipy import stats

                    z_alpha = stats.norm.ppf(1 - alpha / 2)
                    z_beta = stats.norm.ppf(power)
                    n = ((z_alpha + z_beta) / effect) ** 2

                elif test_type == "proportion":
                    # z-test for one proportion
                    p0 = 0.5
                    p1 = p0 + effect
                    z_alpha = stats.norm.ppf(1 - alpha / 2)
                    z_beta = stats.norm.ppf(power)
                    n = ((z_alpha * np.sqrt(p0 * (1 - p0)) + z_beta * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2

                sample_sizes.append(int(np.ceil(n)))

            # Add trace
            fig.add_trace(
                go.Scatter(
                    x=effect_sizes,
                    y=sample_sizes,
                    mode="lines+markers",
                    name=f"Power = {power:.2f}",
                    line=dict(width=2),
                    marker=dict(size=6),
                )
            )

        # Update layout
        fig.update_layout(
            title="Sample Size Comparison",
            xaxis_title="Effect Size",
            yaxis_title="Required Sample Size",
            hovermode="x unified",
            template="plotly_white",
            showlegend=True,
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
            margin=dict(l=50, r=50, t=50, b=50),
        )

        return fig

    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
        )
        return fig
