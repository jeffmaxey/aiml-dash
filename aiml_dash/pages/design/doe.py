"""
Design of Experiments (DOE) Page
=================================

Create factorial and fractional factorial experimental designs.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from itertools import product

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the DOE page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Design of Experiments",
                "Create (partial) factorial designs for experimental studies. Define factors and levels to generate optimal experimental designs.",
                icon="carbon:chemistry",
            ),
            dmc.Grid([
                # Left panel - design inputs
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Design Settings", order=4),
                                        dmc.NumberInput(
                                            id="doe-max-levels",
                                            label="Maximum levels",
                                            description="Maximum number of levels across all factors",
                                            value=2,
                                            min=2,
                                            max=10,
                                            step=1,
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.NumberInput(
                                                    id="doe-trials",
                                                    label="Number of trials",
                                                    description="Leave empty for automatic",
                                                    value=None,
                                                    min=1,
                                                    step=1,
                                                    style={"flex": 1},
                                                ),
                                                dmc.NumberInput(
                                                    id="doe-seed",
                                                    label="Random seed",
                                                    value=1234,
                                                    min=0,
                                                    step=1,
                                                    style={"flex": 1},
                                                ),
                                            ],
                                            grow=True,
                                        ),
                                        dmc.Divider(
                                            label="Add Factor",
                                            labelPosition="center",
                                        ),
                                        dmc.TextInput(
                                            id="doe-factor-name",
                                            label="Factor name",
                                            placeholder="e.g., price, temperature",
                                        ),
                                        dmc.TextInput(
                                            id="doe-level-1",
                                            label="Level 1",
                                            placeholder="e.g., low, $10",
                                        ),
                                        dmc.TextInput(
                                            id="doe-level-2",
                                            label="Level 2",
                                            placeholder="e.g., high, $20",
                                        ),
                                        html.Div(id="doe-extra-levels"),
                                        dmc.Group(
                                            [
                                                dmc.Button(
                                                    "Add Factor",
                                                    id="doe-add-factor",
                                                    leftSection=DashIconify(icon="carbon:add", width=20),
                                                    variant="light",
                                                    color="blue",
                                                ),
                                                dmc.Button(
                                                    "Remove Last",
                                                    id="doe-remove-factor",
                                                    leftSection=DashIconify(
                                                        icon="carbon:subtract",
                                                        width=20,
                                                    ),
                                                    variant="light",
                                                    color="red",
                                                ),
                                            ],
                                            grow=True,
                                        ),
                                        dmc.Divider(),
                                        dmc.MultiSelect(
                                            id="doe-interactions",
                                            label="Interactions",
                                            description="Select factor interactions to include",
                                            data=[],
                                            placeholder="Select interactions...",
                                            searchable=True,
                                        ),
                                        dmc.Button(
                                            "Create Design",
                                            id="doe-create-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
                                        ),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Export Design", order=4),
                                        dmc.Button(
                                            "Download Partial Design (CSV)",
                                            id="doe-download-partial",
                                            leftSection=DashIconify(icon="carbon:download", width=20),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                        dmc.Button(
                                            "Download Full Design (CSV)",
                                            id="doe-download-full",
                                            leftSection=DashIconify(icon="carbon:download", width=20),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                        dmc.Button(
                                            "Save to Dataset",
                                            id="doe-save-dataset",
                                            leftSection=DashIconify(icon="carbon:save", width=20),
                                            color="blue",
                                            fullWidth=True,
                                        ),
                                    ],
                                    gap="sm",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                            mt="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                # Right panel - design output
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Design Factors", order=4),
                                        dmc.Textarea(
                                            id="doe-factors-display",
                                            placeholder="Factors will appear here after adding them...\n\nFormat: factor_name; level1; level2; ...",
                                            minRows=6,
                                            autosize=True,
                                        ),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Design Summary", order=4),
                                        html.Div(id="doe-summary"),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                            mt="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Experimental Design", order=4),
                                        html.Div(id="doe-design-table"),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                            mt="md",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden components
            dcc.Store(id="doe-factors-store", data=[]),
            dcc.Download(id="doe-download-partial-data"),
            dcc.Download(id="doe-download-full-data"),
            html.Div(id="doe-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks


@callback(
    Output("doe-factors-store", "data"),
    Output("doe-factors-display", "value"),
    Output("doe-interactions", "data"),
    Output("doe-factor-name", "value"),
    Output("doe-level-1", "value"),
    Output("doe-level-2", "value"),
    Input("doe-add-factor", "n_clicks"),
    Input("doe-remove-factor", "n_clicks"),
    State("doe-factor-name", "value"),
    State("doe-level-1", "value"),
    State("doe-level-2", "value"),
    State("doe-max-levels", "value"),
    State("doe-factors-store", "data"),
    prevent_initial_call=True,
)
def manage_factors(add_clicks, remove_clicks, factor_name, level1, level2, max_levels, factors):
    """Manage the list of factors."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "doe-add-factor":
        # Add new factor
        if not factor_name or not level1 or not level2:
            return (
                factors,
                _format_factors_display(factors),
                _create_interaction_options(factors),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        # Create factor entry
        new_factor = {
            "name": factor_name.strip(),
            "levels": [level1.strip(), level2.strip()],
        }

        # Check if max levels exceeded
        if len(new_factor["levels"]) > max_levels:
            return (
                factors,
                _format_factors_display(factors),
                _create_interaction_options(factors),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        factors.append(new_factor)
        return (
            factors,
            _format_factors_display(factors),
            _create_interaction_options(factors),
            "",
            "",
            "",
        )

    elif button_id == "doe-remove-factor":
        # Remove last factor
        if factors:
            factors.pop()
        return (
            factors,
            _format_factors_display(factors),
            _create_interaction_options(factors),
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    return dash.no_update


@callback(
    Output("doe-summary", "children"),
    Output("doe-design-table", "children"),
    Output("doe-notification", "children"),
    Input("doe-create-btn", "n_clicks"),
    State("doe-factors-store", "data"),
    State("doe-interactions", "value"),
    State("doe-trials", "value"),
    State("doe-seed", "value"),
    prevent_initial_call=True,
)
def create_design(n_clicks, factors, interactions, n_trials, seed):
    """Create the experimental design."""
    if not factors:
        notification = dmc.Notification(
            title="No factors defined",
            message="Please add at least one factor before creating a design.",
            color="red",
            action="show",
            icon=DashIconify(icon="carbon:warning"),
        )
        return None, None, notification

    try:
        # Generate full factorial design
        np.random.seed(seed if seed else 1234)

        # Create all combinations of factor levels
        factor_names = [f["name"] for f in factors]
        factor_levels = [f["levels"] for f in factors]
        design_combinations = list(product(*factor_levels))

        # Create DataFrame
        df = pd.DataFrame(design_combinations, columns=factor_names)

        # Add interaction terms if specified
        if interactions:
            for interaction in interactions:
                parts = interaction.split(":")
                if len(parts) == 2 and parts[0] in df.columns and parts[1] in df.columns:
                    df[interaction] = df[parts[0]].astype(str) + ":" + df[parts[1]].astype(str)

        # Sample if n_trials specified
        if n_trials and n_trials < len(df):
            df = df.sample(n=n_trials, random_state=seed)
            df = df.reset_index(drop=True)

        # Add run order
        df.insert(0, "run", range(1, len(df) + 1))

        # Store design in data_manager
        data_manager.add_dataset("doe_design", df, "Generated DOE design")

        # Create summary
        summary = dmc.Stack(
            [
                dmc.Text("Design type: Full factorial", size="sm"),
                dmc.Text(f"Number of factors: {len(factors)}", size="sm"),
                dmc.Text(f"Number of runs: {len(df)}", size="sm"),
                dmc.Text(f"Total combinations: {len(design_combinations)}", size="sm"),
                dmc.Text(
                    f"Interactions: {len(interactions) if interactions else 0}",
                    size="sm",
                ),
            ],
            gap="xs",
        )

        # Create table
        table = dag.AgGrid(
            id="doe-design-grid",
            rowData=df.to_dict("records"),
            columnDefs=[{"field": col, "sortable": True, "filter": True} for col in df.columns],
            defaultColDef={
                "resizable": True,
                "sortable": True,
                "filter": True,
            },
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 20,
                "domLayout": "autoHeight",
            },
            style={"height": "500px"},
        )

        notification = dmc.Notification(
            title="Design created",
            message=f"Created design with {len(df)} runs",
            color="green",
            action="show",
            icon=DashIconify(icon="carbon:checkmark"),
        )

        return summary, table, notification

    except Exception as e:
        notification = dmc.Notification(
            title="Error creating design",
            message=str(e),
            color="red",
            action="show",
            icon=DashIconify(icon="carbon:warning"),
        )
        return None, None, notification


@callback(
    Output("doe-download-partial-data", "data"),
    Input("doe-download-partial", "n_clicks"),
    prevent_initial_call=True,
)
def download_partial(n_clicks):
    """Download partial design."""
    if "doe_design" in data_manager.datasets:
        df = data_manager.get_dataset("doe_design")
        return dcc.send_data_frame(df.to_csv, "doe_partial_design.csv", index=False)
    return dash.no_update


@callback(
    Output("doe-download-full-data", "data"),
    Input("doe-download-full", "n_clicks"),
    State("doe-factors-store", "data"),
    prevent_initial_call=True,
)
def download_full(n_clicks, factors):
    """Download full factorial design."""
    if not factors:
        return dash.no_update

    try:
        # Generate full factorial design
        factor_names = [f["name"] for f in factors]
        factor_levels = [f["levels"] for f in factors]
        design_combinations = list(product(*factor_levels))

        df = pd.DataFrame(design_combinations, columns=factor_names)
        df.insert(0, "run", range(1, len(df) + 1))

        return dcc.send_data_frame(df.to_csv, "doe_full_design.csv", index=False)
    except Exception:
        return dash.no_update


@callback(
    Output("doe-notification", "children", allow_duplicate=True),
    Input("doe-save-dataset", "n_clicks"),
    prevent_initial_call=True,
)
def save_to_dataset(n_clicks):
    """Save design to dataset manager."""
    if "doe_design" in data_manager.datasets:
        notification = dmc.Notification(
            title="Design saved",
            message="Design saved as 'doe_design' dataset",
            color="green",
            action="show",
            icon=DashIconify(icon="carbon:checkmark"),
        )
        return notification

    notification = dmc.Notification(
        title="No design to save",
        message="Please create a design first",
        color="yellow",
        action="show",
        icon=DashIconify(icon="carbon:warning"),
    )
    return notification


def _format_factors_display(factors):
    """Format factors for display."""
    if not factors:
        return ""

    lines = []
    for f in factors:
        levels = "; ".join(f["levels"])
        lines.append(f"{f['name']}; {levels}")

    return "\n".join(lines)


def _create_interaction_options(factors):
    """Create interaction options from factors."""
    if len(factors) < 2:
        return []

    factor_names = [f["name"] for f in factors]
    interactions = []

    for i in range(len(factor_names)):
        for j in range(i + 1, len(factor_names)):
            interaction = f"{factor_names[i]}:{factor_names[j]}"
            interactions.append({"label": interaction, "value": interaction})

    return interactions
