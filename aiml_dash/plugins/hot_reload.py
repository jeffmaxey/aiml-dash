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
from collections.abc import Callable
from pathlib import Path
from typing import Any

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

        Parameters
        ----------
        plugins_path : Path
            Root directory containing plugin packages to watch.
        reload_callback : Callable[[str], None]
            Callback invoked with the changed plugin identifier.
        """
        self.plugins_path = plugins_path
        self.reload_callback = reload_callback
        self.last_reload_time: dict[str, float] = {}
        self.debounce_seconds = 1.0

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Parameters
        ----------
        event : FileSystemEvent
            File system event emitted by watchdog.
        """
        if event.is_directory:
            return

        file_path = Path(str(event.src_path))

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
        logger.info("Plugin file modified: %s", file_path)
        logger.info("Reloading plugin: %s", plugin_dir)

        try:
            self.reload_callback(plugin_dir)
        except (RuntimeError, ImportError, AttributeError, ValueError) as exc:
            logger.exception("Error reloading plugin '%s': %s", plugin_dir, exc)


class PluginHotReloader:
    """Hot-reloader for plugins during development."""

    def __init__(
        self,
        plugins_path: Path,
        reload_callback: Callable[[str], None],
    ):
        """Initialize the hot-reloader.

        Parameters
        ----------
        plugins_path : Path
            Root directory containing plugin packages to watch.
        reload_callback : Callable[[str], None]
            Callback invoked with the changed plugin identifier.
        """
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError("watchdog package required for hot-reloading")

        self.plugins_path = plugins_path
        self.reload_callback = reload_callback
        self.observer = Observer()
        self.event_handler = PluginReloadHandler(plugins_path, reload_callback)

    def start(self) -> None:
        """Start watching for plugin changes."""
        logger.info("Starting plugin hot-reloader for: %s", self.plugins_path)
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

    def __enter__(self) -> PluginHotReloader:
        """Context manager entry."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit.

        Parameters
        ----------
        exc_type : Any
            Exception type, if an error occurred.
        exc_val : Any
            Exception instance, if an error occurred.
        exc_tb : Any
            Exception traceback object, if an error occurred.
        """
        self.stop()


def reload_plugin_module(
    plugin_id: str,
    plugins_package: str = "aiml_dash.plugins",
) -> bool:
    """Reload a plugin module and its loaded submodules.

    Parameters
    ----------
    plugin_id : str
        Identifier of the plugin package to reload.
    plugins_package : str
        Dotted package prefix containing plugins.

    Returns
    -------
    value : bool
        ``True`` when reload succeeds, else ``False``.
    """
    module_path = f"{plugins_package}.{plugin_id}"

    try:
        base_submodules = [
            "layout",
            "components",
            "callbacks",
            "styles",
            "constants",
        ]
        modules_to_reload = {module_path}
        modules_to_reload.update(f"{module_path}.{sub}" for sub in base_submodules)

        # Also reload any already imported nested submodules,
        # for example pages.*.
        module_prefix = f"{module_path}."
        modules_to_reload.update(
            loaded_name
            for loaded_name in sys.modules
            if loaded_name.startswith(module_prefix)
        )

        # Deterministic order: deepest modules first, then lexical.
        ordered_modules = sorted(
            modules_to_reload,
            key=lambda name: (-name.count("."), name),
        )
        for mod_path in ordered_modules:
            if mod_path in sys.modules:
                logger.debug("Reloading module: %s", mod_path)
                importlib.reload(sys.modules[mod_path])

        logger.info(
            "Successfully reloaded plugin '%s' (%d modules)",
            plugin_id,
            len(ordered_modules),
        )
        return True

    except (
        ImportError,
        AttributeError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
    ) as exc:
        logger.exception("Failed to reload plugin '%s': %s", plugin_id, exc)
        return False


def create_hot_reloader(
    plugins_path: Path,
    on_reload: Callable[[str], None] | None = None,
) -> PluginHotReloader | None:
    """Create a hot-reloader for plugins.

    Parameters
    ----------
    plugins_path : Path
        Root directory containing plugin packages to watch.
    on_reload : Callable[[str], None] | None
        Optional callback invoked after a successful reload.

    Returns
    -------
    value : PluginHotReloader | None
        Active hot-reloader instance, or ``None`` when watchdog is unavailable.
    """
    if not WATCHDOG_AVAILABLE:
        logger.warning("Hot-reloading not available (watchdog not installed)")
        return None

    def reload_callback(plugin_id: str) -> None:
        """Callback for reloading a plugin.

        Parameters
        ----------
        plugin_id : str
            Plugin identifier that changed on disk.
        """
        success = reload_plugin_module(plugin_id)
        if success and on_reload:
            on_reload(plugin_id)

    return PluginHotReloader(plugins_path, reload_callback)
