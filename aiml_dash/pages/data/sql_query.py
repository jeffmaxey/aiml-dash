"""
SQL Query Page
==============

Execute SQL queries against configured database connections and load results into datasets.
"""

from __future__ import annotations

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html
from dash_iconify import DashIconify

from aiml_dash.components.common import create_page_header
from aiml_dash.utils.data_manager import data_manager
from aiml_dash.utils.database import db_manager
from aiml_dash.utils.logging import get_logger

logger = get_logger(__name__)

__all__ = ["layout"]


def layout() -> dmc.Container:
    """Create the SQL Query page layout."""
    return dmc.Container(
        [
            create_page_header(
                "SQL Query",
                "Connect to databases and execute SQL queries. Load query results as datasets.",
                icon="carbon:data-base",
            ),
            dmc.Grid([
                # Left panel - connection management
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Database Connections", fw=600, size="lg"),
                                        dmc.Divider(),
                                        dmc.Select(
                                            id="sql-connection-selector",
                                            label="Select Connection",
                                            placeholder="Choose database connection...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Button(
                                            "New Connection",
                                            id="sql-new-connection-btn",
                                            leftSection=DashIconify(icon="carbon:add"),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                        dmc.Button(
                                            "Test Connection",
                                            id="sql-test-connection-btn",
                                            leftSection=DashIconify(icon="carbon:checkmark"),
                                            variant="outline",
                                            fullWidth=True,
                                        ),
                                        html.Div(id="sql-connection-status"),
                                    ],
                                    gap="sm",
                                ),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=4,
                ),
                # Right panel - query execution
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Execute Query", fw=600, size="lg"),
                                        dmc.Divider(),
                                        dmc.Textarea(
                                            id="sql-query-input",
                                            label="SQL Query",
                                            placeholder="SELECT * FROM table_name LIMIT 100",
                                            minRows=6,
                                            autosize=True,
                                            description="Enter your SQL query here",
                                        ),
                                        dmc.TextInput(
                                            id="sql-dataset-name",
                                            label="Dataset Name",
                                            placeholder="query_result",
                                            description="Name for the resulting dataset",
                                        ),
                                        dmc.Group([
                                            dmc.Button(
                                                "Execute & Load",
                                                id="sql-execute-btn",
                                                leftSection=DashIconify(icon="carbon:play"),
                                                color="blue",
                                            ),
                                            dmc.Button(
                                                "Preview",
                                                id="sql-preview-btn",
                                                leftSection=DashIconify(icon="carbon:view"),
                                                variant="light",
                                            ),
                                        ]),
                                    ],
                                    gap="md",
                                ),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=8,
                ),
            ]),
            # Results panel
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Query Results", fw=600),
                            html.Div(id="sql-results-container"),
                        ],
                        gap="md",
                    ),
                ],
                withBorder=True,
                radius="md",
                p="md",
                mt="md",
            ),
            # Modals
            dmc.Modal(
                id="sql-connection-modal",
                title="New Database Connection",
                size="xl",
                children=[
                    dmc.Stack(
                        [
                            dmc.Select(
                                id="sql-db-dialect",
                                label="Database Type",
                                value="mssql",
                                data=[
                                    {"label": "SQL Server", "value": "mssql"},
                                    {"label": "PostgreSQL", "value": "postgresql"},
                                    {"label": "MySQL", "value": "mysql"},
                                    {"label": "SQLite", "value": "sqlite"},
                                ],
                            ),
                            dmc.TextInput(
                                id="sql-conn-name",
                                label="Connection Name",
                                placeholder="my_database",
                                required=True,
                            ),
                            dmc.TextInput(
                                id="sql-server",
                                label="Server",
                                placeholder="localhost",
                            ),
                            dmc.TextInput(
                                id="sql-database",
                                label="Database",
                                placeholder="database_name",
                            ),
                            dmc.TextInput(
                                id="sql-username",
                                label="Username (optional)",
                                placeholder="username",
                            ),
                            dmc.PasswordInput(
                                id="sql-password",
                                label="Password (optional)",
                                placeholder="password",
                            ),
                            dmc.NumberInput(
                                id="sql-port",
                                label="Port (optional)",
                                placeholder="1433",
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Save Connection",
                                        id="sql-save-connection-btn",
                                        color="blue",
                                    ),
                                    dmc.Button(
                                        "Cancel",
                                        id="sql-cancel-connection-btn",
                                        variant="subtle",
                                    ),
                                ],
                                justify="flex-end",
                            ),
                        ],
                        gap="sm",
                    ),
                ],
            ),
            html.Div(id="sql-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("sql-connection-selector", "data"),
    Input("app-state", "modified_timestamp"),
)
def update_connection_list(ts):
    """Update the list of available connections."""
    connections = db_manager.list_connections()
    return [{"label": name, "value": name} for name in connections]


@callback(
    Output("sql-connection-modal", "opened"),
    Input("sql-new-connection-btn", "n_clicks"),
    Input("sql-save-connection-btn", "n_clicks"),
    Input("sql-cancel-connection-btn", "n_clicks"),
    State("sql-connection-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_connection_modal(new_clicks, save_clicks, cancel_clicks, is_open):
    """Toggle the connection modal."""
    return not is_open


@callback(
    Output("sql-notification", "children"),
    Input("sql-save-connection-btn", "n_clicks"),
    State("sql-conn-name", "value"),
    State("sql-db-dialect", "value"),
    State("sql-server", "value"),
    State("sql-database", "value"),
    State("sql-username", "value"),
    State("sql-password", "value"),
    State("sql-port", "value"),
    prevent_initial_call=True,
)
def save_connection(n_clicks, name, dialect, server, database, username, password, port):
    """Save a new database connection."""
    if not n_clicks or not name:
        return dash.no_update

    try:
        db_manager.add_connection(
            name=name,
            dialect=dialect,
            server=server,
            database=database,
            username=username,
            password=password,
            port=port,
        )

        return dmc.Notification(
            title="Success",
            message=f"Connection '{name}' saved successfully",
            action="show",
            color="green",
            icon=DashIconify(icon="carbon:checkmark"),
        )

    except Exception as e:
        logger.error(f"Error saving connection: {e}", exc_info=True)
        return dmc.Notification(
            title="Error",
            message=f"Failed to save connection: {e!s}",
            action="show",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )


@callback(
    Output("sql-connection-status", "children"),
    Input("sql-test-connection-btn", "n_clicks"),
    State("sql-connection-selector", "value"),
    prevent_initial_call=True,
)
def test_connection(n_clicks, connection_name):
    """Test a database connection."""
    if not n_clicks or not connection_name:
        return dash.no_update

    try:
        # Try to get tables as a connection test
        tables = db_manager.get_tables(connection_name)

        return dmc.Alert(
            [
                dmc.Text("Connection successful!", fw=500),
                dmc.Text(f"Found {len(tables)} tables", size="sm"),
            ],
            title="Test Successful",
            color="green",
            icon=DashIconify(icon="carbon:checkmark"),
        )

    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        return dmc.Alert(
            f"Connection failed: {e!s}",
            title="Test Failed",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )


@callback(
    Output("sql-results-container", "children"),
    Input("sql-execute-btn", "n_clicks"),
    Input("sql-preview-btn", "n_clicks"),
    State("sql-connection-selector", "value"),
    State("sql-query-input", "value"),
    State("sql-dataset-name", "value"),
    prevent_initial_call=True,
)
def execute_query(exec_clicks, preview_clicks, connection_name, query, dataset_name):
    """Execute SQL query and optionally load as dataset."""
    ctx = dash.callback_context
    if not ctx.triggered or not connection_name or not query:
        return dmc.Center(
            dmc.Text("Select a connection and enter a query", c="dimmed"),
            style={"height": "200px"},
        )

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    try:
        # Execute query
        df = db_manager.query_dataframe(connection_name, query)

        if df.empty:
            return dmc.Alert("Query returned no results", color="yellow")

        # If execute button was clicked, load as dataset
        if button_id == "sql-execute-btn" and dataset_name:
            data_manager.add_dataset(
                dataset_name,
                df,
                description=f"SQL query result from {connection_name}",
                load_command=f"# SQL Query\n{query}",
            )
            data_manager.set_active_dataset(dataset_name)

            return dmc.Stack(
                [
                    dmc.Alert(
                        f"Loaded {len(df)} rows as dataset '{dataset_name}'",
                        title="Success",
                        color="green",
                        icon=DashIconify(icon="carbon:checkmark"),
                    ),
                    dmc.Text(f"{len(df)} rows × {len(df.columns)} columns", size="sm", c="dimmed"),
                    dag.AgGrid(
                        rowData=df.head(100).to_dict("records"),
                        columnDefs=[{"field": col, "filter": True} for col in df.columns],
                        defaultColDef={"resizable": True, "sortable": True},
                        dashGridOptions={"pagination": True},
                        className="ag-theme-alpine",
                        style={"height": "400px"},
                    ),
                ],
                gap="sm",
            )

        # Preview mode - just show results
        return dmc.Stack(
            [
                dmc.Text(f"{len(df)} rows × {len(df.columns)} columns", size="sm", c="dimmed"),
                dag.AgGrid(
                    rowData=df.head(100).to_dict("records"),
                    columnDefs=[{"field": col, "filter": True} for col in df.columns],
                    defaultColDef={"resizable": True, "sortable": True},
                    dashGridOptions={"pagination": True},
                    className="ag-theme-alpine",
                    style={"height": "400px"},
                ),
            ],
            gap="sm",
        )

    except Exception as e:
        logger.error(f"Query execution failed: {e}", exc_info=True)
        return dmc.Alert(
            f"Query failed: {e!s}",
            title="Execution Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
