"""
Plugin manager for automatic discovery, registration, and initialization of plugins.

This module provides a centralized PluginManager class to handle all backend plugin
operations, separating concerns from UI-related functionality.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable, Sequence

from aiml_dash.plugins.models import Plugin


class PluginManager:
    """
    Centralized manager for plugin discovery, registration, and initialization.

    The PluginManager handles:
    - Automatic discovery of plugins from the plugins directory
    - Plugin registration and initialization
    - Management of plugin configurations and defaults
    - Separation of backend logic from UI concerns

    Attributes:
        _plugins: Ordered list of registered plugins
        _plugin_registry: Dictionary mapping plugin IDs to Plugin instances
    """

    def __init__(self, plugins: Sequence[Plugin] | None = None) -> None:
        """
        Initialize the PluginManager.

        Args:
            plugins: Optional list of plugins to register. If None, uses auto-discovery.
        """
        self._plugins: list[Plugin] = []
        self._plugin_registry: dict[str, Plugin] = {}

        if plugins is not None:
            for plugin in plugins:
                self.register_plugin(plugin)
        else:
            self.discover_plugins()

    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a plugin with the manager.

        Args:
            plugin: Plugin instance to register
        """
        if plugin.id not in self._plugin_registry:
            self._plugins.append(plugin)
            self._plugin_registry[plugin.id] = plugin

    def discover_plugins(self) -> None:
        """
        Automatically discover and register plugins from the plugins package.

        Searches for modules in the plugins package that have a get_plugin() function
        and automatically registers them.
        """
        import aiml_dash.plugins as plugins_package

        # Get the path to the plugins package
        plugins_path = plugins_package.__path__

        # Iterate through all modules in the plugins package
        for _importer, modname, ispkg in pkgutil.iter_modules(plugins_path):
            # Skip special modules
            if modname.startswith("_") or modname in ("models", "registry", "plugin_manager"):
                continue

            # Only process packages (directories with __init__.py)
            if ispkg:
                try:
                    # Import the plugin module
                    module = importlib.import_module(f"aiml_dash.plugins.{modname}")

                    # Check if the module has a get_plugin function
                    if hasattr(module, "get_plugin"):
                        plugin = module.get_plugin()
                        self.register_plugin(plugin)
                except Exception:  # noqa: S112
                    # Silently skip plugins that fail to load
                    # This allows the system to continue working even if one plugin is broken
                    # Logging would introduce a dependency and noise during normal operations
                    continue

    def get_plugins(self) -> Sequence[Plugin]:
        """
        Return the ordered list of registered plugins.

        Returns:
            Sequence of Plugin instances in registration order
        """
        return self._plugins

    def get_plugin_registry(self) -> dict[str, Plugin]:
        """
        Return plugins keyed by their identifier.

        Returns:
            Dictionary mapping plugin IDs to Plugin instances
        """
        return self._plugin_registry.copy()

    def get_plugin_metadata(self) -> list[dict[str, object]]:
        """
        Return plugin metadata for UI rendering.

        Returns:
            List of dictionaries containing plugin metadata
        """
        metadata = []
        for plugin in self._plugins:
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

    def get_default_enabled_plugins(self) -> list[str]:
        """
        Return the list of plugins enabled by default, including locked plugins.

        Returns:
            List of plugin IDs that are enabled by default
        """
        return [plugin.id for plugin in self._plugins if plugin.default_enabled or plugin.locked]

    def normalize_enabled_plugins(self, enabled_plugins: Iterable[str] | None) -> list[str]:
        """
        Normalize enabled plugins to include locked entries and filter invalid IDs.

        Args:
            enabled_plugins: Optional iterable of plugin IDs to enable

        Returns:
            List of valid, normalized plugin IDs including locked plugins
        """
        enabled = list(enabled_plugins or self.get_default_enabled_plugins())
        for plugin in self._plugin_registry.values():
            if plugin.locked and plugin.id not in enabled:
                enabled.append(plugin.id)
        return [plugin_id for plugin_id in enabled if plugin_id in self._plugin_registry]

    def register_callbacks(self, app: object) -> None:
        """
        Register callbacks defined by all plugins.

        Args:
            app: Dash application instance
        """
        for plugin in self._plugins:
            if plugin.register_callbacks:
                plugin.register_callbacks(app)


# Global singleton instance for backward compatibility
_default_manager: PluginManager | None = None


def get_default_manager() -> PluginManager:
    """
    Get or create the default global PluginManager instance.

    Returns:
        The global PluginManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = PluginManager()
    return _default_manager
