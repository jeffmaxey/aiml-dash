"""Plugin factory helpers for AIML Dash.

This module provides utilities to build ``Plugin`` and ``PluginPage`` objects
from the dictionary-based page definitions used by each plugin's ``constants``
module and the callable-based page layouts defined in ``layout`` modules.

Functions:
    build_plugin_pages: Create a list of ``PluginPage`` objects.
    build_plugin: Create a complete ``Plugin`` object from metadata and pages.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from aiml_dash.plugins.models import Plugin, PluginPage


def build_plugin_pages(
    page_definitions: Sequence[dict[str, Any]],
    page_layouts: dict[str, Callable[[], Any]],
) -> list[PluginPage]:
    """Build a list of ``PluginPage`` objects from definitions and layouts.

    Each entry in *page_definitions* must contain at least ``"id"``,
    ``"label"``, and ``"icon"`` keys.  The corresponding layout callable is
    looked up by page ``id`` in *page_layouts*.  Definitions whose ``id`` has
    no matching layout are silently skipped.

    Parameters
    ----------
    page_definitions : Sequence[dict[str, Any]]
        Per-page metadata dictionaries (typically from a plugin's
        ``constants.PAGE_DEFINITIONS``).
    page_layouts : dict[str, Callable[[], Any]]
        Mapping of page id → layout callable (typically from a plugin's
        ``layout.PAGE_LAYOUTS``).

    Returns
    -------
    list[PluginPage]
        Ordered list of ``PluginPage`` instances with layouts attached.
    """
    pages: list[PluginPage] = []
    for defn in page_definitions:
        page_id = defn.get("id", "")
        layout = page_layouts.get(page_id)
        if layout is None:
            continue
        pages.append(
            PluginPage(
                id=page_id,
                label=defn.get("label", page_id),
                icon=defn.get("icon", "carbon:document"),
                layout=layout,
                section=defn.get("section", "Core"),
                group=defn.get("group"),
                order=defn.get("order", 0),
                group_order=defn.get("group_order", 0),
                description=defn.get("description"),
            )
        )
    return pages


def build_plugin(
    *,
    plugin_id: str,
    plugin_name: str,
    plugin_description: str,
    plugin_version: str,
    page_definitions: Sequence[dict[str, Any]],
    page_layouts: dict[str, Callable[[], Any]],
    register_callbacks: Callable[[object], None] | None = None,
    default_enabled: bool = True,
    locked: bool = False,
) -> Plugin:
    """Build a ``Plugin`` object from metadata, page definitions, and layouts.

    Parameters
    ----------
    plugin_id : str
        Unique plugin identifier (e.g. ``"core"``).
    plugin_name : str
        Human-readable plugin name.
    plugin_description : str
        Brief description of the plugin's purpose.
    plugin_version : str
        Semantic version string (e.g. ``"1.0.0"``).
    page_definitions : Sequence[dict[str, Any]]
        Per-page metadata list (from the plugin's ``constants`` module).
    page_layouts : dict[str, Callable[[], Any]]
        Mapping of page id → layout callable (from the plugin's ``layout``
        module).
    register_callbacks : Callable[[object], None] | None
        Optional function to register Dash callbacks for the plugin.
    default_enabled : bool
        Whether the plugin is enabled when first loaded.
    locked : bool
        When ``True`` the plugin cannot be disabled by the user.

    Returns
    -------
    Plugin
        Fully configured ``Plugin`` instance.
    """
    pages = build_plugin_pages(page_definitions, page_layouts)
    return Plugin(
        id=plugin_id,
        name=plugin_name,
        description=plugin_description,
        pages=pages,
        version=plugin_version,
        default_enabled=default_enabled,
        locked=locked,
        register_callbacks=register_callbacks,
    )
