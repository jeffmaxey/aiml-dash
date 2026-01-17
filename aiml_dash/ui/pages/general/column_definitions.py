"""
AG Grid Column Definitions Module

This module provides reusable column definition functions for AG Grid data tables
throughout the application. It centralizes all table column configurations to ensure
consistency across different views and enable easy maintenance.

Column definitions control how data is displayed in AG Grid tables, including:
- Field mappings and header names
- Sorting, filtering, and width settings
- Custom cell renderers and formatters
- Tooltips and conditional styling
- Row selection and pinned columns

Table Types Supported:
    1. All Experiments Table - Lab view with experiment listings
    2. Top Variants Table - Experiment view showing best performers
    3. Matched Sequences Table - Sequence alignment results
    4. Hot/Cold Spots Table - GoF/LoF variant analysis
    5. Related Variants Table - Similar sequences to current experiment

Design Philosophy:
    - Reusable column functions for common fields
    - Optional parameter records for customization
    - Consistent field naming via global_strings
    - Composable column definitions via concatenation
    - Separation of concerns (structure vs styling)

Usage Pattern:
    >>> column_defs = get_experiment_id({"width": 170}) + get_experiment_name({"flex": 2})
    >>> # Pass to AG Grid component's columnDefs prop

WARNING: DO NOT modify definitions without understanding full impact!
Changes here affect ALL tables in the application.

Author: Enhanced Documentation
Date: January 7, 2026
"""

from levseq_dash.app import global_strings as gs
from . import styles


def get_checkbox():
    """
    Create checkbox column definition for row selection.

    Adds a checkbox column at the start of the table that enables:
    - Individual row selection via clicking
    - Select all/none via header checkbox
    - Multi-row selection for bulk operations

    The checkbox column has no header text and minimal width to save space.
    Selected rows can be retrieved via AG Grid's getSelectedRows() API.

    Returns:
        list: Single-element list containing checkbox column definition.
            Contains properties:
            - headerCheckboxSelection: Enables header select-all checkbox
            - checkboxSelection: Enables row checkboxes
            - headerName: Empty string (no header text)
            - width: 30 pixels (minimal width)

    Usage:
        >>> column_defs = get_checkbox() + get_experiment_id() + ...
        >>> # Checkbox will be first column

    Notes:
        - Typically used as first column for visibility
        - Works with AG Grid row selection APIs
        - Does not include field mapping (no data binding)
    """
    return [
        {  # Checkbox column for row selection
            "headerCheckboxSelection": True,  # Header checkbox for select all/none
            "checkboxSelection": True,  # Row-level checkboxes
            "headerName": "",  # No header text needed
            "width": 30,  # Minimal width for checkbox
        }
    ]


def get_experiment_id(record=None):
    """
    Create experiment ID column definition with UUID truncation.

    Displays experiment IDs in a truncated format to save horizontal space
    while providing the full UUID on hover via tooltip. This balances
    readability with information density.

    The ID format is typically: "prefix-uuid" (e.g., "exp-abc123...")
    Display shows first 13 characters which captures prefix + partial UUID.

    Args:
        record (dict, optional): Additional properties to merge into column definition.
            Common overrides: width, flex, pinned, initialSort
            Example: {"width": 170, "pinned": "left"}
            Default: None (use base definition only)

    Returns:
        list: Single-element list containing experiment ID column definition.
            Contains properties:
            - field: Data field name (gs.cc_experiment_id)
            - headerName: Column header text
            - valueFormatter: JavaScript function to truncate display
            - tooltipField: Shows full ID on hover

    Value Formatter:
        JavaScript: params.value.slice(0, 13)
        Shows first 13 characters of experiment ID
        Full ID visible in tooltip on hover

    Usage:
        >>> # Basic usage
        >>> cols = get_experiment_id()
        >>>
        >>> # With custom width
        >>> cols = get_experiment_id({"width": 170})
        >>>
        >>> # Pinned to left side
        >>> cols = get_experiment_id({"width": 170, "pinned": "left"})

    Notes:
        - UUIDs are unique identifiers for experiments
        - Truncation improves table density
        - Tooltip ensures full ID is accessible
        - Can be pinned for always-visible reference
    """
    c = [
        {
            "field": gs.cc_experiment_id,
            "headerName": gs.header_experiment_id,
            # Truncate to first 13 characters for compact display
            "valueFormatter": {
                "function": "params.value.slice(0, 13)"  # Shows prefix + partial UUID
            },
            "tooltipField": "experiment_id",  # Full UUID on hover
        }
    ]
    if record:
        c[0].update(record)  # Merge custom properties

    return c


def get_experiment_name(record=None):
    """
    Create experiment name column definition.

    Displays the user-provided name for the experiment. This is typically
    a descriptive label that helps identify experiments by their purpose
    or characteristics rather than just an ID.

    Names can be long, so tooltip support ensures full text is readable
    even when column width is constrained.

    Args:
        record (dict, optional): Additional properties to merge into column definition.
            Common overrides: width, flex, tooltipField
            Example: {"flex": 10} for proportional width
            Default: None (use base definition only)

    Returns:
        list: Single-element list containing experiment name column definition.
            Contains properties:
            - field: Data field name (gs.c_experiment_name)
            - headerName: Column header text
            - tooltipField: Shows full name on hover if truncated

    Typical Usage:
        >>> # With flex sizing for variable width
        >>> cols = get_experiment_name({"flex": 10})
        >>>
        >>> # With fixed width
        >>> cols = get_experiment_name({"width": 250})

    Notes:
        - User-editable field during experiment creation
        - Often set to flexible width (flex) for responsiveness
        - Tooltip handles overflow gracefully
        - Important for experiment identification
    """
    c = [
        {
            "field": gs.c_experiment_name,
            "headerName": gs.header_experiment_name,
            "tooltipField": gs.c_experiment_name,  # Full name on hover
        }
    ]
    if record:
        c[0].update(record)  # Merge custom properties

    return c


def get_experiment_meta(record_1=None, record_2=None, record_3=None, record_4=None, record_5=None):
    """
    Create experiment metadata column definitions (5 columns).

    Provides standardized columns for core experiment metadata that appears
    across multiple table views. Each column can be customized independently
    via optional record parameters.

    Metadata Columns:
        1. experiment_date - When experiment was conducted
        2. upload_time_stamp - When uploaded to database
        3. assay - Experimental technique used
        4. mutagenesis_method - Library generation method (epPCR/SSM)
        5. plates_count - Number of plates in experiment

    Args:
        record_1 (dict, optional): Properties for experiment_date column.
            Example: {"flex": 3, "width": 120}
            Default: None

        record_2 (dict, optional): Properties for upload_time_stamp column.
            Example: {"flex": 4, "initialSort": "desc"}
            Default: None

        record_3 (dict, optional): Properties for assay column.
            Example: {"flex": 3, "width": 130}
            Default: None

        record_4 (dict, optional): Properties for mutagenesis_method column.
            Example: {"flex": 3, "width": 130}
            Default: None

        record_5 (dict, optional): Properties for plates_count column.
            Example: {"flex": 2, "width": 90}
            Default: None

    Returns:
        list: List of 5 column definition dictionaries.
            Each contains field, headerName, filter type, and tooltip.

    Column Filters:
        - Date columns: agDateColumnFilter (for date range filtering)
        - Plates count: agNumberColumnFilter (for numeric filtering)

    Usage:
        >>> # Default metadata columns
        >>> cols = get_experiment_meta(None, None, None, None, None)
        >>>
        >>> # Custom widths and sort
        >>> cols = get_experiment_meta(
        ...     {"width": 120},  # date
        ...     {"width": 120, "initialSort": "desc"},  # upload timestamp
        ...     {"width": 130},  # assay
        ...     {"width": 130},  # method
        ...     {"width": 90}    # plates
        ... )

    Notes:
        - All parameters are optional for flexibility
        - Date fields support date range filtering
        - Upload timestamp commonly used for default sort
        - Tooltips show full text on hover
    """
    c = [
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
            "tooltipField": "experiment_date",
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
            "tooltipField": "upload_time_stamp",
        },
        {
            "field": "assay",
            "tooltipField": "assay",
        },
        {
            "field": gs.cc_mutagenesis,
            "headerName": gs.header_mutagenesis,
            "tooltipField": gs.cc_mutagenesis,
        },
        {
            "field": "plates_count",
            "headerName": "# plates",
            "filter": "agNumberColumnFilter",
        },
    ]

    if record_1:
        c[0].update(record_1)
    if record_2:
        c[1].update(record_2)
    if record_3:
        c[2].update(record_3)
    if record_4:
        c[3].update(record_4)
    if record_5:
        c[4].update(record_5)

    return c


def get_experiment_doi(record=None):
    """
    Create DOI column definition with clickable link renderer.

    Displays Digital Object Identifier (DOI) for published experiments
    as clickable links. Uses custom cell renderer to format as hyperlink.

    DOIs are persistent identifiers for scientific publications that link
    to the published paper or data repository.

    Args:
        record (dict, optional): Additional properties to merge.
            Example: {"flex": 4, "width": 150}
            Default: None

    Returns:
        list: Single-element list with DOI column definition.
            Contains:
            - field: "doi"
            - headerName: "DOI"
            - tooltipField: Shows full DOI on hover
            - cellRenderer: "DOILink" (custom renderer for clickable links)

    Cell Renderer:
        - DOILink: Custom React component that renders DOI as hyperlink
        - Typically opens doi.org/[identifier] in new tab
        - Handles missing/null DOIs gracefully

    Usage:
        >>> cols = get_experiment_doi({"flex": 4})

    Notes:
        - Not all experiments have DOIs (may be unpublished)
        - Renderer should handle null values
        - Links open in new browser tab
    """
    c = [
        {"field": "doi", "headerName": "DOI", "tooltipField": "doi", "cellRenderer": "DOILink"},
    ]
    if record:
        c[0].update(record)
    return c


def get_experiment_meta_smiles(record_1=None, record_2=None):
    """
    Create substrate and product SMILES column definitions (2 columns).

    SMILES (Simplified Molecular Input Line Entry System) strings represent
    the chemical structures of substrate (input) and product (output) molecules
    in the enzymatic reaction.

    These are critical for:
    - Understanding reaction chemistry
    - Comparing reactions across experiments
    - Searching by chemical structure

    Args:
        record_1 (dict, optional): Properties for substrate SMILES column.
            Example: {"flex": 5, "width": 200}
            Default: None

        record_2 (dict, optional): Properties for product SMILES column.
            Example: {"flex": 5, "width": 200}
            Default: None

    Returns:
        list: List of 2 column definitions for substrate and product.
            Each includes field and tooltipField for hover display.

    SMILES Format:
        - Text representation of molecular structure
        - Example: "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
        - Can be very long for complex molecules
        - Tooltips essential for readability

    Usage:
        >>> # Flexible widths
        >>> cols = get_experiment_meta_smiles({"flex": 5}, {"flex": 5})
        >>>
        >>> # Fixed widths
        >>> cols = get_experiment_meta_smiles({"width": 200}, {"width": 200})

    Notes:
        - Both columns typically same width for balance
        - SMILES can be parsed for structure visualization
        - Tooltips show full string if truncated
    """
    c = [
        {
            "field": gs.cc_substrate,
            # "headerName": gs.header_substrate,
            "tooltipField": gs.cc_substrate,
        },
        {
            "field": gs.cc_product,
            # "headerName": gs.header_product,
            "tooltipField": gs.cc_product,
        },
    ]

    if record_1:
        c[0].update(record_1)
    if record_2:
        c[1].update(record_2)

    return c


def get_smiles(record):
    """
    Create SMILES column definition with molecule display.

    Displays molecular structure as SMILES string. This is the primary
    column for showing chemical structure information in tables where
    the substrate/product distinction is not needed.

    SMILES (Simplified Molecular Input Line Entry System) is a text
    representation of molecular structure that can be parsed for
    visualization and analysis.

    Args:
        record (dict): Additional properties to merge.
            Example: {"flex": 5, "width": 200}
            Required for setting column width/flex.

    Returns:
        list: Single-element list with SMILES column definition.
            Contains:
            - field: Uses gs.c_smiles constant
            - headerName: Uses gs.header_smiles constant
            - tooltipField: Shows full SMILES on hover

    Usage:
        >>> cols = get_smiles({"flex": 5})
        >>> cols = get_smiles({"width": 200})

    Notes:
        - SMILES strings can be very long
        - Tooltip essential for full structure view
        - Distinct from get_experiment_meta_smiles (substrate/product pair)
        - May be used with custom cell renderer for visualization
    """
    c = [
        {
            "field": gs.c_smiles,
            "headerName": gs.header_smiles,
            "tooltipField": gs.c_smiles,
        }
    ]
    if record:
        c[0].update(record)
    return c


def get_plate_well(record_1):
    """
    Create plate and well location column definitions (2 columns).

    Displays the physical location where variants were sampled:
    - Plate: Plate identifier/number
    - Well: Well position in microtiter format (A1-H12 for 96-well)

    These enable:
    - Tracing variants back to physical samples
    - Identifying plate position effects
    - Reconstructing plate layouts for QC

    Well Format:
    - Rows: A-H (8 rows for 96-well) or A-P (16 rows for 384-well)
    - Columns: 1-12 (96-well) or 1-24 (384-well)
    - Examples: "A1", "H12", "E7"

    Args:
        record_1 (dict): Properties for plate column.
            Example: {"flex": 2}
            Required for setting plate column width/flex.

    Returns:
        list: List of 2 column definitions (plate, well).
            - plate: Uses gs.c_plate field, includes tooltipField
            - well: Uses gs.c_well field, fixed width of 80px

    Usage:
        >>> cols = get_plate_well({"flex": 2})

    Notes:
        - Well column has fixed 80px width (compact)
        - Plate column flexible based on record_1
        - Critical for laboratory traceability
        - Enable filtering to find specific locations
    """
    c = [
        {
            "field": gs.c_plate,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_plate,
            # "flex": 2,
        },
        {
            "field": gs.c_well,
            "width": 80,
        },
    ]
    if record_1:
        c[0].update(record_1)

    return c


def get_fitness_ratio(record_1, record_2):
    """
    Create fitness value and ratio column definitions (2 columns).

    Displays quantitative fitness measurements:
    - Fitness value: Raw measured activity/performance
    - Ratio: Relative performance (to parent or best variant)

    These metrics are fundamental for:
    - Ranking variants by performance
    - Understanding evolutionary improvement
    - Comparing across different experiments

    Ratios are unitless (activity_variant / activity_reference):
    - 1.0 = Same as reference
    - 2.0 = Double the activity
    - 0.5 = Half the activity

    Args:
        record_1 (dict): Properties for fitness_value column.
            Example: {"flex": 2, "width": 95}
            Required for setting fitness column properties.

        record_2 (dict): Properties for ratio column.
            Example: {"flex": 2, "initialSort": "desc"}
            Required for setting ratio column properties.

    Returns:
        list: List of 2 column definitions.
            - fitness_value: Uses gs.c_fitness_value field
            - ratio: Uses gs.c_ratio field
            Both include tooltipField for hover display.

    Usage:
        >>> # Equal widths
        >>> cols = get_fitness_ratio({"flex": 2}, {"flex": 2})
        >>>
        >>> # Sort by ratio descending (best first)
        >>> cols = get_fitness_ratio({"flex": 2}, {"flex": 2, "initialSort": "desc"})

    Notes:
        - Ratio column commonly used for default sort
        - Both columns should have numeric filtering enabled
        - Fitness values may have experiment-specific units
        - Ratios enable unit-free comparison
    """
    c = [
        {
            "field": gs.c_fitness_value,
            "headerName": gs.header_fitness,
            "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            # "flex": 2,
            # "cellStyle": {"styleConditions": styles.data_bars_colorscale(df, gs.c_fitness_value)},
        },
        {
            "field": gs.cc_ratio,
            "filter": "agNumberColumnFilter",
            # "flex": 2,
            # "cellStyle": {"styleConditions": styles.data_bars_group_mean_colorscale(df)},
        },
    ]

    if record_1:
        c[0].update(record_1)

    if record_2:
        c[1].update(record_2)

    return c


def get_substitutions(record):
    """
    Create amino acid substitutions column definition.

    Displays the specific amino acid changes in the variant sequence
    relative to the parent/wild-type sequence. Critical for understanding
    the genetic basis of fitness changes.

    Substitution Format:
        - Single: "A123V" (Alanine at position 123 to Valine)
        - Multiple: "A123V/T45S" (slash-separated list)
        - Insertions/Deletions may be included

    This column is essential for:
    - Identifying key mutations
    - Understanding structure-function relationships
    - Designing follow-up experiments
    - Literature comparisons

    Args:
        record (dict): Additional properties to merge.
            Example: {"flex": 4, "width": 150}
            Required for setting column width/flex.

    Returns:
        list: Single-element list with substitutions column definition.
            Contains:
            - field: Uses gs.c_substitutions constant
            - headerName: Uses gs.header_substitutions constant
            - tooltipField: Shows full list on hover

    Usage:
        >>> cols = get_substitutions({"flex": 4})

    Notes:
        - Can be very long for variants with many mutations
        - Tooltip critical for viewing full substitution list
        - May be parsed for computational analysis
        - Enable text filtering to find specific substitutions
    """
    c = [
        {
            "field": gs.c_substitutions,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_substitutions,
            "headerName": gs.header_substitutions,
        },
    ]
    if record:
        c[0].update(record)
    return c


def get_alignment_scores():
    """
    Create alignment score column definitions.

    Displays sequence alignment quality metrics. Currently returns only
    the normalized score (% Match), though raw scores are available in
    commented code if needed.

    Alignment Score Types:
        - Raw Score: Total alignment score from algorithm (commented out)
        - Normalized Score: Percentage of perfect match (0-100%)

    Higher scores indicate better sequence similarity:
    - 100% = Perfect match
    - 95% = Very high similarity
    - 50% = Moderate similarity
    - <25% = Low similarity

    Returns:
        list: Single-element list with normalized score column.
            Contains:
            - field: "norm_score"
            - headerName: "% Match"
            - initialSort: "desc" (best matches first)
            - filter: agNumberColumnFilter (for range queries)
            - width: 130px (fixed)

    Usage:
        >>> cols = get_alignment_scores()

    Notes:
        - Default sort is descending (best matches first)
        - Number filter enables queries like >90, <50, etc.
        - Raw alignment score currently disabled (see TODO)
        - Consider enabling raw score for advanced users
    """
    c = [
        # TODO: do we need to show the raw score
        # {
        #     "field": "alignment_score",
        #     "filter": "agNumberColumnFilter",
        #     "headerName": "Score",
        #     "width": 100,
        # },
        {
            "field": "norm_score",
            "initialSort": "desc",  # sort based on this column
            "headerName": "% Match",
            "filter": "agNumberColumnFilter",
            "width": 130,
        },
    ]
    return c


def get_alignment_stats():
    """
    Create alignment statistics column definitions (3 columns).

    Provides detailed breakdown of sequence alignment quality:
    - Identities: Number of exact amino acid matches
    - Gaps: Number of insertion/deletion positions
    - Mismatches: Number of differing amino acids

    These statistics complement the overall % Match score by showing
    the composition of the alignment.

    Statistics Interpretation:
        - High identities + low gaps/mismatches = high quality alignment
        - Many gaps = insertion/deletion events
        - Many mismatches = divergent sequences

    Returns:
        list: List of 3 column definitions.
            Each column includes:
            - field: "identities", "gaps", "mismatches"
            - headerName: "# matches", "# gaps", "# mismatches"
            - filter: agNumberColumnFilter (for numeric filtering)
            - width: 110px (fixed, compact)

    Usage:
        >>> cols = get_alignment_stats()

    Notes:
        - All three columns have same width (110px) for visual balance
        - Number filters enable queries (gaps=0, identities>100, etc.)
        - Total length = identities + gaps + mismatches
        - Useful for QC and filtering by alignment quality
    """
    return [
        {
            "field": "identities",
            "headerName": "# matches",
            "filter": "agNumberColumnFilter",
            "width": 110,
        },
        {
            "field": "gaps",
            "headerName": "# gaps",
            "filter": "agNumberColumnFilter",
            "width": 80,
        },
        {
            "field": "mismatches",
            "headerName": "# mismatches",
            "filter": "agNumberColumnFilter",
            "width": 127,
        },
        {
            "field": gs.cc_seq_alignment_mismatches,
            "headerName": "Mismatched Residue",
            "tooltipField": gs.cc_seq_alignment_mismatches,
            "width": 300,
        },
    ]


def get_alignment_string():
    """
    Create sequence alignment visualization column definition.

    Displays the formatted sequence alignment string with visual indicators
    for matches, mismatches, and gaps. Uses custom cell renderer for
    monospace formatting and proper display.

    Alignment Format:
        - Monospace font for proper character alignment
        - Multi-line display with auto-height rows
        - Typically shows:
            * Query sequence
            * Alignment markers (|, :, .)
            * Reference sequence

    Returns:
        list: Single-element list with alignment column definition.
            Contains:
            - field: Uses gs.cc_seq_alignment constant
            - autoHeight: True (row height adjusts to content)
            - cellRenderer: "seqAlignmentVis" (custom visualization)
            - cellStyle: Monospace font, small size, pre-wrap whitespace
            - width: 7000px (very wide to prevent wrapping)

    Cell Styling:
        - fontFamily: monospace (critical for alignment)
        - fontSize: 10 (compact display)
        - lineHeight: 1.1 (tight spacing)
        - whiteSpace: pre-wrap (preserve formatting)
        - padding: 5px (breathing room)

    Usage:
        >>> cols = get_alignment_string()

    Notes:
        - Requires custom cellRenderer component
        - autoHeight essential for multi-line display
        - Very wide column (7000px) prevents sequence wrapping
        - Monospace font critical for proper alignment
        - Typically placed at end of column list
    """
    return [
        {
            "field": gs.cc_seq_alignment,
            "autoHeight": True,  # Makes the row height adjust to content
            "cellRenderer": "seqAlignmentVis",
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                "fontFamily": "monospace",
                "fontSize": 10,
                "lineHeight": "1.1",
                "padding": "5px",
            },
            "width": 7000,
        },
    ]


def get_top_variant_column_defs(df):
    """
    Create complete column definitions for top variants table.

    Assembles the standard column set for displaying high-performing
    variants within a single experiment. Focuses on variant identity,
    location, and fitness metrics.

    Column Composition:
        1. SMILES (flex: 2) - Molecular structure
        2. Plate/Well (flex: 2) - Physical location
        3. Substitutions (flex: 3) - Amino acid changes
        4. Fitness + Ratio (flex: 2 each) - Performance metrics

    Args:
        df (DataFrame): Variant data for calculating conditional styles.
            Used for data bars colorscale on ratio column.
            Must contain fitness and ratio columns.

    Returns:
        list: Complete column definition array.
            Concatenated from: get_smiles + get_plate_well +
            get_substitutions + get_fitness_ratio

    Usage:
        >>> cols = get_top_variant_column_defs(variants_df)

    Notes:
        - No checkbox column (single-experiment view)
        - Ratio column includes data bars visualization
        - All columns use flexible widths for responsiveness
        - Typically sorted by fitness ratio descending
    """
    column_def = (
        get_smiles({"flex": 2})
        + get_plate_well({"flex": 2})
        + get_substitutions({"flex": 3})
        + get_fitness_ratio(
            {"flex": 2},
            {"flex": 2, "cellStyle": {"styleConditions": styles.data_bars_group_mean_colorscale(df)}},
        )
    )

    return column_def


def get_all_experiments_column_defs():
    """
    Create complete column definitions for all experiments table.

    Assembles the full column set for the laboratory-wide experiments
    overview. Enables multi-selection, sorting, and comprehensive
    metadata display.

    Column Composition:
        1. Checkbox - Multi-select for batch operations
        2. Experiment ID (width: 170) - UUID identifier
        3. Experiment Name (flex: 10) - User-provided name
        4. DOI (flex: 4) - Publication link
        5. Substrate SMILES (flex: 5) - Input molecule
        6. Product SMILES (flex: 5) - Output molecule
        7. Metadata (5 columns):
           - Date (flex: 3)
           - Upload timestamp (flex: 4, default sort DESC)
           - Assay (flex: 3)
           - Mutagenesis method (flex: 3)
           - Plates count (flex: 2)

    Returns:
        list: Complete column definition array.
            Concatenated from: get_checkbox + get_experiment_id +
            get_experiment_name + get_experiment_doi +
            get_experiment_meta_smiles + get_experiment_meta

    Default Sort:
        - Upload timestamp (most recent first)

    Usage:
        >>> cols = get_all_experiments_column_defs()

    Notes:
        - Checkbox enables batch selection for export/comparison
        - All columns use flexible widths for responsiveness
        - Upload timestamp provides default chronological view
        - Used in main lab view/landing page
    """

    column_def = (
        get_checkbox()
        + get_experiment_id({"width": 170})
        + get_experiment_name({"flex": 10})
        + get_experiment_doi({"flex": 4})
        + get_experiment_meta_smiles({"flex": 5}, {"flex": 5})
        + get_experiment_meta(
            {"flex": 3},  # experiment_date
            {"flex": 4, "initialSort": "desc"},  # sort by upload_time_stamp
            {"flex": 3},  # assay
            {"flex": 3},  # mutagenesis method
            {"flex": 2},
        )
    )

    return column_def


def get_matched_sequences_column_defs():
    """
    Create complete column definitions for sequence alignment results table.

    Assembles comprehensive column set for displaying sequence similarity
    search results. Includes experiment metadata, alignment statistics,
    hot/cold spot indicators, and full alignment visualization.

    Column Composition:
        1. Experiment ID (width: 170) - Can be pinned left if needed
        2. SMILES (width: 200) - Can be pinned left if needed
        3. Experiment Name (width: 250)
        4. Alignment Scores (1 column) - % Match with initial sort desc
        5. Substrate SMILES (width: 200)
        6. Product SMILES (width: 200)
        7. Metadata (5 columns, fixed widths 90-130px):
           - Date, Upload timestamp, Assay, Method, Plates
           - Method uses valueFormatter for abbreviation
        8. Alignment Stats (3 columns) - Matches, gaps, mismatches
        9. Hot Indices (width: 250) - High activity positions
        10. Cold Indices (width: 250) - Low activity positions
        11. Alignment String (width: 7000) - Visual alignment display

    Returns:
        list: Complete column definition array.
            Includes commented examples of column pinning.

    Column Pinning:
        - Commented code shows how to pin ID and SMILES columns
        - Pinning: {"pinned": "left"} keeps columns visible during scroll

    Usage:
        >>> cols = get_matched_sequences_column_defs()

    Notes:
        - Very wide table (includes alignment string at 7000px)
        - Default sort by % Match descending (best matches first)
        - Hot/cold indices identify key positions for mutagenesis
        - Method formatter: shortenMutagenesisMethod() abbreviates text
        - Used in sequence search/alignment results view
    """
    column_def = (
        # if you want to pin any of the columns, here's how you do it
        # get_experiment_id({"width": 120, "pinned": "left"})
        # + get_smiles({"width": 150, "pinned": "left"})
        get_experiment_id({"width": 170})
        + get_smiles({"width": 200})
        + get_experiment_name({"width": 250})
        + get_alignment_scores()
        + get_experiment_meta_smiles({"width": 200}, {"width": 200})
        + get_experiment_meta(
            {"width": 120},
            {"width": 120},
            {"width": 130},
            {
                "width": 130,  # mutagenesis method
                "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            },
            {"width": 90},
        )
        + get_alignment_stats()
    )
    column_def += [
        {
            "field": gs.cc_hot_indices_per_smiles,
            "headerName": gs.header_hot_indices_per_smiles,
            "width": 250,
        },
        {
            "field": gs.cc_cold_indices_per_smiles,
            "headerName": gs.header_cold_indices_per_smiles,
            "width": 250,
        },
    ]
    column_def += get_alignment_string()

    return column_def


def get_matched_sequences_exp_hot_cold_data_column_defs():
    """
    Create complete column definitions for hot/cold spot analysis table.

    Assembles column set for displaying variants associated with identified
    hot spots (beneficial mutations) and cold spots (deleterious mutations)
    across experiments.

    Column Composition:
        1. Experiment ID (width: 170, pinned left) - Fixed during scroll
        2. Experiment Name (width: 250)
        3. Hot/Cold Type (flex: 1) - Indicator: "Hot" or "Cold"
        4. SMILES (flex: 2) - Molecular structure
        5. Plate/Well (flex: 2) - Physical location
        6. Substitutions (flex: 3) - Amino acid changes
        7. Fitness + Ratio (flex: 2 each) - Performance metrics
        8. Parent Sequence (flex: 5) - Full amino acid sequence

    Returns:
        list: Complete column definition array.
            Experiment ID pinned left for context during scroll.

    Hot/Cold Classification:
        - Hot spots: Positions where mutations consistently improve fitness
        - Cold spots: Positions where mutations consistently decrease fitness
        - Critical for rational protein engineering

    Usage:
        >>> cols = get_matched_sequences_exp_hot_cold_data_column_defs()

    Notes:
        - Experiment ID pinned for context during horizontal scroll
        - Hot/cold type enables filtering by spot classification
        - Parent sequence shows full AA context (flex: 5, largest column)
        - Used in hot/cold spot analysis view
        - Supports rational mutagenesis strategy design
    """
    column_def = get_experiment_id({"width": 170, "pinned": "left"})
    column_def += get_experiment_name({"width": 250})
    column_def += [
        {
            "field": gs.cc_hot_cold_type,
            "headerName": gs.header_hot_cold_type,
            # "width": 150,
            "flex": 1,
        },
    ]
    column_def += (
        get_smiles({"flex": 2})
        + get_plate_well({"flex": 2})
        + get_substitutions({"flex": 3})
        + get_fitness_ratio({"flex": 2}, {"flex": 2})
    )
    column_def += [
        {
            "field": "parent_sequence",
            "headerName": gs.header_aa_sequence,
            "tooltipField": "parent_sequence",
            "flex": 5,
            # "cellStyle": {"styleConditions": styles.data_bars_colorscale(df, gs.c_fitness_value)},
        },
    ]
    return column_def


def get_an_experiments_matched_sequences_column_defs():
    """
    Create complete column definitions for experiment-specific alignment table.

    Assembles comprehensive column set for displaying related variants
    within a single experiment context. Similar to get_matched_sequences_column_defs
    but optimized for single-experiment focus.

    Column Composition:
        1. Experiment ID (width: 170, pinned left) - Context during scroll
        2. Experiment Name (width: 250)
        3. Alignment Scores (1 column) - % Match with default sort
        4. SMILES (width: 150) - Molecular structure
        5. Substitutions (width: 200) - Amino acid changes
        6. Plate/Well (width: 130) - Physical location
        7. Fitness + Ratio (width: 130 each) - Performance metrics
        8. Substrate SMILES (width: 150)
        9. Product SMILES (width: 150)
        10. Metadata (5 columns, fixed widths 90-130px):
            - Date, Upload timestamp, Assay, Method, Plates
            - Method uses valueFormatter for abbreviation
        11. Alignment Stats (3 columns) - Matches, gaps, mismatches
        12. Alignment String (width: 7000) - Visual alignment

    Returns:
        list: Complete column definition array.
            All columns use fixed widths (no flex) for consistency.

    Column Pinning:
        - Experiment ID pinned left for context
        - Commented code shows option for sort by ID (typically not used)

    Usage:
        >>> cols = get_an_experiments_matched_sequences_column_defs()

    Notes:
        - Fixed widths throughout (no flex) for stable layout
        - Experiment ID pinned for context during scroll
        - Default sort by alignment score descending
        - Method formatter: shortenMutagenesisMethod() abbreviates text
        - Includes full alignment string visualization at end
        - Used in single-experiment "related variants" view
    """
    column_def = (
        # It doesn't make sense to sort by experiment ID but keeping commented for PI if of interest
        # get_experiment_id({"width": 120, "pinned": "left", "initialSort": "desc"})
        get_experiment_id({"width": 170, "pinned": "left"})
        + get_experiment_name({"width": 250})
        + get_alignment_scores()
    )
    column_def += (
        get_smiles({"width": 150})
        + get_substitutions({"width": 200})
        + get_plate_well({"width": 130})
        + get_fitness_ratio({"width": 130}, {"width": 130})
        + get_experiment_meta_smiles({"width": 150}, {"width": 150})
        + get_experiment_meta(
            {"width": 120},
            {"width": 120},
            {"width": 130},
            {
                "width": 130,  # mutagenesis method
                "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            },
            {"width": 90},
        )
        + get_alignment_stats()
        + get_alignment_string()
    )

    return column_def
