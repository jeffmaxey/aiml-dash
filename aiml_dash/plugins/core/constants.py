"""Constants for the core plugin.

This module defines plugin-specific constants used throughout the core plugin,
including page IDs, default values, and configuration settings.
"""

# Page identifiers
HOME_PAGE_ID = "home"
SETTINGS_PAGE_ID = "settings"
HELP_PAGE_ID = "help"
LOGS_PAGE_ID = "logs"

# Plugin metadata
PLUGIN_ID = "core"
PLUGIN_NAME = "Core Pages"
PLUGIN_VERSION = "1.1.0"
PLUGIN_DESCRIPTION = "Home, settings, help documentation, and application logs for AIML Dash."

# Section and ordering
SECTION_NAME = "Core"
HOME_PAGE_ORDER = 1
SETTINGS_PAGE_ORDER = 2
HELP_PAGE_ORDER = 3
LOGS_PAGE_ORDER = 4

# Icons
HOME_ICON = "carbon:home"
SETTINGS_ICON = "carbon:settings"
HELP_ICON = "carbon:help"
LOGS_ICON = "carbon:document-tasks"

PAGE_DEFINITIONS = [
    {
        "id": HOME_PAGE_ID,
        "label": "Home",
        "icon": HOME_ICON,
        "section": SECTION_NAME,
        "order": HOME_PAGE_ORDER,
        "description": "Main dashboard and overview page",
    },
    {
        "id": SETTINGS_PAGE_ID,
        "label": "Settings",
        "icon": SETTINGS_ICON,
        "section": SECTION_NAME,
        "order": SETTINGS_PAGE_ORDER,
        "description": "Application settings and configuration",
    },
    {
        "id": HELP_PAGE_ID,
        "label": "Help",
        "icon": HELP_ICON,
        "section": SECTION_NAME,
        "order": HELP_PAGE_ORDER,
        "description": "Help documentation and user guides",
    },
    {
        "id": LOGS_PAGE_ID,
        "label": "Logs",
        "icon": LOGS_ICON,
        "section": SECTION_NAME,
        "order": LOGS_PAGE_ORDER,
        "description": "Application logs and diagnostics",
    },
]
