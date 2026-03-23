"""Plugin configuration and settings management for AIML Dash.

This module handles plugin-specific configuration, including loading,
validating, and persisting plugin settings.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from aiml_dash.plugins.models import Plugin
from aiml_dash.utils.config import get_settings

logger = logging.getLogger(__name__)


class PluginConfig:
    """Plugin configuration manager."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the plugin config manager.

        Parameters
        ----------
        config_dir : Path | None
            Value provided for this parameter."""
        if config_dir is None:
            config_dir = get_settings().plugin_config_dir

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._configs: dict[str, dict[str, Any]] = {}

    def _get_config_file(self, plugin_id: str) -> Path:
        """Get the configuration file path for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.

        Returns
        -------
        value : Path
            Result produced by this function."""
        return self.config_dir / f"{plugin_id}.json"

    def load_config(self, plugin_id: str) -> dict[str, Any]:
        """Load configuration for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.

        Returns
        -------
        value : dict[str, Any]
            Result produced by this function."""
        if plugin_id in self._configs:
            return self._configs[plugin_id]

        config_file = self._get_config_file(plugin_id)

        if config_file.exists():
            try:
                with open(config_file) as f:
                    config: dict[str, Any] = json.load(f)
                logger.info(f"Loaded config for plugin '{plugin_id}'")
                self._configs[plugin_id] = config
                return config
            except Exception as e:
                logger.exception(f"Error loading config for plugin '{plugin_id}': {e}")

        # Return empty config if file doesn't exist or error occurred
        empty_config: dict[str, Any] = {}
        self._configs[plugin_id] = empty_config
        return empty_config

    def save_config(self, plugin_id: str, config: dict[str, Any]) -> bool:
        """Save configuration for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.
        config : dict[str, Any]
            Input value for ``config``.

        Returns
        -------
        value : bool
            Result produced by this function."""
        config_file = self._get_config_file(plugin_id)

        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            self._configs[plugin_id] = config
            logger.info(f"Saved config for plugin '{plugin_id}'")
            return True
        except Exception as e:
            logger.exception(f"Error saving config for plugin '{plugin_id}': {e}")
            return False

    def update_config(self, plugin_id: str, updates: dict[str, Any]) -> bool:
        """Update configuration for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.
        updates : dict[str, Any]
            Input value for ``updates``.

        Returns
        -------
        value : bool
            Result produced by this function."""
        config = self.load_config(plugin_id)
        config.update(updates)
        return self.save_config(plugin_id, config)

    def get_setting(self, plugin_id: str, key: str, default: Any = None) -> Any:
        """Get a specific setting for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.
        key : str
            Input value for ``key``.
        default : Any
            Input value for ``default``.

        Returns
        -------
        value : Any
            Result produced by this function."""
        config = self.load_config(plugin_id)
        return config.get(key, default)

    def set_setting(self, plugin_id: str, key: str, value: Any) -> bool:
        """Set a specific setting for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.
        key : str
            Input value for ``key``.
        value : Any
            Input value for ``value``.

        Returns
        -------
        value : bool
            Result produced by this function."""
        return self.update_config(plugin_id, {key: value})

    def validate_config(
        self, plugin: Plugin, config: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate plugin configuration against schema.

        Parameters
        ----------
        plugin : Plugin
            Input value for ``plugin``.
        config : dict[str, Any]
            Input value for ``config``.

        Returns
        -------
        value : tuple[bool, list[str]]
            Result produced by this function."""
        if not plugin.config_schema:
            return True, []

        errors = []

        # Check required fields
        required = plugin.config_schema.get("required", [])
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate field types
        properties = plugin.config_schema.get("properties", {})
        for field, value in config.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type:
                    actual_type = type(value).__name__
                    # Map Python types to JSON schema types
                    type_map = {
                        "str": "string",
                        "int": "integer",
                        "float": "number",
                        "bool": "boolean",
                        "list": "array",
                        "dict": "object",
                    }
                    json_type = type_map.get(actual_type, actual_type)
                    if json_type != expected_type:
                        errors.append(
                            f"Field '{field}' has type {actual_type}, expected {expected_type}"
                        )

        return len(errors) == 0, errors

    def delete_config(self, plugin_id: str) -> bool:
        """Delete configuration for a plugin.

        Parameters
        ----------
        plugin_id : str
            Input value for ``plugin_id``.

        Returns
        -------
        value : bool
            Result produced by this function."""
        config_file = self._get_config_file(plugin_id)

        try:
            if config_file.exists():
                config_file.unlink()
            if plugin_id in self._configs:
                del self._configs[plugin_id]
            logger.info(f"Deleted config for plugin '{plugin_id}'")
            return True
        except Exception as e:
            logger.exception(f"Error deleting config for plugin '{plugin_id}': {e}")
            return False
