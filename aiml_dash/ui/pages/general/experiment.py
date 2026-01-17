"""
Experiment Page Layout Module

This module provides the main experiment dashboard layout using Dash Mantine Components.
It displays experiment details, protein sequence information, visualization plots,
and tools for analyzing related variants.

Components:
    - Slider controls for residue visualization
    - EPPCR (Error-Prone PCR) plot layout
    - Single-site mutagenesis plot layout
    - Main experiment dashboard with multiple sections
    - Sequence alignment form
    - Related variants results card
    - Tab-based navigation

Author: AIML Dash Team
Date: 2026-01-07
"""

import dash_mantine_components as dmc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app import global_strings_html as gsh
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.components.widgets import generate_label_with_info


def get_slider_area_layout():
    """
    Create the slider control area for residue filtering and visualization.

    This component includes:
    - A switch to toggle between all residues and filtered view
    - A dropdown to select SMILES for residue highlighting
    - A range slider for filtering residues by ratio

    Returns:
        dmc.Card: A Mantine card containing the slider controls
    """
    return dmc.Card(
        [
            # Top row: Switch and SMILES selection dropdown
            dmc.Grid(
                [
                    # Column 1: View toggle switch with info icon
                    dmc.GridCol(
                        dmc.Group(
                            [
                                dmc.Switch(
                                    id="id-switch-residue-view",
                                    className="custom-switch",
                                    label=gs.view_all,
                                    checked=False,  # Mantine uses 'checked' instead of 'value'
                                ),
                                widgets.get_info_icon_tooltip_bundle(
                                    info_icon_id="id-switch-residue-view-info",
                                    help_string=gs.exp_slider_help,
                                    location="top",
                                ),
                            ],
                            gap="xs",
                        ),
                        span=4,
                    ),
                    # Column 2: Label for SMILES selection
                    dmc.GridCol(
                        dmc.Text(
                            gs.select_smiles,
                            ta="right",  # Text align right
                            size="sm",
                        ),
                        style=vis.border_column,
                    ),
                    # Column 3: SMILES dropdown selector
                    dmc.GridCol(
                        dcc.Dropdown(
                            id="id-list-smiles-residue-highlight",
                            disabled=True,
                        ),
                        style=vis.border_column,
                    ),
                ],
                align="center",
                mt="sm",
                px="xs",
            ),
            # Bottom section: Filtered residue display and range slider
            dmc.Stack(
                [
                    html.Div(
                        id="id-div-filtered-residue",
                        children="",
                        className="mt-3 text-body fw-bolder",
                    ),
                    dcc.RangeSlider(
                        id="id-slider-ratio",
                        min=0,
                        marks=None,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": True,
                        },
                        className="custom-slider fw-bold mt-3 mb-3",
                        disabled=True,
                    ),
                ],
                style=vis.border_row,
                gap="xs",
            ),
        ],
        withBorder=True,
        radius="sm",
    )


def get_eppcr_plot_layout():
    """
    Create the EPPCR (Error-Prone PCR) retention of function plot layout.

    This component displays a ranking plot showing retention of function
    across different plates and SMILES configurations for EPPCR experiments.

    Returns:
        dmc.Card: A Mantine card containing the EPPCR plot and controls
    """
    return dmc.Card(
        [
            # Card header
            dmc.Text(
                gs.retention_function,
                className=vis.top_card_head,
                fw=700,
                size="lg",
            ),
            # Card body with dropdowns and graph
            dmc.Stack(
                [
                    # Dropdown controls row
                    dmc.Grid(
                        [
                            # Plate selection dropdown
                            dmc.GridCol(
                                dmc.Stack(
                                    [
                                        dmc.Text(gs.select_plate, size="sm", fw=500),
                                        dcc.Dropdown(id="id-list-plates-ranking-plot"),
                                    ],
                                    gap="xs",
                                    className="dbc",
                                ),
                                style=vis.border_column,
                            ),
                            # SMILES selection dropdown
                            dmc.GridCol(
                                dmc.Stack(
                                    [
                                        dmc.Text(gs.select_smiles, size="sm", fw=500),
                                        dcc.Dropdown(id="id-list-smiles-ranking-plot"),
                                    ],
                                    gap="xs",
                                    className="dbc",
                                ),
                                style=vis.border_column,
                            ),
                        ],
                        gutter="xs",
                    ),
                    # Plotly graph component
                    html.Div(
                        [dcc.Graph("id-experiment-ranking-plot")],
                        style=vis.border_row,
                    ),
                ],
                gap="sm",
                p="sm",  # Padding to prevent graph from clamping to card edges
                style=vis.border_card,
            ),
        ],
        style=vis.card_shadow,
        withBorder=True,
    )


def get_ssm_plot_layout():
    """
    Create the Single-Site Mutagenesis (SSM) plot layout.

    This component displays mutation effects at individual residue positions
    for single-site mutagenesis experiments.

    Returns:
        dmc.Card: A Mantine card containing the SSM plot and controls
    """
    return dmc.Card(
        [
            # Card header
            dmc.Text(
                "Single Site Mutagenesis",
                className=vis.top_card_head,
                fw=700,
                size="lg",
            ),
            # Card body with dropdowns and graph
            dmc.Stack(
                [
                    # Dropdown controls row
                    dmc.Grid(
                        [
                            # Residue position selection dropdown
                            dmc.GridCol(
                                dmc.Stack(
                                    [
                                        dmc.Text("Select Residue Position", size="sm", fw=500),
                                        dcc.Dropdown(id="id-list-ssm-residue-positions"),
                                    ],
                                    gap="xs",
                                    className="dbc",
                                ),
                                style=vis.border_column,
                            ),
                            # SMILES selection dropdown
                            dmc.GridCol(
                                dmc.Stack(
                                    [
                                        dmc.Text(gs.select_smiles, size="sm", fw=500),
                                        dcc.Dropdown(id="id-list-smiles-ssm-plot"),
                                    ],
                                    gap="xs",
                                    className="dbc",
                                ),
                                style=vis.border_column,
                            ),
                        ],
                        gutter="xs",
                    ),
                    # Plotly graph component
                    html.Div(
                        [dcc.Graph("id-experiment-ssm-plot")],
                        style=vis.border_row,
                    ),
                ],
                gap="sm",
                p="sm",  # Padding to prevent graph from clamping to card edges
                style=vis.border_card,
            ),
        ],
        style=vis.card_shadow,
        withBorder=True,
    )


def get_tab_experiment_main():
    """
    Create the main experiment dashboard tab.

    This is the primary view that displays comprehensive experiment information including:
    - Protein sequence
    - Experiment metadata and reaction images
    - Top variants table
    - 3D protein structure viewer
    - Heatmap visualization
    - Ranking/SSM plots

    Returns:
        dmc.Container: A fluid container with all experiment dashboard components
    """
    return dmc.Container(
        [
            # Spacing at top
            dmc.Space(h="md"),
            # ==========================================
            # SECTION 1: Protein Sequence Card
            # ==========================================
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Card(
                            [
                                dmc.Text(
                                    gs.sequence,
                                    className=vis.top_card_head,
                                    fw=700,
                                    size="lg",
                                ),
                                html.Div(
                                    id="id-experiment-sequence",
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                            withBorder=True,
                        ),
                        style=vis.border_column,
                    ),
                ],
            ),
            dmc.Space(h="md"),
            # ==========================================
            # SECTION 2: Experiment Info and Reaction Cards
            # ==========================================
            dmc.Grid(
                [
                    # Experiment Info Card
                    dmc.GridCol(
                        dmc.Card(
                            [
                                dmc.Text(
                                    "Experiment Info",
                                    className=vis.top_card_head,
                                    fw=700,
                                    size="lg",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                generate_label_with_info(gs.experiment, "id-experiment-name"),
                                                generate_label_with_info(gs.paper_doi, "id-experiment-doi"),
                                                generate_label_with_info(gs.date, "id-experiment-date"),
                                                generate_label_with_info(gs.upload_date, "id-experiment-upload"),
                                                generate_label_with_info(
                                                    gs.technique, "id-experiment-mutagenesis-method"
                                                ),
                                                generate_label_with_info(gs.assay, "id-experiment-assay"),
                                                generate_label_with_info(gs.plates_count, "id-experiment-plate-count"),
                                                generate_label_with_info(gs.smiles_file, "id-experiment-file-smiles"),
                                                generate_label_with_info(
                                                    gs.additional_info, "id-experiment-additional-info"
                                                ),
                                            ],
                                            className="overflow-auto",
                                            style={
                                                # Allow long SMILES strings to break appropriately
                                                "wordBreak": "break-all",
                                                "whiteSpace": "normal",
                                                "minWidth": "150px",
                                                "maxHeight": "280px",  # Limit height with scroll
                                            },
                                        )
                                    ],
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                            withBorder=True,
                        ),
                        className="mb-3",
                        style=vis.border_column,
                    ),
                    # Reaction Image Card
                    dmc.GridCol(
                        dmc.Card(
                            [
                                dmc.Text(
                                    gs.reaction,
                                    className=vis.top_card_head,
                                    fw=700,
                                    size="lg",
                                ),
                                dmc.Stack(
                                    [
                                        # Reaction image
                                        html.Img(
                                            id="id-experiment-reaction-image",
                                            className="mx-auto d-block",  # Center the image
                                        ),
                                        # Substrate and product SMILES
                                        dmc.Grid(
                                            [
                                                dmc.GridCol(
                                                    [
                                                        generate_label_with_info(
                                                            gs.sub_smiles, "id-experiment-substrate"
                                                        )
                                                    ],
                                                    span=6,
                                                ),
                                                dmc.GridCol(
                                                    [generate_label_with_info(gs.prod_smiles, "id-experiment-product")],
                                                ),
                                            ],
                                            style=vis.border_row,
                                            p="sm",
                                        ),
                                    ],
                                    gap="xs",
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                            withBorder=True,
                        ),
                        style=vis.border_column,
                        className="mb-3",
                    ),
                ],
            ),
            dmc.Space(h="md"),
            # ==========================================
            # SECTION 3: Top Variants Table and Protein Viewer
            # ==========================================
            dmc.Grid(
                [
                    # Top Variants Table Card
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    dmc.Text(
                                        gs.top_variants,
                                        className=vis.top_card_head,
                                        fw=700,
                                        size="lg",
                                    ),
                                    dmc.Stack(
                                        [
                                            html.Div(
                                                [widgets.get_table_experiment_top_variants()],
                                                className="dbc dbc-ag-grid",
                                            )
                                        ],
                                        p="xs",
                                        mt="md",
                                    ),
                                ],
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                },
                                withBorder=True,
                            ),
                        ],
                        span=6,
                        style=vis.border_column,
                    ),
                    # Protein Viewer Card
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    dmc.Text(
                                        gs.viewer_header,
                                        className=vis.top_card_head,
                                        fw=700,
                                        size="lg",
                                    ),
                                    dmc.Stack(
                                        [
                                            # Slider controls
                                            html.Div(
                                                [get_slider_area_layout()],
                                                style={"padding": "8px"},
                                            ),
                                            # 3D protein viewer
                                            html.Div(widgets.get_protein_viewer()),
                                        ],
                                        gap="xs",
                                    ),
                                ],
                                style=vis.card_shadow,
                                withBorder=True,
                            ),
                        ],
                        span=6,
                        style=vis.border_column,
                    ),
                ],
            ),
            dmc.Space(h="lg"),
            # ==========================================
            # SECTION 4: Heatmap and Ranking/SSM Plots
            # ==========================================
            dmc.Grid(
                [
                    # Well Plate Heatmap Card
                    dmc.GridCol(
                        dmc.Card(
                            [
                                dmc.Text(
                                    gs.well_heatmap,
                                    className=vis.top_card_head,
                                    fw=700,
                                    size="lg",
                                ),
                                dmc.Stack(
                                    [
                                        # Dropdown controls for heatmap
                                        dmc.Grid(
                                            [
                                                # Property selection
                                                dmc.GridCol(
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(gs.select_property, size="sm", fw=500),
                                                            dcc.Dropdown(id="id-list-properties"),
                                                        ],
                                                        gap="xs",
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                                # Plate selection
                                                dmc.GridCol(
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(gs.select_plate, size="sm", fw=500),
                                                            dcc.Dropdown(id="id-list-plates"),
                                                        ],
                                                        gap="xs",
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                                # SMILES selection
                                                dmc.GridCol(
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(gs.select_smiles, size="sm", fw=500),
                                                            dcc.Dropdown(id="id-list-smiles"),
                                                        ],
                                                        gap="xs",
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                            ],
                                            gutter="xs",
                                        ),
                                        # Heatmap graph
                                        html.Div(
                                            [dcc.Graph("id-experiment-heatmap")],
                                            style=vis.border_row,
                                        ),
                                    ],
                                    gap="sm",
                                    p="sm",
                                    style=vis.border_card,
                                ),
                            ],
                            style=vis.card_shadow,
                            withBorder=True,
                        ),
                        span=6,
                        style=vis.border_column,
                    ),
                    # Ranking/SSM Plot Container (togglable)
                    dmc.GridCol(
                        [
                            # EPPCR retention plot (initially hidden)
                            html.Div(
                                id="id-ranking-plot-container",
                                children=get_eppcr_plot_layout(),
                                style={"display": "none"},
                            ),
                            # SSM plot (initially hidden)
                            html.Div(
                                id="id-ssm-plot-container",
                                children=get_ssm_plot_layout(),
                                style={"display": "none"},
                            ),
                        ],
                        span=6,
                        style=vis.border_column,
                    ),
                ],
            ),
        ],
        fluid=True,
        className="g-0 p-1 bs-light-bg-subtle",
        style={},
    )


def get_seq_align_form_exp():
    """
    Create the sequence alignment form for finding related variants.

    This form allows users to:
    - View the query sequence
    - Set similarity threshold
    - Specify residue positions of interest
    - Submit search for related variants

    Returns:
        dmc.Stack: A vertical stack containing the form elements
    """
    return dmc.Stack(
        [
            # Form title
            dmc.Text(
                gs.exp_seq_align_form_input,
                fw=700,
                size="sm",
            ),
            # Query sequence display (populated by callback)
            html.Div(
                id="id-input-exp-related-variants-query-sequence",
                style={
                    "whiteSpace": "normal",
                    "wordWrap": "break-word",
                    "fontSize": "0.85rem",
                },
                className="text-muted mb-1",
            ),
            # Threshold input field
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.seq_align_form_threshold),
                    dmc.GridCol(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-exp-related-variants-threshold",
                                input_value=gs.seq_align_form_threshold_default,
                                info_icon_help_string=gs.help_threshold,
                            ),
                        ],
                        span=3,
                    ),
                ],
                style=vis.border_row,
            ),
            # Residue position input field
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.exp_seq_align_residue),
                    dmc.GridCol(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-exp-related-variants-residue",
                                input_value="",
                                info_icon_help_string=gs.exp_seq_align_residue_help,
                            ),
                        ],
                        span=3,
                    ),
                ],
                style=vis.border_row,
            ),
            # Submit button (centered)
            dmc.Center(
                dmc.Button(
                    gs.seq_align_form_button_sequence_matching,
                    id="id-button-run-seq-matching-exp",
                    n_clicks=0,
                    size="md",
                    fullWidth=True,
                ),
                mt="xl",
                mb="xl",
            ),
        ],
        gap="sm",
    )


def get_card_experiment_related_variants_result():
    """
    Create the results card for related variants comparison.

    This complex card displays side-by-side comparison of:
    - Experiment metadata
    - Reaction images
    - SMILES strings
    - Protein structures
    - Variant substitutions

    Returns:
        dmc.Card: A comprehensive card showing query and selected variant comparison
    """
    return dmc.Card(
        [
            # Card header
            dmc.Text(
                gs.exp_seq_align_related_experiments,
                className=vis.top_card_head,
                fw=700,
                size="lg",
            ),
            # Card body with comparison sections
            dmc.Stack(
                [
                    # ==========================================
                    # Section 1: Experiment IDs (Query vs Selected)
                    # ==========================================
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                [generate_label_with_info(gs.exp_seq_align_query_info_2, "id-exp-related-variants-id")],
                                span=6,
                                className="p-1",
                                style={"borderRight": "1px solid #dee2e6"},
                            ),
                            dmc.GridCol(
                                [
                                    generate_label_with_info(
                                        gs.exp_seq_align_query_info_1, "id-exp-related-variants-selected-id"
                                    )
                                ],
                                className="p-1",
                            ),
                        ],
                        gutter="xs",
                        mt="xs",
                        style={"border": "1px solid #dee2e6"},
                    ),
                    # ==========================================
                    # Section 2: Reaction Images (Query vs Selected)
                    # ==========================================
                    dmc.Grid(
                        [
                            # Query reaction image
                            dmc.GridCol(
                                [
                                    html.Img(
                                        id="id-exp-related-variants-reaction-image",
                                        className="mx-auto d-block",
                                        style={
                                            "width": "100%",
                                            "objectFit": "contain",
                                        },
                                    ),
                                ],
                                span=6,
                                style={"borderRight": "1px solid #dee2e6"},
                            ),
                            # Selected variant reaction image
                            dmc.GridCol(
                                [
                                    html.Img(
                                        id="id-exp-related-variants-selected-reaction-image",
                                        className="mx-auto d-block",
                                        style={"maxWidth": "100%"},
                                    ),
                                ],
                            ),
                        ],
                        gutter="xs",
                        style={"border": "1px solid #dee2e6", "borderTop": "0", "borderBottom": "0"},
                    ),
                    # ==========================================
                    # Section 3: SMILES Strings (Substrate & Product)
                    # ==========================================
                    dmc.Grid(
                        [
                            # Query substrate
                            dmc.GridCol(
                                [generate_label_with_info(gs.sub_smiles, "id-exp-related-variants-substrate")],
                                span=3,
                                className="p-1",
                            ),
                            # Query product
                            dmc.GridCol(
                                [generate_label_with_info(gs.prod_smiles, "id-exp-related-variants-product")],
                                span=3,
                                className="p-1",
                                style={"borderRight": "1px solid #dee2e6"},
                            ),
                            # Selected substrate
                            dmc.GridCol(
                                [generate_label_with_info(gs.sub_smiles, "id-exp-related-variants-selected-substrate")],
                                span=3,
                                className="p-1",
                            ),
                            # Selected product
                            dmc.GridCol(
                                [generate_label_with_info(gs.prod_smiles, "id-exp-related-variants-selected-product")],
                                span=3,
                                className="p-2",
                            ),
                        ],
                        gutter="xs",
                        style={"border": "1px solid #dee2e6", "borderTop": "0"},
                    ),
                    # ==========================================
                    # Section 4: Download Controls and Viewer Headers
                    # ==========================================
                    dmc.Grid(
                        [
                            # Download button with radio options
                            dmc.GridCol(
                                [
                                    widgets.get_download_radio_combo(
                                        "id-button-download-related-variants-results",
                                        "id-button-download-related-variants-results-options",
                                    ),
                                ],
                                span=6,
                                style=vis.border_column,
                            ),
                            # Protein structure viewer headers
                            dmc.GridCol([
                                dmc.Grid(
                                    [
                                        dmc.GridCol(
                                            dmc.Text("Query Protein Structure", ta="center", fw=700),
                                            span=6,
                                            style=vis.border_column,
                                        ),
                                        dmc.GridCol(
                                            dmc.Text("Selected Protein Structure", ta="center", fw=700),
                                            style=vis.border_column,
                                        ),
                                    ],
                                ),
                            ]),
                        ],
                        align="end",
                        gutter="xs",
                        mt="md",
                        style=vis.border_row,
                    ),
                    # ==========================================
                    # Section 5: Variants Table and Protein Viewers
                    # ==========================================
                    dmc.Grid(
                        [
                            # Related variants table
                            dmc.GridCol(
                                [
                                    widgets.get_table_experiment_related_variants(),
                                ],
                                span=6,
                                className="p-1 dbc dbc-ag-grid",
                            ),
                            # Side-by-side protein viewers
                            dmc.GridCol(
                                [
                                    dmc.Grid(
                                        [
                                            # Query protein viewer
                                            dmc.GridCol(
                                                [
                                                    html.Div(id="id-exp-related-variants-protein-viewer"),
                                                ],
                                                span=6,
                                                style=vis.border_column,
                                            ),
                                            # Selected protein viewer
                                            dmc.GridCol(
                                                [
                                                    html.Div(id="id-exp-related-variants-selected-protein-viewer"),
                                                ],
                                                style=vis.border_column,
                                            ),
                                        ],
                                        gutter="xs",
                                        p="xs",
                                    ),
                                ],
                                className="p-1",
                            ),
                        ],
                    ),
                    # ==========================================
                    # Section 6: Substitutions Display
                    # ==========================================
                    dmc.Grid([
                        dmc.GridCol(span=6),  # Empty space for alignment
                        dmc.GridCol([
                            widgets.generate_label_with_info(
                                label=gs.exp_seq_align_substitutions,
                                id_info="id-exp-related-variants-selected-subs",
                            )
                        ]),
                    ]),
                ],
                gap="xs",
            ),
        ],
        style={
            "box-shadow": "1px 2px 7px 0px grey",
            "border-radius": "5px",
        },
        withBorder=True,
    )


def get_tab_experiment_related_variants():
    """
    Create the Related Variants tab content.

    This tab provides tools for searching and analyzing protein variants
    related to the current experiment based on sequence similarity.

    Returns:
        dmc.Stack: A vertical stack containing the related variants interface
    """
    return dmc.Stack(
        [
            # Tab title
            dmc.Title(
                "Search for related variants",
                order=4,
                className="page-title",
            ),
            # Introductory text
            dmc.Text(
                gsh.exp_seq_align_blurb,
                className="px-5 text-primary",
                style={"textWrap": "wrap"},
            ),
            # Search form (centered, 70% width)
            html.Div(
                [get_seq_align_form_exp()],
                style={
                    "width": "70%",
                    "margin": "0 auto",
                },
            ),
            # Summary display area (populated by callback)
            html.Div(
                id="id-summary-exp-related-variants",
                style={"display": "flex", "justifyContent": "center"},
            ),
            # Alert/message display area (populated by callback)
            html.Div(
                id="id-alert-exp-related-variants",
                style={"display": "flex", "justifyContent": "center"},
            ),
            # Results card with loading overlay
            dcc.Loading(
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                type="circle",
                color="var(--bs-secondary)",
                children=html.Div(
                    id="id-div-exp-related-variants",
                    style=vis.display_none,  # Initially hidden
                    children=[get_card_experiment_related_variants_result()],
                ),
                target_components={"id-table-exp-related-variants": "rowData"},
            ),
        ],
        gap="md",
        mt="lg",
    )


def get_layout():
    """
    Create the main experiment page layout with tab navigation.

    This is the top-level layout function that creates a tabbed interface with:
    - Tab 1: Main experiment dashboard
    - Tab 2: Related variants search and comparison

    The layout uses Dash Mantine Components for a modern, accessible interface.

    Returns:
        dmc.Container: The complete experiment page layout with tabs
    """
    return dmc.Container(
        [
            # Client-side storage for listbox state
            dcc.Store(id="id-exp-listbox-store"),
            # Mantine Tabs component
            dmc.Tabs(
                [
                    # Tab navigation list
                    dmc.TabsList([
                        dmc.TabsTab(
                            gs.tab_1,  # "Experiment Dashboard"
                            value="id-tab-exp-dash",
                        ),
                        dmc.TabsTab(
                            gs.tab_2,  # "Related Variants"
                            value="id-tab-exp-variants",
                        ),
                    ]),
                    # Tab 1: Main experiment dashboard
                    dmc.TabsPanel(
                        get_tab_experiment_main(),
                        value="id-tab-exp-dash",
                    ),
                    # Tab 2: Related variants search
                    dmc.TabsPanel(
                        get_tab_experiment_related_variants(),
                        value="id-tab-exp-variants",
                    ),
                ],
                value="id-tab-exp-dash",  # Default active tab
                className="custom-tab-container",
            ),
        ],
        className=vis.main_page_class,
        fluid=True,
    )
