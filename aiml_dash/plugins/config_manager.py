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

logger = logging.getLogger(__name__)


class PluginConfig:
    """Plugin configuration manager."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the plugin config manager.

        Args:
            config_dir: Directory to store plugin configuration files.
                If None, uses a default location.
        """
        if config_dir is None:
            config_dir = Path.home() / ".aiml_dash" / "plugins"

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._configs: dict[str, dict[str, Any]] = {}

    def _get_config_file(self, plugin_id: str) -> Path:
        """Get the configuration file path for a plugin.

        Args:
            plugin_id: Plugin identifier.

        Returns:
            Path: Path to the plugin's config file.
        """
        return self.config_dir / f"{plugin_id}.json"

    def load_config(self, plugin_id: str) -> dict[str, Any]:
        """Load configuration for a plugin.

        Args:
            plugin_id: Plugin identifier.

        Returns:
            dict[str, Any]: Plugin configuration dictionary.
        """
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
                logger.error(f"Error loading config for plugin '{plugin_id}': {e}")

        # Return empty config if file doesn't exist or error occurred
        empty_config: dict[str, Any] = {}
        self._configs[plugin_id] = empty_config
        return empty_config

    def save_config(self, plugin_id: str, config: dict[str, Any]) -> bool:
        """Save configuration for a plugin.

        Args:
            plugin_id: Plugin identifier.
            config: Configuration dictionary to save.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        config_file = self._get_config_file(plugin_id)

        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            self._configs[plugin_id] = config
            logger.info(f"Saved config for plugin '{plugin_id}'")
            return True
        except Exception as e:
            logger.error(f"Error saving config for plugin '{plugin_id}': {e}")
            return False

    def update_config(self, plugin_id: str, updates: dict[str, Any]) -> bool:
        """Update configuration for a plugin.

        Args:
            plugin_id: Plugin identifier.
            updates: Dictionary of configuration updates.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        config = self.load_config(plugin_id)
        config.update(updates)
        return self.save_config(plugin_id, config)

    def get_setting(self, plugin_id: str, key: str, default: Any = None) -> Any:
        """Get a specific setting for a plugin.

        Args:
            plugin_id: Plugin identifier.
            key: Configuration key.
            default: Default value if key doesn't exist.

        Returns:
            Any: Configuration value.
        """
        config = self.load_config(plugin_id)
        return config.get(key, default)

    def set_setting(self, plugin_id: str, key: str, value: Any) -> bool:
        """Set a specific setting for a plugin.

        Args:
            plugin_id: Plugin identifier.
            key: Configuration key.
            value: Configuration value.

        Returns:
            bool: True if setting was successful, False otherwise.
        """
        return self.update_config(plugin_id, {key: value})

    def validate_config(self, plugin: Plugin, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate plugin configuration against schema.

        Args:
            plugin: Plugin to validate configuration for.
            config: Configuration to validate.

        Returns:
            tuple[bool, list[str]]: (is_valid, errors).
        """
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

        Args:
            plugin_id: Plugin identifier.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        config_file = self._get_config_file(plugin_id)

        try:
            if config_file.exists():
                config_file.unlink()
            if plugin_id in self._configs:
                del self._configs[plugin_id]
            logger.info(f"Deleted config for plugin '{plugin_id}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting config for plugin '{plugin_id}': {e}")
            return False
