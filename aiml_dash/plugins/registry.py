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

from aiml_dash.plugins import core, example_plugin, legacy, template_plugin
from aiml_dash.plugins.dependency_manager import resolve_dependencies, validate_plugin
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

    These are core plugins that are always loaded first, including
    essential functionality like the home page and settings.

    Returns:
        Sequence[Plugin]: List of statically registered plugins.
    """
    return [core.get_plugin(), legacy.get_plugin(), example_plugin.get_plugin(), template_plugin.get_plugin()]


def get_plugins(enable_dynamic_loading: bool = False) -> Sequence[Plugin]:
    """Return the ordered list of available plugins.

    Args:
        enable_dynamic_loading: If True, also discover and load plugins
            dynamically from the plugins directory. Default is False for
            backward compatibility.

    Returns:
        Sequence[Plugin]: Combined list of static and dynamically loaded plugins.
    """
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

    Args:
        enable_dynamic_loading: If True, include dynamically loaded plugins.

    Returns:
        dict[str, Plugin]: Dictionary mapping plugin IDs to Plugin objects.
    """
    return {plugin.id: plugin for plugin in get_plugins(enable_dynamic_loading)}


def get_plugin_metadata(enable_dynamic_loading: bool = False) -> list[dict[str, object]]:
    """Return plugin metadata for UI rendering.

    Args:
        enable_dynamic_loading: If True, include dynamically loaded plugins.

    Returns:
        list[dict[str, object]]: List of plugin metadata dictionaries.
    """
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

    This includes plugins where default_enabled=True or locked=True.

    Args:
        enable_dynamic_loading: If True, include dynamically loaded plugins.

    Returns:
        list[str]: List of plugin IDs that should be enabled by default.
    """
    return [plugin.id for plugin in get_plugins(enable_dynamic_loading) if plugin.default_enabled or plugin.locked]


def normalize_enabled_plugins(
    enabled_plugins: Iterable[str] | None, enable_dynamic_loading: bool = False
) -> list[str]:
    """Normalize enabled plugins to include locked entries.

    Ensures that locked plugins (like core) are always enabled, even if
    not explicitly included in the enabled_plugins list.

    Args:
        enabled_plugins: List of plugin IDs that are enabled, or None to use defaults.
        enable_dynamic_loading: If True, consider dynamically loaded plugins.

    Returns:
        list[str]: Normalized list of enabled plugin IDs.
    """
    registry = get_plugin_registry(enable_dynamic_loading)
    enabled = list(enabled_plugins or get_default_enabled_plugins(enable_dynamic_loading))
    for plugin in registry.values():
        if plugin.locked and plugin.id not in enabled:
            enabled.append(plugin.id)
    return [plugin_id for plugin_id in enabled if plugin_id in registry]


def get_pages(enabled_plugins: Iterable[str] | None = None, enable_dynamic_loading: bool = False) -> list[PluginPage]:
    """Return pages for enabled plugins.

    Args:
        enabled_plugins: List of plugin IDs to include, or None for defaults.
        enable_dynamic_loading: If True, include dynamically loaded plugins.

    Returns:
        list[PluginPage]: List of pages from enabled plugins.
    """
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

    Args:
        enabled_plugins: List of plugin IDs to include, or None for defaults.
        enable_dynamic_loading: If True, include dynamically loaded plugins.

    Returns:
        dict[str, PluginPage]: Dictionary mapping page IDs to PluginPage objects.
    """
    return {page.id: page for page in get_pages(enabled_plugins, enable_dynamic_loading)}


def build_navigation_sections(pages: Sequence[PluginPage]) -> list[NavigationSection]:
    """Build navigation sections from plugin pages.

    Organizes pages into a hierarchical structure with sections, groups,
    and individual pages.

    Args:
        pages: List of plugin pages to organize.

    Returns:
        list[NavigationSection]: Organized navigation structure.
    """
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
            section_entry["groups"] = sorted(group_entries, key=lambda item: (item["order"], item["label"]))
        sections.append(section_entry)
    return sections


def register_plugin_callbacks(app: object, enable_dynamic_loading: bool = False) -> None:
    """Register callbacks defined by plugins.

    Args:
        app: The Dash application instance.
        enable_dynamic_loading: If True, include dynamically loaded plugins.
    """
    for plugin in get_plugins(enable_dynamic_loading):
        if plugin.register_callbacks:
            plugin.register_callbacks(app)
