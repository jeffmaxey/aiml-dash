"""Plugin dependency and version management for AIML Dash.

This module handles plugin dependencies, version compatibility checks,
and dependency resolution for the plugin framework.
"""

from __future__ import annotations

import logging
from typing import Sequence

from aiml_dash.plugins.models import Plugin

logger = logging.getLogger(__name__)


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a version string into a tuple of integers.

    Args:
        version_str: Version string (e.g., "1.2.3").

    Returns:
        tuple[int, ...]: Tuple of version components.

    Example:
        >>> parse_version("1.2.3")
        (1, 2, 3)
    """
    try:
        return tuple(int(x) for x in version_str.split("."))
    except (ValueError, AttributeError):
        logger.warning(f"Invalid version string: {version_str}")
        return (0, 0, 0)


def check_version_compatibility(
    plugin: Plugin, app_version: str = "0.0.1"
) -> tuple[bool, str]:
    """Check if a plugin is compatible with the application version.

    Args:
        plugin: Plugin to check compatibility for.
        app_version: Current application version.

    Returns:
        tuple[bool, str]: (is_compatible, error_message).
            If compatible, error_message is empty.
    """
    app_ver = parse_version(app_version)

    # Check minimum version
    if plugin.min_app_version:
        min_ver = parse_version(plugin.min_app_version)
        if app_ver < min_ver:
            return False, f"Plugin '{plugin.name}' requires app version >= {plugin.min_app_version}"

    # Check maximum version
    if plugin.max_app_version:
        max_ver = parse_version(plugin.max_app_version)
        if app_ver > max_ver:
            return False, f"Plugin '{plugin.name}' requires app version <= {plugin.max_app_version}"

    return True, ""


def check_dependencies(
    plugin: Plugin, available_plugins: dict[str, Plugin]
) -> tuple[bool, str]:
    """Check if all plugin dependencies are available.

    Args:
        plugin: Plugin to check dependencies for.
        available_plugins: Dictionary of available plugins by ID.

    Returns:
        tuple[bool, str]: (dependencies_met, error_message).
            If dependencies are met, error_message is empty.
    """
    if not plugin.dependencies:
        return True, ""

    missing = []
    for dep_id in plugin.dependencies:
        if dep_id not in available_plugins:
            missing.append(dep_id)

    if missing:
        return False, f"Plugin '{plugin.name}' missing dependencies: {', '.join(missing)}"

    return True, ""


def resolve_dependencies(
    plugins: Sequence[Plugin],
) -> tuple[list[Plugin], list[str]]:
    """Resolve plugin dependencies and return plugins in load order.

    Uses topological sort to determine the correct loading order based on
    dependencies. Plugins with no dependencies are loaded first, followed
    by plugins whose dependencies have been loaded.

    Args:
        plugins: List of plugins to resolve dependencies for.

    Returns:
        tuple[list[Plugin], list[str]]: (sorted_plugins, errors).
            sorted_plugins contains plugins in load order.
            errors contains any dependency resolution errors.
    """
    plugin_map = {p.id: p for p in plugins}
    resolved = []
    unresolved = set(p.id for p in plugins)
    errors = []

    # Detect circular dependencies
    def has_circular_dependency(plugin_id: str, visited: set[str]) -> bool:
        if plugin_id in visited:
            return True
        visited.add(plugin_id)
        plugin = plugin_map.get(plugin_id)
        if plugin and plugin.dependencies:
            for dep_id in plugin.dependencies:
                if dep_id in plugin_map and has_circular_dependency(dep_id, visited):
                    return True
        visited.remove(plugin_id)
        return False

    # Check for circular dependencies
    for plugin_id in plugin_map:
        if has_circular_dependency(plugin_id, set()):
            errors.append(f"Circular dependency detected involving plugin '{plugin_id}'")
            return [], errors

    # Resolve dependencies using topological sort
    while unresolved:
        # Find plugins with no unresolved dependencies
        ready = []
        for plugin_id in unresolved:
            plugin = plugin_map[plugin_id]
            deps_resolved = all(
                dep_id not in unresolved for dep_id in plugin.dependencies
            )
            if deps_resolved:
                ready.append(plugin_id)

        if not ready:
            # No progress can be made - circular dependency or missing dependency
            remaining = [plugin_map[pid].name for pid in unresolved]
            errors.append(f"Cannot resolve dependencies for: {', '.join(remaining)}")
            break

        # Add ready plugins to resolved list
        for plugin_id in ready:
            resolved.append(plugin_map[plugin_id])
            unresolved.remove(plugin_id)

    return resolved, errors


def validate_plugin(
    plugin: Plugin,
    available_plugins: dict[str, Plugin],
    app_version: str = "0.0.1",
) -> tuple[bool, list[str]]:
    """Validate a plugin's compatibility and dependencies.

    Args:
        plugin: Plugin to validate.
        available_plugins: Dictionary of available plugins by ID.
        app_version: Current application version.

    Returns:
        tuple[bool, list[str]]: (is_valid, errors).
            is_valid is True if all checks pass.
            errors contains any validation error messages.
    """
    errors = []

    # Check version compatibility
    is_compatible, error = check_version_compatibility(plugin, app_version)
    if not is_compatible:
        errors.append(error)

    # Check dependencies
    deps_met, error = check_dependencies(plugin, available_plugins)
    if not deps_met:
        errors.append(error)

    return len(errors) == 0, errors
