"""Reusable components for the example plugin.

This module provides reusable UI components for the example plugin. Components
defined here can be used across multiple layouts or pages within the plugin.

Components:
    create_example_stat: Creates a statistic card with icon, label, and value.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_example_stat(label: str, value: str, icon: str) -> dmc.Card:
    """Create a statistic card for the example plugin.

    Args:
        label: The label text displayed above the value (e.g., "Status").
        value: The main value to display (e.g., "Ready").
        icon: The Iconify icon identifier (e.g., "carbon:checkmark").

    Returns:
        dmc.Card: A card component containing the icon, label, and value
            in a structured layout.
    """
    return dmc.Card(
        [
            dmc.Group([
                dmc.ThemeIcon(DashIconify(icon=icon, width=18), radius="xl", variant="light"),
                dmc.Stack([
                    dmc.Text(label, size="sm", c="dimmed"),
                    dmc.Text(value, fw=600),
                ], gap=2),
            ], gap="sm"),
        ],
        withBorder=True,
        radius="md",
        p="md",
    )
