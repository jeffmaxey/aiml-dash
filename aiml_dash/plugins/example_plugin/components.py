"""Reusable components for the example plugin.

This module provides reusable UI components for the example plugin. Components
defined here can be used across multiple layouts or pages within the plugin.

Components:
    create_example_stat: Creates a statistic card with icon, label, and value.
    create_feature_card: Creates a feature highlight card with icon, title, and description.
    create_architecture_item: Creates an architecture overview row.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.example_plugin.styles import CARD_STYLE


def create_example_stat(label: str, value: str, icon: str, color: str = "blue") -> dmc.Card:
    """Create a statistic card for the example plugin.

    Parameters
    ----------
    label : str
        Short label describing the statistic.
    value : str
        Display value for the statistic.
    icon : str
        Iconify identifier for the icon.
    color : str
        Mantine colour used for the theme icon.

    Returns
    -------
    dmc.Card
        A bordered card displaying the statistic.
    """
    return dmc.Card(
        [
            dmc.Group(
                [
                    dmc.ThemeIcon(
                        DashIconify(icon=icon, width=22),
                        radius="xl",
                        size="lg",
                        variant="light",
                        color=color,
                    ),
                    dmc.Stack(
                        [
                            dmc.Text(label, size="sm", c="dimmed"),
                            dmc.Text(value, fw=700, size="lg"),
                        ],
                        gap=2,
                    ),
                ],
                gap="sm",
            ),
        ],
        withBorder=True,
        radius="md",
        p="md",
        style=CARD_STYLE,
    )


def create_feature_card(title: str, description: str, icon: str, color: str = "blue") -> dmc.Card:
    """Create a feature highlight card.

    Parameters
    ----------
    title : str
        Card heading.
    description : str
        Short explanation of the feature.
    icon : str
        Iconify identifier for the icon.
    color : str
        Mantine colour used for the theme icon.

    Returns
    -------
    dmc.Card
        A bordered card describing a plugin feature.
    """
    return dmc.Card(
        [
            dmc.ThemeIcon(
                DashIconify(icon=icon, width=24),
                radius="xl",
                size="xl",
                variant="light",
                color=color,
                mb="sm",
            ),
            dmc.Text(title, fw=600, size="md"),
            dmc.Text(description, size="sm", c="dimmed", mt="xs"),
        ],
        withBorder=True,
        radius="md",
        p="lg",
        style=CARD_STYLE,
    )


def create_architecture_item(label: str, description: str, icon: str) -> dmc.Group:
    """Create an architecture overview row.

    Parameters
    ----------
    label : str
        Module or concept name.
    description : str
        Brief explanation.
    icon : str
        Iconify identifier for the icon.

    Returns
    -------
    dmc.Group
        A horizontal group showing an icon, label, and description.
    """
    return dmc.Group(
        [
            dmc.ThemeIcon(
                DashIconify(icon=icon, width=18),
                radius="md",
                size="md",
                variant="light",
                color="gray",
            ),
            dmc.Stack(
                [
                    dmc.Text(label, fw=600, size="sm"),
                    dmc.Text(description, size="xs", c="dimmed"),
                ],
                gap=0,
            ),
        ],
        gap="sm",
    )
