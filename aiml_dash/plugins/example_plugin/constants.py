"""Constants for the example plugin.

This module defines plugin-specific constants used throughout the example plugin,
including page IDs, default values, and configuration settings.
"""

# Page identifiers
EXAMPLE_PAGE_ID = "example"

# Plugin metadata
PLUGIN_ID = "example"
PLUGIN_NAME = "Example Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Interactive showcase of the AIML Dash plugin architecture."

# Section and ordering
SECTION_NAME = "Plugins"
GROUP_NAME = "Example Plugin"
PAGE_ORDER = 1
GROUP_ORDER = 2

# Icons
EXAMPLE_ICON = "carbon:apps"

# Layout configuration
CONTAINER_SIZE = "lg"

PAGE_DEFINITIONS = [
    {
        "id": EXAMPLE_PAGE_ID,
        "label": "Example",
        "icon": EXAMPLE_ICON,
        "section": SECTION_NAME,
        "group": GROUP_NAME,
        "order": PAGE_ORDER,
        "group_order": GROUP_ORDER,
        "description": "Interactive showcase of the AIML Dash plugin architecture",
    }
]
