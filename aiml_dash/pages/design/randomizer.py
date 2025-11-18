"""
Randomizer Page
===============

Randomly assign subjects to treatment groups or generate random sequences.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the Randomizer page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Randomizer",
                "Randomly assign subjects to treatment groups with optional blocking and balance constraints.",
                icon="carbon:shuffle",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.NumberInput(
                                            id="rand-n-subjects",
                                            label="Number of subjects",
                                            value=100,
                                            min=2,
                                            step=1,
                                        ),
                                        dmc.NumberInput(
                                            id="rand-n-groups",
                                            label="Number of groups",
                                            value=2,
                                            min=2,
                                            max=10,
                                            step=1,
                                        ),
                                        dmc.Textarea(
                                            id="rand-group-names",
                                            label="Group names (one per line)",
                                            placeholder="Control\nTreatment",
                                            minRows=3,
                                        ),
                                        dmc.Select(
                                            id="rand-method",
                                            label="Randomization method",
                                            value="simple",
                                            data=[
                                                {
                                                    "label": "Simple randomization",
                                                    "value": "simple",
                                                },
                                                {
                                                    "label": "Block randomization",
                                                    "value": "block",
                                                },
                                                {
                                                    "label": "Stratified randomization",
                                                    "value": "stratified",
                                                },
                                            ],
                                        ),
                                        dmc.NumberInput(
                                            id="rand-seed",
                                            label="Random seed",
                                            value=1234,
                                            min=0,
                                        ),
                                        dmc.Button(
                                            "Randomize",
                                            id="rand-generate",
                                            leftSection=DashIconify(icon="carbon:shuffle", width=20),
                                            fullWidth=True,
                                            color="green",
                                        ),
                                        dmc.Divider(),
                                        dmc.Button(
                                            "Download Assignment (CSV)",
                                            id="rand-download",
                                            leftSection=DashIconify(icon="carbon:download", width=20),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Assignment Summary", order=4),
                                        html.Div(id="rand-summary"),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Random Assignment", order=4),
                                        html.Div(id="rand-table"),
                                    ],
                                    gap="xs",
                                )
                            ],
                            withBorder=True,
                            p="md",
                            mt="md",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            dcc.Store(id="rand-result"),
            dcc.Download(id="rand-download-data"),
        ],
        fluid=True,
    )


# Callbacks


@callback(
    Output("rand-summary", "children"),
    Output("rand-table", "children"),
    Output("rand-result", "data"),
    Input("rand-generate", "n_clicks"),
    State("rand-n-subjects", "value"),
    State("rand-n-groups", "value"),
    State("rand-group-names", "value"),
    State("rand-method", "value"),
    State("rand-seed", "value"),
    prevent_initial_call=True,
)
def generate_randomization(n_clicks, n_subjects, n_groups, group_names_text, method, seed):
    """Generate random assignment to treatment groups."""
    try:
        # Parse group names
        if group_names_text and group_names_text.strip():
            group_names = [name.strip() for name in group_names_text.split("\n") if name.strip()]
            if len(group_names) != n_groups:
                # Use default names if mismatch
                group_names = [f"Group {i + 1}" for i in range(n_groups)]
        else:
            group_names = [f"Group {i + 1}" for i in range(n_groups)]

        # Set random seed
        np.random.seed(seed if seed else 1234)

        # Generate randomization
        if method == "simple":
            # Simple randomization - completely random assignment
            assignments = np.random.choice(group_names, size=n_subjects)

        elif method == "block":
            # Block randomization - balanced within blocks
            block_size = n_groups * 2  # Block size is 2x number of groups
            n_blocks = int(np.ceil(n_subjects / block_size))
            assignments = []
            for _ in range(n_blocks):
                block = list(group_names) * 2  # Each group appears twice per block
                np.random.shuffle(block)
                assignments.extend(block)
            assignments = assignments[:n_subjects]  # Trim to exact size

        elif method == "stratified":
            # Stratified randomization - balanced overall
            base_size = n_subjects // n_groups
            remainder = n_subjects % n_groups
            assignments = []
            for i, group in enumerate(group_names):
                count = base_size + (1 if i < remainder else 0)
                assignments.extend([group] * count)
            np.random.shuffle(assignments)

        else:
            assignments = np.random.choice(group_names, size=n_subjects)

        # Create DataFrame
        df = pd.DataFrame({"subject_id": range(1, n_subjects + 1), "group": assignments})

        # Save to data manager
        data_manager.add_dataset("randomization", df, "Random group assignment")

        # Count assignments per group
        group_counts = df["group"].value_counts().sort_index()

        # Create summary
        summary = dmc.Stack(
            [
                dmc.Alert(
                    f"Randomized {n_subjects} subjects to {n_groups} groups",
                    color="green",
                    icon=DashIconify(icon="carbon:checkmark"),
                ),
                dmc.SimpleGrid(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text(group, size="sm", style={"color": "gray"}),
                                        dmc.Text(
                                            f"{count} subjects",
                                            style={"fontWeight": "bold"},
                                        ),
                                        dmc.Text(
                                            f"{count / n_subjects * 100:.1f}%",
                                            size="sm",
                                        ),
                                    ],
                                    gap=2,
                                    align="center",
                                )
                            ],
                            withBorder=True,
                            p="sm",
                        )
                        for group, count in group_counts.items()
                    ],
                    cols=min(n_groups, 4),
                ),
            ],
            gap="md",
        )

        # Create table
        table = dag.AgGrid(
            id="rand-assignment-grid",
            rowData=df.to_dict("records"),
            columnDefs=[
                {
                    "field": "subject_id",
                    "headerName": "Subject ID",
                    "sortable": True,
                    "filter": True,
                },
                {
                    "field": "group",
                    "headerName": "Group",
                    "sortable": True,
                    "filter": True,
                },
            ],
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
            style={"height": "400px"},
        )

        return summary, table, df.to_dict("records")

    except Exception as e:
        error_msg = dmc.Alert(
            f"Error generating randomization: {str(e)}",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
        return error_msg, None, None


@callback(
    Output("rand-download-data", "data"),
    Input("rand-download", "n_clicks"),
    State("rand-result", "data"),
    prevent_initial_call=True,
)
def download_randomization(n_clicks, result_data):
    """Download randomization assignment."""
    if result_data:
        df = pd.DataFrame(result_data)
        return dcc.send_data_frame(df.to_csv, "randomization.csv", index=False)
    return dash.no_update
