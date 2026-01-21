"""Styles for the basics plugin.

This module defines style constants and configuration for the basics plugin.
All style definitions from pages/basics have been reviewed and are kept inline
within the layout functions for better maintainability and locality.
"""

from aiml_dash.plugins.basics_plugin.constants import CONTAINER_SIZE

# Layout configuration
BASICS_CONTAINER_SIZE = CONTAINER_SIZE
BASICS_PADDING = "md"

# Common inline styles (used in multiple places)
HIDDEN_STYLE = {"display": "none"}
VISIBLE_STYLE = {"display": "block"}

# Container max widths
MAX_WIDTH_STANDARD = {"maxWidth": "1400px"}
MAX_WIDTH_FULL = {"maxWidth": "100%"}

# AG Grid table heights
TABLE_HEIGHT_SMALL = {"height": "100px"}
TABLE_HEIGHT_MEDIUM = {"height": "150px"}
TABLE_HEIGHT_LARGE = {"height": "300px"}

# Code element font size
CODE_FONT_SIZE = {"fontSize": "0.875rem"}

