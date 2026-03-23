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
from functools import lru_cache
from typing import TypedDict

from aiml_dash.auth import AuthorizationService, UserContext
from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.runtime import PluginRuntime
from aiml_dash.utils.config import get_settings
from aiml_dash.utils.logging import get_logger

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


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _default_runtime() -> PluginRuntime:
    """Return the default plugin runtime."""
    settings = get_settings()
    return PluginRuntime(
        settings=settings,
        authorization=AuthorizationService(settings),
    )


def get_static_plugins() -> Sequence[Plugin]:
    """Return the list of statically registered plugins.

    Returns
    -------
    value : Sequence[Plugin]
        Result produced by this function."""
    return _default_runtime().get_static_plugins()


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
    return _default_runtime().get_plugins(enable_dynamic_loading=enable_dynamic_loading)


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
    return _default_runtime().get_plugin_registry(
        enable_dynamic_loading=enable_dynamic_loading
    )


def get_plugin_metadata(
    enable_dynamic_loading: bool = False,
    user: UserContext | None = None,
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
    return _default_runtime().get_plugin_metadata(
        enable_dynamic_loading=enable_dynamic_loading,
        user=user,
    )


def get_default_enabled_plugins(
    enable_dynamic_loading: bool = False,
    user: UserContext | None = None,
) -> list[str]:
    """Return the list of plugins enabled by default.

    Parameters
    ----------
    enable_dynamic_loading : bool
        Input value for ``enable_dynamic_loading``.

    Returns
    -------
    value : list[str]
        Result produced by this function."""
    return _default_runtime().get_default_enabled_plugins(
        enable_dynamic_loading=enable_dynamic_loading,
        user=user,
    )


def normalize_enabled_plugins(
    enabled_plugins: Iterable[str] | None,
    enable_dynamic_loading: bool = False,
    user: UserContext | None = None,
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
    return _default_runtime().normalize_enabled_plugins(
        enabled_plugins,
        enable_dynamic_loading=enable_dynamic_loading,
        user=user,
    )


def get_pages(
    enabled_plugins: Iterable[str] | None = None,
    enable_dynamic_loading: bool = False,
    user: UserContext | None = None,
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
    return _default_runtime().get_pages(
        enabled_plugins,
        enable_dynamic_loading=enable_dynamic_loading,
        user=user,
    )


def get_page_registry(
    enabled_plugins: Iterable[str] | None = None,
    enable_dynamic_loading: bool = False,
    user: UserContext | None = None,
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
    return _default_runtime().get_page_registry(
        enabled_plugins,
        enable_dynamic_loading=enable_dynamic_loading,
        user=user,
    )


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
    runtime = _default_runtime()
    if enable_dynamic_loading and not runtime.settings.enable_dynamic_plugins:
        logger.info("Dynamic loading requested for callback registration")
    runtime.register_plugin_callbacks(app)
