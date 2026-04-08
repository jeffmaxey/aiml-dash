"""Reusable components for the template plugin.

This module provides reusable UI components for the template plugin. Components
defined here can be used across multiple layouts or pages within the plugin.

Components:
    create_template_card: Creates an instruction card with icon, title, and description.
    create_step_card: Creates a numbered step card for the getting-started guide.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.template_plugin.styles import CARD_STYLE


def create_template_card(title: str, description: str, icon: str, color: str = "blue") -> dmc.Card:
    """Create a template instruction card.

    Parameters
    ----------
    title : str
        Card heading text.
    description : str
        Explanatory text displayed below the heading.
    icon : str
        Iconify identifier for the icon.
    color : str
        Mantine color used for the theme icon.

    Returns
    -------
    dmc.Card
        A bordered card showing the instruction.
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


def create_step_card(step: str, title: str, description: str) -> dmc.Card:
    """Create a numbered step card for the getting-started guide.

    Parameters
    ----------
    step : str
        Step number or label (e.g. ``"1"``).
    title : str
        Step heading.
    description : str
        Detailed instructions for the step.

    Returns
    -------
    dmc.Card
        A bordered card with step number badge, title, and description.
    """
    return dmc.Card(
        dmc.Group(
            [
                dmc.Badge(step, size="xl", radius="xl", variant="light", color="blue"),
                dmc.Stack(
                    [
                        dmc.Text(title, fw=600, size="sm"),
                        dmc.Text(description, size="xs", c="dimmed"),
                    ],
                    gap=2,
                ),
            ],
            gap="md",
            align="flex-start",
        ),
        withBorder=True,
        radius="md",
        p="md",
        style=CARD_STYLE,
    )
