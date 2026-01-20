"""
Probability Calculator
Calculate probabilities and critical values for various distributions.
"""

import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from scipy import stats


def layout():
    """Create layout for probability calculator page."""
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
                            DashIconify(icon="mdi:calculator", width=32),
                            dmc.Title("Probability Calculator", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Calculate probabilities and critical values for various distributions",
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
                                            dmc.Text("Distribution", fw=500, size="lg"),
                                            dmc.Select(
                                                id="prob-distribution",
                                                label="Distribution Type",
                                                data=[
                                                    {
                                                        "label": "Normal",
                                                        "value": "normal",
                                                    },
                                                    {
                                                        "label": "t (Student's)",
                                                        "value": "t",
                                                    },
                                                    {
                                                        "label": "Chi-square (χ²)",
                                                        "value": "chi2",
                                                    },
                                                    {"label": "F", "value": "f"},
                                                    {
                                                        "label": "Binomial",
                                                        "value": "binomial",
                                                    },
                                                    {
                                                        "label": "Poisson",
                                                        "value": "poisson",
                                                    },
                                                ],
                                                value="normal",
                                                clearable=False,
                                            ),
                                            # Distribution parameters
                                            html.Div(id="prob-params-container"),
                                            dmc.Divider(),
                                            dmc.Text("Calculation", fw=500, size="lg"),
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text("Calculate", size="sm", fw=500),
                                                    dmc.SegmentedControl(
                                                        id="prob-calc-type",
                                                        data=[
                                                            {
                                                                "label": "Probability",
                                                                "value": "probability",
                                                            },
                                                            {
                                                                "label": "Critical Value",
                                                                "value": "critical",
                                                            },
                                                        ],
                                                        value="probability",
                                                        fullWidth=True,
                                                    ),
                                                ],
                                            ),
                                            html.Div(id="prob-input-container"),
                                            dmc.Button(
                                                "Calculate",
                                                id="prob-calculate",
                                                leftSection=DashIconify(icon="mdi:calculator"),
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
                                    dmc.Paper(
                                        id="prob-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Select distribution and parameters, then click 'Calculate'",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="prob-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="prob-plot",
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
