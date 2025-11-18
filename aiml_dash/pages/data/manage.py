"""
Manage Page
===========

Data management - load, save, and preview datasets.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the Manage page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Data Management",
                "Load, save, and manage datasets. Upload CSV or Excel files, or work with sample data.",
                icon="carbon:data-table",
            ),
            dmc.Grid([
                # Left column - data actions
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        # Upload section
                                        dmc.Text("Load Data", fw=600, size="sm"),
                                        dcc.Upload(
                                            id="upload-data",
                                            children=dmc.Button(
                                                "Upload File (CSV, Excel)",
                                                leftSection=DashIconify(icon="carbon:upload"),
                                                variant="light",
                                                fullWidth=True,
                                            ),
                                            multiple=False,
                                        ),
                                        dmc.Divider(),
                                        # Dataset info
                                        dmc.Text(
                                            "Current Dataset Info",
                                            fw=600,
                                            size="sm",
                                        ),
                                        html.Div(id="manage-dataset-info"),
                                        dmc.Divider(),
                                        # Preview options
                                        dmc.Text("Preview Options", fw=600, size="sm"),
                                        dmc.SegmentedControl(
                                            id="preview-type",
                                            value="preview",
                                            data=[
                                                {
                                                    "label": "Preview",
                                                    "value": "preview",
                                                },
                                                {
                                                    "label": "Structure",
                                                    "value": "structure",
                                                },
                                                {
                                                    "label": "Summary",
                                                    "value": "summary",
                                                },
                                            ],
                                            fullWidth=True,
                                        ),
                                        # Description
                                        dmc.Textarea(
                                            id="dataset-description",
                                            label="Dataset Description",
                                            placeholder="Add a description for this dataset...",
                                            minRows=3,
                                            autosize=True,
                                        ),
                                        dmc.Button(
                                            "Save Description",
                                            id="save-description-btn",
                                            variant="light",
                                            leftSection=DashIconify(icon="carbon:save"),
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
                    span=4,
                ),
                # Right column - preview
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                html.Div(id="manage-preview-content"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=8,
                ),
            ]),
            # Notifications
            html.Div(id="manage-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("manage-notification", "children"),
    Output("app-state", "data", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_file(contents, filename):
    """Handle file upload."""
    if contents is None:
        return dash.no_update, dash.no_update

    success, message = data_manager.load_from_file(contents, filename)

    notification = dmc.Notification(
        title="Upload " + ("Successful" if success else "Failed"),
        message=message,
        color="green" if success else "red",
        action="show",
        autoClose=5000,
        icon=DashIconify(icon="carbon:checkmark" if success else "carbon:warning"),
    )

    # Update app state to trigger dataset selector refresh
    return notification, {"timestamp": dash.callback_context.triggered[0]["value"]}


@callback(
    Output("manage-dataset-info", "children"),
    Output("dataset-description", "value"),
    Input("dataset-selector", "value"),
)
def update_dataset_info(dataset_name):
    """Display current dataset information."""
    if not dataset_name:
        return dmc.Text("No dataset selected", c="dimmed", size="sm"), ""

    info = data_manager.get_dataset_info(dataset_name)

    info_items = [
        dmc.Group(
            [
                DashIconify(icon="carbon:row", width=16),
                dmc.Text(f"{info.get('rows', 0):,} rows", size="sm"),
            ],
            gap="xs",
        ),
        dmc.Group(
            [
                DashIconify(icon="carbon:column", width=16),
                dmc.Text(f"{info.get('columns', 0)} columns", size="sm"),
            ],
            gap="xs",
        ),
        dmc.Group(
            [
                DashIconify(icon="carbon:data-volume", width=16),
                dmc.Text(f"{info.get('memory_usage', 0):.2f} MB", size="sm"),
            ],
            gap="xs",
        ),
    ]

    return dmc.Stack(info_items, gap="xs"), info.get("description", "")


@callback(
    Output("manage-preview-content", "children"),
    Input("dataset-selector", "value"),
    Input("preview-type", "value"),
)
def update_preview(dataset_name, preview_type):
    """Update the data preview panel."""
    if not dataset_name:
        return dmc.Center(dmc.Text("No dataset selected", c="dimmed"), style={"height": "400px"})

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Text("Error loading dataset", c="red")

    if preview_type == "preview":
        # Show first 20 rows
        return dmc.Stack(
            [
                dmc.Text(f"First 20 rows of {len(df):,} total", size="sm", c="dimmed"),
                dag.AgGrid(
                    rowData=df.head(20).to_dict("records"),
                    columnDefs=[{"field": i, "filter": True} for i in df.columns],
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "minWidth": 100,
                    },
                    dashGridOptions={"pagination": True, "paginationPageSize": 20},
                    className="ag-theme-alpine",
                    style={"height": "500px"},
                ),
            ],
            gap="sm",
        )

    elif preview_type == "structure":
        # Show data types and info
        structure_data = []
        for col in df.columns:
            structure_data.append({
                "Column": col,
                "Type": str(df[col].dtype),
                "Non-Null": f"{df[col].notna().sum():,}",
                "Null": f"{df[col].isna().sum():,}",
                "Unique": f"{df[col].nunique():,}",
            })

        return dmc.Stack(
            [
                dmc.Text("Dataset Structure", size="sm", c="dimmed"),
                dag.AgGrid(
                    rowData=structure_data,
                    columnDefs=[{"field": i, "filter": True} for i in structure_data[0].keys()],
                    defaultColDef={"resizable": True, "sortable": True},
                    className="ag-theme-alpine",
                    style={"height": "400px"},
                ),
            ],
            gap="sm",
        )

    elif preview_type == "summary":
        # Show statistical summary
        summary = df.describe(include="all").T
        summary["column"] = summary.index
        summary = summary.reset_index(drop=True)

        # Reorder columns
        cols = ["column"] + [c for c in summary.columns if c != "column"]
        summary = summary[cols]

        return dmc.Stack(
            [
                dmc.Text("Statistical Summary", size="sm", c="dimmed"),
                dag.AgGrid(
                    rowData=summary.to_dict("records"),
                    columnDefs=[
                        {
                            "field": i,
                            "type": "numericColumn" if i != "column" else None,
                            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
                            if i != "column"
                            else None,
                            "filter": True,
                            "minWidth": 100,
                        }
                        for i in summary.columns
                    ],
                    defaultColDef={"resizable": True, "sortable": True},
                    className="ag-theme-alpine",
                    style={"height": "400px"},
                ),
            ],
            gap="sm",
        )

    return dmc.Text("Unknown preview type", c="red")


@callback(
    Output("manage-notification", "children", allow_duplicate=True),
    Input("save-description-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("dataset-description", "value"),
    prevent_initial_call=True,
)
def save_description(n_clicks, dataset_name, description):
    """Save dataset description."""
    if not n_clicks or not dataset_name:
        return dash.no_update

    if dataset_name in data_manager.datasets:
        data_manager.descriptions[dataset_name] = description

        return dmc.Notification(
            title="Description Saved",
            message=f"Description updated for {dataset_name}",
            color="green",
            action="show",
            autoClose=3000,
            icon=DashIconify(icon="carbon:checkmark"),
        )

    return dash.no_update
