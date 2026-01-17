"""Reusable components for core plugin pages."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.core.styles import CARD_STYLE


def create_section_header(title: str, description: str) -> dmc.Stack:
    """Create a section header with title and description."""

    return dmc.Stack([
        dmc.Title(title, order=2),
        dmc.Text(description, c="dimmed"),
    ], gap="xs")


def create_feature_card(title: str, description: str, icon: str) -> dmc.Card:
    """Create a feature highlight card."""

    return dmc.Card(
        [
            dmc.Group([
                dmc.ThemeIcon(DashIconify(icon=icon, width=20), radius="xl", variant="light"),
                dmc.Text(title, fw=600),
            ], gap="sm"),
            dmc.Text(description, size="sm", c="dimmed", mt="xs"),
        ],
        withBorder=True,
        radius="md",
        p="md",
        style=CARD_STYLE,
    )


def create_step_card(step: str, title: str, description: str, code: str | None = None) -> dmc.Card:
    """Create an instructional step card."""

    content = [
        dmc.Group([
            dmc.Badge(step, color="blue", variant="filled"),
            dmc.Text(title, fw=600),
        ], gap="sm"),
        dmc.Text(description, size="sm", c="dimmed", mt="xs"),
    ]
    if code:
        content.append(dmc.Code(code, block=True, mt="sm"))
    return dmc.Card(content, withBorder=True, radius="md", p="md")


def create_resource_item(title: str, description: str, icon: str) -> dmc.Group:
    """Create a resource line item."""

    return dmc.Group([
        dmc.ThemeIcon(DashIconify(icon=icon, width=18), radius="xl", variant="light"),
        dmc.Stack(
            [
                dmc.Text(title, fw=500),
                dmc.Text(description, size="sm", c="dimmed"),
            ],
            gap=2,
        ),
    ], gap="sm", align="flex-start")


def create_plugin_toggle_card(plugin: dict[str, object], checked: bool) -> dmc.Card:
    """Create a plugin toggle card."""

    locked = bool(plugin.get("locked"))
    return dmc.Card(
        [
            dmc.Group([
                dmc.Stack([
                    dmc.Text(plugin.get("name", "Plugin"), fw=600),
                    dmc.Text(plugin.get("description", ""), size="sm", c="dimmed"),
                    dmc.Text(f"Version {plugin.get('version', '1.0')}", size="xs", c="dimmed"),
                ], gap=4),
                dmc.Switch(
                    id={"type": "plugin-toggle", "plugin": plugin.get("id")},
                    checked=checked,
                    disabled=locked,
                    onLabel="On",
                    offLabel="Off",
                    color="blue",
                ),
            ], justify="space-between", align="flex-start"),
        ],
        withBorder=True,
        radius="md",
        p="md",
    )
