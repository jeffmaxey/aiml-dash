"""
Sampling Page
=============

Generate random samples using different sampling methods.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np

from components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the Sampling page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Sampling",
                "Generate random samples from your dataset using various sampling methods (random, stratified, cluster).",
                icon="carbon:diagram-reference",
            ),
            create_two_column_layout(
                create_control_card(
                    [
                        dmc.Select(
                            id="sampling-method",
                            label="Sampling method",
                            value="random",
                            data=[
                                {
                                    "label": "Random",
                                    "value": "random",
                                },
                                {
                                    "label": "Stratified",
                                    "value": "stratified",
                                },
                                {
                                    "label": "Cluster",
                                    "value": "cluster",
                                },
                            ],
                        ),
                        dmc.NumberInput(
                            id="sampling-size",
                            label="Sample size",
                            value=100,
                            min=1,
                            step=1,
                        ),
                        dmc.Select(
                            id="sampling-strata-var",
                            label="Stratification variable",
                            placeholder="Select variable...",
                            data=[],
                        ),
                        dmc.NumberInput(
                            id="sampling-seed",
                            label="Random seed",
                            value=1234,
                            min=0,
                        ),
                        create_action_button(
                            button_id="sampling-generate",
                            label="Generate Sample",
                            icon="carbon:play",
                            color="green",
                        ),
                    ],
                ),
                create_results_card(
                    [
                        dmc.Title("Sample Summary", order=4),
                        html.Div(id="sampling-summary"),
                    ],
                ),
            ),
            dcc.Store(id="sampling-result"),
            dcc.Download(id="sampling-download-data"),
        ],
        fluid=True,
    )


# Callbacks


@callback(
    Output("sampling-strata-var", "data"),
    Output("sampling-strata-var", "disabled"),
    Input("sampling-method", "value"),
)
def update_strata_options(method):
    """Update stratification variable options based on method."""
    if method == "stratified":
        # Get available datasets
        dataset_names = app_manager.data_manager.get_dataset_names()
        if dataset_names:
            # Get first dataset columns
            first_dataset = dataset_names[0]
            df = app_manager.data_manager.get_dataset(first_dataset)
            if df is not None:
                columns = [{"label": col, "value": col} for col in df.columns]
                return columns, False

    return [], True


@callback(
    Output("sampling-summary", "children"),
    Output("sampling-result", "data"),
    Input("sampling-generate", "n_clicks"),
    State("sampling-method", "value"),
    State("sampling-size", "value"),
    State("sampling-strata-var", "value"),
    State("sampling-seed", "value"),
    prevent_initial_call=True,
)
def generate_sample(n_clicks, method, size, strata_var, seed):
    """Generate sample from dataset."""
    dataset_names = app_manager.data_manager.get_dataset_names()
    if not dataset_names:
        return dmc.Alert(
            "No datasets available. Please load a dataset first.",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        ), None

    try:
        # Get first dataset
        dataset_name = dataset_names[0]
        df = app_manager.data_manager.get_dataset(dataset_name)

        if df is None:
            return dmc.Alert(
                "Error loading dataset.",
                color="red",
                icon=DashIconify(icon="carbon:warning"),
            ), None

        np.random.seed(seed if seed else 1234)

        # Perform sampling
        if method == "random":
            sample_df = df.sample(n=min(size, len(df)), random_state=seed)

        elif method == "stratified":
            if not strata_var or strata_var not in df.columns:
                return dmc.Alert(
                    "Please select a stratification variable.",
                    color="yellow",
                    icon=DashIconify(icon="carbon:warning"),
                ), None

            # Stratified sampling - proportional allocation
            sample_df = df.groupby(strata_var, group_keys=False).apply(
                lambda x: x.sample(n=max(1, int(size * len(x) / len(df))), random_state=seed)
            )

        elif method == "cluster":
            # Simple cluster sampling - random rows
            sample_df = df.sample(n=min(size, len(df)), random_state=seed)

        else:
            sample_df = df.sample(n=min(size, len(df)), random_state=seed)

        # Save sample to data manager
        app_manager.data_manager.add_dataset(f"{dataset_name}_sample", sample_df, f"Sample from {dataset_name}")

        # Create summary
        summary = dmc.Stack(
            [
                dmc.Alert(
                    f"Sample generated with {len(sample_df)} observations",
                    color="green",
                    icon=DashIconify(icon="carbon:checkmark"),
                ),
                dmc.SimpleGrid(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Original dataset", size="sm", c="dimmed"),
                                        dmc.Text(f"{len(df)} observations", fw=500),
                                    ],
                                    gap=0,
                                    align="center",
                                )
                            ],
                            withBorder=True,
                            p="xs",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Sample size", size="sm", c="dimmed"),
                                        dmc.Text(f"{len(sample_df)} observations", fw=500),
                                    ],
                                    gap=0,
                                    align="center",
                                )
                            ],
                            withBorder=True,
                            p="xs",
                        ),
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Sampling rate", size="sm", c="dimmed"),
                                        dmc.Text(
                                            f"{len(sample_df) / len(df) * 100:.1f}%",
                                            fw=500,
                                        ),
                                    ],
                                    gap=0,
                                    align="center",
                                )
                            ],
                            withBorder=True,
                            p="xs",
                        ),
                    ],
                    cols=3,
                ),
                dmc.Button(
                    "Download Sample (CSV)",
                    id="sampling-download-btn",
                    leftSection=DashIconify(icon="carbon:download", width=20),
                    variant="light",
                    color="blue",
                ),
                # Show sample preview
                dmc.Card(
                    [
                        dmc.Stack(
                            [
                                dmc.Text("Sample Preview (first 10 rows)", size="sm", fw=500),
                                dmc.Table(
                                    striped=True,
                                    highlightOnHover=True,
                                    withTableBorder=True,
                                    withColumnBorders=True,
                                    data={
                                        "head": list(sample_df.columns),
                                        "body": sample_df.head(10).values.tolist(),
                                    },
                                ),
                            ],
                            gap="xs",
                        )
                    ],
                    withBorder=True,
                    p="sm",
                    mt="md",
                ),
            ],
            gap="md",
        )

        return summary, sample_df.to_dict("records")

    except Exception as e:
        return dmc.Alert(
            f"Error generating sample: {str(e)}",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        ), None


@callback(
    Output("sampling-download-data", "data"),
    Input("sampling-download-btn", "n_clicks"),
    State("sampling-result", "data"),
    prevent_initial_call=True,
)
def download_sample(n_clicks, sample_data):
    """Download sample data."""
    if sample_data:
        df = pd.DataFrame(sample_data)
        return dcc.send_data_frame(df.to_csv, "sample_data.csv", index=False)
    return dash.no_update
