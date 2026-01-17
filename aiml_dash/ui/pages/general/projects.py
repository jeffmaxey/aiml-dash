"""
Projects Page - Manage Projects and Experiments

This module provides a page for managing projects with AG Grid integration.
Users can create new projects, view existing projects in a table, and open selected projects
to view and manage experiments and datasets.

Author: AIML Dash Team
Date: 2026-01-13
"""

from datetime import datetime

import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, ctx, dcc, html
from dash_iconify import DashIconify


# Sample data for experiments
SAMPLE_EXPERIMENTS = [
    {
        "id": "exp-1",
        "name": "Baseline Model",
        "type": "Linear Regression",
        "created": "2026-01-10",
        "status": "Completed",
        "accuracy": "0.85",
    },
    {
        "id": "exp-2",
        "name": "Feature Engineering v1",
        "type": "Random Forest",
        "created": "2026-01-11",
        "status": "Running",
        "accuracy": "0.89",
    },
    {
        "id": "exp-3",
        "name": "Neural Network Test",
        "type": "Neural Network",
        "created": "2026-01-12",
        "status": "Completed",
        "accuracy": "0.92",
    },
]

# Sample data for datasets
SAMPLE_DATASETS = [
    {
        "id": "ds-1",
        "name": "training_data.csv",
        "rows": 10000,
        "columns": 25,
        "size": "2.3 MB",
        "uploaded": "2026-01-08",
    },
    {
        "id": "ds-2",
        "name": "test_data.csv",
        "rows": 2500,
        "columns": 25,
        "size": "580 KB",
        "uploaded": "2026-01-08",
    },
    {
        "id": "ds-3",
        "name": "validation_data.csv",
        "rows": 2500,
        "columns": 25,
        "size": "575 KB",
        "uploaded": "2026-01-09",
    },
]


def layout():
    """
    Create the projects page layout.

    Returns:
        dmc.Container: The complete projects page layout with stores and content area
    """
    return dmc.Container(
        [
            # Store for current view state (list or detail)
            dcc.Store(id="project-view-state", data={"view": "list", "project_id": None}),
            # Store for selected project data
            dcc.Store(id="selected-project-store"),
            # Store for selected experiment
            dcc.Store(id="selected-experiment-store"),
            # Store for selected dataset
            dcc.Store(id="selected-dataset-store"),
            # Notification Container
            html.Div(id="project-notification-container"),
            # Main content container
            html.Div(id="projects-main-content"),
        ],
        fluid=True,
        size="xl",
        p="md",
    )


def create_projects_list():
    """Create the projects list view."""
    return [
        # Page Header
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Title("Projects", order=2),
                        dmc.Button(
                            "Create New Project",
                            leftSection=DashIconify(icon="carbon:add", width=20),
                            id="create-project-btn",
                            variant="filled",
                            color="blue",
                        ),
                    ],
                    justify="space-between",
                    mb="md",
                ),
                dmc.Text(
                    "Manage your projects and experiments. Select a project from the table below to open it.",
                    size="sm",
                    c="gray",
                    mb="lg",
                ),
            ],
        ),
        # Projects Grid
        dmc.Paper(
            [
                dag.AgGrid(
                    id="projects-grid",
                    columnDefs=[
                        {
                            "field": "name",
                            "headerName": "Project Name",
                            "filter": True,
                            "checkboxSelection": True,
                            "headerCheckboxSelection": False,
                        },
                        {
                            "field": "description",
                            "headerName": "Description",
                            "filter": True,
                            "flex": 2,
                        },
                        {
                            "field": "created",
                            "headerName": "Created",
                            "filter": "agDateColumnFilter",
                        },
                        {
                            "field": "modified",
                            "headerName": "Last Modified",
                            "filter": "agDateColumnFilter",
                        },
                        {
                            "field": "status",
                            "headerName": "Status",
                            "filter": True,
                            "cellStyle": {
                                "styleConditions": [
                                    {
                                        "condition": "params.value == 'Active'",
                                        "style": {"backgroundColor": "#d4f4dd", "color": "#0ca678"},
                                    },
                                    {
                                        "condition": "params.value == 'Archived'",
                                        "style": {"backgroundColor": "#f4f4f4", "color": "#666666"},
                                    },
                                ]
                            },
                        },
                    ],
                    rowData=[
                        {
                            "id": "proj-1",
                            "name": "Customer Segmentation",
                            "description": "K-means clustering analysis of customer data",
                            "created": "2026-01-05",
                            "modified": "2026-01-12",
                            "status": "Active",
                        },
                        {
                            "id": "proj-2",
                            "name": "Sales Forecasting",
                            "description": "Time series analysis for quarterly sales predictions",
                            "created": "2025-12-15",
                            "modified": "2026-01-10",
                            "status": "Active",
                        },
                        {
                            "id": "proj-3",
                            "name": "Product Recommendation",
                            "description": "Collaborative filtering model for e-commerce",
                            "created": "2025-11-20",
                            "modified": "2025-12-01",
                            "status": "Archived",
                        },
                        {
                            "id": "proj-4",
                            "name": "Churn Prediction",
                            "description": "Logistic regression model for customer churn",
                            "created": "2026-01-01",
                            "modified": "2026-01-11",
                            "status": "Active",
                        },
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "filter": True,
                    },
                    dashGridOptions={
                        "rowSelection": "single",
                        "animateRows": True,
                        "pagination": True,
                        "paginationPageSize": 10,
                    },
                    style={"height": "500px"},
                ),
            ],
            shadow="sm",
            p="md",
            radius="md",
            withBorder=True,
        ),
        # Action Buttons for Selected Project
        dmc.Group(
            [
                dmc.Button(
                    "Open Project",
                    leftSection=DashIconify(icon="carbon:folder-open", width=20),
                    id="open-project-btn",
                    variant="filled",
                    color="blue",
                    disabled=True,
                ),
                dmc.Button(
                    "Delete Project",
                    leftSection=DashIconify(icon="carbon:trash-can", width=20),
                    id="delete-project-btn",
                    variant="light",
                    color="red",
                    disabled=True,
                ),
                dmc.Button(
                    "Archive Project",
                    leftSection=DashIconify(icon="carbon:archive", width=20),
                    id="archive-project-btn",
                    variant="light",
                    color="gray",
                    disabled=True,
                ),
            ],
            mt="md",
        ),
        # Modal for Creating New Project
        dmc.Modal(
            [
                dmc.Stack(
                    [
                        dmc.TextInput(
                            label="Project Name",
                            placeholder="Enter project name",
                            id="new-project-name",
                            required=True,
                        ),
                        dmc.Textarea(
                            label="Description",
                            placeholder="Enter project description (optional)",
                            id="new-project-description",
                            minRows=3,
                        ),
                        dmc.Select(
                            label="Project Type",
                            placeholder="Select project type",
                            id="new-project-type",
                            data=["Data Analysis", "Predictive Modeling", "Visualization", "Experiment Design"],
                            value="Data Analysis",
                        ),
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Create",
                                    id="create-project-submit",
                                    variant="filled",
                                    color="blue",
                                ),
                                dmc.Button(
                                    "Cancel",
                                    id="create-project-cancel",
                                    variant="subtle",
                                    color="gray",
                                ),
                            ],
                            justify="flex-end",
                            mt="md",
                        ),
                    ],
                    gap="md",
                )
            ],
            id="create-project-modal",
            title="Create New Project",
            size="lg",
            opened=False,
        ),
    ]


def create_project_detail(project_data):
    """Create the project detail view with experiments and datasets."""
    if not project_data:
        return create_empty_state(message="No project selected")

    project_name = project_data.get("name", "Unknown Project")
    project_description = project_data.get("description", "No description")

    return [
        # Back button and header
        dmc.Group(
            [
                dmc.Button(
                    "Back to Projects",
                    leftSection=DashIconify(icon="carbon:arrow-left", width=20),
                    id="back-to-projects-btn",
                    variant="subtle",
                    color="gray",
                    mb="md",
                ),
            ],
        ),
        # Project Details Card
        dmc.Card(
            [
                dmc.Stack(
                    [
                        dmc.Group(
                            [
                                DashIconify(icon="carbon:folder", width=40, height=40, color="#1971c2"),
                                dmc.Stack(
                                    [
                                        dmc.Title(project_name, order=2),
                                        dmc.Badge(
                                            project_data.get("status", "Active"),
                                            color="green" if project_data.get("status") == "Active" else "gray",
                                            variant="light",
                                        ),
                                    ],
                                    gap=5,
                                ),
                            ],
                            gap="md",
                        ),
                        dmc.Text(project_description, size="sm", c="gray"),
                        dmc.Group(
                            [
                                dmc.Text(
                                    f"Created: {project_data.get('created', 'N/A')}",
                                    size="xs",
                                    c="dimmed",
                                ),
                                dmc.Text("•", size="xs", c="dimmed"),
                                dmc.Text(
                                    f"Last Modified: {project_data.get('modified', 'N/A')}",
                                    size="xs",
                                    c="dimmed",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    gap="sm",
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            p="lg",
            mb="xl",
        ),
        # Tabs for Experiments and Datasets
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.TabsTab(
                        "Experiments", value="experiments", leftSection=DashIconify(icon="carbon:test-tool", width=16)
                    ),
                    dmc.TabsTab(
                        "Datasets", value="datasets", leftSection=DashIconify(icon="carbon:data-table", width=16)
                    ),
                ]),
                # Experiments Tab
                dmc.TabsPanel(
                    [
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Title("Experiments", order=4, mt="md"),
                                        dmc.Group(
                                            [
                                                dmc.Button(
                                                    "Create Experiment",
                                                    leftSection=DashIconify(icon="carbon:add", width=18),
                                                    id="create-experiment-btn",
                                                    size="sm",
                                                    variant="filled",
                                                    color="blue",
                                                ),
                                                dmc.Button(
                                                    "Import",
                                                    leftSection=DashIconify(icon="carbon:upload", width=18),
                                                    id="import-experiment-btn",
                                                    size="sm",
                                                    variant="light",
                                                ),
                                                dmc.Button(
                                                    "Export",
                                                    leftSection=DashIconify(icon="carbon:download", width=18),
                                                    id="export-experiment-btn",
                                                    size="sm",
                                                    variant="light",
                                                    disabled=True,
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                    justify="space-between",
                                    mb="md",
                                ),
                                # Experiments Grid
                                dmc.Paper(
                                    [
                                        dag.AgGrid(
                                            id="experiments-grid",
                                            columnDefs=[
                                                {
                                                    "field": "name",
                                                    "headerName": "Experiment Name",
                                                    "filter": True,
                                                    "checkboxSelection": True,
                                                    "headerCheckboxSelection": False,
                                                },
                                                {
                                                    "field": "type",
                                                    "headerName": "Type",
                                                    "filter": True,
                                                },
                                                {
                                                    "field": "created",
                                                    "headerName": "Created",
                                                    "filter": "agDateColumnFilter",
                                                },
                                                {
                                                    "field": "status",
                                                    "headerName": "Status",
                                                    "filter": True,
                                                    "cellStyle": {
                                                        "styleConditions": [
                                                            {
                                                                "condition": "params.value == 'Completed'",
                                                                "style": {
                                                                    "backgroundColor": "#d4f4dd",
                                                                    "color": "#0ca678",
                                                                },
                                                            },
                                                            {
                                                                "condition": "params.value == 'Running'",
                                                                "style": {
                                                                    "backgroundColor": "#fff4e6",
                                                                    "color": "#e67700",
                                                                },
                                                            },
                                                            {
                                                                "condition": "params.value == 'Failed'",
                                                                "style": {
                                                                    "backgroundColor": "#ffe9e9",
                                                                    "color": "#c92a2a",
                                                                },
                                                            },
                                                        ]
                                                    },
                                                },
                                                {
                                                    "field": "accuracy",
                                                    "headerName": "Accuracy",
                                                    "filter": "agNumberColumnFilter",
                                                },
                                            ],
                                            rowData=SAMPLE_EXPERIMENTS,
                                            columnSize="sizeToFit",
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                            },
                                            dashGridOptions={
                                                "rowSelection": "single",
                                                "animateRows": True,
                                            },
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="md",
                                    radius="md",
                                    withBorder=True,
                                ),
                                # Experiment Actions
                                dmc.Group(
                                    [
                                        dmc.Button(
                                            "Open Experiment",
                                            leftSection=DashIconify(icon="carbon:launch", width=18),
                                            id="open-experiment-btn",
                                            size="sm",
                                            disabled=True,
                                        ),
                                        dmc.Button(
                                            "Delete Experiment",
                                            leftSection=DashIconify(icon="carbon:trash-can", width=18),
                                            id="delete-experiment-btn",
                                            size="sm",
                                            variant="light",
                                            color="red",
                                            disabled=True,
                                        ),
                                    ],
                                    mt="sm",
                                ),
                            ],
                            gap="xs",
                        )
                    ],
                    value="experiments",
                    pt="md",
                ),
                # Datasets Tab
                dmc.TabsPanel(
                    [
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Title("Datasets", order=4, mt="md"),
                                        dmc.Group(
                                            [
                                                dmc.Button(
                                                    "Add Dataset",
                                                    leftSection=DashIconify(icon="carbon:add", width=18),
                                                    id="create-dataset-btn",
                                                    size="sm",
                                                    variant="filled",
                                                    color="blue",
                                                ),
                                                dmc.Button(
                                                    "Import",
                                                    leftSection=DashIconify(icon="carbon:upload", width=18),
                                                    id="import-dataset-btn",
                                                    size="sm",
                                                    variant="light",
                                                ),
                                                dmc.Button(
                                                    "Export",
                                                    leftSection=DashIconify(icon="carbon:download", width=18),
                                                    id="export-dataset-btn",
                                                    size="sm",
                                                    variant="light",
                                                    disabled=True,
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                    justify="space-between",
                                    mb="md",
                                ),
                                # Datasets Grid
                                dmc.Paper(
                                    [
                                        dag.AgGrid(
                                            id="datasets-grid",
                                            columnDefs=[
                                                {
                                                    "field": "name",
                                                    "headerName": "Dataset Name",
                                                    "filter": True,
                                                    "checkboxSelection": True,
                                                    "headerCheckboxSelection": False,
                                                },
                                                {
                                                    "field": "rows",
                                                    "headerName": "Rows",
                                                    "filter": "agNumberColumnFilter",
                                                },
                                                {
                                                    "field": "columns",
                                                    "headerName": "Columns",
                                                    "filter": "agNumberColumnFilter",
                                                },
                                                {
                                                    "field": "size",
                                                    "headerName": "Size",
                                                    "filter": True,
                                                },
                                                {
                                                    "field": "uploaded",
                                                    "headerName": "Uploaded",
                                                    "filter": "agDateColumnFilter",
                                                },
                                            ],
                                            rowData=SAMPLE_DATASETS,
                                            columnSize="sizeToFit",
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                            },
                                            dashGridOptions={
                                                "rowSelection": "single",
                                                "animateRows": True,
                                            },
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="md",
                                    radius="md",
                                    withBorder=True,
                                ),
                                # Dataset Actions
                                dmc.Group(
                                    [
                                        dmc.Button(
                                            "View Dataset",
                                            leftSection=DashIconify(icon="carbon:view", width=18),
                                            id="view-dataset-btn",
                                            size="sm",
                                            disabled=True,
                                        ),
                                        dmc.Button(
                                            "Delete Dataset",
                                            leftSection=DashIconify(icon="carbon:trash-can", width=18),
                                            id="delete-dataset-btn",
                                            size="sm",
                                            variant="light",
                                            color="red",
                                            disabled=True,
                                        ),
                                    ],
                                    mt="sm",
                                ),
                            ],
                            gap="xs",
                        )
                    ],
                    value="datasets",
                    pt="md",
                ),
            ],
            value="experiments",
            variant="default",
        ),
        # Modals for creating experiments and datasets
        dmc.Modal(
            [
                dmc.Stack(
                    [
                        dmc.TextInput(
                            label="Experiment Name",
                            placeholder="Enter experiment name",
                            id="new-experiment-name",
                            required=True,
                        ),
                        dmc.Select(
                            label="Experiment Type",
                            placeholder="Select type",
                            id="new-experiment-type",
                            data=[
                                "Linear Regression",
                                "Logistic Regression",
                                "Random Forest",
                                "Neural Network",
                                "Other",
                            ],
                            value="Linear Regression",
                        ),
                        dmc.Textarea(
                            label="Description",
                            placeholder="Enter experiment description (optional)",
                            id="new-experiment-description",
                            minRows=3,
                        ),
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Create",
                                    id="create-experiment-submit",
                                    variant="filled",
                                    color="blue",
                                ),
                                dmc.Button(
                                    "Cancel",
                                    id="create-experiment-cancel",
                                    variant="subtle",
                                    color="gray",
                                ),
                            ],
                            justify="flex-end",
                            mt="md",
                        ),
                    ],
                    gap="md",
                )
            ],
            id="create-experiment-modal",
            title="Create New Experiment",
            size="lg",
            opened=False,
        ),
        dmc.Modal(
            [
                dmc.Stack(
                    [
                        dmc.TextInput(
                            label="Dataset Name",
                            placeholder="Enter dataset name",
                            id="new-dataset-name",
                            required=True,
                        ),
                        dmc.Divider(label="Data Source", labelPosition="center"),
                        # Radio group for data source selection
                        dmc.RadioGroup(
                            [
                                dmc.Radio("Upload CSV File", value="file"),
                                dmc.Radio("Database Connection", value="database"),
                                dmc.Radio("Connect to Existing Dataset", value="existing"),
                            ],
                            id="dataset-source-type",
                            value="file",
                            label="Select Data Source Type",
                            size="sm",
                            mb="md",
                        ),
                        # File upload section
                        html.Div(
                            [
                                dmc.Text("Upload a CSV file from your computer", size="sm", c="gray", mb="xs"),
                                dmc.Button(
                                    "Choose File",
                                    id="upload-dataset-btn",
                                    variant="light",
                                    fullWidth=True,
                                    leftSection=DashIconify(icon="carbon:document-add", width=18),
                                ),
                            ],
                            id="file-upload-section",
                        ),
                        # Database connection section
                        html.Div(
                            [
                                dmc.Select(
                                    label="Database Type",
                                    placeholder="Select database type",
                                    id="dataset-db-type",
                                    data=["PostgreSQL", "MySQL", "SQL Server", "SQLite", "Oracle"],
                                    leftSection=DashIconify(icon="carbon:data-base", width=16),
                                    mb="sm",
                                ),
                                dmc.TextInput(
                                    label="Host",
                                    placeholder="localhost or IP address",
                                    id="dataset-db-host",
                                    leftSection=DashIconify(icon="carbon:network-3", width=16),
                                    mb="sm",
                                ),
                                dmc.Group(
                                    [
                                        dmc.TextInput(
                                            label="Port",
                                            placeholder="5432",
                                            id="dataset-db-port",
                                            style={"flex": 1},
                                        ),
                                        dmc.TextInput(
                                            label="Database",
                                            placeholder="database name",
                                            id="dataset-db-name",
                                            style={"flex": 2},
                                        ),
                                    ],
                                    grow=True,
                                    mb="sm",
                                ),
                                dmc.TextInput(
                                    label="Username",
                                    placeholder="database user",
                                    id="dataset-db-username",
                                    leftSection=DashIconify(icon="carbon:user", width=16),
                                    mb="sm",
                                ),
                                dmc.PasswordInput(
                                    label="Password",
                                    placeholder="Enter password",
                                    id="dataset-db-password",
                                    leftSection=DashIconify(icon="carbon:password", width=16),
                                    mb="sm",
                                ),
                                dmc.TextInput(
                                    label="Table Name",
                                    placeholder="Enter table name",
                                    id="dataset-db-table",
                                    leftSection=DashIconify(icon="carbon:table", width=16),
                                    required=True,
                                ),
                                dmc.Group(
                                    [
                                        dmc.Button(
                                            "Test Connection",
                                            id="test-db-connection-btn",
                                            variant="light",
                                            size="sm",
                                            leftSection=DashIconify(icon="carbon:plug", width=16),
                                        ),
                                        html.Div(id="db-connection-status"),
                                    ],
                                    mt="sm",
                                    align="center",
                                ),
                            ],
                            id="database-connection-section",
                            style={"display": "none"},
                        ),
                        # Existing dataset section
                        html.Div(
                            [
                                dmc.Text("Link to an existing dataset in the system", size="sm", c="gray", mb="xs"),
                                dmc.Select(
                                    label="Available Datasets",
                                    placeholder="Select a dataset",
                                    id="existing-dataset-select",
                                    data=["sales_2024.csv", "customer_data.csv", "inventory.csv", "transactions.csv"],
                                    searchable=True,
                                ),
                            ],
                            id="existing-dataset-section",
                            style={"display": "none"},
                        ),
                        dmc.Divider(),
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Add Dataset",
                                    id="create-dataset-submit",
                                    variant="filled",
                                    color="blue",
                                ),
                                dmc.Button(
                                    "Cancel",
                                    id="create-dataset-cancel",
                                    variant="subtle",
                                    color="gray",
                                ),
                            ],
                            justify="flex-end",
                            mt="md",
                        ),
                    ],
                    gap="md",
                )
            ],
            id="create-dataset-modal",
            title="Add Dataset to Project",
            size="xl",
            opened=False,
        ),
    ]


# ==============================================================================
# CALLBACKS
# ==============================================================================


@callback(
    Output("projects-main-content", "children"),
    Input("project-view-state", "data"),
)
def update_main_content(view_state):
    """Update main content based on view state."""
    if view_state.get("view") == "detail":
        project_data = view_state.get("project_data")
        return create_project_detail(project_data)
    else:
        return create_projects_list()


@callback(
    Output("project-view-state", "data"),
    Input("open-project-btn", "n_clicks"),
    Input("back-to-projects-btn", "n_clicks"),
    State("selected-project-store", "data"),
    State("project-view-state", "data"),
    prevent_initial_call=True,
)
def navigate_project_views(_open_clicks, _back_clicks, selected_project, current_state):
    """Handle navigation between list and detail views."""
    if ctx.triggered_id == "open-project-btn" and selected_project:
        return {
            "view": "detail",
            "project_id": selected_project.get("id"),
            "project_data": selected_project,
        }
    elif ctx.triggered_id == "back-to-projects-btn":
        return {"view": "list", "project_id": None}
    return current_state


@callback(
    Output("create-project-modal", "opened"),
    Input("create-project-btn", "n_clicks"),
    Input("create-project-cancel", "n_clicks"),
    Input("create-project-submit", "n_clicks"),
    State("create-project-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_create_modal(_open_clicks, _cancel_clicks, _submit_clicks, is_open):
    """Toggle the create project modal."""
    if ctx.triggered_id == "create-project-submit":
        return False
    return not is_open


@callback(
    [
        Output("projects-grid", "rowData", allow_duplicate=True),
        Output("project-notification-container", "children", allow_duplicate=True),
        Output("new-project-name", "value"),
        Output("new-project-description", "value"),
    ],
    Input("create-project-submit", "n_clicks"),
    [
        State("new-project-name", "value"),
        State("new-project-description", "value"),
        State("new-project-type", "value"),
        State("projects-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def create_new_project(n_clicks, name, description, _project_type, current_data):
    """Create a new project and add it to the grid."""
    if not n_clicks or not name:
        return current_data, None, "", ""

    # Create new project entry
    new_project = {
        "id": f"proj-{len(current_data) + 1}",
        "name": name,
        "description": description or "No description provided",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "modified": datetime.now().strftime("%Y-%m-%d"),
        "status": "Active",
    }

    # Add to existing data
    updated_data = [*current_data, new_project]

    # Create success notification
    notification = dmc.Notification(
        id="create-project-notification",
        title="Project Created",
        message=f"Project '{name}' has been created successfully!",
        color="green",
        action="show",
        icon=DashIconify(icon="carbon:checkmark-filled"),
        autoClose=3000,
    )

    return updated_data, notification, "", ""


@callback(
    [
        Output("open-project-btn", "disabled"),
        Output("delete-project-btn", "disabled"),
        Output("archive-project-btn", "disabled"),
        Output("selected-project-store", "data"),
    ],
    Input("projects-grid", "selectedRows"),
    prevent_initial_call=True,
)
def update_button_states(selected_rows):
    """Enable/disable action buttons based on row selection."""
    if selected_rows and len(selected_rows) > 0:
        selected_project = selected_rows[0]
        return False, False, False, selected_project
    else:
        return True, True, True, None


@callback(
    [
        Output("projects-grid", "rowData"),
        Output("project-notification-container", "children", allow_duplicate=True),
    ],
    Input("delete-project-btn", "n_clicks"),
    [
        State("selected-project-store", "data"),
        State("projects-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def delete_selected_project(n_clicks, selected_project, current_data):
    """Delete the selected project from the grid."""
    if not n_clicks or not selected_project:
        return current_data, None

    updated_data = [p for p in current_data if p.get("id") != selected_project.get("id")]

    notification = dmc.Notification(
        id="delete-project-notification",
        title="Project Deleted",
        message=f"Project '{selected_project.get('name', 'Unknown')}' has been deleted.",
        color="red",
        action="show",
        icon=DashIconify(icon="carbon:trash-can"),
        autoClose=3000,
    )

    return updated_data, notification


@callback(
    [
        Output("projects-grid", "rowData", allow_duplicate=True),
        Output("project-notification-container", "children", allow_duplicate=True),
    ],
    Input("archive-project-btn", "n_clicks"),
    [
        State("selected-project-store", "data"),
        State("projects-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def archive_selected_project(n_clicks, selected_project, current_data):
    """Archive the selected project."""
    if not n_clicks or not selected_project:
        return current_data, None

    updated_data = []
    for project in current_data:
        if project.get("id") == selected_project.get("id"):
            project["status"] = "Archived"
        updated_data.append(project)

    notification = dmc.Notification(
        id="archive-project-notification",
        title="Project Archived",
        message=f"Project '{selected_project.get('name', 'Unknown')}' has been archived.",
        color="gray",
        action="show",
        icon=DashIconify(icon="carbon:archive"),
        autoClose=3000,
    )

    return updated_data, notification


# ==============================================================================
# EXPERIMENT CALLBACKS
# ==============================================================================


@callback(
    Output("create-experiment-modal", "opened"),
    Input("create-experiment-btn", "n_clicks"),
    Input("create-experiment-cancel", "n_clicks"),
    Input("create-experiment-submit", "n_clicks"),
    State("create-experiment-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_experiment_modal(_open_clicks, _cancel_clicks, _submit_clicks, is_open):
    """Toggle the create experiment modal."""
    if ctx.triggered_id == "create-experiment-submit":
        return False
    return not is_open


@callback(
    [
        Output("experiments-grid", "rowData", allow_duplicate=True),
        Output("project-notification-container", "children", allow_duplicate=True),
        Output("new-experiment-name", "value"),
        Output("new-experiment-description", "value"),
    ],
    Input("create-experiment-submit", "n_clicks"),
    [
        State("new-experiment-name", "value"),
        State("new-experiment-type", "value"),
        State("new-experiment-description", "value"),
        State("experiments-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def create_new_experiment(n_clicks, name, exp_type, _description, current_data):
    """Create a new experiment and add it to the grid."""
    if not n_clicks or not name:
        return current_data, None, "", ""

    new_experiment = {
        "id": f"exp-{len(current_data) + 1}",
        "name": name,
        "type": exp_type,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "status": "Pending",
        "accuracy": "N/A",
    }

    updated_data = [*current_data, new_experiment]

    notification = dmc.Notification(
        id="create-experiment-notification",
        title="Experiment Created",
        message=f"Experiment '{name}' has been created successfully!",
        color="green",
        action="show",
        icon=DashIconify(icon="carbon:checkmark-filled"),
        autoClose=3000,
    )

    return updated_data, notification, "", ""


@callback(
    [
        Output("open-experiment-btn", "disabled"),
        Output("delete-experiment-btn", "disabled"),
        Output("export-experiment-btn", "disabled"),
        Output("selected-experiment-store", "data"),
    ],
    Input("experiments-grid", "selectedRows"),
    prevent_initial_call=True,
)
def update_experiment_button_states(selected_rows):
    """Enable/disable experiment action buttons based on row selection."""
    if selected_rows and len(selected_rows) > 0:
        selected_experiment = selected_rows[0]
        return False, False, False, selected_experiment
    else:
        return True, True, True, None


@callback(
    [
        Output("experiments-grid", "rowData"),
        Output("project-notification-container", "children", allow_duplicate=True),
    ],
    Input("delete-experiment-btn", "n_clicks"),
    [
        State("selected-experiment-store", "data"),
        State("experiments-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def delete_selected_experiment(n_clicks, selected_experiment, current_data):
    """Delete the selected experiment from the grid."""
    if not n_clicks or not selected_experiment:
        return current_data, None

    updated_data = [e for e in current_data if e.get("id") != selected_experiment.get("id")]

    notification = dmc.Notification(
        id="delete-experiment-notification",
        title="Experiment Deleted",
        message=f"Experiment '{selected_experiment.get('name', 'Unknown')}' has been deleted.",
        color="red",
        action="show",
        icon=DashIconify(icon="carbon:trash-can"),
        autoClose=3000,
    )

    return updated_data, notification


# ==============================================================================
# DATASET CALLBACKS
# ==============================================================================


@callback(
    [
        Output("file-upload-section", "style"),
        Output("database-connection-section", "style"),
        Output("existing-dataset-section", "style"),
    ],
    Input("dataset-source-type", "value"),
)
def toggle_dataset_source_sections(source_type):
    """Show/hide dataset source sections based on selection."""
    file_style = {"display": "block"} if source_type == "file" else {"display": "none"}
    db_style = {"display": "block"} if source_type == "database" else {"display": "none"}
    existing_style = {"display": "block"} if source_type == "existing" else {"display": "none"}

    return file_style, db_style, existing_style


@callback(
    Output("db-connection-status", "children"),
    Input("test-db-connection-btn", "n_clicks"),
    [
        State("dataset-db-type", "value"),
        State("dataset-db-host", "value"),
        State("dataset-db-port", "value"),
        State("dataset-db-name", "value"),
        State("dataset-db-username", "value"),
        State("dataset-db-password", "value"),
    ],
    prevent_initial_call=True,
)
def test_database_connection(n_clicks, db_type, host, port, db_name, username, _password):
    """Test the database connection with provided credentials."""
    if not n_clicks:
        return None

    # Validate required fields
    if not all([db_type, host, db_name, username]):
        return dmc.Badge(
            "Missing required fields",
            color="red",
            variant="filled",
            leftSection=DashIconify(icon="carbon:warning", width=14),
        )

    # In a real implementation, you would test the actual connection here
    # For now, we'll simulate a successful connection
    try:
        # Simulate connection test
        # connection_string = f"{db_type}://{username}:{password}@{host}:{port}/{db_name}"
        # Test connection logic would go here

        return dmc.Badge(
            "Connection successful!",
            color="green",
            variant="filled",
            leftSection=DashIconify(icon="carbon:checkmark-filled", width=14),
        )
    except Exception:
        return dmc.Badge(
            "Connection failed",
        )


def toggle_dataset_modal(_open_clicks, _cancel_clicks, _submit_clicks, is_open):
    """Toggle the create dataset modal."""
    if ctx.triggered_id == "create-dataset-submit":
        return False
    return not is_open


@callback(
    [
        Output("datasets-grid", "rowData", allow_duplicate=True),
        Output("project-notification-container", "children", allow_duplicate=True),
        Output("new-dataset-name", "value"),
    ],
    Input("create-dataset-submit", "n_clicks"),
    [
        State("new-dataset-name", "value"),
        State("dataset-source-type", "value"),
        State("dataset-db-type", "value"),
        State("dataset-db-host", "value"),
        State("dataset-db-port", "value"),
        State("dataset-db-name", "value"),
        State("dataset-db-table", "value"),
        State("existing-dataset-select", "value"),
        State("datasets-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def create_new_dataset(
    n_clicks, name, source_type, db_type, db_host, db_port, db_name, db_table, existing_dataset, current_data
):
    """Create a new dataset and add it to the grid."""
    if not n_clicks or not name:
        return current_data, None, ""

    # Determine dataset details based on source type
    if source_type == "database":
        if not all([db_type, db_host, db_name, db_table]):
            notification = dmc.Notification(
                id="create-dataset-error",
                title="Missing Information",
                message="Please fill in all required database connection fields.",
                color="red",
                action="show",
                icon=DashIconify(icon="carbon:warning"),
                autoClose=3000,
            )
            return current_data, notification, ""

        dataset_name = f"{db_table} ({db_type})"
        source_info = f"{db_type}://{db_host}:{db_port}/{db_name}/{db_table}"
    elif source_type == "existing":
        if not existing_dataset:
            notification = dmc.Notification(
                id="create-dataset-error",
                title="No Dataset Selected",
                message="Please select an existing dataset to link.",
                color="red",
                action="show",
                icon=DashIconify(icon="carbon:warning"),
                autoClose=3000,
            )
            return current_data, notification, ""
        dataset_name = existing_dataset
        source_info = "Linked dataset"
    else:  # file upload
        dataset_name = name if name.endswith(".csv") else f"{name}.csv"
        source_info = "CSV file"

    new_dataset = {
        "id": f"ds-{len(current_data) + 1}",
        "name": dataset_name,
        "rows": 0,  # Would be populated after loading
        "columns": 0,  # Would be populated after loading
        "size": "0 KB",  # Would be calculated after loading
        "uploaded": datetime.now().strftime("%Y-%m-%d"),
        "source": source_info,
    }

    updated_data = [*current_data, new_dataset]

    notification = dmc.Notification(
        id="create-dataset-notification",
        title="Dataset Added",
        message=f"Dataset '{dataset_name}' has been added to the project!",
        color="green",
        action="show",
        icon=DashIconify(icon="carbon:checkmark-filled"),
        autoClose=3000,
    )

    return updated_data, notification, ""


@callback(
    [
        Output("view-dataset-btn", "disabled"),
        Output("delete-dataset-btn", "disabled"),
        Output("export-dataset-btn", "disabled"),
        Output("selected-dataset-store", "data"),
    ],
    Input("datasets-grid", "selectedRows"),
    prevent_initial_call=True,
)
def update_dataset_button_states(selected_rows):
    """Enable/disable dataset action buttons based on row selection."""
    if selected_rows and len(selected_rows) > 0:
        selected_dataset = selected_rows[0]
        return False, False, False, selected_dataset
    else:
        return True, True, True, None


@callback(
    [
        Output("datasets-grid", "rowData"),
        Output("project-notification-container", "children", allow_duplicate=True),
    ],
    Input("delete-dataset-btn", "n_clicks"),
    [
        State("selected-dataset-store", "data"),
        State("datasets-grid", "rowData"),
    ],
    prevent_initial_call=True,
)
def delete_selected_dataset(n_clicks, selected_dataset, current_data):
    """Delete the selected dataset from the grid."""
    if not n_clicks or not selected_dataset:
        return current_data, None

    updated_data = [d for d in current_data if d.get("id") != selected_dataset.get("id")]

    notification = dmc.Notification(
        id="delete-dataset-notification",
        title="Dataset Deleted",
        message=f"Dataset '{selected_dataset.get('name', 'Unknown')}' has been deleted.",
        color="red",
        action="show",
        icon=DashIconify(icon="carbon:trash-can"),
        autoClose=3000,
    )

    return updated_data, notification
