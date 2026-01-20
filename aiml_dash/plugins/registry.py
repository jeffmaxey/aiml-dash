"""
Plugin registry and navigation helpers for AIML Dash.

This module provides backward-compatible functions that delegate to the PluginManager
for backend operations while maintaining UI-related functionality.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypedDict

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.plugin_manager import get_default_manager

SECTION_ORDER = [
    "Core",
    "Data",
    "Basics",
    "Design",
    "Model",
    "Multivariate",
    "Plugins",
]

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
    """Typed structure for grouped navigation pages."""

    label: str
    order: int
    pages: list[PluginPage]


class NavigationSection(TypedDict, total=False):
    """Typed structure for navigation sections."""

    label: str
    icon: str
    pages: list[PluginPage]
    groups: list[NavigationGroup]


def get_plugins() -> Sequence[Plugin]:
    """
    Return the ordered list of available plugins.

    Delegates to PluginManager for plugin discovery and registration.
    """
    return get_default_manager().get_plugins()


def get_plugin_registry() -> dict[str, Plugin]:
    """
    Return plugins keyed by their identifier.

    Delegates to PluginManager for plugin registry access.
    """
    return get_default_manager().get_plugin_registry()


def get_plugin_metadata() -> list[dict[str, object]]:
    """
    Return plugin metadata for UI rendering.

    Delegates to PluginManager for metadata generation.
    """
    return get_default_manager().get_plugin_metadata()


def get_default_enabled_plugins() -> list[str]:
    """
    Return the list of plugins enabled by default, including locked plugins.

    Delegates to PluginManager for default plugin management.
    """
    return get_default_manager().get_default_enabled_plugins()


def normalize_enabled_plugins(enabled_plugins: Iterable[str] | None) -> list[str]:
    """
    Normalize enabled plugins to include locked entries.

    Delegates to PluginManager for normalization logic.
    """
    return get_default_manager().normalize_enabled_plugins(enabled_plugins)


def get_pages(enabled_plugins: Iterable[str] | None = None) -> list[PluginPage]:
    """Return pages for enabled plugins."""

    enabled = set(normalize_enabled_plugins(enabled_plugins))
    pages: list[PluginPage] = []
    for plugin in get_plugins():
        if plugin.id in enabled:
            pages.extend(plugin.pages)
    return pages


def get_page_registry(enabled_plugins: Iterable[str] | None = None) -> dict[str, PluginPage]:
    """Return page registry keyed by page id for enabled plugins."""

    return {page.id: page for page in get_pages(enabled_plugins)}


def build_navigation_sections(pages: Sequence[PluginPage]) -> list[NavigationSection]:
    """Build navigation sections from plugin pages."""

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


def register_plugin_callbacks(app: object) -> None:
    """
    Register callbacks defined by plugins.

    Delegates to PluginManager for callback registration.
    """
    get_default_manager().register_callbacks(app)
