"""
AIML Dash - Theme Configuration
================================

Centralized theme configuration for the AIML Data Dash application.
This file contains all theme-related configurations including font families,
colors, and component styles used throughout the application.

Author: Converted from aiml.data R package
License: AGPL-3
"""

# Theme configuration for Mantine components
THEME_CONFIG = {
    "fontFamily": "'Inter', sans-serif",
    "primaryColor": "blue",
    "components": {
        "Button": {"defaultProps": {"fw": 400}},
        "Alert": {"styles": {"title": {"fontWeight": 500}}},
        "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
    },
}
