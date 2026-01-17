"""
Reusable UI widget components for the LevSeq Dash application.

This module provides a comprehensive library of pre-configured UI components
built with Dash Mantine Components (DMC). These widgets are used throughout
the application for consistent user interface elements.

Component Categories:
    - **Tables**: AG Grid table configurations for various data views
        * Experiment dashboards (top variants, related variants)
        * Laboratory-wide views (all experiments)
        * Sequence alignment results (matched sequences, hot/cold spots)

    - **Viewers**: Interactive visualization components
        * Molstar protein structure viewer

    - **Form Elements**: Mantine input controls with integrated help
        * Text components with fixed widths for horizontal forms
        * Text inputs with info icon tooltips
        * Radio groups for download options

    - **Information Display**: Components for showing metadata
        * Labels with associated info displays
        * Info icons with Mantine tooltips

    - **Alerts**: User feedback components with Mantine styling
        * Error alerts (red color)
        * Success/info alerts (blue color)
        * Markdown-enabled alerts for rich formatting

Design Philosophy:
    - Consistent Mantine theming across all components
    - Built-in tooltips for user guidance
    - Responsive layouts with flexible widths
    - Accessibility-friendly implementations
    - Reusable with configuration parameters

Dependencies:
    - dash_mantine_components: Modern UI framework (fully migrated)
    - dash_ag_grid: High-performance data tables
    - dash_molstar: 3D protein structure visualization
    - global_strings: Application-wide string constants
    - column_definitions: AG Grid column configurations
    - vis: Visualization utilities and icon system

Usage:
    >>> from levseq_dash.app.components import widgets
    >>> # Create experiment table
    >>> table = widgets.get_table_all_experiments()
    >>> # Create input with help tooltip
    >>> input_field = widgets.get_input_plus_info_ico_bundle(
    ...     "my-input", "default value", "Help text"
    ... )

Notes:
    - All AG Grid tables use consistent defaultColDef settings
    - Mantine tooltips have customizable show/hide delays
    - Row heights optimized for compact display (30px)
    - All components support Dash callbacks for interactivity
    - Fully migrated from Bootstrap to Mantine components

Warning:
    Do not modify widget configurations without testing across all pages.
    Changes to defaultColDef or dashGridOptions affect multiple tables.
"""

from enum import Enum

import dash_ag_grid as dag
import dash_mantine_components as dmc
import dash_molstar
from dash import dcc, html

from . import global_strings as gs
from . import column_definitions as cd
from . import styles

# ========================================
# Tables: Experiment Dashboard Components
# ========================================


def get_table_experiment_top_variants():
    """
    Create AG Grid table for top-performing variants in an experiment.

    Displays the highest-fitness enzyme variants from a single experiment,
    including SMILES, plate location, substitutions, and fitness metrics.
    Supports single-row selection for protein structure viewing.

    Table Features:
        - Single-row selection (for 3D viewer)
        - Dynamic column definitions (set via callback)
        - Auto-sizing columns for optimal width
        - Pagination enabled
        - Parent variant highlighted in bold
        - Interactive tooltips with 1s show delay

    Grid Configuration:
        - Height: 755px (viewport-optimized)
        - Row height: 30px (compact display)
        - Header height: 50px (allows text wrapping)
        - Sorting, filtering, resizing enabled
        - Cell text selection enabled

    Returns:
        dag.AgGrid: Configured AG Grid component.
            - id: "id-table-exp-top-variants"
            - columnSize: "autoSize" (columns auto-adjust)
            - rowSelection: "single" (for protein viewer)
            - pagination: True

    Row Styling:
        - Parent variant (#PARENT# substitution): Bold font weight
        - Regular variants: Standard styling

    Usage:
        >>> table = get_table_experiment_top_variants()
        >>> # Column definitions set dynamically in callback based on data

    Notes:
        - Column definitions set in callback (include colored columns)
        - Used in experiment detail view alongside protein viewer
        - Row selection triggers protein structure update
        - Auto-height rows accommodate multi-line content
        - Tooltip interaction enabled for copying text from tooltips
    """
    return dag.AgGrid(
        id="id-table-exp-top-variants",
        # Column definitions include colored columns and are set dynamically in callback
        # columnDefs=components.get_top_variant_column_defs(),
        columnSize="autoSize",  # Auto-adjust column widths based on content
        defaultColDef={
            # WARNING: Do NOT set "flex": 1 here - it overrides individual column widths
            "sortable": True,  # Enable sorting on all columns
            "resizable": True,  # Allow manual column resizing
            "filter": True,  # Enable filtering on all columns
            # Both settings below required for header text wrapping
            "wrapHeaderText": True,  # Allow header text to wrap
            "autoHeaderHeight": True,  # Auto-adjust header height for wrapped text
            "filterParams": {
                # Show reset and apply buttons in filter
                "buttons": ["reset", "apply"],
                "closeOnApply": True,  # Close filter menu after applying
            },
            # Cell styling for compact display (optional, currently disabled)
            # 'cellStyle': {
            #     'fontSize': '12px',
            #     'padding': '5px',
            #     'verticalAlign': 'middle',
            # }
            # CRITICAL: autoHeight must be True for cells to adjust row height per column
            "autoHeight": True,  # Adjust row height to fit wrapped cell text
        },
        # Viewport-optimized height
        style={"height": "755px", "width": "100%"},
        dashGridOptions={
            "rowSelection": "single",  # Single-row selection for protein viewer integration
            # Enable text selection within cells for copying
            "enableCellTextSelection": True,
            "rowHeight": 30,  # Compact row height (30px)
            "headerHeight": 50,  # Taller headers to accommodate wrapped text
            "pagination": True,  # Enable pagination controls
            # Tooltip configuration for user guidance
            # tooltipInteraction=True allows hovering over tooltips and selecting text
            "tooltipInteraction": True,
            # Tooltip timing (milliseconds): 1s show delay, 2s hide delay
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
        rowClassRules={
            # Conditional row styling based on data values
            # Highlight parent variant (#PARENT#) with bold font
            "fw-bold": "params.data.amino_acid_substitutions == '#PARENT#'",
            # Alternative conditional styling examples (currently disabled):
            # "bg-secondary": "params.data.well == 'A2'",
            # "text-info fw-bold fs-5": "params.data.well == 'A1'",
            # "text-warning fw-bold fs-5": "['#PARENT#'].includes(params.data.amino_acid_substitutions)",
        },
    )


def get_table_experiment_related_variants():
    """
    Create AG Grid table for related variants from sequence alignment.

    Displays enzyme variants that match the query sequence across all
    experiments in the database. Shows comprehensive alignment statistics,
    experiment metadata, and full sequence alignment visualization.

    Table Features:
        - Single-row selection
        - Wide table with horizontal scroll (for alignment strings)
        - Pagination enabled
        - Fixed column definitions from column_definitions module
        - Interactive tooltips with 1s show delay

    Grid Configuration:
        - Height: Dynamic (styles.related_variants_table_height)
        - Row height: 30px (may expand for alignment visualization)
        - Sorting, filtering, resizing enabled
        - Always show horizontal scroll
        - Cell text selection enabled

    Column Layout:
        - Experiment ID (pinned left, width: 170px)
        - Experiment name (width: 250px)
        - Alignment scores (% Match, sorted descending by default)
        - SMILES, substitutions, plate/well
        - Fitness metrics (width: 130px each)
        - Substrate/product SMILES
        - Experiment metadata (date, assay, method, plates)
        - Alignment stats (matches, gaps, mismatches)
        - Alignment string visualization (very wide: 7000px)

    Returns:
        dag.AgGrid: Configured AG Grid component.
            - id: "id-table-exp-related-variants"
            - columnDefs: From cd.get_an_experiments_matched_sequences_column_defs()
            - rowSelection: "single"
            - pagination: True

    Usage:
        >>> table = get_table_experiment_related_variants()
        >>> # Used in experiment view to show similar sequences

    Notes:
        - Used in single-experiment context for finding related variants
        - Column definitions include pinned experiment ID for context
        - Alignment string requires horizontal scrolling
        - Auto-height rows accommodate multi-line alignment display
        - Pagination improves performance with many results
    """
    return dag.AgGrid(
        id="id-table-exp-related-variants",
        # Column definitions for experiment-specific matched sequences
        columnDefs=cd.get_an_experiments_matched_sequences_column_defs(),
        defaultColDef={
            # WARNING: Do NOT set "flex": 1 here - it overrides individual column widths
            "sortable": True,  # Enable sorting on all columns
            "resizable": True,  # Allow manual column resizing
            "filter": True,  # Enable filtering on all columns
            # Both settings below required for header text wrapping
            "wrapHeaderText": True,  # Allow header text to wrap
            "autoHeaderHeight": True,  # Auto-adjust header height for wrapped text
            "filterParams": {
                # Show reset and apply buttons in filter
                "buttons": ["reset", "apply"],
                "closeOnApply": True,  # Close filter menu after applying
            },
            # Optional cell styling for compact display (currently disabled)
            # "cellStyle": {
            #     "whiteSpace": "normal",  # Allow text wrapping
            #     "wordBreak": "break-word",  # Break long words
            #     # "fontSize": "12px",  # Smaller font
            #     # 'padding': '5px',  # Tighter padding
            #     # 'verticalAlign': 'middle',  # Vertical alignment
            # },
            # CRITICAL: autoHeight must be True for cells to adjust row height per column
            "autoHeight": True,  # Adjust row height to fit wrapped cell text
        },
        # Dynamic height from vis module for consistent viewport usage
        style={"height": styles.related_variants_table_height, "width": "100%"},
        dashGridOptions={
            # Always show horizontal scroll for wide alignment columns
            "alwaysShowHorizontalScroll": True,  # Essential for alignment string visibility
            "rowSelection": "single",  # Single-row selection
            # Enable text selection within cells for copying
            "enableCellTextSelection": True,
            # Base row height (expands with alignment visualization)
            "rowHeight": 30,
            "pagination": True,  # Enable pagination for performance
            # Alternative: auto page size based on height (currently disabled)
            # "paginationAutoPageSize": True,  # Auto-calculate rows per page
            # Note: Loading too many non-visible rows impacts performance
            # Tooltip configuration for user guidance
            # tooltipInteraction=True allows hovering over tooltips and selecting text
            "tooltipInteraction": True,
            # Tooltip timing (milliseconds): 1s show delay, 2s hide delay
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# ========================================
# Tables: Laboratory-Wide View Components
# ========================================


def get_table_all_experiments():
    """
    Create AG Grid table for laboratory-wide experiments overview.

    Displays all experiments in the database with comprehensive metadata.
    Supports multi-row selection for batch operations (export, comparison).
    Sorted by upload timestamp (most recent first) by default.

    Table Features:
        - Multi-row selection (checkbox column)
        - Pagination enabled
        - Compact row/header heights (30px each)
        - Fixed column definitions from column_definitions module
        - Interactive tooltips with 1s show delay

    Grid Configuration:
        - Height: 600px (fits standard viewport)
        - Row height: 30px (compact, similar to ag-theme-balham)
        - Header height: 30px (compact headers)
        - Sorting, filtering, resizing enabled
        - Cell text selection enabled

    Column Layout:
        - Checkbox (multi-select)
        - Experiment ID (width: 170px)
        - Experiment name (flex: 10, expandable)
        - DOI link (flex: 4)
        - Substrate SMILES (flex: 5)
        - Product SMILES (flex: 5)
        - Metadata (5 columns):
          * Date (flex: 3)
          * Upload timestamp (flex: 4, initial sort DESC)
          * Assay (flex: 3)
          * Mutagenesis method (flex: 3)
          * Plates count (flex: 2)

    Returns:
        dag.AgGrid: Configured AG Grid component.
            - id: "id-table-all-experiments"
            - columnDefs: From cd.get_all_experiments_column_defs()
            - rowSelection: "multiple" (checkbox selection)
            - pagination: True

    Usage:
        >>> table = get_table_all_experiments()
        >>> # Used in main lab view/landing page

    Notes:
        - Used in laboratory landing page view
        - Default sort by upload_time_stamp descending (newest first)
        - Multi-selection enables batch export and comparison
        - Compact styling optimized for many rows
        - All columns use flexible widths for responsiveness
    """
    return dag.AgGrid(
        id="id-table-all-experiments",
        # Column definitions for laboratory-wide experiments view
        columnDefs=cd.get_all_experiments_column_defs(),
        defaultColDef={
            # WARNING: Do NOT set "flex": 1 here - it overrides individual column widths
            "sortable": True,  # Enable sorting on all columns
            "resizable": True,  # Allow manual column resizing
            "filter": True,  # Enable filtering on all columns
            # Both settings below required for header text wrapping
            "wrapHeaderText": True,  # Allow header text to wrap
            "autoHeaderHeight": True,  # Auto-adjust header height for wrapped text
            "filterParams": {
                # Show reset and apply buttons in filter
                "buttons": ["reset", "apply"],
                "closeOnApply": True,  # Close filter menu after applying
            },
            # CRITICAL: autoHeight must be True for cells to adjust row height per column
            "autoHeight": True,  # Adjust row height to fit wrapped cell text
        },
        # Standard height for lab view
        style={"height": "600px", "width": "100%"},
        dashGridOptions={
            # Multi-row selection for batch operations (export, comparison)
            "rowSelection": "multiple",  # Enable checkbox column for multi-select
            # Alternative selection options (currently disabled):
            # "suppressRowClickSelection": True,  # Disable row click selection
            # "animateRows": True,  # Animate row movements
            # Enable text selection within cells for copying
            "enableCellTextSelection": True,
            "pagination": True,  # Enable pagination controls
            # Compact spacing similar to ag-theme-balham
            "rowHeight": 30,  # Smaller rows (compact display)
            "headerHeight": 30,  # Smaller headers (compact display)
            # Tooltip configuration for user guidance
            # tooltipInteraction=True allows hovering over tooltips and selecting text
            "tooltipInteraction": True,
            # Tooltip timing (milliseconds): 1s show delay, 2s hide delay
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# ========================================
# Tables: Sequence Alignment Components
# ========================================


def get_table_matched_sequences():
    """
    Create AG Grid table for sequence alignment search results.

    Displays enzyme variants matching a query sequence across all experiments.
    Includes comprehensive alignment statistics, experiment metadata,
    hot/cold spot indicators, and full alignment visualization.

    Table Features:
        - Single-row selection
        - Very wide table with horizontal scroll (alignment strings ~7000px)
        - Pagination enabled
        - Fixed column definitions from column_definitions module
        - Interactive tooltips with 1s show delay

    Grid Configuration:
        - Height: Dynamic (styles.seq_match_table_height)
        - Row height: 30px base (varies with alignment display)
        - Sorting, filtering, resizing enabled
        - Always show horizontal scroll
        - Cell text selection enabled

    Column Layout:
        - Experiment ID (width: 170px)
        - SMILES (width: 200px)
        - Experiment name (width: 250px)
        - Alignment scores (% Match column, sorted descending)
        - Substrate/product SMILES (width: 200px each)
        - Experiment metadata (5 columns, fixed widths):
          * Date, upload timestamp, assay, method (with formatter), plates
        - Alignment stats (3 columns: matches, gaps, mismatches)
        - Hot/cold indices (width: 250px each)
        - Alignment string visualization (width: 7000px)

    Returns:
        dag.AgGrid: Configured AG Grid component.
            - id: "id-table-matched-sequences"
            - columnDefs: From cd.get_matched_sequences_column_defs()
            - rowSelection: "single"
            - pagination: True

    Usage:
        >>> table = get_table_matched_sequences()
        >>> # Used in sequence search results view

    Notes:
        - Used in sequence alignment search results page
        - Default sort by % Match descending (best matches first)
        - Hot/cold indices identify beneficial/deleterious mutation sites
        - Alignment string requires extensive horizontal scrolling
        - Pagination essential for performance with many results
        - Auto-height disabled for alignment strings (fixed row height)
    """
    return dag.AgGrid(
        id="id-table-matched-sequences",
        # Column definitions for sequence alignment search results
        columnDefs=cd.get_matched_sequences_column_defs(),
        defaultColDef={
            # WARNING: Do NOT set "flex": 1 here - it overrides individual column widths
            "sortable": True,  # Enable sorting on all columns
            "resizable": True,  # Allow manual column resizing
            "filter": True,  # Enable filtering on all columns
            # Both settings below required for header text wrapping
            "wrapHeaderText": True,  # Allow header text to wrap
            "autoHeaderHeight": True,  # Auto-adjust header height for wrapped text
            "filterParams": {
                # Show reset and apply buttons in filter
                "buttons": ["reset", "apply"],
                "closeOnApply": True,  # Close filter menu after applying
            },
            # Optional cell styling for text wrapping (currently disabled)
            # "cellStyle": {
            #     "whiteSpace": "normal",  # Allow text wrapping
            #     "wordBreak": "break-word",  # Break long words
            #     # "fontSize": "12px",  # Smaller font
            #     # 'padding': '5px',  # Tighter padding
            #     # 'verticalAlign': 'middle',  # Vertical alignment
            # },
            # Note: autoHeight disabled for alignment strings (use fixed row height)
            # "autoHeight": True,  # Would adjust row height to fit wrapped cell text
        },
        # Dynamic height from vis module for consistent viewport usage
        style={"height": styles.seq_match_table_height, "width": "100%"},
        dashGridOptions={
            # Always show horizontal scroll for very wide alignment columns
            "alwaysShowHorizontalScroll": True,  # Essential for alignment string visibility
            "rowSelection": "single",  # Single-row selection
            # Enable text selection within cells for copying
            "enableCellTextSelection": True,
            "rowHeight": 30,  # Base row height
            "pagination": True,  # Enable pagination for performance
            # Alternative: auto page size based on height (currently disabled)
            # Note: Loading too many non-visible rows impacts rendering performance
            # "paginationAutoPageSize": True,  # Auto-calculate rows per page
            # Tooltip configuration for user guidance
            # tooltipInteraction=True allows hovering over tooltips and selecting text
            "tooltipInteraction": True,
            # Tooltip timing (milliseconds): 1s show delay, 2s hide delay
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


def get_table_matched_sequences_exp_hot_cold_data():
    """
    Create AG Grid table for hot/cold spot analysis data.

    Displays enzyme variants classified by whether they contain beneficial
    (hot spot) or deleterious (cold spot) mutations. Used for understanding
    which positions in the protein sequence consistently improve or impair
    enzyme activity.

    Table Features:
        - No row selection (display-only)
        - Pagination enabled
        - Compact row height (30px)
        - Fixed column definitions from column_definitions module
        - Interactive tooltips with 1s show delay

    Grid Configuration:
        - Height: 800px (tall table for comprehensive data)
        - Row height: 30px (compact display)
        - Sorting, filtering, resizing enabled
        - Cell text selection enabled

    Column Layout:
        - Experiment ID (width: 170px, pinned left)
        - Experiment name (width: 250px)
        - Hot/Cold type indicator (flex: 1)
        - SMILES (flex: 2)
        - Plate/Well (flex: 2)
        - Substitutions (flex: 3)
        - Fitness + Ratio (flex: 2 each)
        - Parent sequence (flex: 5, full AA sequence)

    Hot/Cold Classification:
        - Hot spots: Positions where mutations consistently improve fitness
        - Cold spots: Positions where mutations consistently decrease fitness

    Returns:
        dag.AgGrid: Configured AG Grid component.
            - id: "id-table-matched-sequences-exp-hot-cold-data"
            - columnDefs: From cd.get_matched_sequences_exp_hot_cold_data_column_defs()
            - pagination: True
            - No row selection

    Usage:
        >>> table = get_table_matched_sequences_exp_hot_cold_data()
        >>> # Used in hot/cold spot analysis view

    Notes:
        - Used in hot/cold spot analysis page
        - Experiment ID pinned left for context during horizontal scroll
        - Hot/cold type column enables filtering by classification
        - Parent sequence column shows full amino acid context
        - Critical for rational protein engineering strategies
        - Pagination essential for viewing large datasets
    """
    return dag.AgGrid(
        id="id-table-matched-sequences-exp-hot-cold-data",
        # Column definitions for hot/cold spot analysis
        columnDefs=cd.get_matched_sequences_exp_hot_cold_data_column_defs(),
        defaultColDef={
            # WARNING: Do NOT set "flex": 1 here - it overrides individual column widths
            "sortable": True,  # Enable sorting on all columns
            "resizable": True,  # Allow manual column resizing
            "filter": True,  # Enable filtering on all columns
            # Both settings below required for header text wrapping
            "wrapHeaderText": True,  # Allow header text to wrap
            "autoHeaderHeight": True,  # Auto-adjust header height for wrapped text
            "filterParams": {
                # Show reset and apply buttons in filter
                "buttons": ["reset", "apply"],
                "closeOnApply": True,  # Close filter menu after applying
            },
        },
        # Tall table for comprehensive data
        style={"height": "800px", "width": "100%"},
        dashGridOptions={
            # Row selection disabled (display-only table)
            # Alternative options currently disabled:
            # "rowSelection": "multiple",  # Multi-select
            # "suppressRowClickSelection": True,  # Disable row click selection
            # "animateRows": True,  # Animate row movements
            # Enable text selection within cells for copying
            "enableCellTextSelection": True,
            "rowHeight": 30,  # Compact row height
            "pagination": True,  # Enable pagination for performance
            # Alternative: auto page size based on height (currently disabled)
            # Note: Loading too many non-visible rows impacts rendering performance
            # "paginationAutoPageSize": True,  # Auto-calculate rows per page
            # Tooltip configuration for user guidance
            # tooltipInteraction=True allows hovering over tooltips and selecting text
            "tooltipInteraction": True,
            # Tooltip timing (milliseconds): 1s show delay, 2s hide delay
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# --------------------------------
# Protein Viewer
# --------------------------------
def get_protein_viewer():
    """
    Create a Molstar protein structure viewer component.

    Returns:
        dash_molstar.MolstarViewer: Configured 3D protein viewer.
    """
    return dash_molstar.MolstarViewer(
        id="id-viewer",
        # data=data,
        style={"width": "auto", "height": "600px"},
        layout={
            # "layoutShowControls": True,
            # https://dash-molstar.readthedocs.io/en/latest/load.html#general-options
            # ‘outside’, ‘portrait’, ‘landscape’ and ‘reactive’ (default)
            "layoutControlsDisplay": "landscape",
            "layoutIsExpanded": False,  # if true it makes it full screen
        },
    )


# ========================================
# Form Components and Input Elements
# ========================================


def get_label_fixed_for_form(string, w=2):
    """
    Create fixed-width label for horizontal form layouts using Mantine.

    Generates a bold, consistently-sized label to align with form inputs.
    Used in horizontal forms where labels appear left of inputs.

    Args:
        string (str): Label text to display.
            Example: "Experiment Name", "Description", "Date"

        w (int, optional): Width proportion (1-12, Bootstrap-style for compatibility).
            Default: 2 (narrow label column)
            Common values:
            - 2: Narrow labels (~16.6% width)
            - 3: Medium labels (~25% width)
            - 4: Wide labels (~33.3% width)
            Note: Width converted to percentage for Mantine styling

    Returns:
        dmc.Text: Mantine text component styled as form label.
            - weight: Bold (700)
            - size: "md" (medium size)
            - style: Fixed width based on grid proportion

    Usage:
        >>> label = get_label_fixed_for_form("Name:", w=3)
        >>> # Use in horizontal form with dmc.Grid

    Notes:
        - Mantine Text component provides consistent theming
        - Width calculated as percentage: (w / 12) * 100%
        - Bold weight and medium size match previous Bootstrap styling
        - Fully migrated from dbc.Label to dmc.Text
    """
    # Calculate width percentage based on 12-column grid
    width_percent = f"{(w / 12) * 100}%"

    return dmc.Text(
        string,
        weight=700,  # Bold font weight
        size="md",  # Medium font size
        style={"width": width_percent, "display": "inline-block"},
    )


def get_info_icon_tooltip_bundle(info_icon_id, help_string, location, allow_html=False):
    """
    Create info icon with Mantine tooltip for contextual help.

    Combines an information icon with a hover tooltip to provide users
    with contextual help without cluttering the interface.

    Args:
        info_icon_id (str): Unique ID for the icon element.
            Used for component identification.

        help_string (str): Tooltip text content to display.
            Can be plain text or HTML/Markdown if allow_html=True.

        location (str): Tooltip placement relative to icon.
            Options: 'top', 'bottom', 'left', 'right', 'top-start', 'top-end',
            'bottom-start', 'bottom-end', 'left-start', 'left-end',
            'right-start', 'right-end'
            Common: 'top' (above icon), 'right' (beside icon)

        allow_html (bool, optional): Whether to allow HTML/Markdown in tooltip.
            Default: False (plain text only)
            If True, renders Markdown with HTML support

    Returns:
        dmc.Tooltip: Mantine tooltip wrapping icon.
            Tooltip automatically shows on hover with smooth transitions.

    Usage:
        >>> bundle = get_info_icon_tooltip_bundle(
        ...     "my-field-info",
        ...     "Enter experiment name (required)",
        ...     "top"
        ... )
        >>> # Place next to form input

    Notes:
        - Icon color controlled by "main-color" CSS class
        - Tooltip appears on hover with smooth Mantine transitions
        - withArrow adds visual pointer for better UX
        - Mantine tooltip API: wraps children instead of targeting by ID
        - Fully migrated from Bootstrap to Mantine pattern
    """
    # Prepare tooltip content (plain text or HTML)
    tooltip_content = get_tooltip(info_icon_id, help_string, location, allow_html)

    return dmc.Tooltip(
        label=tooltip_content,  # Tooltip text content
        position=location,  # Placement: top, bottom, left, right, etc.
        withArrow=True,  # Show visual arrow pointing to icon
        children=html.Div(
            id=info_icon_id,
            children=styles.get_icon(styles.icon_info, styles.SMALL),  # Small info icon
            className="main-color",  # Apply theme color
        ),
    )


def get_tooltip(target_id, string, tip_placement, allow_html=False):
    """
    Create Mantine tooltip component attached to a target element.

    Provides hover tooltips for any UI element identified by its ID.
    Supports plain text or rich HTML/Markdown content.

    Note: Mantine tooltips work differently than Bootstrap tooltips.
    They wrap the target element rather than referencing it by ID.
    This function returns just the tooltip content; the caller must
    wrap the target element with dmc.Tooltip.

    Args:
        target_id (str): ID of the element to attach tooltip to.
            Used for backwards compatibility but not in Mantine API.

        string (str): Tooltip text content.
            Plain text or HTML/Markdown if allow_html=True.

        tip_placement (str): Tooltip placement relative to target.
            Options: 'top', 'bottom', 'left', 'right',
            'top-start', 'top-end', 'bottom-start', 'bottom-end',
            'left-start', 'left-end', 'right-start', 'right-end'
            Common: 'top' (above element)

        allow_html (bool, optional): Whether to render HTML/Markdown.
            Default: False (plain text only)
            If True, wraps string in dcc.Markdown with HTML enabled

    Returns:
        str or html.Div: Tooltip content.
            - Plain string for text-only tooltips
            - html.Div with Markdown for HTML tooltips

    Usage:
        >>> # For use with Mantine tooltip wrapper:
        >>> dmc.Tooltip(
        ...     label=get_tooltip("", "Help text", "top"),
        ...     position="top",
        ...     withArrow=True,
        ...     children=html.Div(id="my-element", ...)
        ... )

    Notes:
        - Mantine tooltips have better positioning and styling
        - Tooltips appear automatically on hover
        - HTML mode enables rich formatting (bold, lists, links)
        - withArrow adds visual pointer to target element
        - Fully migrated from dbc.Tooltip to dmc.Tooltip pattern
    """
    # If HTML/Markdown enabled, wrap in Markdown component
    if allow_html:
        return html.Div(dcc.Markdown(string, dangerously_allow_html=True))

    return string  # Plain text for Mantine label


def get_input_plus_info_ico_bundle(input_id, input_value, info_icon_help_string):
    """
    Create Mantine text input with adjacent info icon and tooltip.

    Combines a text input field with contextual help icon, providing
    a clean interface with inline assistance.

    Args:
        input_id (str): Unique ID for the input element.
            Used for callbacks and form submissions.

        input_value (str): Initial value for the input field.
            Can be empty string "" for blank input.

        info_icon_help_string (str): Help text for tooltip.
            Displayed when hovering over info icon.

    Returns:
        dmc.Group: Mantine group container with input and info icon.
            Layout: Horizontal group with center alignment
            Spacing: "xs" (extra small gap between components)

    Input Features:
        - debounce: 300 (waits 300ms after user stops typing before callback)
        - Mantine theming applied automatically

    Usage:
        >>> input_field = get_input_plus_info_ico_bundle(
        ...     "experiment-name",
        ...     "My Experiment",
        ...     "Enter a descriptive name for your experiment"
        ... )

    Notes:
        - Debounce improves performance by reducing callback frequency
        - dmc.Group provides consistent spacing with Mantine theme
        - Info icon with tooltip positioned to the right of input
        - align="center" ensures vertical centering of components
        - Fully migrated from Bootstrap to Mantine components
    """
    return dmc.Group(
        [
            # Mantine text input field
            dmc.TextInput(
                id=input_id,
                value=input_value,  # Initial/default value
                debounce=300,  # Wait 300ms after typing stops before callback
                style={"flex": 1},  # Take available space
            ),
            # Info icon with tooltip
            get_info_icon_tooltip_bundle(
                info_icon_id=f"{input_id}-info",  # Auto-generate unique ID
                help_string=info_icon_help_string,  # Tooltip text
                location="top",  # Tooltip appears above icon
            ),
        ],
        gap="xs",  # Extra small gap (5px in default theme)
        align="center",  # Vertical centering
    )


class DownloadType(Enum):
    """
    Enumeration for download data type selection options.

    Defines the two download modes available in the application:
    - ORIGINAL: Download all data from the table (unfiltered)
    - FILTERED: Download only currently visible/filtered data

    Values:
        ORIGINAL (int): Value 1 - Download complete dataset
        FILTERED (int): Value 2 - Download filtered subset

    Usage:
        >>> download_mode = DownloadType.ORIGINAL
        >>> if download_mode == DownloadType.ORIGINAL:
        ...     # Export all rows
        >>> elif download_mode == DownloadType.FILTERED:
        ...     # Export only filtered rows

    Notes:
        - Used in radio button groups for download options
        - Integer values for compatibility with Dash components
        - ORIGINAL is typically the default selection
    """

    ORIGINAL = 1  # Download all data (unfiltered)
    FILTERED = 2  # Download filtered data only


def get_radio_items_download_options(radio_id):
    """
    Create Mantine radio buttons for selecting download data type (original/filtered).

    Provides a radio group with two options for download data selection:
    - Original: Download all data (unfiltered)
    - Filtered: Download only currently visible/filtered data

    Args:
        radio_id (str): Unique ID for the radio button group.
            Used in callbacks to detect selection changes.

    Returns:
        dmc.Group: Container with radio group and tooltips.
            Components:
            - dmc.RadioGroup: Radio button selector
            - Two dmc.Tooltip components for each option

    Radio Options:
        - Original (value=1): Download all data
            Icon + "Download Original" text
            Tooltip: Help text for unfiltered download
        - Filtered (value=2): Download visible data
            Icon + "Download Filtered" text
            Tooltip: Help text for filtered download

    Default Selection:
        - ORIGINAL (value=1)

    Usage:
        >>> radio_group = get_radio_items_download_options("my-download-radio")
        >>> # Use in callback to determine download type

    Notes:
        - Each option has dedicated tooltip with help text
        - Tooltips wrap individual radio items for proper targeting
        - Horizontal layout (not stacked)
        - Mantine theming applied automatically
        - Fully migrated from dbc.RadioItems to dmc.RadioGroup
    """
    # Generate unique IDs for individual radio option tooltips
    id_1 = f"{radio_id}_1"
    id_2 = f"{radio_id}_2"

    return dmc.Group(
        [
            # Tooltip for original option
            dmc.Tooltip(
                label=gs.help_download_mode_unfiltered,
                position="top",
                withArrow=True,
                children=html.Span(
                    id=id_1,
                    children=[
                        styles.get_icon(styles.icon_download),
                        gs.download_original,
                    ],
                    style={"display": "inline-flex", "alignItems": "center"},
                ),
            ),
            # Tooltip for filtered option
            dmc.Tooltip(
                label=gs.help_download_mode_filtered,
                position="top",
                withArrow=True,
                children=html.Span(
                    id=id_2,
                    children=[
                        styles.get_icon(styles.icon_download),
                        gs.download_filtered,
                    ],
                    style={"display": "inline-flex", "alignItems": "center"},
                ),
            ),
            # Mantine radio group
            dmc.RadioGroup(
                id=radio_id,
                value=str(DownloadType.ORIGINAL.value),  # Default: Original
                children=[
                    dmc.Radio(label="", value=str(DownloadType.ORIGINAL.value)),
                    dmc.Radio(label="", value=str(DownloadType.FILTERED.value)),
                ],
                size="sm",  # Small radio buttons
            ),
        ],
        gap="md",  # Medium gap between components
        align="center",  # Vertical centering
    )


def get_download_text_icon_combo(text_string):
    """
    Create a download icon with accompanying text.

    Args:
        text_string: Text to display next to download icon.

    Returns:
        html.Span: Combined icon and text component.
    """
    return html.Span([
        html.Span(styles.get_icon(styles.icon_download)),
        html.Span(
            [text_string],
            style={"marginLeft": "12px"},
        ),
    ])


def get_download_radio_combo(button_id, radio_id):
    """
    Create Mantine download button with integrated radio selection for data type.

    Combines a download button and radio options in a single horizontal
    layout, allowing users to select download type (original/filtered)
    before clicking the download button.

    Args:
        button_id (str): Unique ID for the download button.
            Used in callbacks to detect button clicks.

        radio_id (str): Unique ID for the radio button group.
            Used in callbacks to detect selection changes.

    Returns:
        dmc.Group: Mantine group container with button and radio selection.
            Layout: [Download Button] [Radio Options]
            Horizontal group with consistent spacing

    Components:
        - Download button (Mantine styled, primary variant)
        - Radio group (original/filtered options with tooltips)
        - Tooltips for all interactive elements

    Radio Options:
        - Original (value=1): Download all data
        - Filtered (value=2): Download visible data only

    Default Selection:
        - ORIGINAL (unfiltered data)

    Usage:
        >>> combo = get_download_radio_combo(
        ...     "download-btn",
        ...     "download-radio"
        ... )
        >>> # Use in page layout alongside data tables

    Notes:
        - Each component has its own tooltip for clear guidance
        - Radio options wrapped in tooltips for proper targeting
        - dmc.Group provides consistent Mantine spacing
        - Button and radio group align horizontally
        - Fully migrated from Bootstrap to Mantine components
    """
    # Generate unique IDs for individual radio option tooltips
    id_1 = f"{radio_id}_1"  # Original option ID
    id_2 = f"{radio_id}_2"  # Filtered option ID

    return dmc.Group(
        [
            # Mantine download button with tooltip
            dmc.Tooltip(
                label=gs.help_download,
                position="top",
                withArrow=True,
                children=dmc.Button(
                    children=[get_download_text_icon_combo(gs.download_results)],  # Icon + text
                    id=button_id,  # Button ID for callbacks
                    n_clicks=0,  # Initialize click counter
                    size="sm",  # Small button size
                    variant="filled",  # Filled primary button
                    color="blue",  # Primary blue color
                ),
            ),
            # Radio options with tooltips
            dmc.Group(
                [
                    # Original option with tooltip
                    dmc.Tooltip(
                        label=gs.help_download_mode_unfiltered,
                        position="top",
                        withArrow=True,
                        children=html.Span(
                            id=id_1,
                            children=[
                                # Download icon
                                styles.get_icon(styles.icon_download),
                                " ",  # Space
                                gs.download_original,  # "Download Original" text
                            ],
                            style={"display": "inline-flex", "alignItems": "center"},
                        ),
                    ),
                    # Filtered option with tooltip
                    dmc.Tooltip(
                        label=gs.help_download_mode_filtered,
                        position="top",
                        withArrow=True,
                        children=html.Span(
                            id=id_2,
                            children=[
                                # Download icon
                                styles.get_icon(styles.icon_download),
                                " ",  # Space
                                gs.download_filtered,  # "Download Filtered" text
                            ],
                            style={"display": "inline-flex", "alignItems": "center"},
                        ),
                    ),
                    # Radio group for selection
                    dmc.RadioGroup(
                        id=radio_id,
                        # Default: Original
                        value=str(DownloadType.ORIGINAL.value),
                        children=[
                            dmc.Radio(label="", value=str(DownloadType.ORIGINAL.value)),
                            dmc.Radio(label="", value=str(DownloadType.FILTERED.value)),
                        ],
                        size="sm",  # Small radio buttons
                    ),
                ],
                gap="sm",  # Small gap between radio components
                align="center",  # Vertical centering
            ),
        ],
        gap="md",  # Medium gap between button and radio group
        align="center",  # Vertical centering
    )


def generate_label_with_info(label, id_info):
    """
    Create bold label with associated dynamic info display area.

    Generates a two-part component: a bold label followed by a span
    where dynamic content can be inserted via callbacks.

    Commonly used in experiment detail views to show metadata:
    - "Experiment Name: [dynamic name]"
    - "Date: [dynamic date]"
    - "DOI: [dynamic link]"

    Args:
        label (str): Label text to display (without colon).
            Colon automatically appended.
            Example: "Experiment Name" becomes "Experiment Name:"

        id_info (str): ID for the info content element.
            Content populated via callbacks.
            Used to update displayed value dynamically.

    Returns:
        html.Div: Container with label and info spans.
            - First span: Bold label with colon
            - Second span: Dynamic content area
            - Style: Word breaking and text wrapping enabled

    Styling:
        - Label: Uses styles.experiment_info style (typically bold)
        - Container: wordBreak="break-all" (breaks long words)
        - Container: whiteSpace="normal" (allows text wrapping)

    Usage:
        >>> label = generate_label_with_info("Experiment Name", "exp-name-display")
        >>> # In callback:
        >>> @app.callback(Output("exp-name-display", "children"), ...)
        >>> def update_name(...):
        ...     return "My Experiment"

    Notes:
        - Colon automatically added after label text
        - Word breaking critical for long values (UUIDs, URLs)
        - Text wrapping prevents horizontal overflow
        - Commonly used in metadata display sections
        - Style prevents layout breaking with long content
    """
    return html.Div(
        [
            # Label with colon (bold styling from styles.experiment_info)
            html.Span(f"{label}:", style=styles.experiment_info),
            # Dynamic content area (populated via callbacks)
            html.Span(id=id_info),
        ],
        style={
            "wordBreak": "break-all",  # Break long words (prevents overflow)
            "whiteSpace": "normal",  # Allow text wrapping to next line
        },
    )


def get_alert(alert_message, error=True, is_markdown=False):
    """
    Create dismissable Mantine alert component for user notifications.

    Provides feedback to users through color-coded alerts that can be
    dismissed. Supports error alerts (red) and success/info alerts (blue),
    with optional Markdown formatting for rich content.

    Args:
        alert_message (str): Message text to display.
            Plain text or Markdown if is_markdown=True.
            Examples:
            - "Form submission successful!"
            - "Error: Invalid experiment name"
            - "**Bold text** and [links](url) work with Markdown"

        error (bool, optional): Whether this is an error alert.
            Default: True (error alert with red styling)
            False: Info/success alert with blue styling

        is_markdown (bool, optional): Whether to render as Markdown.
            Default: False (plain text)
            If True, enables rich formatting (bold, italics, links, lists)

    Returns:
        dmc.Alert: Mantine alert component.
            - children: Alert message (text or Markdown)
            - color: "red" for errors, "blue" for info
            - withCloseButton: True (user can dismiss)
            - title: Alert title based on type

    Alert Types:
        - Error (error=True): Red color, "Error" title
        - Info/Success (error=False): Blue color, "Info" title

    Usage:
        >>> # Error alert
        >>> alert = get_alert("Invalid input data", error=True)
        >>>
        >>> # Success alert
        >>> alert = get_alert("Upload successful!", error=False)
        >>>
        >>> # Markdown alert
        >>> msg = "**Important:** Visit [docs](https://example.com)"
        >>> alert = get_alert(msg, error=False, is_markdown=True)

    Notes:
        - Mantine alerts have consistent theming with rest of UI
        - withCloseButton adds dismissal functionality
        - Markdown mode enables dangerously_allow_html (security consideration)
        - Mantine color variants: "red", "blue", "green", "yellow", etc.
        - Commonly used for form validation and operation feedback
        - Fully migrated from dbc.Alert to dmc.Alert
    """
    # Determine alert color and title based on error flag
    color = "red" if error else "blue"
    title = "Error" if error else "Info"

    # If Markdown enabled, render rich content
    # Note: dangerously_allow_html=True is a security consideration
    if is_markdown:
        children = dcc.Markdown(alert_message, dangerously_allow_html=True)
    else:
        children = alert_message  # Plain text

    return dmc.Alert(
        title=title,  # Alert title
        children=children,  # Alert message content
        color=color,  # Color variant (red or blue)
        withCloseButton=True,  # User can dismiss alert
    )
