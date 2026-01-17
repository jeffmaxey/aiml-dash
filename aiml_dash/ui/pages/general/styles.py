"""
Styles and Visual Components Module

This module provides styling constants, icon definitions, and visualization utilities
for the Dash application. It centralizes all visual styling elements to ensure
consistency across the application.

Contents:
    - Inline style dictionaries for common UI elements
    - Height constants for responsive layouts
    - Border and debugging styles
    - Icon definitions using Font Awesome 6
    - Utility functions for icons and data visualization

Style Categories:
    1. Upload Styles: Visual feedback for file uploads
    2. Layout Heights: Responsive viewport-based heights
    3. Border Styles: Development/debugging utilities
    4. Card Styles: Shadows and borders for cards
    5. Display Styles: Show/hide utilities
    6. Component Classes: CSS class names for styling

Icon System:
    - Uses Font Awesome 6 Solid icons via DashIconify
    - Predefined size constants (LARGE, MEDIUM, SMALL)
    - Icon identifier strings for common actions

Utility Functions:
    - get_icon(): Creates icon components with sizing
    - data_bars_group_mean_colorscale(): Generates color gradients for AG Grid cells

Design Philosophy:
    - Centralized style management
    - Reusable style constants
    - Consistent visual language
    - Responsive viewport units
    - Accessible color schemes

Author: Mantine Components Compatibility Update
Date: January 7, 2026
"""

import pandas as pd
import plotly_express as px
from dash_iconify import DashIconify

from levseq_dash.app import global_strings as gs

# --------------------
#   Inline Styles - File Upload Components
# --------------------

# Default upload button/area styling
upload_default = {
    "borderWidth": "1px",
    "borderStyle": "dashed",  # Dashed border indicates droppable area
    "padding": "10px",
    "textAlign": "center",
    "cursor": "pointer",  # Shows clickable cursor on hover
}

# Success state styling for successful uploads
upload_success = success_style = {
    "borderWidth": "4px",
    "borderStyle": "dashed",
    "padding": "10px",
    "textAlign": "center",
    "cursor": "pointer",
    "borderColor": "green",  # Green indicates success
}

# --------------------
#   Layout Heights - Responsive Viewport-Based Sizing
# --------------------

# Sequence Match page component heights
# These must be coordinated to prevent overflow/scrolling issues
seq_match_table_height = "75vh"  # 75% of viewport height for results table
seq_match_protein_viewer_height = "55vh"  # 55% of viewport for 3D protein viewer
seq_match_card_height = "95vh"  # 95% of viewport for containing card (includes headers/padding)

# Related Variants section heights
# Used in experiment detail views for variant comparison
related_variants_table_height = "65vh"  # Table of related sequence variants
related_protein_viewer_height = "65vh"  # Protein structure viewer for selected variant

# --------------------
#   Border Styles - Debugging and Development Utilities
# --------------------

# Visual debugging borders (set to 0px for production)
# Change to "1px" to visualize component boundaries during development
border_row = {"border": "0px solid blue"}  # Grid row boundaries
border_column = {"border": "0px solid red"}  # Grid column boundaries
border_card = {"border": "0px solid cyan"}  # Card component boundaries
border_table = {"border": "0px solid magenta"}  # Table component boundaries

# --------------------
#   Component Styles - Cards and Containers
# --------------------

# Card shadow effect for depth and elevation
card_shadow = {
    "box-shadow": "1px 2px 7px 0px grey",  # Subtle shadow for depth
    "border-radius": "5px",  # Rounded corners
}

# Section visibility controls
section_vis = {
    "visibility": "hidden",  # Hidden but occupies space
    "height": "70px",  # Fixed height when hidden
}

# Display utilities
display_block = {"display": "block"}  # Show element
display_none = {"display": "none"}  # Hide element (no space)

# --------------------
#   CSS Class Names - Bootstrap and Custom Classes
# --------------------

# Card header styling - used across all card components
top_card_head = "card-title fw-bold custom-card-header"

# Card body text emphasis
top_card_body = "text-primary-emphasis"

# Experiment information display styling
experiment_info = {
    "fontWeight": "bold",
    "marginRight": "15px",
}

# Main page padding class - ensures consistent alignment across pages
main_page_class = "p-1"

# --------------------
#   Icon System - Font Awesome 6 Solid
# --------------------

# Icon size constants (in pixels)
LARGE = 50  # Large icons for primary actions
MEDIUM = 20  # Medium icons for navigation and secondary actions
SMALL = 16  # Small icons for inline use

# Icon identifier strings from Font Awesome 6 Solid
# Reference: https://icon-sets.iconify.design/fa6-solid/
icon_home = "fa6-solid:house"  # Home/landing page
icon_menu = "fa6-solid:bars"  # Hamburger menu
icon_upload = "fa6-solid:upload"  # Upload files
icon_download = "fa6-solid:download"  # Download data
icon_info = "fa6-solid:circle-info"  # Information tooltip
icon_sequence = "fa6-solid:dna"  # DNA/sequence data
icon_search = "fa6-solid:magnifying-glass"  # Search/find
icon_about = "fa6-solid:circle-question"  # About/help
icon_del_exp = "fa6-solid:trash-can"  # Delete experiment
icon_go_to_next = "fa6-solid:circle-chevron-right"  # Navigate to detail
icon_database = "fa6-solid:database"  # Database/explore


def get_icon(icon_string, size=MEDIUM):
    """
    Create a Dash Iconify icon component.

    Args:
        icon_string: Icon identifier string (e.g., 'fa6-solid:house').
        size: Icon size in pixels (default: MEDIUM).

    Returns:
        DashIconify: Configured icon component.
    """
    return DashIconify(icon=icon_string, width=size)


def data_bars_group_mean_colorscale(
    df,
    value_col=gs.cc_ratio,
    min_col="min_group_ratio",
    max_col="max_group_ratio",
):
    """
    Generate AG Grid cell styles with color gradient bars for ratio visualization.

    Creates conditional cell styles with background color gradients based on normalized
    ratio values, using min/max values for proper scaling.

    Args:
        df: DataFrame containing the data.
        value_col: Column name for ratio values (default: gs.cc_ratio).
        min_col: Column name for minimum group ratio (default: 'min_group_ratio').
        max_col: Column name for maximum group ratio (default: 'max_group_ratio').

    Returns:
        list: List of style dictionaries for AG Grid cellClassRules.
    """

    styles = []

    # Fast early return if required columns don't exist or are entirely null
    if value_col not in df.columns or min_col not in df.columns or max_col not in df.columns:
        return styles

    # Fast check: if the entire ratio column is null/NaN, return empty styles
    if df[value_col].isna().all() or df[value_col].isnull().all():
        return styles

    # Also check if min/max columns are entirely null, which would make coloring meaningless
    if df[min_col].isna().all() or df[max_col].isna().all():
        return styles

    if gs.hashtag_parent not in df[gs.c_substitutions].values:
        return styles

    n_bins = 96
    color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, [i / n_bins for i in range(n_bins)])
    color_scale.reverse()

    # Normalize function for color scale mapping
    def normalize(value, min_val, max_val):
        return (value - min_val) / (max_val - min_val) if max_val - min_val != 0 else 0.5  # Avoid div by zero

    # Get color scale range (from -1 to 1)
    n_colors = len(color_scale)

    for _, row in df.iterrows():
        ratio = row[value_col]
        min_value = row[min_col]
        max_value = row[max_col]

        if pd.isna(ratio) or pd.isna(min_value) or pd.isna(max_value):
            continue  # Skip missing values

        # Normalize value to range (0, 1) for color mapping
        norm_ratio = normalize(ratio, min_value, max_value)
        color_index = int(norm_ratio * (n_colors - 1))  # Scale to color map index
        bar_color = color_scale[color_index]  # Pick color from scale

        # Determine bar width
        bar_width = int(norm_ratio * 100)  # Convert to percentage
        text_color = "white" if bar_width > 89 else "black"
        # Define bar style using CSS linear gradient
        background_style = f"""
            linear-gradient(90deg,
            {bar_color} 0%,
            {bar_color} {bar_width}%,
            white {bar_width}%,
            white 100%)
        """

        styles.append({
            "condition": f"params.value == {ratio}",
            "style": {
                "background": background_style,
                "color": text_color,
                # "textAlign": "center",
            },
        })

    return styles
