"""Styles for the template plugin.

This module defines style constants and configuration for the template plugin.
These constants ensure consistent styling across the plugin's components.
"""

from aiml_dash.plugins.template_plugin.constants import CONTAINER_SIZE

# Layout configuration
TEMPLATE_CONTAINER_SIZE = CONTAINER_SIZE

# Shared card style for uniform height in grids
CARD_STYLE: dict[str, str] = {"height": "100%"}

# Section spacing
SECTION_GAP = "xl"
