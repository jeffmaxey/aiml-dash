"""Tests for aiml_dash.plugins.runtime module.

Verifies that PluginRuntime correctly loads plugins, filters by RBAC, handles
enable/disable logic, and registers callbacks.
"""

from __future__ import annotations

import pytest

from aiml_dash.auth import AuthorizationService, UserContext
from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.runtime import PluginRuntime
from aiml_dash.utils.config import get_settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runtime() -> PluginRuntime:
    """Return a PluginRuntime using the default application settings."""
    settings = get_settings()
    auth = AuthorizationService(settings)
    return PluginRuntime(settings=settings, authorization=auth)


@pytest.fixture()
def viewer_user() -> UserContext:
    return UserContext(user_id="alice", roles=("viewer",))


@pytest.fixture()
def no_role_user() -> UserContext:
    return UserContext(user_id="anon", roles=())


# ---------------------------------------------------------------------------
# Static plugins
# ---------------------------------------------------------------------------


class TestGetStaticPlugins:
    """Tests for PluginRuntime.get_static_plugins()."""

    def test_returns_sequence_of_plugins(self, runtime):
        """get_static_plugins() should return a non-empty sequence of Plugins."""
        plugins = runtime.get_static_plugins()
        assert len(plugins) > 0
        assert all(isinstance(p, Plugin) for p in plugins)

    def test_contains_core_plugin(self, runtime):
        """Static plugins must include the core plugin."""
        plugin_ids = {p.id for p in runtime.get_static_plugins()}
        assert "core" in plugin_ids

    def test_contains_expected_plugins(self, runtime):
        """All well-known static plugins should be present."""
        plugin_ids = {p.id for p in runtime.get_static_plugins()}
        for expected in ("core", "basics", "data", "design", "model", "multivariate"):
            assert expected in plugin_ids, f"Missing plugin: {expected}"


# ---------------------------------------------------------------------------
# get_plugins / get_plugin_registry
# ---------------------------------------------------------------------------


class TestGetPlugins:
    """Tests for PluginRuntime.get_plugins() and get_plugin_registry()."""

    def test_get_plugins_returns_plugins(self, runtime):
        """get_plugins() should return Plugin objects."""
        plugins = runtime.get_plugins()
        assert len(plugins) > 0
        assert all(isinstance(p, Plugin) for p in plugins)

    def test_static_plugins_subset_of_dynamic(self, runtime):
        """All static plugins should appear in the dynamic plugin list."""
        static_ids = {p.id for p in runtime.get_static_plugins()}
        dynamic_ids = {p.id for p in runtime.get_plugins(enable_dynamic_loading=True)}
        assert static_ids.issubset(dynamic_ids)

    def test_registry_is_dict_keyed_by_id(self, runtime):
        """get_plugin_registry() should return a dict keyed by plugin id."""
        registry = runtime.get_plugin_registry()
        assert isinstance(registry, dict)
        for key, plugin in registry.items():
            assert key == plugin.id

    def test_registry_contains_core(self, runtime):
        """Plugin registry must contain 'core'."""
        assert "core" in runtime.get_plugin_registry()


# ---------------------------------------------------------------------------
# Plugin metadata
# ---------------------------------------------------------------------------


class TestGetPluginMetadata:
    """Tests for PluginRuntime.get_plugin_metadata()."""

    def test_returns_list_of_dicts(self, runtime):
        """get_plugin_metadata() should return a list of dicts."""
        meta = runtime.get_plugin_metadata()
        assert isinstance(meta, list)
        assert all(isinstance(m, dict) for m in meta)

    def test_metadata_keys(self, runtime):
        """Each metadata entry should have the expected keys."""
        meta = runtime.get_plugin_metadata()
        for entry in meta:
            for key in ("id", "name", "description", "version", "default_enabled", "locked"):
                assert key in entry, f"Missing key '{key}' in metadata entry"

    def test_rbac_filters_restricted_plugin(self, runtime):
        """Plugins with allowed_roles should be hidden from unauthorized users."""
        # Create a restricted plugin
        restricted = Plugin(
            id="restricted",
            name="Restricted",
            description="For admins only",
            pages=[],
            version="1.0",
            default_enabled=True,
            locked=False,
            allowed_roles=("admin",),
        )
        runtime._static_plugins = list(runtime._ensure_static_plugins()) + [restricted]  # noqa: SLF001

        no_role = UserContext(user_id="anon", roles=())
        meta_ids = {m["id"] for m in runtime.get_plugin_metadata(user=no_role)}
        assert "restricted" not in meta_ids

        admin = UserContext(user_id="bob", roles=("admin",))
        meta_ids_admin = {m["id"] for m in runtime.get_plugin_metadata(user=admin)}
        assert "restricted" in meta_ids_admin

        # Restore original plugins
        runtime._static_plugins = None  # noqa: SLF001


# ---------------------------------------------------------------------------
# Default enabled plugins
# ---------------------------------------------------------------------------


class TestGetDefaultEnabledPlugins:
    """Tests for PluginRuntime.get_default_enabled_plugins()."""

    def test_core_is_default_enabled(self, runtime):
        """Core plugin must be in the default-enabled list."""
        defaults = runtime.get_default_enabled_plugins()
        assert "core" in defaults

    def test_all_defaults_are_strings(self, runtime):
        """Default enabled plugins should be a list of strings."""
        defaults = runtime.get_default_enabled_plugins()
        assert isinstance(defaults, list)
        assert all(isinstance(d, str) for d in defaults)


# ---------------------------------------------------------------------------
# normalize_enabled_plugins
# ---------------------------------------------------------------------------


class TestNormalizeEnabledPlugins:
    """Tests for PluginRuntime.normalize_enabled_plugins()."""

    def test_locked_plugin_always_included(self, runtime):
        """Core (locked) plugin should always be included after normalization."""
        normalized = runtime.normalize_enabled_plugins([])
        assert "core" in normalized

    def test_none_input_includes_locked(self, runtime):
        """Passing None should still include locked plugins."""
        normalized = runtime.normalize_enabled_plugins(None)
        assert "core" in normalized

    def test_unknown_ids_are_removed(self, runtime):
        """Plugin ids not in the registry should be filtered out."""
        normalized = runtime.normalize_enabled_plugins(["core", "nonexistent_plugin"])
        assert "nonexistent_plugin" not in normalized
        assert "core" in normalized

    def test_preserves_valid_unlocked_plugins(self, runtime):
        """Valid unlocked plugin ids should be preserved."""
        normalized = runtime.normalize_enabled_plugins(["core", "basics"])
        assert "basics" in normalized


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


class TestGetPages:
    """Tests for PluginRuntime.get_pages() and get_page_registry()."""

    def test_get_pages_returns_plugin_pages(self, runtime):
        """get_pages() should return PluginPage objects."""
        pages = runtime.get_pages()
        assert len(pages) > 0
        assert all(isinstance(p, PluginPage) for p in pages)

    def test_home_page_present_by_default(self, runtime):
        """The home page must be accessible with default settings."""
        pages = runtime.get_pages()
        page_ids = {p.id for p in pages}
        assert "home" in page_ids

    def test_disabled_plugin_pages_absent(self, runtime):
        """Pages from a disabled plugin should not appear."""
        pages = runtime.get_pages(enabled_plugins=["core"])
        page_ids = {p.id for p in pages}
        # 'example' page should not be present when example plugin is disabled
        assert "example" not in page_ids
        # Home should still be present
        assert "home" in page_ids

    def test_page_registry_keyed_by_id(self, runtime):
        """get_page_registry() should return a dict keyed by page id."""
        registry = runtime.get_page_registry(["core"])
        assert isinstance(registry, dict)
        assert "home" in registry
        for key, page in registry.items():
            assert key == page.id


# ---------------------------------------------------------------------------
# Callback registration
# ---------------------------------------------------------------------------


class TestRegisterCallbacks:
    """Tests for PluginRuntime.register_plugin_callbacks()."""

    def test_register_does_not_raise(self, runtime):
        """register_plugin_callbacks() should run without raising exceptions."""
        # Use a minimal mock app that records calls
        class MockApp:
            calls: list[str] = []

        runtime.register_plugin_callbacks(MockApp())
