"""Dynamic plugin loader for AIML Dash.

This module provides functionality to automatically discover and load plugins
from the plugins directory. It uses Python's importlib to dynamically import
plugin modules that follow the standard plugin structure.

The loader supports:
- Automatic discovery of plugin directories
- Dynamic import of plugin modules
- Validation of plugin structure
- Error handling for malformed plugins
"""

import importlib
import logging
from collections.abc import Sequence
from pathlib import Path

from aiml_dash.plugins.models import Plugin

logger = logging.getLogger(__name__)


def discover_plugin_directories(plugins_path: Path) -> list[Path]:
    """Discover plugin directories in the plugins folder.

    Parameters
    ----------
    plugins_path : Path
        Input value for ``plugins_path``.

    Returns
    -------
    value : list[Path]
        Result produced by this function."""
    if not plugins_path.exists() or not plugins_path.is_dir():
        logger.warning(f"Plugins directory not found: {plugins_path}")
        return []

    plugin_dirs = []
    for item in plugins_path.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            init_file = item / "__init__.py"
            if init_file.exists():
                plugin_dirs.append(item)
                logger.debug(f"Discovered plugin directory: {item.name}")

    return plugin_dirs


def load_plugin(
    plugin_dir: Path, plugins_package: str = "aiml_dash.plugins"
) -> Plugin | None:
    """Load a plugin from a directory.

    Parameters
    ----------
    plugin_dir : Path
        Input value for ``plugin_dir``.
    plugins_package : str
        Input value for ``plugins_package``.

    Returns
    -------
    value : Plugin | None
        Result produced by this function."""
    plugin_name = plugin_dir.name
    module_path = f"{plugins_package}.{plugin_name}"

    try:
        # Import the plugin module
        module = importlib.import_module(module_path)

        # Check if the module has a get_plugin function
        if not hasattr(module, "get_plugin"):
            logger.warning(
                f"Plugin '{plugin_name}' does not have a get_plugin() function"
            )
            return None

        # Call get_plugin to get the plugin definition
        plugin = module.get_plugin()

        # Validate plugin is of the correct type
        if not isinstance(plugin, Plugin):
            logger.warning(
                f"Plugin '{plugin_name}' get_plugin() did not return a Plugin instance"
            )
            return None

        logger.info(f"Successfully loaded plugin: {plugin.name} (id: {plugin.id})")
        return plugin

    except ImportError as e:
        logger.exception(f"Failed to import plugin '{plugin_name}': {e}")
        return None
    except Exception as e:
        logger.exception(f"Error loading plugin '{plugin_name}': {e}")
        return None


def load_plugins_dynamically(
    plugins_path: Path | None = None, plugins_package: str = "aiml_dash.plugins"
) -> Sequence[Plugin]:
    """Dynamically load all plugins from the plugins directory.

    Parameters
    ----------
    plugins_path : Path | None
        Input value for ``plugins_path``.
    plugins_package : str
        Input value for ``plugins_package``.

    Returns
    -------
    value : Sequence[Plugin]
        Result produced by this function."""
    if plugins_path is None:
        # Default to the plugins directory in the same package as this module
        current_file = Path(__file__).resolve()
        plugins_path = current_file.parent

    logger.info(f"Discovering plugins in: {plugins_path}")

    # Discover plugin directories
    plugin_dirs = discover_plugin_directories(plugins_path)

    if not plugin_dirs:
        logger.warning("No plugin directories found")
        return []

    # Load each plugin
    plugins = []
    for plugin_dir in plugin_dirs:
        plugin = load_plugin(plugin_dir, plugins_package)
        if plugin is not None:
            plugins.append(plugin)

    logger.info(f"Successfully loaded {len(plugins)} plugin(s)")
    return plugins


def validate_plugin_structure(plugin_dir: Path) -> tuple[bool, str]:
    """Validate that a plugin directory has the required structure.

    Parameters
    ----------
    plugin_dir : Path
        Input value for ``plugin_dir``.

    Returns
    -------
    value : tuple[bool, str]
        Result produced by this function."""
    required_files = [
        "__init__.py",
        "layout.py",
        "components.py",
        "callbacks.py",
        "styles.py",
        "constants.py",
    ]

    missing_files = []
    for filename in required_files:
        file_path = plugin_dir / filename
        if not file_path.exists():
            missing_files.append(filename)

    if missing_files:
        return False, f"Missing required files: {', '.join(missing_files)}"

    return True, ""
