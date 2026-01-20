"""Tests for the PluginManager class."""

from unittest.mock import MagicMock

import pytest

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.plugin_manager import PluginManager, get_default_manager


def test_plugin_manager_initialization_with_plugins():
    """Test PluginManager initialization with explicit plugins."""
    plugin = Plugin(
        id="test",
        name="Test Plugin",
        description="A test plugin",
        pages=[],
        version="1.0",
        default_enabled=True,
    )

    manager = PluginManager(plugins=[plugin])

    assert len(manager.get_plugins()) == 1
    assert manager.get_plugin_registry()["test"] == plugin


def test_plugin_manager_automatic_discovery():
    """Test automatic plugin discovery."""
    manager = PluginManager()

    # Should discover all available plugins
    plugins = manager.get_plugins()
    assert len(plugins) > 0

    # Should include core plugin
    registry = manager.get_plugin_registry()
    assert "core" in registry


def test_plugin_manager_register_plugin():
    """Test manual plugin registration."""
    manager = PluginManager(plugins=[])

    plugin = Plugin(
        id="manual",
        name="Manual Plugin",
        description="Manually registered",
        pages=[],
    )

    manager.register_plugin(plugin)

    assert "manual" in manager.get_plugin_registry()
    assert len(manager.get_plugins()) == 1


def test_plugin_manager_register_plugin_prevents_duplicates():
    """Test that registering the same plugin twice doesn't create duplicates."""
    plugin = Plugin(
        id="duplicate",
        name="Duplicate Plugin",
        description="Test duplicate",
        pages=[],
    )

    manager = PluginManager(plugins=[plugin])
    initial_count = len(manager.get_plugins())

    manager.register_plugin(plugin)

    # Should still have the same count
    assert len(manager.get_plugins()) == initial_count


def test_plugin_manager_get_plugins():
    """Test get_plugins returns correct sequence."""
    plugin1 = Plugin(id="first", name="First", description="First plugin", pages=[])
    plugin2 = Plugin(id="second", name="Second", description="Second plugin", pages=[])

    manager = PluginManager(plugins=[plugin1, plugin2])
    plugins = manager.get_plugins()

    assert len(plugins) == 2
    assert plugins[0].id == "first"
    assert plugins[1].id == "second"


def test_plugin_manager_get_plugin_registry():
    """Test get_plugin_registry returns correct dictionary."""
    plugin = Plugin(
        id="registry_test",
        name="Registry Test",
        description="Test registry",
        pages=[],
    )

    manager = PluginManager(plugins=[plugin])
    registry = manager.get_plugin_registry()

    assert isinstance(registry, dict)
    assert "registry_test" in registry
    assert registry["registry_test"] == plugin

    # Should return a copy, not the original
    registry["new_key"] = plugin
    assert "new_key" not in manager.get_plugin_registry()


def test_plugin_manager_get_plugin_metadata():
    """Test get_plugin_metadata returns correct metadata structure."""
    plugin = Plugin(
        id="meta_test",
        name="Metadata Test",
        description="Test metadata",
        pages=[],
        version="2.0",
        default_enabled=False,
        locked=True,
    )

    manager = PluginManager(plugins=[plugin])
    metadata = manager.get_plugin_metadata()

    assert len(metadata) == 1
    assert metadata[0]["id"] == "meta_test"
    assert metadata[0]["name"] == "Metadata Test"
    assert metadata[0]["description"] == "Test metadata"
    assert metadata[0]["version"] == "2.0"
    assert metadata[0]["default_enabled"] is False
    assert metadata[0]["locked"] is True


def test_plugin_manager_get_default_enabled_plugins():
    """Test get_default_enabled_plugins returns correct IDs."""
    plugin1 = Plugin(
        id="enabled",
        name="Enabled",
        description="Default enabled",
        pages=[],
        default_enabled=True,
    )
    plugin2 = Plugin(
        id="disabled",
        name="Disabled",
        description="Default disabled",
        pages=[],
        default_enabled=False,
    )
    plugin3 = Plugin(
        id="locked",
        name="Locked",
        description="Locked plugin",
        pages=[],
        default_enabled=False,
        locked=True,
    )

    manager = PluginManager(plugins=[plugin1, plugin2, plugin3])
    defaults = manager.get_default_enabled_plugins()

    assert "enabled" in defaults
    assert "locked" in defaults
    assert "disabled" not in defaults


def test_plugin_manager_normalize_enabled_plugins_with_none():
    """Test normalize_enabled_plugins with None returns defaults."""
    plugin = Plugin(
        id="default",
        name="Default",
        description="Default plugin",
        pages=[],
        default_enabled=True,
    )

    manager = PluginManager(plugins=[plugin])
    normalized = manager.normalize_enabled_plugins(None)

    assert "default" in normalized


def test_plugin_manager_normalize_enabled_plugins_adds_locked():
    """Test normalize_enabled_plugins includes locked plugins."""
    plugin1 = Plugin(
        id="normal",
        name="Normal",
        description="Normal plugin",
        pages=[],
        locked=False,
    )
    plugin2 = Plugin(
        id="locked",
        name="Locked",
        description="Locked plugin",
        pages=[],
        locked=True,
    )

    manager = PluginManager(plugins=[plugin1, plugin2])
    normalized = manager.normalize_enabled_plugins(["normal"])

    assert "normal" in normalized
    assert "locked" in normalized


def test_plugin_manager_normalize_enabled_plugins_filters_invalid():
    """Test normalize_enabled_plugins filters invalid plugin IDs."""
    plugin = Plugin(
        id="valid",
        name="Valid",
        description="Valid plugin",
        pages=[],
    )

    manager = PluginManager(plugins=[plugin])
    normalized = manager.normalize_enabled_plugins(["valid", "invalid", "nonexistent"])

    assert "valid" in normalized
    assert "invalid" not in normalized
    assert "nonexistent" not in normalized


def test_plugin_manager_register_callbacks():
    """Test register_callbacks calls plugin callback functions."""
    mock_app = MagicMock()
    callback_called = []

    def test_callback(app):
        callback_called.append(True)

    plugin = Plugin(
        id="callback_test",
        name="Callback Test",
        description="Test callbacks",
        pages=[],
        register_callbacks=test_callback,
    )

    manager = PluginManager(plugins=[plugin])
    manager.register_callbacks(mock_app)

    assert len(callback_called) == 1


def test_plugin_manager_register_callbacks_with_none():
    """Test register_callbacks handles plugins without callbacks."""
    mock_app = MagicMock()
    plugin = Plugin(
        id="no_callback",
        name="No Callback",
        description="No callbacks",
        pages=[],
        register_callbacks=None,
    )

    manager = PluginManager(plugins=[plugin])
    # Should not raise an error
    manager.register_callbacks(mock_app)


def test_get_default_manager_singleton():
    """Test get_default_manager returns singleton instance."""
    manager1 = get_default_manager()
    manager2 = get_default_manager()

    assert manager1 is manager2


def test_plugin_manager_discover_plugins_handles_errors():
    """Test that discover_plugins gracefully handles plugin loading errors."""
    # This test verifies that the manager can handle plugins that fail to load
    # The actual discovery should not crash even if some plugins have issues
    manager = PluginManager()

    # Should have discovered some plugins despite any potential errors
    assert len(manager.get_plugins()) >= 1
