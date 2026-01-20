"""Reusable components for the template plugin.

This module provides reusable UI components for the template plugin. Components
defined here can be used across multiple layouts or pages within the plugin.

Components:
    create_template_card: Creates an instruction card with icon, title, and description.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_template_card(title: str, description: str, icon: str) -> dmc.Card:
    """Create a template instruction card.

    Args:
        title: The card title text (e.g., "Layout").
        description: The description text explaining the component's purpose.
        icon: The Iconify icon identifier (e.g., "carbon:layout").

    Returns:
        dmc.Card: A card component containing the icon, title, and description
            in a structured layout suitable for instructional content.
    """
    return dmc.Card(
        [
            dmc.Group([
                dmc.ThemeIcon(DashIconify(icon=icon, width=18), radius="xl", variant="light"),
                dmc.Text(title, fw=600),
            ], gap="sm"),
            dmc.Text(description, size="sm", c="dimmed", mt="xs"),
        ],
        withBorder=True,
        radius="md",
        p="md",
    )
