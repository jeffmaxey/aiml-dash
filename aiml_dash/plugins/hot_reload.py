"""Hot-reloading support for AIML Dash plugins.

This module provides functionality to watch plugin directories for changes
and automatically reload plugins during development without restarting the
application.
"""

from __future__ import annotations

import importlib
import logging
import sys
import time
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog not available - hot-reloading disabled")


class PluginReloadHandler(FileSystemEventHandler):
    """File system event handler for plugin hot-reloading."""

    def __init__(
        self,
        plugins_path: Path,
        reload_callback: Callable[[str], None],
    ):
        """Initialize the reload handler.

        Args:
            plugins_path: Path to the plugins directory.
            reload_callback: Function to call when a plugin needs reloading.
                Receives the plugin directory name as argument.
        """
        self.plugins_path = plugins_path
        self.reload_callback = reload_callback
        self.last_reload_time = {}
        self.debounce_seconds = 1.0

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Args:
            event: File system event.
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process Python files
        if file_path.suffix != ".py":
            return

        # Get plugin directory
        try:
            plugin_dir = file_path.relative_to(self.plugins_path).parts[0]
        except (ValueError, IndexError):
            return

        # Debounce rapid consecutive changes
        current_time = time.time()
        last_reload = self.last_reload_time.get(plugin_dir, 0)
        if current_time - last_reload < self.debounce_seconds:
            return

        self.last_reload_time[plugin_dir] = current_time
        logger.info(f"Plugin file modified: {file_path}")
        logger.info(f"Reloading plugin: {plugin_dir}")

        try:
            self.reload_callback(plugin_dir)
        except Exception as e:
            logger.error(f"Error reloading plugin '{plugin_dir}': {e}")


class PluginHotReloader:
    """Hot-reloader for plugins during development."""

    def __init__(self, plugins_path: Path, reload_callback: Callable[[str], None]):
        """Initialize the hot-reloader.

        Args:
            plugins_path: Path to the plugins directory.
            reload_callback: Function to call when a plugin needs reloading.
        """
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError("watchdog package required for hot-reloading")

        self.plugins_path = plugins_path
        self.reload_callback = reload_callback
        self.observer = Observer()
        self.event_handler = PluginReloadHandler(plugins_path, reload_callback)

    def start(self) -> None:
        """Start watching for plugin changes."""
        logger.info(f"Starting plugin hot-reloader for: {self.plugins_path}")
        self.observer.schedule(
            self.event_handler,
            str(self.plugins_path),
            recursive=True,
        )
        self.observer.start()
        logger.info("Plugin hot-reloader started")

    def stop(self) -> None:
        """Stop watching for plugin changes."""
        logger.info("Stopping plugin hot-reloader")
        self.observer.stop()
        self.observer.join()
        logger.info("Plugin hot-reloader stopped")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def reload_plugin_module(plugin_id: str, plugins_package: str = "aiml_dash.plugins") -> bool:
    """Reload a plugin module and its submodules.

    Args:
        plugin_id: ID of the plugin to reload.
        plugins_package: Python package path for plugins.

    Returns:
        bool: True if reload was successful, False otherwise.
    """
    module_path = f"{plugins_package}.{plugin_id}"

    try:
        # Get all submodules to reload
        submodules = ["layout", "components", "callbacks", "styles", "constants"]
        modules_to_reload = [module_path]
        modules_to_reload.extend([f"{module_path}.{sub}" for sub in submodules])

        # Reload in reverse order (submodules first, then main module)
        for mod_path in reversed(modules_to_reload):
            if mod_path in sys.modules:
                logger.debug(f"Reloading module: {mod_path}")
                importlib.reload(sys.modules[mod_path])

        logger.info(f"Successfully reloaded plugin: {plugin_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to reload plugin '{plugin_id}': {e}")
        return False


def create_hot_reloader(
    plugins_path: Path,
    on_reload: Callable[[str], None] | None = None,
) -> PluginHotReloader | None:
    """Create a hot-reloader for plugins.

    Args:
        plugins_path: Path to the plugins directory.
        on_reload: Optional callback to execute after reloading a plugin.

    Returns:
        PluginHotReloader | None: Hot-reloader instance, or None if watchdog
            is not available.
    """
    if not WATCHDOG_AVAILABLE:
        logger.warning("Hot-reloading not available (watchdog not installed)")
        return None

    def reload_callback(plugin_id: str) -> None:
        """Callback for reloading a plugin."""
        success = reload_plugin_module(plugin_id)
        if success and on_reload:
            on_reload(plugin_id)

    return PluginHotReloader(plugins_path, reload_callback)
