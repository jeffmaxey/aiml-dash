"""Callbacks for core plugin pages."""

from __future__ import annotations

import base64
import binascii
import json

import dash
from dash import ALL, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.core.components import create_plugin_toggle_card


def _get_locked_plugins(metadata: list[dict[str, object]] | None) -> set[str]:
    """Return a set of locked plugin identifiers."""

    if not metadata:
        return set()
    locked: set[str] = set()
    for plugin in metadata:
        plugin_id = plugin.get("id")
        if plugin_id and plugin.get("locked"):
            locked.add(plugin_id)
    return locked


@callback(
    Output("plugin-toggle-container", "children"),
    Input("plugin-metadata", "data"),
    Input("enabled-plugins", "data"),
)
def render_plugin_toggles(metadata: list[dict[str, object]] | None, enabled_plugins: list[str] | None):
    """Render the plugin toggle cards."""

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


@callback(
    Output("enabled-plugins", "data", allow_duplicate=True),
    Input({"type": "plugin-toggle", "plugin": ALL}, "checked"),
    State({"type": "plugin-toggle", "plugin": ALL}, "id"),
    State("plugin-metadata", "data"),
    prevent_initial_call=True,
)
def update_enabled_plugins(checked_values, ids, metadata):
    """Update enabled plugins based on toggle state."""

    if not ids:
        return dash.no_update
    locked = _get_locked_plugins(metadata)
    enabled = []
    for checked, item in zip(checked_values, ids):
        plugin_id = item.get("plugin") if isinstance(item, dict) else None
        if not plugin_id:
            continue
        if checked or plugin_id in locked:
            enabled.append(plugin_id)
    return enabled


@callback(
    Output("enabled-plugins", "data", allow_duplicate=True),
    Output("plugin-import-status", "children"),
    Input("plugin-import-upload", "contents"),
    State("plugin-metadata", "data"),
    prevent_initial_call=True,
)
def import_plugin_configuration(contents: str | None, metadata: list[dict[str, object]] | None):
    """Import plugin configuration from an uploaded JSON file."""

    if not contents:
        return dash.no_update, dash.no_update

    metadata = metadata or []
    valid_plugins = {plugin.get("id") for plugin in metadata if plugin.get("id")}
    locked = _get_locked_plugins(metadata)

    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        payload = json.loads(decoded.decode("utf-8"))
        if "enabled_plugins" in payload:
            enabled_plugins = payload.get("enabled_plugins")
        else:
            enabled_plugins = payload.get("plugins")
        if not isinstance(enabled_plugins, list):
            raise ValueError("Missing enabled_plugins list")
        cleaned = [plugin for plugin in enabled_plugins if plugin in valid_plugins]
        final_plugins = sorted(set(cleaned) | locked)
        message = dmc.Alert(
            "Plugin configuration imported successfully.",
            color="green",
            icon=DashIconify(icon="carbon:checkmark"),
            title="Import complete",
        )
        return final_plugins, message
    except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        message = dmc.Alert(
            f"Import failed: {exc}",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
            title="Import failed",
        )
        return dash.no_update, message


def register_callbacks(_app: object) -> None:
    """Register core plugin callbacks."""

    ...
