"""Example plugin definition.

This module defines an example plugin for AIML Dash, demonstrating the minimal
structure and components needed to create a functional plugin. Use this as a
reference when developing new plugins.

The plugin follows the standard AIML Dash plugin structure:
- layout.py: Defines page layouts using Dash Mantine Components
- components.py: Contains reusable UI components
- callbacks.py: Manages interactivity and callbacks (optional)
- styles.py: Contains plugin-specific styles
- constants.py: Defines plugin-specific constants

Example Usage:
    The plugin is automatically discovered and loaded by the plugin registry.
    Users can enable or disable it through the settings page.
"""

from aiml_dash.plugins.example_plugin import callbacks
from aiml_dash.plugins.example_plugin.constants import (
    EXAMPLE_ICON,
    EXAMPLE_PAGE_ID,
    GROUP_NAME,
    GROUP_ORDER,
    PAGE_ORDER,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SECTION_NAME,
)
from aiml_dash.plugins.example_plugin.layout import example_layout
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the example plugin definition.

    Returns:
        Plugin: The example plugin containing a single demonstration page
            showing how to structure a basic plugin with Dash Mantine Components.
    """
    pages = [
        PluginPage(
            id=EXAMPLE_PAGE_ID,
            label="Example",
            icon=EXAMPLE_ICON,
            section=SECTION_NAME,
            group=GROUP_NAME,
            order=PAGE_ORDER,
            group_order=GROUP_ORDER,
            layout=example_layout,
            description="Demonstration of a minimal plugin structure",
        )
    ]

    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
