"""Tests for plugin registry helpers.

This module contains tests for plugin registration, page management,
navigation building, and plugin enabling/disabling functionality.
"""

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.registry import (
    build_navigation_sections,
    get_default_enabled_plugins,
    get_page_registry,
    get_pages,
    get_plugin_registry,
    get_plugins,
    normalize_enabled_plugins,
)


def test_plugin_registry_contains_expected_plugins():
    """Ensure required plugins are registered."""
    registry = get_plugin_registry()
    assert "core" in registry
    assert "legacy" in registry
    assert "example" in registry
    assert "template" in registry


def test_default_enabled_plugins_include_core():
    """Core plugin should be enabled by default."""
    defaults = get_default_enabled_plugins()
    assert "core" in defaults


def test_normalize_enabled_plugins_adds_locked_core():
    """Locked plugins should be included after normalization."""
    normalized = normalize_enabled_plugins([])
    assert "core" in normalized


def test_page_registry_has_home_page():
    """Default page registry should include the home page."""
    registry = get_page_registry(get_default_enabled_plugins())
    assert "home" in registry


def test_build_navigation_sections_contains_core():
    """Navigation sections should include the Core section."""
    sections = build_navigation_sections(list(get_page_registry(get_default_enabled_plugins()).values()))
    section_labels = [section["label"] for section in sections]
    assert "Core" in section_labels


class TestPluginEnableDisable:
    """Tests for plugin enabling and disabling functionality."""

    def test_disabling_unlocked_plugin(self):
        """Test that unlocked plugins can be disabled."""
        # Get all plugins
        all_plugins = get_default_enabled_plugins()

        # Disable the example plugin (which is unlocked)
        enabled = [p for p in all_plugins if p != "example"]

        pages = get_pages(enabled)
        page_ids = {p.id for p in pages}

        # Example page should not be in the pages
        assert "example" not in page_ids

        # Core pages should still be present
        assert "home" in page_ids

    def test_locked_plugin_cannot_be_disabled(self):
        """Test that locked plugins (like core) are always enabled."""
        # Try to disable all plugins
        enabled = []

        normalized = normalize_enabled_plugins(enabled)

        # Core should still be enabled because it's locked
        assert "core" in normalized

    def test_enabling_previously_disabled_plugin(self):
        """Test re-enabling a previously disabled plugin."""
        # Start with defaults
        defaults = get_default_enabled_plugins()

        # Disable template (which is disabled by default)
        disabled = [p for p in defaults if p != "template"]

        # Re-enable template
        enabled = disabled + ["template"]

        pages = get_pages(enabled)
        page_ids = {p.id for p in pages}

        # Template page should now be present
        assert "template" in page_ids


class TestPluginMetadata:
    """Tests for plugin metadata."""

    def test_all_plugins_have_required_metadata(self):
        """Ensure all plugins have required metadata fields."""
        registry = get_plugin_registry()

        for plugin_id, plugin in registry.items():
            assert plugin.id == plugin_id
            assert isinstance(plugin.name, str)
            assert len(plugin.name) > 0
            assert isinstance(plugin.description, str)
            assert len(plugin.description) > 0
            assert isinstance(plugin.version, str)
            assert isinstance(plugin.default_enabled, bool)
            assert isinstance(plugin.locked, bool)

    def test_core_plugin_is_locked(self):
        """Ensure core plugin is locked."""
        registry = get_plugin_registry()
        core = registry["core"]
        assert core.locked is True

    def test_example_plugin_is_unlocked(self):
        """Ensure example plugin is not locked."""
        registry = get_plugin_registry()
        example = registry["example"]
        assert example.locked is False


class TestNavigationStructure:
    """Tests for navigation structure building."""

    def test_navigation_respects_section_order(self):
        """Test that navigation sections follow the defined order."""
        pages = list(get_page_registry(get_default_enabled_plugins()).values())
        sections = build_navigation_sections(pages)

        section_labels = [s["label"] for s in sections]

        # Core should come first
        if "Core" in section_labels:
            assert section_labels.index("Core") == 0

        # Plugins should come last (if present)
        if "Plugins" in section_labels:
            assert section_labels.index("Plugins") == len(section_labels) - 1

    def test_navigation_groups_pages_correctly(self):
        """Test that pages are grouped correctly within sections."""
        pages = list(get_page_registry(get_default_enabled_plugins()).values())
        sections = build_navigation_sections(pages)

        for section in sections:
            # Check that pages are sorted by order
            if "pages" in section:
                orders = [p.order for p in section["pages"]]
                assert orders == sorted(orders)

            # Check that groups are present and sorted
            if "groups" in section:
                for group in section["groups"]:
                    page_orders = [p.order for p in group["pages"]]
                    assert page_orders == sorted(page_orders)

    def test_all_sections_have_icons(self):
        """Test that all navigation sections have icons."""
        pages = list(get_page_registry(get_default_enabled_plugins()).values())
        sections = build_navigation_sections(pages)

        for section in sections:
            assert "icon" in section
            assert isinstance(section["icon"], str)
            assert len(section["icon"]) > 0


class TestDynamicPluginLoading:
    """Tests for dynamic plugin loading functionality."""

    def test_static_plugins_always_loaded(self):
        """Test that static plugins are always loaded."""
        plugins_static = get_plugins(enable_dynamic_loading=False)
        plugins_dynamic = get_plugins(enable_dynamic_loading=True)

        static_ids = {p.id for p in plugins_static}
        dynamic_ids = {p.id for p in plugins_dynamic}

        # All static plugins should be in dynamic list
        assert static_ids.issubset(dynamic_ids)

    def test_registry_functions_with_dynamic_loading(self):
        """Test that registry functions work with dynamic loading enabled."""
        registry = get_plugin_registry(enable_dynamic_loading=True)

        assert "core" in registry
        assert isinstance(registry["core"], Plugin)

        pages = get_pages(enable_dynamic_loading=True)
        assert len(pages) > 0
        assert all(isinstance(p, PluginPage) for p in pages)

    def test_default_enabled_plugins_with_dynamic_loading(self):
        """Test getting default enabled plugins with dynamic loading."""
        defaults = get_default_enabled_plugins(enable_dynamic_loading=True)

        assert "core" in defaults
        assert isinstance(defaults, list)
        assert all(isinstance(p, str) for p in defaults)
