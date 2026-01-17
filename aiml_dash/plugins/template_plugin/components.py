"""Reusable components for the template plugin."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_template_card(title: str, description: str, icon: str) -> dmc.Card:
    """Create a template instruction card."""

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
