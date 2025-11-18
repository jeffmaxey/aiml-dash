"""
Explore Page
============

Statistical exploration and summary statistics with grouping.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag

from components.common import create_page_header, create_filter_section
from utils.data_manager import data_manager
from utils.statistics import STAT_FUNCTIONS, explore


def layout():
    """Create the Explore page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Explore Data",
                "Calculate summary statistics and explore data patterns. Group by variables and apply multiple statistical functions.",
                icon="carbon:explore",
            ),
            create_filter_section(),
            dmc.Grid([
                # Left panel - controls
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.MultiSelect(
                                            id="explore-vars",
                                            label="Variables to Explore",
                                            placeholder="Select variables...",
                                            description="Select numeric or categorical variables",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.MultiSelect(
                                            id="explore-byvar",
                                            label="Group By (optional)",
                                            placeholder="Select grouping variables...",
                                            description="Group statistics by these variables",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.MultiSelect(
                                            id="explore-functions",
                                            label="Functions to Apply",
                                            value=["mean", "sd", "min", "max"],
                                            data=[
                                                {"label": v[1], "value": k}
                                                for k, v in STAT_FUNCTIONS.items()
                                                if k
                                                in [
                                                    "n_obs",
                                                    "n_missing",
                                                    "mean",
                                                    "median",
                                                    "sd",
                                                    "min",
                                                    "max",
                                                    "p25",
                                                    "p75",
                                                ]
                                            ],  # type: ignore
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.Button(
                                            "Calculate Statistics",
                                            id="explore-calculate-btn",
                                            leftSection=DashIconify(icon="carbon:calculator"),
                                            fullWidth=True,
                                        ),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=4,
                ),
                # Right panel - results
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text("Summary Statistics", fw=600),
                                                dmc.Button(
                                                    "Export CSV",
                                                    id="explore-export-btn",
                                                    size="xs",
                                                    variant="light",
                                                    leftSection=DashIconify(
                                                        icon="carbon:download",
                                                        width=14,
                                                    ),
                                                ),
                                            ],
                                            justify="space-between",
                                        ),
                                        html.Div(id="explore-results"),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=8,
                ),
            ]),
            dcc.Download(id="explore-download"),
            html.Div(id="explore-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("explore-vars", "data"),
    Output("explore-byvar", "data"),
    Input("dataset-selector", "value"),
)
def update_explore_selectors(dataset_name):
    """Update variable selectors based on dataset."""
    if not dataset_name:
        return [], []

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return [], []

    # All columns for vars
    var_options = [{"label": col, "value": col} for col in df.columns]

    # Categorical/low-cardinality columns for grouping
    byvar_options = []
    for col in df.columns:
        # Include if categorical or low cardinality
        if df[col].dtype in ["object", "category"] or df[col].nunique() < 20:
            byvar_options.append({"label": col, "value": col})

    return var_options, byvar_options


@callback(
    Output("explore-results", "children"),
    Input("explore-calculate-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("explore-vars", "value"),
    State("explore-byvar", "value"),
    State("explore-functions", "value"),
    State("data-filter-input", "value"),
    prevent_initial_call=True,
)
def calculate_statistics(n_clicks, dataset_name, vars, byvar, functions, data_filter):
    """Calculate and display summary statistics."""
    if not n_clicks or not dataset_name or not vars or not functions:
        return dmc.Center(
            dmc.Text("Select variables and functions, then click Calculate", c="dimmed"),
            style={"height": "300px"},
        )

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Alert("Error loading dataset", color="red")

    try:
        # Calculate statistics
        result = explore(
            df,
            vars=vars,
            byvar=byvar if byvar else None,
            fun=functions,
            data_filter=data_filter,
        )

        if result.empty:
            return dmc.Alert("No results to display", color="yellow")

        # Format for display
        return dmc.Stack(
            [
                dmc.Text(
                    f"{len(result)} rows × {len(result.columns)} columns",
                    size="sm",
                    c="dimmed",
                ),
                dag.AgGrid(
                    rowData=result.to_dict("records"),
                    columnDefs=[
                        {
                            "field": col,
                            "type": "numericColumn" if result[col].dtype in ["int64", "float64"] else None,
                            "valueFormatter": {"function": "d3.format(',.4f')(params.value)"}
                            if result[col].dtype in ["int64", "float64"]
                            else None,
                            "filter": True,
                        }
                        for col in result.columns
                    ],
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "minWidth": 100,
                    },
                    className="ag-theme-alpine",
                    style={"height": "400px"},
                ),
            ],
            gap="sm",
        )

    except Exception as e:
        return dmc.Alert(
            f"Error calculating statistics: {str(e)}",
            title="Calculation Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )


@callback(
    Output("explore-download", "data"),
    Input("explore-export-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("explore-vars", "value"),
    State("explore-byvar", "value"),
    State("explore-functions", "value"),
    State("data-filter-input", "value"),
    prevent_initial_call=True,
)
def export_statistics(n_clicks, dataset_name, vars, byvar, functions, data_filter):
    """Export statistics to CSV."""
    if not n_clicks or not dataset_name or not vars or not functions:
        return dash.no_update

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dash.no_update

    try:
        result = explore(
            df,
            vars=vars,
            byvar=byvar if byvar else None,
            fun=functions,
            data_filter=data_filter,
        )
        return dcc.send_data_frame(result.to_csv, f"{dataset_name}_explore.csv", index=False)
    except:
        return dash.no_update
