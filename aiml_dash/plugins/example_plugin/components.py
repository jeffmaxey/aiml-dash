"""Reusable components for the example plugin."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_example_stat(label: str, value: str, icon: str) -> dmc.Card:
    """Create a statistic card for the example plugin."""

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
