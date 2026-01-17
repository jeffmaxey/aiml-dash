"""
Transform Page
==============

Data transformation - create new variables, change types, apply functions.
"""

import dash
from dash import html, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from components.common import (
    create_action_button,
    create_control_card,
    create_page_header,
    create_results_card,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager
from utils.settings import app_settings
from utils.transforms import TRANSFORM_FUNCTIONS, create_variable


def layout():
    """Create the Transform page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Transform Data",
                "Create new variables, apply transformations, and change variable types.",
                icon="carbon:settings-adjust",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList([
                        dmc.TabsTab("Create Variable", value="create"),
                        dmc.TabsTab("Transform", value="transform"),
                        dmc.TabsTab("Type Conversion", value="type"),
                        dmc.TabsTab("Binning", value="bin"),
                    ]),
                    # Create Variable Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        create_control_card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.TextInput(
                                                            id="create-var-name",
                                                            label="New Variable Name",
                                                            placeholder="new_variable",
                                                            required=True,
                                                        ),
                                                        dmc.Textarea(
                                                            id="create-var-expression",
                                                            label="Expression",
                                                            placeholder="e.g., price * 1.1 or carat ** 2",
                                                            description="Use column names and Python operators",
                                                            minRows=3,
                                                            required=True,
                                                        ),
                                                        create_action_button(
                                                            button_id="create-var-btn",
                                                            label="Create Variable",
                                                            icon="carbon:add",
                                                        ),
                                                    ],
                                                    gap="md",
                                                )
                                            ],
                                            title="Create Variable",
                                        ),
                                    ],
                                    span=6,
                                ),
                                dmc.GridCol(
                                    [
                                        create_results_card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Text(
                                                            "Preview",
                                                            fw=600,
                                                            size="sm",
                                                        ),
                                                        html.Div(id="create-var-preview"),
                                                    ],
                                                    gap="sm",
                                                )
                                            ],
                                        ),
                                    ],
                                    span=6,
                                ),
                            ]),
                        ],
                        value="create",
                    ),
                    # Transform Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        create_control_card(
                                            [
                                                dmc.Select(
                                                    id="transform-var",
                                                    label="Variable to Transform",
                                                    placeholder="Select variable...",
                                                    searchable=True,
                                                ),
                                                dmc.Select(
                                                    id="transform-function",
                                                    label="Transformation",
                                                    data=[
                                                        {
                                                            "label": v[0],
                                                            "value": k,
                                                        }
                                                        for k, v in TRANSFORM_FUNCTIONS.items()
                                                        if k
                                                        in [
                                                            "center",
                                                            "standardize",
                                                            "square",
                                                            "inverse",
                                                            "ln",
                                                            "log10",
                                                            "exp",
                                                            "sqrt",
                                                        ]
                                                    ],
                                                    placeholder="Select transformation...",
                                                ),
                                                create_action_button(
                                                    button_id="apply-transform-btn",
                                                    label="Apply Transformation",
                                                    icon="carbon:function",
                                                ),
                                            ],
                                            title="Transform Variable",
                                        ),
                                    ],
                                    span=6,
                                ),
                            ]),
                        ],
                        value="transform",
                    ),
                    # Type Conversion Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        create_control_card(
                                            [
                                                dmc.Select(
                                                    id="type-var",
                                                    label="Variable",
                                                    placeholder="Select variable...",
                                                    searchable=True,
                                                ),
                                                dmc.Select(
                                                    id="type-target",
                                                    label="Convert To",
                                                    data=[
                                                        {
                                                            "label": "Integer",
                                                            "value": "integer",
                                                        },
                                                        {
                                                            "label": "Numeric (Float)",
                                                            "value": "numeric",
                                                        },
                                                        {
                                                            "label": "Factor (Categorical)",
                                                            "value": "factor",
                                                        },
                                                        {
                                                            "label": "Character (String)",
                                                            "value": "character",
                                                        },
                                                    ],
                                                    placeholder="Select target type...",
                                                ),
                                                create_action_button(
                                                    button_id="convert-type-btn",
                                                    label="Convert Type",
                                                    icon="carbon:data-class",
                                                ),
                                            ],
                                            title="Type Conversion",
                                        ),
                                    ],
                                    span=6,
                                ),
                            ]),
                        ],
                        value="type",
                    ),
                    # Binning Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        create_control_card(
                                            [
                                                dmc.Select(
                                                    id="bin-var",
                                                    label="Variable to Bin",
                                                    placeholder="Select numeric variable...",
                                                    searchable=True,
                                                ),
                                                dmc.NumberInput(
                                                    id="bin-n",
                                                    label="Number of Bins",
                                                    value=5,
                                                    min=2,
                                                    max=20,
                                                    step=1,
                                                ),
                                                dmc.TextInput(
                                                    id="bin-name",
                                                    label="New Variable Name",
                                                    placeholder="variable_bin",
                                                ),
                                                create_action_button(
                                                    button_id="create-bin-btn",
                                                    label="Create Bins",
                                                    icon="carbon:categories",
                                                ),
                                            ],
                                            title="Binning",
                                        ),
                                    ],
                                    span=6,
                                ),
                            ]),
                        ],
                        value="bin",
                    ),
                ],
                value="create",
            ),
            html.Div(id="transform-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1200px"},
    )


@callback(
    Output("transform-var", "data"),
    Output("type-var", "data"),
    Output("bin-var", "data"),
    Input("dataset-selector", "value"),
)
def update_transform_selectors(dataset_name):
    """Update variable selectors."""
    if not dataset_name:
        return [], [], []

    df = app_manager.data_manager.get_dataset(dataset_name)
    if df is None:
        return [], [], []

    all_vars = [{"label": col, "value": col} for col in df.columns]
    numeric_vars = [{"label": col, "value": col} for col in df.columns if df[col].dtype in ["int64", "float64"]]

    return all_vars, all_vars, numeric_vars


@callback(
    Output("transform-notification", "children"),
    Output("app-state", "data", allow_duplicate=True),
    Input("create-var-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("create-var-name", "value"),
    State("create-var-expression", "value"),
    prevent_initial_call=True,
)
def create_new_variable(n_clicks, dataset_name, var_name, expression):
    """Create a new variable from expression."""
    if not n_clicks or not dataset_name or not var_name or not expression:
        return dash.no_update, dash.no_update

    df = app_manager.data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Notification(
            title="Error",
            message="Could not load dataset",
            color="red",
            action="show",
        ), dash.no_update

    try:
        df_new = create_variable(df, var_name, expression)
        app_manager.data_manager.add_dataset(
            dataset_name,
            df_new,
            description=app_manager.data_manager.descriptions.get(dataset_name, ""),
            load_command=app_manager.data_manager.load_commands.get(dataset_name, ""),
        )

        return dmc.Notification(
            title="Success",
            message=f"Created variable '{var_name}'",
            color="green",
            action="show",
            icon=DashIconify(icon="carbon:checkmark"),
        ), {"timestamp": dash.callback_context.triggered[0]["value"]}

    except Exception as e:
        return dmc.Notification(
            title="Error",
            message=f"Could not create variable: {str(e)}",
            color="red",
            action="show",
        ), dash.no_update


@callback(
    Output("transform-notification", "children", allow_duplicate=True),
    Output("app-state", "data", allow_duplicate=True),
    Input("apply-transform-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("transform-var", "value"),
    State("transform-function", "value"),
    prevent_initial_call=True,
)
def apply_transformation(n_clicks, dataset_name, var, function):
    """Apply transformation to variable."""
    if not n_clicks or not dataset_name or not var or not function:
        return dash.no_update, dash.no_update

    df = app_manager.data_manager.get_dataset(dataset_name)
    if df is None:
        return dash.no_update, dash.no_update

    try:
        from utils.transforms import mutate_ext

        df_new = mutate_ext(df, var, function)
        app_manager.data_manager.add_dataset(
            dataset_name,
            df_new,
            description=app_manager.data_manager.descriptions.get(dataset_name, ""),
            load_command=app_manager.data_manager.load_commands.get(dataset_name, ""),
        )

        return dmc.Notification(
            title="Success",
            message=f"Applied {function} to {var}",
            color="green",
            action="show",
        ), {"timestamp": "transform"}

    except Exception as e:
        return dmc.Notification(
            title="Error",
            message=f"Transformation failed: {str(e)}",
            color="red",
            action="show",
        ), dash.no_update
