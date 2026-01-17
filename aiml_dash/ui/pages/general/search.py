"""
Search Page - Sequence Alignment and Matching Interface

This module implements the search/find sequences page where users can:
- Input query sequences for alignment
- Configure matching thresholds and parameters
- View matched sequences in a sortable table
- Visualize protein structures with highlighted residues
- Explore reaction data for matched sequences
- Analyze GoF (Gain of Function) and LoF (Loss of Function) residues

The page uses Dash Mantine Components for a modern, responsive UI with:
- Form inputs for sequence queries and parameters
- Interactive data tables with AG Grid
- 3D protein structure viewer
- Reaction image displays with SMILES strings
- Downloadable results in multiple formats

Components:
    - get_seq_align_form(): Input form for sequence alignment parameters
    - create_layout_reaction(): Reusable reaction image with SMILES display
    - get_similar_sequences_results_layout(): Results section with tables and visualizations
    - get_layout(): Main page layout composition

Author: Conversion to Mantine Components
Date: January 7, 2026
"""

import dash_mantine_components as dmc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app import global_strings_html as gsh
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.components.widgets import generate_label_with_info


def get_seq_align_form():
    """
    Create the sequence alignment input form.

    Generates a form with three main inputs:
    1. Query sequence text area - for entering amino acid sequences
    2. Threshold slider - for setting alignment similarity threshold
    3. Hot/Cold count - number of GoF/LoF variants to display

    The form includes:
    - Labels with info icons for guidance
    - Input validation and debouncing
    - Submit button for running sequence matching

    Returns:
        html.Div: Form layout with input fields and submit button

    Form Inputs:
        - id-input-query-sequence: Textarea for sequence input
        - id-input-query-sequence-threshold: Threshold value input
        - id-input-num-hot-cold: Number of variants input
        - id-button-run-seq-matching: Submit button
    """
    """
    Create the sequence alignment input form.
    
    Generates a form with three main inputs:
    1. Query sequence text area - for entering amino acid sequences
    2. Threshold slider - for setting alignment similarity threshold
    3. Hot/Cold count - number of GoF/LoF variants to display
    
    The form includes:
    - Labels with info icons for guidance
    - Input validation and debouncing
    - Submit button for running sequence matching
    
    Returns:
        html.Div: Form layout with input fields and submit button
        
    Form Inputs:
        - id-input-query-sequence: Textarea for sequence input
        - id-input-query-sequence-threshold: Threshold value input
        - id-input-num-hot-cold: Number of variants input
        - id-button-run-seq-matching: Submit button
    """
    # Main form container centered on page
    return html.Div(
        [
            # Query sequence input row
            dmc.Grid(
                [
                    # Label column
                    widgets.get_label_fixed_for_form(gs.seq_align_form_input),
                    # Input column
                    dmc.GridCol(
                        [
                            dmc.Textarea(
                                id="id-input-query-sequence",
                                value=gs.seq_align_form_input_sequence_default,
                                placeholder=gs.seq_align_form_placeholder,
                                autosize=True,
                                minRows=4,
                                w="100%",
                                className="dbc",
                            ),
                        ],
                        span="auto",
                    ),
                ],
                mb="xs",
                style=vis.border_row,
            ),
            # Threshold input row
            dmc.Grid(
                [
                    # Label column
                    widgets.get_label_fixed_for_form(gs.seq_align_form_threshold),
                    # Input column (fixed width)
                    dmc.GridCol(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-query-sequence-threshold",
                                input_value=gs.seq_align_form_threshold_default,
                                info_icon_help_string=gs.help_threshold,
                            )
                        ],
                        span=2,
                    ),
                ],
                mb="xs",
                style=vis.border_row,
            ),
            # Hot/Cold variants count input row
            dmc.Grid(
                [
                    # Label column
                    widgets.get_label_fixed_for_form(gs.seq_align_form_hot_cold),
                    # Input column (fixed width)
                    dmc.GridCol(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-num-hot-cold",
                                input_value=gs.seq_align_form_hot_cold_n,
                                info_icon_help_string=gs.help_gof_lof,
                            ),
                        ],
                        span=2,
                    ),
                ],
                mb="xs",
                style=vis.border_row,
            ),
            # Submit button row (centered)
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Button(
                            gs.seq_align_form_button_sequence_matching,
                            id="id-button-run-seq-matching",
                            n_clicks=0,
                            size="md",
                            fullWidth=True,
                        ),
                        span="auto",
                    ),
                ],
                mt="sm",
                mb="xl",
            ),
        ],
        style={
            "width": "60%",  # Form width as percentage
            "margin": "0 auto",  # Center horizontally
        },
    )


def create_layout_reaction(id_image, id_substrate_smiles, id_product_smiles):
    """
    Create a reaction visualization layout with substrate → product.

    This reusable component displays:
    - Reaction image showing the transformation
    - Substrate SMILES string (left column)
    - Product SMILES string (right column)

    The layout is responsive with the image scaling to container width.
    Used in multiple places across the search results.

    Args:
        id_image (str): Component ID for the reaction image element
        id_substrate_smiles (str): Component ID for substrate SMILES display
        id_product_smiles (str): Component ID for product SMILES display

    Returns:
        html.Div: Reaction layout with image and SMILES strings

    Layout Structure:
        - Top: Centered reaction image (scales to fit)
        - Bottom: Two-column grid with substrate (left) and product (right)

    Example:
        >>> layout = create_layout_reaction(
        ...     "reaction-img-1",
        ...     "substrate-smiles-1",
        ...     "product-smiles-1"
        ... )
    """
    # Container for reaction visualization
    return html.Div([
        # Reaction image row - centered and responsive
        dmc.Grid(
            [
                dmc.GridCol(
                    html.Img(
                        id=id_image,
                        className="mx-auto d-block",  # Center the image
                        style={"maxWidth": "100%"},  # Responsive width
                    ),
                    span=12,
                ),
            ],
        ),
        # SMILES strings row - two equal columns
        dmc.Grid(
            [
                # Substrate SMILES (left column)
                dmc.GridCol(
                    [
                        generate_label_with_info(
                            gs.sub_smiles,
                            id_substrate_smiles,
                        )
                    ],
                    span=6,  # Fixed width to prevent collapsing
                    style=vis.border_column,
                ),
                # Product SMILES (right column)
                dmc.GridCol(
                    [
                        generate_label_with_info(
                            gs.prod_smiles,
                            id_product_smiles,
                        )
                    ],
                    span=6,  # Fixed width to prevent collapsing
                    style=vis.border_column,
                ),
            ],
            p="sm",
        ),
    ])


def get_similar_sequences_results_layout():
    """
    Create the results section layout for matched sequences.

    This complex layout displays search results across three main areas:
    1. Matched sequences table (left) - sortable/filterable data grid
    2. Protein visualization (right top) - 3D structure with highlighted residues
    3. GoF/LoF residue data (bottom) - detailed variant analysis table

    Features:
    - Download options for both result tables
    - Interactive AG Grid tables with sorting/filtering
    - 3D protein viewer with residue highlighting
    - Reaction visualization for selected sequences
    - Color-coded residue highlights (GoF=red, LoF=blue, Both=purple)

    Returns:
        html.Div: Complete results layout (initially hidden)

    Component IDs:
        - id-div-seq-alignment-results: Main container (visibility controlled)
        - id-table-matched-sequences: Primary results table
        - id-viewer-selected-seq-matched-protein: 3D protein structure
        - id-selected-seq-matched-reaction-image: Reaction image
        - id-table-matched-sequences-exp-hot-cold-data: GoF/LoF data table

    Layout Structure:
        Row 1: Two-column layout
            - Left (width=7): Matched sequences table with download
            - Right (width=5): Protein viewer + reaction image
        Row 2: Full-width
            - GoF/LoF residue analysis table with download
    """
    # Main results container (hidden by default, shown when results available)
    return html.Div(
        id="id-div-seq-alignment-results",
        style=vis.display_none,  # Initially hidden
        children=[
            # Top row: Results table (left) and visualization (right)
            dmc.Grid(
                [
                    # Left column - Matched sequences table
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    # Card header
                                    dmc.CardSection(
                                        dmc.Text(
                                            gs.seg_align_results,
                                            size="lg",
                                            fw=600,
                                        ),
                                        withBorder=True,
                                        p="sm",
                                        className=vis.top_card_head,
                                    ),
                                    # Card body with table
                                    dmc.CardSection(
                                        [
                                            # Download controls and info row
                                            dmc.Grid(
                                                [
                                                    # Download button with format options
                                                    dmc.GridCol(
                                                        widgets.get_download_radio_combo(
                                                            "id-button-download-matched-sequences-results",
                                                            "id-button-download-matched-sequences-results-options",
                                                        ),
                                                        span="auto",
                                                        style=vis.border_column,
                                                    ),
                                                    # Info display with tooltip
                                                    dmc.GridCol(
                                                        [
                                                            dmc.Group(
                                                                [
                                                                    html.Span(
                                                                        id="id-div-matched-sequences-info",
                                                                        className="fw-bolder",
                                                                    ),
                                                                    html.Span(
                                                                        [
                                                                            widgets.get_info_icon_tooltip_bundle(
                                                                                info_icon_id="id-info-1",
                                                                                help_string=gsh.markdown_note_matched_seq,
                                                                                location="top",
                                                                                allow_html=True,
                                                                            )
                                                                        ],
                                                                        style={"margin": "5px"},
                                                                    ),
                                                                ],
                                                                gap="xs",
                                                                justify="flex-end",
                                                            ),
                                                        ],
                                                        span="auto",
                                                        style=vis.border_column,
                                                    ),
                                                ],
                                                mb="sm",
                                                gutter="xs",
                                                align="center",
                                            ),
                                            # Data table row
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        widgets.get_table_matched_sequences(),
                                                        span=12,
                                                    ),
                                                ],
                                                className="dbc dbc-ag-grid",
                                            ),
                                        ],
                                        p="xs",
                                        mt="md",
                                    ),
                                ],
                                shadow="sm",
                                radius="md",
                                withBorder=True,
                                h=vis.seq_match_card_height,
                            ),
                        ],
                        span=7,
                        style=vis.border_column,
                    ),
                    # Right column - Protein viewer and reaction
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    # Card header
                                    dmc.CardSection(
                                        dmc.Text(
                                            gs.seq_align_visualize,
                                            size="lg",
                                            fw=600,
                                        ),
                                        withBorder=True,
                                        p="sm",
                                        className=vis.top_card_head,
                                    ),
                                    # Card body with reaction and protein viewer
                                    dmc.CardSection(
                                        [
                                            # Reaction visualization (top)
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        create_layout_reaction(
                                                            "id-selected-seq-matched-reaction-image",
                                                            "id-selected-seq-matched-substrate",
                                                            "id-selected-seq-matched-product",
                                                        ),
                                                        span=12,
                                                    ),
                                                ],
                                                mb="sm",
                                                className="border rounded-1",
                                                p="xs",
                                            ),
                                            # 3D Protein viewer (middle)
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        html.Div(id="id-viewer-selected-seq-matched-protein"),
                                                        span=12,
                                                    ),
                                                ],
                                            ),
                                            # Residue highlight legend (bottom)
                                            dmc.Stack(
                                                [
                                                    widgets.generate_label_with_info(
                                                        label="Residue with both GoF and LoF (purple):",
                                                        id_info="id-div-selected-seq-matched-protein-highlights-info1",
                                                    ),
                                                    widgets.generate_label_with_info(
                                                        label="Residue with GoF only (red): ",
                                                        id_info="id-div-selected-seq-matched-protein-highlights-info2",
                                                    ),
                                                    widgets.generate_label_with_info(
                                                        label="Residue with LoF only (blue): ",
                                                        id_info="id-div-selected-seq-matched-protein-highlights-info3",
                                                    ),
                                                ],
                                                gap="xs",
                                            ),
                                        ],
                                        p="xs",
                                        mb="md",
                                    ),
                                ],
                                shadow="sm",
                                radius="md",
                                withBorder=True,
                                h=vis.seq_match_card_height,
                            ),
                        ],
                        span=5,
                        style=vis.border_column,
                    ),
                ],
                gutter="sm",
                mt="lg",
                mb="lg",
            ),
            # Bottom row: GoF/LoF residue data table (full width)
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    # Card header
                                    dmc.CardSection(
                                        dmc.Text(
                                            gs.seq_align_residues,
                                            size="lg",
                                            fw=600,
                                        ),
                                        withBorder=True,
                                        p="sm",
                                        className=vis.top_card_head,
                                    ),
                                    # Card body with download and table
                                    dmc.CardSection(
                                        [
                                            # Download controls row
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        widgets.get_download_radio_combo(
                                                            "id-button-download-hot-cold-results",
                                                            "id-button-download-hot-cold-results-options",
                                                        ),
                                                        span="auto",
                                                    ),
                                                ],
                                                mb="sm",
                                                gutter="xs",
                                            ),
                                            # Data table row
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        widgets.get_table_matched_sequences_exp_hot_cold_data(),
                                                        span=12,
                                                    ),
                                                ],
                                                className="dbc dbc-ag-grid",
                                            ),
                                        ],
                                        p="xs",
                                        mt="md",
                                    ),
                                ],
                                shadow="sm",
                                radius="md",
                                withBorder=True,
                            ),
                        ],
                        span=12,
                        style=vis.border_column,
                    ),
                ],
                mt="lg",
                mb="lg",
            ),
        ],
    )


def get_layout():
    """
    Create the main search page layout.

    Assembles the complete sequence search interface with:
    - Page header and description
    - Sequence alignment input form
    - Summary and alert message areas
    - Loading indicator
    - Results section (tables, protein viewer, reaction display)

    The layout uses a vertical flow with:
    1. Title and introductory text at top
    2. Centered input form
    3. Status message containers
    4. Loading spinner wrapping results
    5. Results section (hidden until search completes)

    Returns:
        html.Div: Complete page layout with all components

    Component IDs:
        - id-summary-seq-alignment: Summary message container
        - id-alert-seq-alignment: Alert message container
        - id-table-matched-sequences: Results table (loading trigger)

    Loading Behavior:
        - Spinner appears when table data is loading
        - Blur effect applied to underlying content
        - Results section becomes visible when data loads
    """
    # Main page container
    return html.Div(
        [
            # Page header section
            html.Div(
                [
                    dmc.Title(gs.nav_find_seq, order=4, className="page-title"),
                    dmc.Divider(size="sm"),
                    # Introductory text with padding
                    dmc.Text(
                        gsh.seq_align_blurb,
                        px="xl",
                        c="blue",
                        style={"whiteSpace": "pre-wrap"},
                    ),
                ],
            ),
            # Form section - centered input form
            dmc.Grid(
                [
                    dmc.GridCol(
                        [get_seq_align_form()],
                        span=12,
                    ),
                ],
            ),
            # Summary message container (dynamically populated)
            html.Div(
                id="id-summary-seq-alignment",
                className="d-flex justify-content-center",
            ),
            # Alert message container (dynamically populated)
            html.Div(
                id="id-alert-seq-alignment",
                className="d-flex justify-content-center",
            ),
            # Results section with loading spinner
            dcc.Loading(
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                type="circle",
                color="var(--bs-secondary)",
                # Loading triggered by results table data updates
                target_components={"id-table-matched-sequences": "rowData"},
                children=get_similar_sequences_results_layout(),
            ),
        ],
        className=vis.main_page_class,
    )
