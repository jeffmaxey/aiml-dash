"""Core plugin providing home, help, and settings pages.

This module defines the core plugin for AIML Dash, which provides essential
pages including the home page, settings, and help documentation. The core
plugin is locked and cannot be disabled.

The plugin follows the standard AIML Dash plugin structure:
- layout.py: Defines page layouts
- components.py: Contains reusable UI components
- callbacks.py: Manages interactivity and callbacks
- styles.py: Contains plugin-specific styles
- constants.py: Defines plugin-specific constants
"""

from aiml_dash.plugins.core import callbacks
from aiml_dash.plugins.core.constants import (
    HELP_ICON,
    HELP_PAGE_ID,
    HELP_PAGE_ORDER,
    HOME_ICON,
    HOME_PAGE_ORDER,
    LOGS_ICON,
    LOGS_PAGE_ID,
    LOGS_PAGE_ORDER,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SECTION_NAME,
    SETTINGS_ICON,
    SETTINGS_PAGE_ID,
    SETTINGS_PAGE_ORDER,
)
from aiml_dash.plugins.core.layout import help_layout, home_layout, logs_layout, settings_layout
from aiml_dash.plugins.models import HOME_PAGE_ID, Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the core plugin definition.

    Returns:
        Plugin: The core plugin containing home, settings, and help pages.
            This plugin is locked and cannot be disabled.
    """
    pages = [
        PluginPage(
            id=HOME_PAGE_ID,
            label="Home",
            icon=HOME_ICON,
            section=SECTION_NAME,
            order=HOME_PAGE_ORDER,
            layout=home_layout,
            description="Main dashboard and overview page",
        ),
        PluginPage(
            id=SETTINGS_PAGE_ID,
            label="Settings",
            icon=SETTINGS_ICON,
            section=SECTION_NAME,
            order=SETTINGS_PAGE_ORDER,
            layout=settings_layout,
            description="Application settings and configuration",
        ),
        PluginPage(
            id=HELP_PAGE_ID,
            label="Help",
            icon=HELP_ICON,
            section=SECTION_NAME,
            order=HELP_PAGE_ORDER,
            layout=help_layout,
            description="Help documentation and user guides",
        ),
        PluginPage(
            id=LOGS_PAGE_ID,
            label="Logs",
            icon=LOGS_ICON,
            section=SECTION_NAME,
            order=LOGS_PAGE_ORDER,
            layout=logs_layout,
            description="Application logs and diagnostics",
        ),
    ]

    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=True,
        locked=True,
        register_callbacks=callbacks.register_callbacks,
    )
