"""Tests for aiml_dash.plugins.marketplace module.

Covers PluginMarketplace construction, search_plugins, get_plugin_info,
install_plugin, update_plugin, uninstall_plugin, list_installed_plugins,
check_updates, and the create_marketplace_client factory.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aiml_dash.plugins.marketplace import PluginMarketplace, create_marketplace_client


# ---------------------------------------------------------------------------
# PluginMarketplace construction
# ---------------------------------------------------------------------------


class TestPluginMarketplaceInit:
    """Tests for PluginMarketplace.__init__."""

    def test_default_marketplace_url(self):
        """Default marketplace URL should be the canonical one."""
        mp = PluginMarketplace()
        assert mp.marketplace_url == "https://plugins.aiml-dash.org"

    def test_custom_marketplace_url(self):
        """A custom URL should override the default."""
        mp = PluginMarketplace("https://example.com/plugins")
        assert mp.marketplace_url == "https://example.com/plugins"

    def test_cache_empty_on_creation(self):
        """The internal cache should be empty after construction."""
        mp = PluginMarketplace()
        assert mp._cache == {}


# ---------------------------------------------------------------------------
# search_plugins
# ---------------------------------------------------------------------------


class TestSearchPlugins:
    """Tests for PluginMarketplace.search_plugins."""

    def test_returns_list(self):
        """search_plugins() should return a list."""
        mp = PluginMarketplace()
        result = mp.search_plugins()
        assert isinstance(result, list)

    def test_empty_list_placeholder(self):
        """The placeholder implementation should return an empty list."""
        mp = PluginMarketplace()
        assert mp.search_plugins() == []

    def test_with_query_still_returns_list(self):
        """search_plugins() should accept a query string and return a list."""
        mp = PluginMarketplace()
        result = mp.search_plugins("machine learning")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_plugin_info
# ---------------------------------------------------------------------------


class TestGetPluginInfo:
    """Tests for PluginMarketplace.get_plugin_info."""

    def test_returns_none_placeholder(self):
        """Placeholder implementation should return None."""
        mp = PluginMarketplace()
        result = mp.get_plugin_info("some-plugin")
        assert result is None

    def test_accepts_any_plugin_id(self):
        """get_plugin_info() should accept any string without raising."""
        mp = PluginMarketplace()
        mp.get_plugin_info("")
        mp.get_plugin_info("a-b-c-123")


# ---------------------------------------------------------------------------
# install_plugin
# ---------------------------------------------------------------------------


class TestInstallPlugin:
    """Tests for PluginMarketplace.install_plugin."""

    def test_returns_tuple(self, tmp_path):
        """install_plugin() should return a (bool, str) tuple."""
        mp = PluginMarketplace()
        result = mp.install_plugin("my-plugin", tmp_path)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_false_not_implemented(self, tmp_path):
        """Placeholder should report failure."""
        mp = PluginMarketplace()
        success, _ = mp.install_plugin("my-plugin", tmp_path)
        assert success is False

    def test_message_is_string(self, tmp_path):
        """The second element of the tuple should be a string."""
        mp = PluginMarketplace()
        _, msg = mp.install_plugin("x", tmp_path)
        assert isinstance(msg, str)

    def test_version_parameter_accepted(self, tmp_path):
        """install_plugin() should accept an optional version without raising."""
        mp = PluginMarketplace()
        success, _ = mp.install_plugin("x", tmp_path, version="1.2.3")
        assert success is False


# ---------------------------------------------------------------------------
# update_plugin
# ---------------------------------------------------------------------------


class TestUpdatePlugin:
    """Tests for PluginMarketplace.update_plugin."""

    def test_returns_tuple(self, tmp_path):
        """update_plugin() should return a (bool, str) tuple."""
        mp = PluginMarketplace()
        result = mp.update_plugin("x", tmp_path)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_false_not_implemented(self, tmp_path):
        """Placeholder should report failure."""
        mp = PluginMarketplace()
        success, _ = mp.update_plugin("x", tmp_path)
        assert success is False


# ---------------------------------------------------------------------------
# uninstall_plugin
# ---------------------------------------------------------------------------


class TestUninstallPlugin:
    """Tests for PluginMarketplace.uninstall_plugin."""

    def test_returns_tuple(self, tmp_path):
        """uninstall_plugin() should return a (bool, str) tuple."""
        mp = PluginMarketplace()
        plugin_dir = tmp_path / "myplugin"
        plugin_dir.mkdir()
        result = mp.uninstall_plugin(plugin_dir)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_removes_existing_directory(self, tmp_path):
        """uninstall_plugin() should delete an existing plugin directory."""
        mp = PluginMarketplace()
        plugin_dir = tmp_path / "myplugin"
        plugin_dir.mkdir()
        (plugin_dir / "__init__.py").touch()
        success, _ = mp.uninstall_plugin(plugin_dir)
        assert success is True
        assert not plugin_dir.exists()

    def test_returns_false_for_missing_directory(self, tmp_path):
        """uninstall_plugin() should return False when directory doesn't exist."""
        mp = PluginMarketplace()
        missing = tmp_path / "nonexistent_plugin"
        success, msg = mp.uninstall_plugin(missing)
        assert success is False
        assert isinstance(msg, str)

    def test_success_message_contains_path(self, tmp_path):
        """Success message should mention the plugin directory path."""
        mp = PluginMarketplace()
        plugin_dir = tmp_path / "theplugin"
        plugin_dir.mkdir()
        _, msg = mp.uninstall_plugin(plugin_dir)
        assert str(plugin_dir) in msg or "theplugin" in msg


# ---------------------------------------------------------------------------
# list_installed_plugins
# ---------------------------------------------------------------------------


class TestListInstalledPlugins:
    """Tests for PluginMarketplace.list_installed_plugins."""

    def test_returns_list(self, tmp_path):
        """list_installed_plugins() should return a list."""
        mp = PluginMarketplace()
        result = mp.list_installed_plugins(tmp_path)
        assert isinstance(result, list)

    def test_empty_for_nonexistent_dir(self, tmp_path):
        """list_installed_plugins() should return [] for a non-existent path."""
        mp = PluginMarketplace()
        result = mp.list_installed_plugins(tmp_path / "missing")
        assert result == []

    def test_discovers_valid_plugin(self, tmp_path):
        """list_installed_plugins() should include dirs that have __init__.py."""
        mp = PluginMarketplace()
        plugin_dir = tmp_path / "myplugin"
        plugin_dir.mkdir()
        (plugin_dir / "__init__.py").touch()
        result = mp.list_installed_plugins(tmp_path)
        assert len(result) == 1
        assert result[0]["id"] == "myplugin"

    def test_ignores_dirs_without_init(self, tmp_path):
        """list_installed_plugins() should skip dirs without __init__.py."""
        mp = PluginMarketplace()
        no_init = tmp_path / "notaplugin"
        no_init.mkdir()
        result = mp.list_installed_plugins(tmp_path)
        assert result == []

    def test_ignores_underscore_dirs(self, tmp_path):
        """list_installed_plugins() should skip directories starting with '_'."""
        mp = PluginMarketplace()
        hidden = tmp_path / "_private"
        hidden.mkdir()
        (hidden / "__init__.py").touch()
        result = mp.list_installed_plugins(tmp_path)
        assert result == []

    def test_plugin_entry_has_required_keys(self, tmp_path):
        """Each entry should contain id, path, and name keys."""
        mp = PluginMarketplace()
        plugin_dir = tmp_path / "coolplugin"
        plugin_dir.mkdir()
        (plugin_dir / "__init__.py").touch()
        result = mp.list_installed_plugins(tmp_path)
        entry = result[0]
        assert "id" in entry
        assert "path" in entry
        assert "name" in entry

    def test_multiple_plugins_discovered(self, tmp_path):
        """Multiple valid plugin dirs should all be discovered."""
        mp = PluginMarketplace()
        for name in ("plugin_a", "plugin_b", "plugin_c"):
            d = tmp_path / name
            d.mkdir()
            (d / "__init__.py").touch()
        result = mp.list_installed_plugins(tmp_path)
        ids = {r["id"] for r in result}
        assert ids == {"plugin_a", "plugin_b", "plugin_c"}


# ---------------------------------------------------------------------------
# check_updates
# ---------------------------------------------------------------------------


class TestCheckUpdates:
    """Tests for PluginMarketplace.check_updates."""

    def test_returns_none_placeholder(self):
        """Placeholder implementation should return None."""
        mp = PluginMarketplace()
        result = mp.check_updates("some-plugin", "1.0.0")
        assert result is None

    def test_accepts_version_string(self):
        """check_updates() should accept any version string without raising."""
        mp = PluginMarketplace()
        mp.check_updates("x", "0.0.1")
        mp.check_updates("x", "99.99.99")


# ---------------------------------------------------------------------------
# create_marketplace_client factory
# ---------------------------------------------------------------------------


class TestCreateMarketplaceClient:
    """Tests for create_marketplace_client()."""

    def test_returns_plugin_marketplace_instance(self):
        """create_marketplace_client() should return a PluginMarketplace."""
        mp = create_marketplace_client()
        assert isinstance(mp, PluginMarketplace)

    def test_custom_url_forwarded(self):
        """Custom URL should be stored on the returned instance."""
        mp = create_marketplace_client("https://my-registry.example.com")
        assert mp.marketplace_url == "https://my-registry.example.com"

    def test_default_url_when_none(self):
        """Passing None should fall back to the default URL."""
        mp = create_marketplace_client(None)
        assert mp.marketplace_url == "https://plugins.aiml-dash.org"
