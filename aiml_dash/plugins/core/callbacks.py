"""Callbacks for core plugin pages."""

from __future__ import annotations

import base64
import binascii
import json
import platform
import sys
from datetime import datetime

import dash
import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback
from dash_iconify import DashIconify

from aiml_dash.plugins.core.components import create_plugin_toggle_card
from aiml_dash.utils.log_manager import log_manager

ENABLED_PLUGINS_KEY = "enabled_plugins"
FALLBACK_PLUGINS_KEY = "plugins"


def _get_locked_plugins(metadata: list[dict[str, object]] | None) -> set[str]:
    """Return a set of locked plugin identifiers."""

    if not metadata:
        return set()
    locked: set[str] = set()
    for plugin in metadata:
        plugin_id = plugin.get("id")
        if plugin_id and plugin.get("locked"):
            locked.add(str(plugin_id))
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
    for checked, item in zip(checked_values, ids, strict=False):
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


# ============================================================================
# Logs Page Callbacks
# ============================================================================

# Store for application start time
_app_start_time = datetime.now()


def _create_log_entry_card(log: dict[str, str]) -> dmc.Card:
    """Create a visual card for a log entry."""
    level = log.get("level", "info")
    
    # Color and icon mapping
    level_config = {
        "debug": {"color": "gray", "icon": "carbon:debug"},
        "info": {"color": "blue", "icon": "carbon:information"},
        "warning": {"color": "yellow", "icon": "carbon:warning"},
        "error": {"color": "red", "icon": "carbon:error"},
    }
    
    config = level_config.get(level, level_config["info"])
    
    return dmc.Card(
        dmc.Group([
            dmc.ThemeIcon(
                DashIconify(icon=config["icon"], width=16),
                size="sm",
                radius="md",
                variant="light",
                color=config["color"],
            ),
            dmc.Stack([
                dmc.Group([
                    dmc.Badge(level.upper(), color=config["color"], size="sm"),
                    dmc.Badge(log.get("source", "core").upper(), variant="outline", size="sm"),
                    dmc.Text(log.get("timestamp", ""), size="xs", c="dimmed"),
                ], gap="xs"),
                dmc.Text(log.get("message", ""), size="sm"),
            ], gap=4),
        ], align="flex-start", gap="sm"),
        withBorder=True,
        radius="sm",
        p="sm",
    )


@callback(
    Output("log-entries-container", "children"),
    Output("log-count-info", "children"),
    Output("log-count-warning", "children"),
    Output("log-count-error", "children"),
    Output("log-count-total", "children"),
    Input("log-refresh-interval", "n_intervals"),
    Input("log-refresh-button", "n_clicks"),
    Input("log-level-filter", "value"),
    Input("log-source-filter", "value"),
    prevent_initial_call=False,
)
def update_log_display(n_intervals, n_clicks, level_filter, source_filter):
    """Update the log display with filtered logs."""
    logs = log_manager.get_logs(
        level_filter=level_filter or "all",
        source_filter=source_filter or "all",
        limit=100,  # Show last 100 logs
    )
    
    counts = log_manager.get_log_counts()
    
    if not logs:
        log_entries = [
            dmc.Text(
                "No logs match the current filters.",
                size="sm",
                c="dimmed",
                ta="center",
                py="xl",
            )
        ]
    else:
        log_entries = [_create_log_entry_card(log) for log in logs]
    
    return (
        log_entries,
        str(counts["info"]),
        str(counts["warning"]),
        str(counts["error"]),
        str(counts["total"]),
    )


@callback(
    Output("log-entries-container", "children", allow_duplicate=True),
    Output("log-count-info", "children", allow_duplicate=True),
    Output("log-count-warning", "children", allow_duplicate=True),
    Output("log-count-error", "children", allow_duplicate=True),
    Output("log-count-total", "children", allow_duplicate=True),
    Input("log-clear-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_logs(n_clicks):
    """Clear all logs."""
    if n_clicks:
        log_manager.clear_logs()
        log_manager.add_log("info", "Logs cleared by user", "core")
        
    return (
        [dmc.Text("Logs cleared.", size="sm", c="dimmed", ta="center", py="xl")],
        "0",
        "0",
        "0",
        "1",
    )


@callback(
    Output("log-download", "data"),
    Input("log-download-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_logs(n_clicks):
    """Download logs as a text file."""
    if n_clicks:
        log_text = log_manager.get_logs_as_text()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return dict(content=log_text, filename=f"aiml_dash_logs_{timestamp}.txt")
    return dash.no_update


@callback(
    Output("sys-python-version", "children"),
    Output("sys-dash-version", "children"),
    Output("sys-uptime", "children"),
    Output("sys-plugin-count", "children"),
    Input("log-refresh-interval", "n_intervals"),
    State("enabled-plugins", "data"),
)
def update_system_info(n_intervals, enabled_plugins):
    """Update system information display."""
    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Dash version
    try:
        import dash as dash_module
        dash_version = dash_module.__version__
    except Exception:
        dash_version = "Unknown"
    
    # Uptime
    uptime_delta = datetime.now() - _app_start_time
    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    
    # Plugin count
    plugin_count = str(len(enabled_plugins or []))
    
    return python_version, dash_version, uptime, plugin_count
