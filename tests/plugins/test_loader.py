"""Tests for the dynamic plugin loader.

This module contains tests for plugin discovery, loading, and validation.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from aiml_dash.plugins.loader import (
    discover_plugin_directories,
    load_plugin,
    load_plugins_dynamically,
    validate_plugin_structure,
)
from aiml_dash.plugins.models import Plugin


class TestDiscoverPluginDirectories:
    """Tests for plugin directory discovery."""

    def test_discovers_valid_plugin_directories(self, tmp_path):
        """Test that valid plugin directories are discovered."""
        # Create valid plugin directories
        plugin1 = tmp_path / "plugin1"
        plugin1.mkdir()
        (plugin1 / "__init__.py").touch()

        plugin2 = tmp_path / "plugin2"
        plugin2.mkdir()
        (plugin2 / "__init__.py").touch()

        # Create an invalid directory (no __init__.py)
        invalid = tmp_path / "invalid"
        invalid.mkdir()

        # Create a hidden directory (starts with _)
        hidden = tmp_path / "_hidden"
        hidden.mkdir()
        (hidden / "__init__.py").touch()

        # Discover plugins
        discovered = discover_plugin_directories(tmp_path)

        assert len(discovered) == 2
        assert plugin1 in discovered
        assert plugin2 in discovered
        assert invalid not in discovered
        assert hidden not in discovered

    def test_handles_nonexistent_directory(self):
        """Test handling of non-existent plugins directory."""
        nonexistent = Path("/nonexistent/path")
        discovered = discover_plugin_directories(nonexistent)
        assert discovered == []

    def test_handles_file_instead_of_directory(self, tmp_path):
        """Test handling when a file is passed instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        discovered = discover_plugin_directories(test_file)
        assert discovered == []


class TestValidatePluginStructure:
    """Tests for plugin structure validation."""

    def test_validates_complete_plugin_structure(self, tmp_path):
        """Test that a complete plugin structure passes validation."""
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        # Create all required files
        required_files = ["__init__.py", "layout.py", "components.py", "callbacks.py", "styles.py", "constants.py"]
        for filename in required_files:
            (plugin_dir / filename).touch()

        is_valid, error_msg = validate_plugin_structure(plugin_dir)
        assert is_valid is True
        assert error_msg == ""

    def test_detects_missing_files(self, tmp_path):
        """Test that missing files are detected."""
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        # Create only some files
        (plugin_dir / "__init__.py").touch()
        (plugin_dir / "layout.py").touch()

        is_valid, error_msg = validate_plugin_structure(plugin_dir)
        assert is_valid is False
        assert "Missing required files" in error_msg
        assert "components.py" in error_msg
        assert "callbacks.py" in error_msg
        assert "styles.py" in error_msg
        assert "constants.py" in error_msg


class TestLoadPlugin:
    """Tests for loading individual plugins."""

    def test_loads_valid_plugin(self):
        """Test loading a valid plugin module."""
        # Use the example_plugin as a known valid plugin
        plugin_path = Path(__file__).parent.parent.parent / "aiml_dash" / "plugins" / "example_plugin"

        plugin = load_plugin(plugin_path, "aiml_dash.plugins")

        assert plugin is not None
        assert isinstance(plugin, Plugin)
        assert plugin.id == "example"
        assert plugin.name == "Example Plugin"

    def test_handles_missing_get_plugin(self, tmp_path):
        """Test handling of plugin without get_plugin function."""
        plugin_dir = tmp_path / "bad_plugin"
        plugin_dir.mkdir()

        # Create __init__.py without get_plugin function
        (plugin_dir / "__init__.py").write_text("# No get_plugin function\n")

        plugin = load_plugin(plugin_dir, "test.plugins")

        # Should return None because module cannot be imported
        assert plugin is None

    def test_handles_import_error(self, tmp_path):
        """Test handling of import errors."""
        plugin_dir = tmp_path / "error_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "__init__.py").touch()

        plugin = load_plugin(plugin_dir, "nonexistent.package")

        assert plugin is None


class TestLoadPluginsDynamically:
    """Tests for dynamic plugin loading."""

    def test_loads_multiple_plugins(self):
        """Test loading multiple plugins dynamically."""
        # Load from the actual plugins directory
        plugins_path = Path(__file__).parent.parent.parent / "aiml_dash" / "plugins"

        plugins = load_plugins_dynamically(plugins_path, "aiml_dash.plugins")

        # Should find at least the example_plugin and template_plugin
        # Note: Only counts plugins with valid structure, not all directories
        assert len(plugins) >= 2, f"Expected at least 2 plugins, found {len(plugins)}"

        plugin_ids = {p.id for p in plugins}
        assert "core" in plugin_ids
        assert "example" in plugin_ids
        assert "template" in plugin_ids

    def test_handles_empty_directory(self, tmp_path):
        """Test handling of empty plugins directory."""
        empty_dir = tmp_path / "empty_plugins"
        empty_dir.mkdir()

        plugins = load_plugins_dynamically(empty_dir)

        assert plugins == []

    def test_skips_invalid_plugins(self, tmp_path):
        """Test that invalid plugins are skipped without crashing."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create one valid plugin
        valid_plugin = plugins_dir / "valid"
        valid_plugin.mkdir()
        (valid_plugin / "__init__.py").write_text(
            """
from aiml_dash.plugins.models import Plugin, PluginPage

def get_plugin():
    return Plugin(
        id='valid',
        name='Valid Plugin',
        description='A valid plugin',
        pages=[]
    )
"""
        )

        # Create one invalid plugin (no __init__.py)
        invalid_plugin = plugins_dir / "invalid"
        invalid_plugin.mkdir()

        # Mock the import to make valid plugin work
        with patch("importlib.import_module") as mock_import:
            from aiml_dash.plugins.models import Plugin

            mock_module = Mock()
            mock_module.get_plugin = lambda: Plugin(
                id="valid", name="Valid Plugin", description="A valid plugin", pages=[]
            )
            mock_import.return_value = mock_module

            plugins = load_plugins_dynamically(plugins_dir, "test.plugins")

            # Should load only the valid plugin
            assert len(plugins) == 1
            assert plugins[0].id == "valid"
