"""
Combine Page
============

Combine datasets using joins and set operations.
"""

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import pandas as pd
from components.common import create_page_header
from dash import Input, Output, State, callback, html
from dash_iconify import DashIconify
from utils.data_manager import data_manager


def layout():
    """Create the Combine page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Combine Datasets",
                "Join or merge multiple datasets. Perform inner, left, right, outer joins, or set operations.",
                icon="carbon:data-connected",
            ),
            dmc.Grid([
                # Left panel - controls
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Select(
                                            id="combine-dataset1",
                                            label="First Dataset",
                                            placeholder="Select first dataset...",
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="combine-dataset2",
                                            label="Second Dataset",
                                            placeholder="Select second dataset...",
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="combine-type",
                                            label="Combine Type",
                                            value="inner",
                                            data=[
                                                {
                                                    "label": "Inner Join",
                                                    "value": "inner",
                                                },
                                                {
                                                    "label": "Left Join",
                                                    "value": "left",
                                                },
                                                {
                                                    "label": "Right Join",
                                                    "value": "right",
                                                },
                                                {
                                                    "label": "Outer Join",
                                                    "value": "outer",
                                                },
                                                {
                                                    "label": "Concatenate (Rows)",
                                                    "value": "concat_rows",
                                                },
                                                {
                                                    "label": "Concatenate (Columns)",
                                                    "value": "concat_cols",
                                                },
                                                {
                                                    "label": "Intersect",
                                                    "value": "intersect",
                                                },
                                                {
                                                    "label": "Union",
                                                    "value": "union",
                                                },
                                                {
                                                    "label": "Difference",
                                                    "value": "difference",
                                                },
                                            ],
                                        ),
                                        dmc.MultiSelect(
                                            id="combine-on",
                                            label="Join On (columns)",
                                            placeholder="Select join columns...",
                                            description="For joins only",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.TextInput(
                                            id="combine-result-name",
                                            label="Result Dataset Name",
                                            placeholder="combined_data",
                                        ),
                                        dmc.Button(
                                            "Combine Datasets",
                                            id="combine-btn",
                                            leftSection=DashIconify(icon="carbon:merge"),
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
                # Right panel - preview
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Result Preview", fw=600),
                                        html.Div(id="combine-preview-container"),
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
            html.Div(id="combine-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("combine-dataset1", "data"),
    Output("combine-dataset2", "data"),
    Input("app-state", "modified_timestamp"),
)
def update_combine_selectors(ts):
    """Update dataset selectors."""
    datasets = data_manager.get_dataset_names()
    data = [{"label": name, "value": name} for name in datasets]
    return data, data


@callback(
    Output("combine-on", "data"),
    Input("combine-dataset1", "value"),
    Input("combine-dataset2", "value"),
)
def update_join_columns(dataset1, dataset2):
    """Update join column options based on selected datasets."""
    if not dataset1 or not dataset2:
        return []

    df1 = data_manager.get_dataset(dataset1)
    df2 = data_manager.get_dataset(dataset2)

    if df1 is None or df2 is None:
        return []

    # Find common columns
    common_cols = set(df1.columns).intersection(set(df2.columns))
    return [{"label": col, "value": col} for col in sorted(common_cols)]


@callback(
    Output("combine-preview-container", "children"),
    Output("combine-notification", "children"),
    Output("app-state", "data", allow_duplicate=True),
    Input("combine-btn", "n_clicks"),
    State("combine-dataset1", "value"),
    State("combine-dataset2", "value"),
    State("combine-type", "value"),
    State("combine-on", "value"),
    State("combine-result-name", "value"),
    prevent_initial_call=True,
)
def combine_datasets(n_clicks, dataset1, dataset2, combine_type, join_on, result_name):
    """Combine two datasets according to specified operation."""
    if not n_clicks or not dataset1 or not dataset2:
        return dash.no_update, dash.no_update, dash.no_update

    df1 = data_manager.get_dataset(dataset1)
    df2 = data_manager.get_dataset(dataset2)

    if df1 is None or df2 is None:
        return (
            dash.no_update,
            dmc.Notification(
                title="Error",
                message="Could not load datasets",
                color="red",
                action="show",
            ),
            dash.no_update,
        )

    try:
        # Perform combination
        if combine_type in ["inner", "left", "right", "outer"]:
            # Join operations
            if not join_on:
                return (
                    dash.no_update,
                    dmc.Notification(
                        title="Error",
                        message="Please select columns to join on",
                        color="yellow",
                        action="show",
                    ),
                    dash.no_update,
                )

            result = pd.merge(df1, df2, on=join_on, how=combine_type)

        elif combine_type == "concat_rows":
            # Concatenate rows (vertical stack)
            result = pd.concat([df1, df2], axis=0, ignore_index=True)

        elif combine_type == "concat_cols":
            # Concatenate columns (horizontal stack)
            result = pd.concat([df1, df2], axis=1)

        elif combine_type == "intersect":
            # Set intersection
            result = pd.merge(df1, df2, how="inner")
            result = result.drop_duplicates()

        elif combine_type == "union":
            # Set union
            result = pd.concat([df1, df2], axis=0, ignore_index=True)
            result = result.drop_duplicates()

        elif combine_type == "difference":
            # Set difference (df1 - df2)
            result = df1[~df1.isin(df2).all(axis=1)]

        else:
            return (
                dash.no_update,
                dmc.Notification(
                    title="Error",
                    message="Unknown combine type",
                    color="red",
                    action="show",
                ),
                dash.no_update,
            )

        # Save result
        if not result_name:
            result_name = f"{dataset1}_{dataset2}_combined"

        data_manager.add_dataset(
            result_name,
            result,
            description=f"Combined from {dataset1} and {dataset2} using {combine_type}",
            load_command=f"# Combined dataset\n{result_name} = pd.merge(...)",
        )
        data_manager.set_active_dataset(result_name)

        # Create preview
        preview = dmc.Stack(
            [
                dmc.Group([
                    dmc.Badge(f"{len(result):,} rows", color="blue"),
                    dmc.Badge(f"{len(result.columns)} columns", color="green"),
                ]),
                dmc.Text(f"Saved as: {result_name}", size="sm", c="dimmed"),
                dag.AgGrid(
                    rowData=result.head(20).to_dict("records"),
                    columnDefs=[{"field": i, "filter": True} for i in result.columns],
                    defaultColDef={"resizable": True, "sortable": True},
                    className="ag-theme-alpine",
                    style={"height": "400px"},
                ),
            ],
            gap="sm",
        )

        notification = dmc.Notification(
            title="Success",
            message=f"Combined datasets saved as '{result_name}'",
            color="green",
            action="show",
            icon=DashIconify(icon="carbon:checkmark"),
        )

        return preview, notification, {"timestamp": "combine"}

    except Exception as e:
        return (
            dash.no_update,
            dmc.Notification(
                title="Error",
                message=f"Could not combine datasets: {e!s}",
                color="red",
                action="show",
            ),
            dash.no_update,
        )
