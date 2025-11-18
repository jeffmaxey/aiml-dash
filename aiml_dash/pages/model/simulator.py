"""
Simulator Page
==============

Run Monte Carlo simulations for scenario analysis and risk assessment.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import numpy as np
import plotly.graph_objects as go

from components.common import create_page_header


def layout():
    """Create the simulator page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Simulate",
                "Run Monte Carlo simulations to model uncertainty and risk. Define variables with distributions and simulate outcomes.",
                icon="carbon:chart-scatter",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Simulation Setup", order=4),
                                        dmc.NumberInput(
                                            id="sim-iterations",
                                            label="Number of Simulations",
                                            value=10000,
                                            min=100,
                                            max=100000,
                                            step=1000,
                                        ),
                                        dmc.NumberInput(
                                            id="sim-seed",
                                            label="Random Seed",
                                            value=1234,
                                            min=0,
                                            step=1,
                                        ),
                                        dmc.Divider(
                                            label="Variables",
                                            labelPosition="center",
                                        ),
                                        dmc.Textarea(
                                            id="sim-formula",
                                            label="Simulation Formula",
                                            description="Enter Python expression (e.g., revenue - cost)",
                                            placeholder="revenue * units - fixed_cost - variable_cost * units",
                                            minRows=3,
                                        ),
                                        dmc.Divider(
                                            label="Define Variables",
                                            labelPosition="center",
                                        ),
                                        dmc.TextInput(
                                            id="sim-var-name",
                                            label="Variable Name",
                                            placeholder="e.g., revenue",
                                        ),
                                        dmc.Select(
                                            id="sim-var-dist",
                                            label="Distribution",
                                            data=[
                                                {
                                                    "label": "Normal",
                                                    "value": "normal",
                                                },
                                                {
                                                    "label": "Uniform",
                                                    "value": "uniform",
                                                },
                                                {
                                                    "label": "Triangular",
                                                    "value": "triangular",
                                                },
                                                {
                                                    "label": "Constant",
                                                    "value": "constant",
                                                },
                                                {
                                                    "label": "Log-Normal",
                                                    "value": "lognormal",
                                                },
                                            ],
                                            value="normal",
                                        ),
                                        html.Div(id="sim-var-params"),
                                        dmc.Group([
                                            dmc.Button(
                                                "Add Variable",
                                                id="sim-add-var-btn",
                                                leftSection=DashIconify(icon="carbon:add", width=16),
                                                variant="light",
                                                size="sm",
                                            ),
                                            dmc.Button(
                                                "Clear All",
                                                id="sim-clear-vars-btn",
                                                leftSection=DashIconify(
                                                    icon="carbon:trash-can",
                                                    width=16,
                                                ),
                                                variant="light",
                                                color="red",
                                                size="sm",
                                            ),
                                        ]),
                                        dmc.Textarea(
                                            id="sim-vars-display",
                                            label="Current Variables",
                                            value="",
                                            minRows=4,
                                            readOnly=True,
                                        ),
                                        dmc.Button(
                                            "Run Simulation",
                                            id="sim-run-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
                                        ),
                                    ],
                                    gap="sm",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                # Right panel
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Distribution",
                                        value="distribution",
                                        leftSection=DashIconify(icon="carbon:chart-histogram"),
                                    ),
                                    dmc.TabsTab(
                                        "Percentiles",
                                        value="percentiles",
                                        leftSection=DashIconify(icon="carbon:chart-area"),
                                    ),
                                    dmc.TabsTab(
                                        "Statistics",
                                        value="statistics",
                                        leftSection=DashIconify(icon="carbon:table"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="sim-summary"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="sim-distribution-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="distribution",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="sim-percentiles-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="percentiles",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="sim-statistics"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="statistics",
                                ),
                            ],
                            value="summary",
                            id="sim-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="sim-vars-store", data=[]),
            dcc.Store(id="sim-results-store"),
            dcc.Download(id="sim-download"),
            html.Div(id="sim-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("sim-var-params", "children"),
    Input("sim-var-dist", "value"),
)
def update_param_inputs(dist_type):
    """Update parameter inputs based on distribution type."""
    if dist_type == "normal":
        return dmc.Stack(
            [
                dmc.NumberInput(id="sim-param-1", label="Mean", value=100, step=1),
                dmc.NumberInput(id="sim-param-2", label="Std Dev", value=10, step=1, min=0),
            ],
            gap="xs",
        )
    elif dist_type == "uniform":
        return dmc.Stack(
            [
                dmc.NumberInput(id="sim-param-1", label="Min", value=0, step=1),
                dmc.NumberInput(id="sim-param-2", label="Max", value=100, step=1),
            ],
            gap="xs",
        )
    elif dist_type == "triangular":
        return dmc.Stack(
            [
                dmc.NumberInput(id="sim-param-1", label="Min", value=0, step=1),
                dmc.NumberInput(id="sim-param-2", label="Mode", value=50, step=1),
                dmc.NumberInput(id="sim-param-3", label="Max", value=100, step=1),
            ],
            gap="xs",
        )
    elif dist_type == "lognormal":
        return dmc.Stack(
            [
                dmc.NumberInput(id="sim-param-1", label="Mean", value=100, step=1),
                dmc.NumberInput(id="sim-param-2", label="Std Dev", value=10, step=1, min=0),
            ],
            gap="xs",
        )
    else:  # constant
        return dmc.NumberInput(id="sim-param-1", label="Value", value=100, step=1)


@callback(
    [Output("sim-vars-store", "data"), Output("sim-vars-display", "value")],
    [Input("sim-add-var-btn", "n_clicks"), Input("sim-clear-vars-btn", "n_clicks")],
    [
        State("sim-var-name", "value"),
        State("sim-var-dist", "value"),
        State("sim-param-1", "value"),
        State("sim-param-2", "value"),
        State("sim-param-3", "value"),
        State("sim-vars-store", "data"),
    ],
    prevent_initial_call=True,
)
def manage_variables(add_clicks, clear_clicks, var_name, dist, p1, p2, p3, vars_data):
    """Add or clear variables."""
    if not vars_data:
        vars_data = []

    triggered_id = ctx.triggered_id

    if triggered_id == "sim-clear-vars-btn":
        return [], ""

    if triggered_id == "sim-add-var-btn" and var_name:
        # Add new variable
        var_def = {
            "name": var_name,
            "dist": dist,
            "params": [p1, p2, p3] if p3 is not None else [p1, p2] if p2 is not None else [p1],
        }
        vars_data.append(var_def)

        # Update display
        display_text = "\n".join([f"{v['name']}: {v['dist']}({', '.join(map(str, v['params']))})" for v in vars_data])

        return vars_data, display_text

    return vars_data, ""


@callback(
    [
        Output("sim-summary", "children"),
        Output("sim-distribution-plot", "figure"),
        Output("sim-percentiles-plot", "figure"),
        Output("sim-statistics", "children"),
        Output("sim-results-store", "data"),
        Output("sim-notification", "children"),
    ],
    Input("sim-run-btn", "n_clicks"),
    [
        State("sim-iterations", "value"),
        State("sim-seed", "value"),
        State("sim-formula", "value"),
        State("sim-vars-store", "data"),
    ],
    prevent_initial_call=True,
)
def run_simulation(n_clicks, n_iter, seed, formula, vars_data):
    """Run Monte Carlo simulation."""
    if not formula or not vars_data:
        return (
            dmc.Text("Please define formula and variables.", c="red"),
            {},
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message="Missing formula or variables",
                color="red",
                action="show",
            ),
        )

    try:
        # Set random seed
        np.random.seed(seed)

        # Generate samples for each variable
        samples = {}
        for var in vars_data:
            name = var["name"]
            dist = var["dist"]
            params = var["params"]

            if dist == "normal":
                samples[name] = np.random.normal(params[0], params[1], n_iter)
            elif dist == "uniform":
                samples[name] = np.random.uniform(params[0], params[1], n_iter)
            elif dist == "triangular":
                samples[name] = np.random.triangular(params[0], params[1], params[2], n_iter)
            elif dist == "lognormal":
                samples[name] = np.random.lognormal(np.log(params[0]), params[1] / params[0], n_iter)
            else:  # constant
                samples[name] = np.full(n_iter, params[0])

        # Evaluate formula
        results = eval(formula, {"__builtins__": {}}, samples)

        # Calculate statistics
        mean = np.mean(results)
        median = np.median(results)
        std = np.std(results)
        p5 = np.percentile(results, 5)
        p95 = np.percentile(results, 95)
        minimum = np.min(results)
        maximum = np.max(results)

        # Summary
        summary = dmc.Stack(
            [
                dmc.Text("Simulation Results", fw=600, size="xl"),
                dmc.Divider(),
                dmc.Text(f"Mean: {mean:,.2f}", size="lg"),
                dmc.Text(f"Median: {median:,.2f}"),
                dmc.Text(f"Std Dev: {std:,.2f}"),
                dmc.Divider(),
                dmc.Text(f"5th Percentile: {p5:,.2f}", c="red"),
                dmc.Text(f"95th Percentile: {p95:,.2f}", c="green"),
                dmc.Divider(),
                dmc.Text(f"Min: {minimum:,.2f}"),
                dmc.Text(f"Max: {maximum:,.2f}"),
            ],
            gap="xs",
        )

        # Distribution plot
        dist_fig = go.Figure()
        dist_fig.add_trace(
            go.Histogram(
                x=results,
                nbinsx=50,
                name="Distribution",
            )
        )
        dist_fig.add_vline(x=mean, line_dash="dash", line_color="red", annotation_text="Mean")
        dist_fig.add_vline(x=median, line_dash="dash", line_color="green", annotation_text="Median")
        dist_fig.update_layout(
            title="Distribution of Simulated Results",
            xaxis_title="Value",
            yaxis_title="Frequency",
        )

        # Percentiles plot
        percentiles = np.arange(1, 100)
        percentile_values = np.percentile(results, percentiles)

        percentiles_fig = go.Figure()
        percentiles_fig.add_trace(
            go.Scatter(
                x=percentiles,
                y=percentile_values,
                mode="lines",
                fill="tozeroy",
                name="Percentiles",
            )
        )
        percentiles_fig.add_hline(y=mean, line_dash="dash", line_color="red", annotation_text="Mean")
        percentiles_fig.update_layout(
            title="Cumulative Percentiles",
            xaxis_title="Percentile",
            yaxis_title="Value",
        )

        # Statistics table
        stats_data = [
            {"Statistic": "Mean", "Value": f"{mean:,.2f}"},
            {"Statistic": "Median", "Value": f"{median:,.2f}"},
            {"Statistic": "Std Dev", "Value": f"{std:,.2f}"},
            {"Statistic": "Min", "Value": f"{minimum:,.2f}"},
            {"Statistic": "Max", "Value": f"{maximum:,.2f}"},
            {"Statistic": "5th Percentile", "Value": f"{p5:,.2f}"},
            {
                "Statistic": "25th Percentile",
                "Value": f"{np.percentile(results, 25):,.2f}",
            },
            {
                "Statistic": "75th Percentile",
                "Value": f"{np.percentile(results, 75):,.2f}",
            },
            {"Statistic": "95th Percentile", "Value": f"{p95:,.2f}"},
        ]

        statistics = dag.AgGrid(
            rowData=stats_data,
            columnDefs=[
                {"field": "Statistic", "flex": 1},
                {"field": "Value", "flex": 1},
            ],
            defaultColDef={"sortable": False},
            style={"height": "400px"},
        )

        return (
            summary,
            dist_fig,
            percentiles_fig,
            statistics,
            {"results": results.tolist()},
            dmc.Notification(
                title="Success",
                message=f"Simulation complete ({n_iter:,} iterations)",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {str(e)}", c="red"),
            {},
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )
