"""Tests for plugin configuration management."""

import tempfile
from pathlib import Path

import pytest

from aiml_dash.plugins.config_manager import PluginConfig
from aiml_dash.plugins.models import Plugin


class TestPluginConfig:
    """Tests for plugin configuration manager."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create a config manager with temp directory."""
        return PluginConfig(temp_config_dir)

    def test_save_and_load_config(self, config_manager):
        """Test saving and loading plugin configuration."""
        config = {"setting1": "value1", "setting2": 42}
        
        success = config_manager.save_config("test_plugin", config)
        assert success is True

        loaded = config_manager.load_config("test_plugin")
        assert loaded == config

    def test_update_config(self, config_manager):
        """Test updating plugin configuration."""
        initial = {"setting1": "value1"}
        config_manager.save_config("test_plugin", initial)

        updates = {"setting2": "value2"}
        success = config_manager.update_config("test_plugin", updates)
        assert success is True

        loaded = config_manager.load_config("test_plugin")
        assert loaded["setting1"] == "value1"
        assert loaded["setting2"] == "value2"

    def test_get_setting(self, config_manager):
        """Test getting a specific setting."""
        config = {"key1": "value1"}
        config_manager.save_config("test_plugin", config)

        value = config_manager.get_setting("test_plugin", "key1")
        assert value == "value1"

        # Test default value
        default = config_manager.get_setting("test_plugin", "nonexistent", "default")
        assert default == "default"

    def test_set_setting(self, config_manager):
        """Test setting a specific value."""
        success = config_manager.set_setting("test_plugin", "key1", "value1")
        assert success is True

        value = config_manager.get_setting("test_plugin", "key1")
        assert value == "value1"

    def test_validate_config_with_schema(self, config_manager):
        """Test validating configuration with schema."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            config_schema={
                "required": ["required_field"],
                "properties": {
                    "required_field": {"type": "string"},
                    "optional_field": {"type": "integer"},
                },
            },
        )

        # Valid config
        valid_config = {"required_field": "value", "optional_field": 42}
        is_valid, errors = config_manager.validate_config(plugin, valid_config)
        assert is_valid is True
        assert len(errors) == 0

        # Missing required field
        invalid_config = {"optional_field": 42}
        is_valid, errors = config_manager.validate_config(plugin, invalid_config)
        assert is_valid is False
        assert len(errors) > 0

    def test_delete_config(self, config_manager):
        """Test deleting plugin configuration."""
        config = {"key": "value"}
        config_manager.save_config("test_plugin", config)

        success = config_manager.delete_config("test_plugin")
        assert success is True

        # Config should be empty after deletion
        loaded = config_manager.load_config("test_plugin")
        assert loaded == {}


class TestPluginConfigIntegration:
    """Integration tests for plugin configuration."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_persistence_across_instances(self, temp_config_dir):
        """Test that config persists across manager instances."""
        # Save config with first instance
        manager1 = PluginConfig(temp_config_dir)
        config = {"key": "value"}
        manager1.save_config("test_plugin", config)

        # Load config with second instance
        manager2 = PluginConfig(temp_config_dir)
        loaded = manager2.load_config("test_plugin")
        assert loaded == config
