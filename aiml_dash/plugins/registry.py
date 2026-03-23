"""
Plugin registry and navigation helpers for AIML Dash.

This module provides the central registry for managing plugins in AIML Dash.
It supports both static plugin registration (for core plugins) and dynamic
plugin discovery and loading.

The registry provides:
- Plugin discovery and loading
- Page registration and routing
- Navigation structure building
- Plugin enable/disable functionality
- Callback registration for plugins
- Dependency management and version checking
- Plugin configuration management
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypedDict

from aiml_dash.plugins import (basics_plugin, core, data_plugin, design_plugin,
                               example_plugin, model_plugin,
                               multivariate_plugin, template_plugin)
from aiml_dash.plugins.loader import load_plugins_dynamically
from aiml_dash.plugins.models import Plugin, PluginPage

# Section ordering for navigation
SECTION_ORDER = [
    "Core",
    "Data",
    "Basics",
    "Design",
    "Model",
    "Multivariate",
    "Plugins",
]

# Icons for navigation sections
SECTION_ICONS = {
    "Core": "carbon:home",
    "Data": "carbon:data-base",
    "Basics": "carbon:calculator",
    "Design": "carbon:chemistry",
    "Model": "carbon:machine-learning",
    "Multivariate": "carbon:chart-multitype",
    "Plugins": "carbon:plugin",
}


class NavigationGroup(TypedDict):
    """Typed structure for grouped navigation pages.

    Attributes:
        label: The display label for the group.
        order: Sort order for the group.
        pages: List of pages in the group.
    """

    label: str
    order: int
    pages: list[PluginPage]


class NavigationSection(TypedDict, total=False):
    """Typed structure for navigation sections.

    Attributes:
        label: The display label for the section.
        icon: The Iconify icon identifier for the section.
        pages: List of pages directly in the section (no group).
        groups: List of grouped pages within the section.
    """

    label: str
    icon: str
    pages: list[PluginPage]
    groups: list[NavigationGroup]


def get_static_plugins() -> Sequence[Plugin]:
    """Return the list of statically registered plugins.

    Returns
    -------
    value : Sequence[Plugin]
        Result produced by this function."""
    return [
        core.get_plugin(),
        data_plugin.get_plugin(),
        basics_plugin.get_plugin(),
        design_plugin.get_plugin(),
        model_plugin.get_plugin(),
        multivariate_plugin.get_plugin(),
        example_plugin.get_plugin(),
        template_plugin.get_plugin(),
    ]


def get_plugins(enable_dynamic_loading: bool = False) -> Sequence[Plugin]:
    """Return the ordered list of available plugins.

    Parameters
    ----------
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : Sequence[Plugin]
        Result produced by this function."""
    plugins = list(get_static_plugins())

    if enable_dynamic_loading:
        # Load dynamic plugins and add any that aren't already registered
        dynamic_plugins = load_plugins_dynamically()
        static_plugin_ids = {p.id for p in plugins}

        for plugin in dynamic_plugins:
            if plugin.id not in static_plugin_ids:
                plugins.append(plugin)

    return plugins


def get_plugin_registry(enable_dynamic_loading: bool = False) -> dict[str, Plugin]:
    """Return plugins keyed by their identifier.

    Parameters
    ----------
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : dict[str, Plugin]
        Result produced by this function."""
    return {plugin.id: plugin for plugin in get_plugins(enable_dynamic_loading)}


def get_plugin_metadata(
    enable_dynamic_loading: bool = False,
) -> list[dict[str, object]]:
    """Return plugin metadata for UI rendering.

    Parameters
    ----------
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : list[dict[str, object]]
        Result produced by this function."""
    metadata = []
    for plugin in get_plugins(enable_dynamic_loading):
        metadata.append(
            {
                "id": plugin.id,
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "locked": plugin.locked,
                "default_enabled": plugin.default_enabled,
            }
        )
    return metadata


def get_default_enabled_plugins(enable_dynamic_loading: bool = False) -> list[str]:
    """Return the list of plugins enabled by default.

    Parameters
    ----------
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : list[str]
        Result produced by this function."""
    return [
        plugin.id
        for plugin in get_plugins(enable_dynamic_loading)
        if plugin.default_enabled or plugin.locked
    ]


def normalize_enabled_plugins(
    enabled_plugins: Iterable[str] | None, enable_dynamic_loading: bool = False
) -> list[str]:
    """Normalize enabled plugins to include locked entries.

    Parameters
    ----------
    enabled_plugins : Iterable[str] | None
        Input value for ``enabled_plugins``.
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : list[str]
        Result produced by this function."""
    registry = get_plugin_registry(enable_dynamic_loading)
    enabled = list(
        enabled_plugins or get_default_enabled_plugins(enable_dynamic_loading)
    )
    for plugin in registry.values():
        if plugin.locked and plugin.id not in enabled:
            enabled.append(plugin.id)
    return [plugin_id for plugin_id in enabled if plugin_id in registry]


def get_pages(
    enabled_plugins: Iterable[str] | None = None, enable_dynamic_loading: bool = False
) -> list[PluginPage]:
    """Return pages for enabled plugins.

    Parameters
    ----------
    enabled_plugins : Iterable[str] | None
        Input value for ``enabled_plugins``.
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : list[PluginPage]
        Result produced by this function."""
    enabled = set(normalize_enabled_plugins(enabled_plugins, enable_dynamic_loading))
    pages: list[PluginPage] = []
    for plugin in get_plugins(enable_dynamic_loading):
        if plugin.id in enabled:
            pages.extend(plugin.pages)
    return pages


def get_page_registry(
    enabled_plugins: Iterable[str] | None = None, enable_dynamic_loading: bool = False
) -> dict[str, PluginPage]:
    """Return page registry keyed by page id for enabled plugins.

    Parameters
    ----------
    enabled_plugins : Iterable[str] | None
        Input value for ``enabled_plugins``.
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : dict[str, PluginPage]
        Result produced by this function."""
    return {
        page.id: page for page in get_pages(enabled_plugins, enable_dynamic_loading)
    }


def build_navigation_sections(pages: Sequence[PluginPage]) -> list[NavigationSection]:
    """Build navigation sections from plugin pages.

    Parameters
    ----------
    pages : Sequence[PluginPage]
        Input value for ``pages``.

    Returns
    -------
    value : list[NavigationSection]
        Result produced by this function."""
    section_map: dict[str, list[PluginPage]] = {}
    for page in pages:
        section_map.setdefault(page.section, []).append(page)

    sections: list[NavigationSection] = []
    for section in SECTION_ORDER:
        if section not in section_map:
            continue
        section_pages = section_map[section]
        groups: dict[str, list[PluginPage]] = {}
        for page in section_pages:
            group_key = page.group or ""
            groups.setdefault(group_key, []).append(page)
        section_entry: NavigationSection = {
            "label": section,
            "icon": SECTION_ICONS.get(section, "carbon:document"),
        }
        if "" in groups:
            section_entry["pages"] = sorted(groups.pop(""), key=lambda item: item.order)
        if groups:
            group_entries: list[NavigationGroup] = []
            for group_label, group_pages in groups.items():
                sorted_pages = sorted(group_pages, key=lambda item: item.order)
                group_entries.append(
                    {
                        "label": group_label,
                        "order": sorted_pages[0].group_order,
                        "pages": sorted_pages,
                    }
                )
            section_entry["groups"] = sorted(
                group_entries, key=lambda item: (item["order"], item["label"])
            )
        sections.append(section_entry)
    return sections


def register_plugin_callbacks(
    app: object, enable_dynamic_loading: bool = False
) -> None:
    """Register callbacks defined by plugins.

    Parameters
    ----------
    app : object
        Input value for ``app``.
    enable_dynamic_loading : bool
        Value provided for this parameter."""
    for plugin in get_plugins(enable_dynamic_loading):
        if plugin.register_callbacks:
            plugin.register_callbacks(app)
