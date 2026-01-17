"""Tests for plugin registry helpers."""

from aiml_dash.plugins.registry import (
    build_navigation_sections,
    get_default_enabled_plugins,
    get_page_registry,
    get_plugin_registry,
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
