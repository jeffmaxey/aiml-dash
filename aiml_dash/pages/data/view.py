"""
View Page
=========

Interactive data table viewer with filtering and sorting.
"""

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from components.common import create_filter_section, create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from utils.data_manager import data_manager


def layout():
    """Create the View page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Data Viewer",
                "Browse and interact with your data. Apply filters, sort columns, and search for specific values.",
                icon="carbon:view",
            ),
            dmc.Stack(
                [
                    # Filter controls
                    create_filter_section(),
                    # Export button
                    dmc.Group([
                        dmc.Button(
                            "Export to CSV",
                            id="view-export-csv",
                            leftSection=DashIconify(icon="carbon:download"),
                            variant="light",
                        ),
                        dcc.Download(id="view-download-csv"),
                    ]),
                    # Data table
                    dmc.Card(
                        [
                            html.Div(id="view-table-container"),
                        ],
                        withBorder=True,
                        radius="md",
                        p="md",
                    ),
                ],
                gap="md",
            ),
        ],
        fluid=True,
        style={"maxWidth": "1600px"},
    )


@callback(
    Output("view-table-container", "children"),
    Input("dataset-selector", "value"),
    Input("data-filter-input", "value"),
    Input("data-sort-input", "value"),
    Input("data-slice-input", "value"),
)
def update_view_table(dataset_name, filter_expr, sort_by, slice_expr):
    """Update the data table based on filters and sorting."""
    if not dataset_name:
        return dmc.Center(
            dmc.Text("No dataset selected", c="dimmed", size="lg"),
            style={"height": "400px"},
        )

    # Get data
    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Text("Error loading dataset", c="red")

    # Apply filters and sorting
    try:
        # Apply filter
        if filter_expr and filter_expr.strip():
            df = df.query(filter_expr)

        # Apply sorting
        if sort_by and sort_by.strip():
            sort_cols = [s.strip() for s in sort_by.split(",")]
            ascending = []
            clean_cols = []
            for col in sort_cols:
                if col.startswith("-"):
                    ascending.append(False)
                    clean_cols.append(col[1:])
                else:
                    ascending.append(True)
                    clean_cols.append(col)

            # Filter valid columns
            valid_cols = [c for c in clean_cols if c in df.columns]
            if valid_cols:
                df = df.sort_values(by=valid_cols, ascending=ascending[: len(valid_cols)])

        # Apply slice
        if slice_expr and slice_expr.strip():
            if ":" in slice_expr:
                parts = slice_expr.split(":")
                start = int(parts[0]) if parts[0] else 0
                end = int(parts[1]) if len(parts) > 1 and parts[1] else len(df)
                df = df.iloc[start:end]
            elif "," in slice_expr:
                indices = [int(i.strip()) for i in slice_expr.split(",")]
                df = df.iloc[indices]

    except Exception as e:
        return dmc.Alert(
            f"Error applying filters: {e!s}",
            title="Filter Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )

    # Create table
    return dmc.Stack(
        [
            dmc.Text(
                f"Showing {len(df):,} rows × {len(df.columns)} columns",
                size="sm",
                c="dimmed",
            ),
            dag.AgGrid(
                id="view-table-grid",
                rowData=df.to_dict("records"),
                columnDefs=[{"field": i, "filter": True, "sortable": True} for i in df.columns],
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": True,
                    "minWidth": 100,
                    "maxWidth": 300,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 50,
                    "animateRows": False,
                },
                className="ag-theme-alpine",
                style={"height": "600px"},
            ),
        ],
        gap="sm",
    )


@callback(
    Output("view-download-csv", "data"),
    Input("view-export-csv", "n_clicks"),
    State("dataset-selector", "value"),
    State("data-filter-input", "value"),
    State("data-sort-input", "value"),
    State("data-slice-input", "value"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, dataset_name, filter_expr, sort_by, slice_expr):
    """Export the current view to CSV."""
    if not n_clicks or not dataset_name:
        return dash.no_update

    # Get filtered data
    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dash.no_update

    # Apply same filters as the view
    try:
        if filter_expr and filter_expr.strip():
            df = df.query(filter_expr)

        if sort_by and sort_by.strip():
            sort_cols = [s.strip() for s in sort_by.split(",")]
            ascending = []
            clean_cols = []
            for col in sort_cols:
                if col.startswith("-"):
                    ascending.append(False)
                    clean_cols.append(col[1:])
                else:
                    ascending.append(True)
                    clean_cols.append(col)

            valid_cols = [c for c in clean_cols if c in df.columns]
            if valid_cols:
                df = df.sort_values(by=valid_cols, ascending=ascending[: len(valid_cols)])

        if slice_expr and slice_expr.strip() and ":" in slice_expr:
            parts = slice_expr.split(":")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else len(df)
            df = df.iloc[start:end]

    except Exception as e:
        print(f"Error exporting: {e!s}")
        return dash.no_update

    # Return CSV download
    return dcc.send_data_frame(df.to_csv, f"{dataset_name}_export.csv", index=False)
