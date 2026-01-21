"""Shared plugin dataclasses for AIML Dash.

This module defines the core data structures used throughout the plugin framework.
These models provide a standardized interface for plugins to integrate with the
main application.

Classes:
    PluginPage: Represents a single page/route provided by a plugin.
    Plugin: Metadata and configuration for a complete plugin.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from dash.development.base_component import Component

# Standard home page ID used across the application
HOME_PAGE_ID = "home"


@dataclass(frozen=True)
class PluginPage:
    """Definition for a plugin-provided page.

    Each page represents a route/view in the application with associated
    layout, navigation metadata, and descriptive information.

    Attributes:
        id: Unique identifier for the page (used for routing).
        label: Display name shown in navigation.
        icon: Iconify icon identifier (e.g., "carbon:home").
        layout: Callable that returns the page's Dash component tree.
        section: Top-level navigation section this page belongs to.
        group: Optional sub-grouping within the section.
        order: Sort order within the group/section (lower numbers first).
        group_order: Sort order for the group itself within the section.
        description: Optional description of the page's purpose.
    """

    id: str
    label: str
    icon: str
    layout: Callable[[], Component]
    section: str
    group: str | None = None
    order: int = 0
    group_order: int = 0
    description: str | None = None


@dataclass(frozen=True)
class Plugin:
    """Metadata describing a plugin and its pages.

    A plugin is a self-contained module that provides one or more pages
    to the application. Plugins can be enabled/disabled at runtime.

    Attributes:
        id: Unique identifier for the plugin.
        name: Human-readable plugin name.
        description: Brief description of the plugin's functionality.
        pages: Sequence of pages provided by this plugin.
        version: Plugin version string (e.g., "1.0.0").
        default_enabled: Whether the plugin is enabled by default.
        locked: If True, plugin cannot be disabled by users.
        register_callbacks: Optional function to register Dash callbacks.
        dependencies: List of plugin IDs that this plugin depends on.
        min_app_version: Minimum application version required (e.g., "0.0.1").
        max_app_version: Maximum application version supported (e.g., "1.0.0").
        config_schema: Optional configuration schema for plugin settings.
        marketplace_url: Optional URL to plugin marketplace/repository.
    """

    id: str
    name: str
    description: str
    pages: Sequence[PluginPage]
    version: str = "1.0"
    default_enabled: bool = True
    locked: bool = False
    register_callbacks: Callable[[object], None] | None = None
    dependencies: Sequence[str] = ()
    min_app_version: str | None = None
    max_app_version: str | None = None
    config_schema: dict | None = None
    marketplace_url: str | None = None
