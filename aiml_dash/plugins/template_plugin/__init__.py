"""Template plugin definition.

This module provides a template for creating new AIML Dash plugins. It serves
as a starting point for plugin development, demonstrating the required structure
and best practices.

The plugin follows the standard AIML Dash plugin structure:
- layout.py: Defines page layouts using Dash Mantine Components
- components.py: Contains reusable UI components
- callbacks.py: Manages interactivity and callbacks (optional)
- styles.py: Contains plugin-specific styles
- constants.py: Defines plugin-specific constants

To create a new plugin:
1. Copy the template_plugin directory to a new name
2. Update constants.py with your plugin's metadata
3. Modify layout.py to define your page structure
4. Add reusable components to components.py
5. Implement callbacks in callbacks.py if needed
6. Define custom styles in styles.py
7. Update __init__.py to use your constants
"""

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.template_plugin import callbacks
from aiml_dash.plugins.template_plugin.constants import (
    GROUP_NAME,
    GROUP_ORDER,
    PAGE_ORDER,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SECTION_NAME,
    TEMPLATE_ICON,
    TEMPLATE_PAGE_ID,
)
from aiml_dash.plugins.template_plugin.layout import template_layout


def get_plugin() -> Plugin:
    """Return the template plugin definition.

    Returns:
        Plugin: The template plugin providing a scaffold for new plugin development.
            This plugin is disabled by default and can be enabled through settings.
    """
    pages = [
        PluginPage(
            id=TEMPLATE_PAGE_ID,
            label="Template",
            icon=TEMPLATE_ICON,
            section=SECTION_NAME,
            group=GROUP_NAME,
            order=PAGE_ORDER,
            group_order=GROUP_ORDER,
            layout=template_layout,
            description="Template for creating new plugins",
        )
    ]

    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=False,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
