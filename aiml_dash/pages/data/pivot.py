"""
Pivot Page
==========

Create pivot tables with aggregations and chi-square tests.
"""

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import pandas as pd
from components.common import create_filter_section, create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from utils.data_manager import data_manager
from utils.statistics import chi_square_test


def layout():
    """Create the Pivot page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Pivot Tables",
                "Create pivot tables to summarize and cross-tabulate data. Perform chi-square tests for independence.",
                icon="carbon:data-reference",
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
                                            id="pivot-rows",
                                            label="Row Variables",
                                            placeholder="Select row variables...",
                                            description="Variables to use as rows",
                                            searchable=True,
                                        ),
                                        dmc.MultiSelect(
                                            id="pivot-cols",
                                            label="Column Variables (optional)",
                                            placeholder="Select column variables...",
                                            description="Variables to use as columns",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.Select(
                                            id="pivot-values",
                                            label="Values (optional)",
                                            placeholder="Select value variable...",
                                            description="Numeric variable to aggregate",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.Select(
                                            id="pivot-aggfunc",
                                            label="Aggregation Function",
                                            value="count",
                                            data=[
                                                {
                                                    "label": "Count",
                                                    "value": "count",
                                                },
                                                {"label": "Sum", "value": "sum"},
                                                {"label": "Mean", "value": "mean"},
                                                {
                                                    "label": "Median",
                                                    "value": "median",
                                                },
                                                {"label": "Min", "value": "min"},
                                                {"label": "Max", "value": "max"},
                                                {
                                                    "label": "Std Dev",
                                                    "value": "std",
                                                },
                                            ],
                                        ),
                                        dmc.Switch(
                                            id="pivot-margins",
                                            label="Show margins (totals)",
                                            checked=True,
                                        ),
                                        dmc.Switch(
                                            id="pivot-normalize",
                                            label="Normalize values",
                                            checked=False,
                                        ),
                                        dmc.Button(
                                            "Create Pivot Table",
                                            id="pivot-create-btn",
                                            leftSection=DashIconify(icon="carbon:table"),
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
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab("Pivot Table", value="table"),
                                    dmc.TabsTab("Chi-Square Test", value="chi2"),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Group(
                                                            [
                                                                dmc.Text(
                                                                    "Pivot Table",
                                                                    fw=600,
                                                                ),
                                                                dmc.Button(
                                                                    "Export CSV",
                                                                    id="pivot-export-btn",
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
                                                        html.Div(id="pivot-table-container"),
                                                    ],
                                                    gap="md",
                                                )
                                            ],
                                            withBorder=True,
                                            p="md",
                                        ),
                                    ],
                                    value="table",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="pivot-chi2-container"),
                                            ],
                                            withBorder=True,
                                            p="md",
                                        ),
                                    ],
                                    value="chi2",
                                ),
                            ],
                            value="table",
                        ),
                    ],
                    span=8,
                ),
            ]),
            dcc.Download(id="pivot-download"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("pivot-rows", "data"),
    Output("pivot-cols", "data"),
    Output("pivot-values", "data"),
    Input("dataset-selector", "value"),
)
def update_pivot_selectors(dataset_name):
    """Update variable selectors for pivot table."""
    if not dataset_name:
        return [], [], []

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return [], [], []

    # Categorical/low-cardinality for rows and columns
    categorical_vars = [
        {"label": col, "value": col}
        for col in df.columns
        if df[col].dtype in ["object", "category"] or df[col].nunique() < 50
    ]

    # Numeric for values
    numeric_vars = [{"label": col, "value": col} for col in df.columns if df[col].dtype in ["int64", "float64"]]

    return categorical_vars, categorical_vars, numeric_vars


@callback(
    Output("pivot-table-container", "children"),
    Output("pivot-chi2-container", "children"),
    Input("pivot-create-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("pivot-rows", "value"),
    State("pivot-cols", "value"),
    State("pivot-values", "value"),
    State("pivot-aggfunc", "value"),
    State("pivot-margins", "checked"),
    State("pivot-normalize", "checked"),
    State("data-filter-input", "value"),
    prevent_initial_call=True,
)
def create_pivot_table(n_clicks, dataset_name, rows, cols, values, aggfunc, margins, normalize, data_filter):
    """Create and display pivot table."""
    if not n_clicks or not dataset_name or not rows:
        empty_msg = dmc.Center(
            dmc.Text("Select row variables and click Create Pivot Table", c="dimmed"),
            style={"height": "400px"},
        )
        return empty_msg, empty_msg

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        error = dmc.Alert("Error loading dataset", color="red")
        return error, error

    # Apply filter
    if data_filter and data_filter.strip():
        try:
            df = df.query(data_filter)
        except:
            pass

    try:
        # If no values specified, use count
        if not values:
            # Create count pivot
            if cols:
                pivot = pd.crosstab(
                    [df[r] for r in rows],
                    [df[c] for c in cols],
                    margins=margins,
                    margins_name="Total",
                )
            else:
                pivot = df[rows].value_counts().reset_index()
                pivot.columns = list(rows) + ["count"]
        else:
            # Create aggregation pivot
            pivot = pd.pivot_table(
                df,
                index=rows,
                columns=cols if cols else None,
                values=values,
                aggfunc=aggfunc,
                margins=margins,
                margins_name="Total",
            )

        # Normalize if requested
        if normalize and not pivot.empty:
            pivot = pivot / pivot.sum().sum()

        # Reset index for display
        pivot_display = pivot.reset_index()

        # Format table
        table = dmc.Stack(
            [
                dmc.Text(
                    f"Pivot: {len(pivot_display)} rows × {len(pivot_display.columns)} columns",
                    size="sm",
                    c="dimmed",
                ),
                dag.AgGrid(
                    rowData=pivot_display.to_dict("records"),
                    columnDefs=[
                        {
                            "field": str(col),
                            "type": "numericColumn" if pivot_display[col].dtype in ["int64", "float64"] else None,
                            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
                            if pivot_display[col].dtype in ["int64", "float64"]
                            else None,
                            "filter": True,
                        }
                        for col in pivot_display.columns
                    ],
                    defaultColDef={"resizable": True, "sortable": True},
                    className="ag-theme-alpine",
                    style={"height": "500px"},
                ),
            ],
            gap="sm",
        )

        # Chi-square test (only for 2-way tables without aggregation)
        if cols and len(cols) == 1 and len(rows) == 1 and not values:
            chi2_results = chi_square_test(pivot.iloc[:-1, :-1] if margins else pivot)

            if "error" in chi2_results:
                chi2_display = dmc.Alert(chi2_results["error"], color="red")
            else:
                chi2_display = dmc.Stack(
                    [
                        dmc.Text("Chi-Square Test of Independence", fw=600, size="lg"),
                        dmc.Divider(),
                        dmc.SimpleGrid(
                            [
                                dmc.Card(
                                    [
                                        dmc.Text(
                                            "Chi-Square Statistic",
                                            size="sm",
                                            c="dimmed",
                                        ),
                                        dmc.Text(
                                            f"{chi2_results['chi2']:.4f}",
                                            size="xl",
                                            fw=700,
                                        ),
                                    ],
                                    withBorder=True,
                                    p="sm",
                                ),
                                dmc.Card(
                                    [
                                        dmc.Text("P-Value", size="sm", c="dimmed"),
                                        dmc.Text(
                                            f"{chi2_results['p_value']:.4f}",
                                            size="xl",
                                            fw=700,
                                        ),
                                    ],
                                    withBorder=True,
                                    p="sm",
                                ),
                                dmc.Card(
                                    [
                                        dmc.Text("Degrees of Freedom", size="sm", c="dimmed"),
                                        dmc.Text(f"{chi2_results['dof']}", size="xl", fw=700),
                                    ],
                                    withBorder=True,
                                    p="sm",
                                ),
                            ],
                            cols=3,
                        ),
                        dmc.Alert(
                            "Variables are statistically independent"
                            if chi2_results["p_value"] >= 0.05
                            else "Variables are statistically dependent",
                            title="Interpretation (α = 0.05)",
                            color="blue" if chi2_results["p_value"] >= 0.05 else "green",
                        ),
                    ],
                    gap="md",
                )
        else:
            chi2_display = dmc.Alert(
                "Chi-square test requires exactly 1 row variable and 1 column variable with count aggregation",
                color="yellow",
            )

        return table, chi2_display

    except Exception as e:
        error = dmc.Alert(
            f"Error creating pivot table: {e!s}",
            title="Pivot Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
        return error, error


@callback(
    Output("pivot-download", "data"),
    Input("pivot-export-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("pivot-rows", "value"),
    State("pivot-cols", "value"),
    State("pivot-values", "value"),
    State("pivot-aggfunc", "value"),
    State("pivot-margins", "checked"),
    State("pivot-normalize", "checked"),
    State("data-filter-input", "value"),
    prevent_initial_call=True,
)
def export_pivot(n_clicks, dataset_name, rows, cols, values, aggfunc, margins, normalize, data_filter):
    """Export pivot table to CSV."""
    if not n_clicks or not dataset_name or not rows:
        return dash.no_update

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dash.no_update

    # Apply filter
    if data_filter and data_filter.strip():
        try:
            df = df.query(data_filter)
        except:
            pass

    try:
        # Recreate pivot
        if not values:
            if cols:
                pivot = pd.crosstab(
                    [df[r] for r in rows],
                    [df[c] for c in cols],
                    margins=margins,
                    margins_name="Total",
                )
            else:
                pivot = df[rows].value_counts().reset_index()
                pivot.columns = list(rows) + ["count"]
        else:
            pivot = pd.pivot_table(
                df,
                index=rows,
                columns=cols if cols else None,
                values=values,
                aggfunc=aggfunc,
                margins=margins,
                margins_name="Total",
            )

        if normalize:
            pivot = pivot / pivot.sum().sum()

        return dcc.send_data_frame(pivot.reset_index().to_csv, f"{dataset_name}_pivot.csv", index=False)
    except:
        return dash.no_update
