"""Constants for the data plugin.

This module defines plugin-specific constants used throughout the data plugin,
including page IDs, display labels, and plugin metadata.
"""

# Plugin metadata
PLUGIN_ID = "data"
PLUGIN_NAME = "Data"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Data management and manipulation tools"

# Section and ordering
SECTION_NAME = "Data"

# Page identifiers
MANAGE_ID = "manage"
VIEW_ID = "view"
EXPLORE_ID = "explore"
TRANSFORM_ID = "transform"
VISUALIZE_ID = "visualize"
PIVOT_ID = "pivot"
COMBINE_ID = "combine"
REPORT_ID = "report"
SQL_QUERY_ID = "sql-query"

# Icons
MANAGE_ICON = "carbon:data-table"
VIEW_ICON = "carbon:view"
EXPLORE_ICON = "carbon:explore"
TRANSFORM_ICON = "carbon:settings-adjust"
VISUALIZE_ICON = "carbon:chart-scatter"
PIVOT_ICON = "carbon:data-reference"
COMBINE_ICON = "carbon:data-connected"
REPORT_ICON = "carbon:document"
SQL_QUERY_ICON = "carbon:data-base"

# Layout configuration
CONTAINER_SIZE = "fluid"

PAGE_DEFINITIONS = [
    {"id": MANAGE_ID, "label": "Manage", "icon": MANAGE_ICON, "section": SECTION_NAME, "order": 1, "description": "Manage datasets"},
    {"id": VIEW_ID, "label": "View", "icon": VIEW_ICON, "section": SECTION_NAME, "order": 2, "description": "View dataset contents"},
    {"id": EXPLORE_ID, "label": "Explore", "icon": EXPLORE_ICON, "section": SECTION_NAME, "order": 3, "description": "Explore data statistics"},
    {"id": TRANSFORM_ID, "label": "Transform", "icon": TRANSFORM_ICON, "section": SECTION_NAME, "order": 4, "description": "Transform data"},
    {"id": VISUALIZE_ID, "label": "Visualize", "icon": VISUALIZE_ICON, "section": SECTION_NAME, "order": 5, "description": "Visualize data"},
    {"id": PIVOT_ID, "label": "Pivot", "icon": PIVOT_ICON, "section": SECTION_NAME, "order": 6, "description": "Pivot tables"},
    {"id": COMBINE_ID, "label": "Combine", "icon": COMBINE_ICON, "section": SECTION_NAME, "order": 7, "description": "Combine datasets"},
    {"id": REPORT_ID, "label": "Report", "icon": REPORT_ICON, "section": SECTION_NAME, "order": 8, "description": "Generate reports"},
    {"id": SQL_QUERY_ID, "label": "SQL Query", "icon": SQL_QUERY_ICON, "section": SECTION_NAME, "order": 9, "description": "SQL queries"},
]
