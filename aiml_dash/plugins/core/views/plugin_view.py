"""View components for plugin management."""

from __future__ import annotations

import dash_mantine_components as dmc

from aiml_dash.plugins.core.components import create_plugin_toggle_card


def render_plugin_toggles(metadata: list[dict[str, object]] | None, enabled_plugins: list[str] | None) -> list | dmc.Alert:
    """
    Render the plugin toggle cards.
    
    Args:
        metadata: List of plugin metadata dictionaries
        enabled_plugins: List of enabled plugin IDs
        
    Returns:
        List of plugin toggle cards or alert if no plugins
    """
    metadata = metadata or []
    enabled = set(enabled_plugins or [])
    
    if not metadata:
        return dmc.Alert("No plugins available.", color="gray", variant="light")

    return [
        create_plugin_toggle_card(
            plugin,
            checked=(plugin.get("id") in enabled or bool(plugin.get("locked"))),
        )
        for plugin in metadata
    ]


def create_no_plugins_message() -> dmc.Alert:
    """
    Create a message for when no plugins are available.
    
    Returns:
        Alert component
    """
    return dmc.Alert(
        "No plugins available.",
        color="gray",
        variant="light"
    )


def create_plugin_list_view(plugins: list[dict[str, object]], enabled_plugins: set[str]) -> list:
    """
    Create a list view of plugins with their toggle cards.
    
    Args:
        plugins: List of plugin metadata
        enabled_plugins: Set of enabled plugin IDs
        
    Returns:
        List of plugin toggle card components
    """
    return [
        create_plugin_toggle_card(
            plugin,
            checked=(plugin.get("id") in enabled_plugins or bool(plugin.get("locked"))),
        )
        for plugin in plugins
    ]
