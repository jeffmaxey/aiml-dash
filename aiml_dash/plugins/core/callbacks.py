"""Callbacks for core plugin pages."""

from __future__ import annotations

import base64
import binascii
import json

import dash
from dash import ALL, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Import controller and view modules
from aiml_dash.plugins.core.controllers import get_locked_plugins
from aiml_dash.plugins.core.views import render_plugin_toggles as view_render_plugin_toggles

ENABLED_PLUGINS_KEY = "enabled_plugins"
FALLBACK_PLUGINS_KEY = "plugins"


@callback(
    Output("plugin-toggle-container", "children"),
    Input("plugin-metadata", "data"),
    Input("enabled-plugins", "data"),
)
def render_plugin_toggles(metadata: list[dict[str, object]] | None, enabled_plugins: list[str] | None):
    """
    Render the plugin toggle cards.
    
    This callback delegates to the view layer for rendering.
    """
    return view_render_plugin_toggles(metadata, enabled_plugins)


@callback(
    Output("enabled-plugins", "data", allow_duplicate=True),
    Input({"type": "plugin-toggle", "plugin": ALL}, "checked"),
    State({"type": "plugin-toggle", "plugin": ALL}, "id"),
    State("plugin-metadata", "data"),
    prevent_initial_call=True,
)
def update_enabled_plugins(checked_values, ids, metadata):
    """
    Update enabled plugins based on toggle state.
    
    This callback uses the controller layer for business logic.
    """
    if not ids:
        return dash.no_update
    
    # Use controller to get locked plugins
    locked = get_locked_plugins(metadata)
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
    """
    Import plugin configuration from an uploaded JSON file.
    
    This callback combines controller logic for data processing and view logic for feedback.
    """
    if not contents:
        return dash.no_update, dash.no_update

    metadata = metadata or []
    valid_plugins = {plugin.get("id") for plugin in metadata if plugin.get("id")}
    
    # Use controller to get locked plugins
    locked = get_locked_plugins(metadata)

    try:
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        payload = json.loads(decoded.decode("utf-8"))
        if ENABLED_PLUGINS_KEY in payload:
            enabled_plugins = payload.get(ENABLED_PLUGINS_KEY)
        else:
            enabled_plugins = payload.get(FALLBACK_PLUGINS_KEY)
        if not isinstance(enabled_plugins, list):
            raise ValueError("Missing enabled_plugins list")
        cleaned = [plugin for plugin in enabled_plugins if plugin in valid_plugins]
        final_plugins = sorted(set(cleaned) | locked)
        
        # View: Success message
        message = dmc.Alert(
            "Plugin configuration imported successfully.",
            color="green",
            icon=DashIconify(icon="carbon:checkmark"),
            title="Import complete",
        )
        return final_plugins, message
    except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        # View: Error message
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
