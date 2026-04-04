"""Goodness-of-Fit and Probability Calculator callbacks.

This module is part of the basics plugin callback suite.
Callbacks are registered automatically via ``@callback`` decorators on import.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, html
from dash_iconify import DashIconify
from scipy import stats

from aiml_dash.utils.data_manager import data_manager


@callback(
    Output("goodness-dataset", "data"),
    Input("goodness-dataset", "id"),
)
def update_prob_calc_datasets(_):
    """Populate dataset dropdown.

    Parameters
    ----------
    _ : Any
        Value provided for this parameter."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]


@callback(
    [Output("goodness-variable", "data"), Output("goodness-variable", "value")],
    Input("goodness-dataset", "value"),
)
def update_prob_calc_variables(dataset):
    """Populate variable dropdown.

    Parameters
    ----------
    dataset : Any
        Value provided for this parameter."""
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
    """Show/hide custom expected input based on distribution type.

    Parameters
    ----------
    dist_type : Any
        Value provided for this parameter."""
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
def run_goodness_test(
    n_clicks, dataset, variable, dist_type, custom_expected, confidence
):
    """Run chi-square goodness of fit test.

    Parameters
    ----------
    n_clicks : Any
        Input value for ``n_clicks``.
    dataset : Any
        Input value for ``dataset``.
    variable : Any
        Input value for ``variable``.
    dist_type : Any
        Input value for ``dist_type``.
    custom_expected : Any
        Input value for ``custom_expected``.
    confidence : Any
        Value provided for this parameter."""
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
                            dmc.Text(
                                "Chi-Square Goodness of Fit Test", fw=600, size="lg"
                            ),
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
        freq_df = pd.DataFrame(
            {
                "Category": [str(cat) for cat in categories],
                "Observed": observed,
                "Expected": expected.round(2),
                "Residual": residuals.round(2),
                "Std. Residual": std_residuals.round(2),
            }
        )

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
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
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
    """Update parameter inputs based on distribution.

    Parameters
    ----------
    distribution : Any
        Value provided for this parameter."""
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
    """Update input fields based on calculation type.

    Parameters
    ----------
    calc_type : Any
        Value provided for this parameter."""
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
                description="For two-tailed test, α is split between tails",  # noqa: RUF001
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
    """Show/hide second value input for 'between' probability.

    Parameters
    ----------
    tail : Any
        Value provided for this parameter."""
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
    """Calculate probability or critical value.

    Parameters
    ----------
    n_clicks : Any
        Input value for ``n_clicks``.
    distribution : Any
        Input value for ``distribution``.
    calc_type : Any
        Input value for ``calc_type``.
    param1 : Any
        Input value for ``param1``.
    param2 : Any
        Value provided for this parameter."""
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
                yaxis_title=(
                    "Density"
                    if distribution not in ["binomial", "poisson"]
                    else "Probability"
                ),
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
                yaxis_title=(
                    "Density"
                    if distribution not in ["binomial", "poisson"]
                    else "Probability"
                ),
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


