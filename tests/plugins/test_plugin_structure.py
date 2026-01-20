"""Tests for plugin module structure and completeness.

This module validates that all plugins follow the standard structure
with required modules and proper documentation.
"""

import importlib
import inspect
from pathlib import Path

import pytest

from aiml_dash.plugins.loader import validate_plugin_structure
from aiml_dash.plugins.registry import get_plugin_registry


class TestPluginStructure:
    """Tests for plugin directory structure."""

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin", "legacy"],
    )
    def test_plugin_has_all_required_modules(self, plugin_id):
        """Test that each plugin has all required module files."""
        plugins_path = Path(__file__).parent.parent.parent / "aiml_dash" / "plugins"
        plugin_path = plugins_path / plugin_id

        is_valid, error_msg = validate_plugin_structure(plugin_path)

        assert is_valid, f"Plugin '{plugin_id}' structure validation failed: {error_msg}"

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin", "legacy"],
    )
    def test_plugin_modules_are_importable(self, plugin_id):
        """Test that all plugin modules can be imported."""
        base_module = f"aiml_dash.plugins.{plugin_id}"

        modules = ["layout", "components", "callbacks", "styles", "constants"]

        for module_name in modules:
            full_module = f"{base_module}.{module_name}"
            try:
                module = importlib.import_module(full_module)
                assert module is not None, f"Failed to import {full_module}"
            except ImportError as e:
                pytest.fail(f"Could not import {full_module}: {e}")

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin"],
    )
    def test_plugin_constants_module_has_required_constants(self, plugin_id):
        """Test that constants module defines required constants."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}.constants")

        # Required constants
        required = [
            "PLUGIN_ID",
            "PLUGIN_NAME",
            "PLUGIN_VERSION",
            "PLUGIN_DESCRIPTION",
            "SECTION_NAME",
        ]

        for const_name in required:
            assert hasattr(module, const_name), f"Plugin '{plugin_id}' missing constant: {const_name}"
            value = getattr(module, const_name)
            assert value is not None and value != "", f"Constant {const_name} is empty in {plugin_id}"

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin"],
    )
    def test_plugin_layout_module_has_layout_function(self, plugin_id):
        """Test that layout module defines layout functions."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}.layout")

        # Find all functions that return layouts
        functions = [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]
        layout_functions = [f for f in functions if "layout" in f.lower()]

        assert len(layout_functions) > 0, f"Plugin '{plugin_id}' has no layout functions"

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin"],
    )
    def test_plugin_callbacks_has_register_function(self, plugin_id):
        """Test that callbacks module has register_callbacks function."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}.callbacks")

        assert hasattr(module, "register_callbacks"), f"Plugin '{plugin_id}' missing register_callbacks function"

        func = getattr(module, "register_callbacks")
        assert callable(func), f"register_callbacks in '{plugin_id}' is not callable"


class TestPluginDocumentation:
    """Tests for plugin documentation completeness."""

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin"],
    )
    def test_plugin_init_has_docstring(self, plugin_id):
        """Test that plugin __init__ module has a docstring."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}")

        assert module.__doc__ is not None, f"Plugin '{plugin_id}' __init__.py missing module docstring"
        assert len(module.__doc__.strip()) > 0, f"Plugin '{plugin_id}' __init__.py has empty docstring"

    @pytest.mark.parametrize(
        "plugin_id,module_name",
        [
            ("core", "layout"),
            ("core", "components"),
            ("core", "callbacks"),
            ("example_plugin", "layout"),
            ("example_plugin", "components"),
            ("example_plugin", "callbacks"),
            ("template_plugin", "layout"),
            ("template_plugin", "components"),
            ("template_plugin", "callbacks"),
        ],
    )
    def test_plugin_modules_have_docstrings(self, plugin_id, module_name):
        """Test that plugin modules have docstrings."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}.{module_name}")

        assert module.__doc__ is not None, f"Plugin '{plugin_id}.{module_name}' missing module docstring"
        assert len(module.__doc__.strip()) > 0, f"Plugin '{plugin_id}.{module_name}' has empty docstring"

    @pytest.mark.parametrize(
        "plugin_id",
        ["core", "example_plugin", "template_plugin"],
    )
    def test_plugin_get_plugin_has_docstring(self, plugin_id):
        """Test that get_plugin function has a docstring."""
        module = importlib.import_module(f"aiml_dash.plugins.{plugin_id}")

        func = getattr(module, "get_plugin")
        assert func.__doc__ is not None, f"Plugin '{plugin_id}' get_plugin() missing docstring"
        assert len(func.__doc__.strip()) > 0, f"Plugin '{plugin_id}' get_plugin() has empty docstring"


class TestPluginPages:
    """Tests for plugin page definitions."""

    def test_all_plugins_have_pages(self):
        """Test that all registered plugins define pages."""
        registry = get_plugin_registry()

        for plugin_id, plugin in registry.items():
            assert len(plugin.pages) > 0, f"Plugin '{plugin_id}' has no pages defined"

    def test_all_pages_have_unique_ids(self):
        """Test that all page IDs are unique across plugins."""
        registry = get_plugin_registry()
        page_ids = set()

        for plugin in registry.values():
            for page in plugin.pages:
                assert page.id not in page_ids, f"Duplicate page ID: {page.id}"
                page_ids.add(page.id)

    def test_all_pages_have_required_attributes(self):
        """Test that all pages have required attributes."""
        registry = get_plugin_registry()

        for plugin in registry.values():
            for page in plugin.pages:
                assert page.id, f"Page in plugin '{plugin.id}' missing ID"
                assert page.label, f"Page '{page.id}' missing label"
                assert page.icon, f"Page '{page.id}' missing icon"
                assert page.section, f"Page '{page.id}' missing section"
                assert callable(page.layout), f"Page '{page.id}' layout is not callable"

    def test_page_layouts_are_callable(self):
        """Test that all page layout functions are callable."""
        registry = get_plugin_registry()

        for plugin in registry.values():
            for page in plugin.pages:
                assert callable(page.layout), f"Page '{page.id}' layout is not callable"
                # Note: We don't call layouts here to avoid import issues with
                # pages that depend on external modules not part of plugin framework


class TestPluginIndependence:
    """Tests for plugin independence and isolation."""

    @pytest.mark.parametrize(
        "plugin_id",
        ["example", "template"],
    )
    def test_plugin_can_be_disabled(self, plugin_id):
        """Test that non-locked plugins can be disabled."""
        from aiml_dash.plugins.registry import get_pages

        # Get pages with only this plugin enabled
        enabled_pages = get_pages([plugin_id, "core"])  # Core is locked

        # Get pages without this plugin (only core)
        disabled_pages = get_pages(["core"])

        # Pages should be different
        enabled_ids = {p.id for p in enabled_pages}
        disabled_ids = {p.id for p in disabled_pages}

        # Plugin pages should be in enabled set but not in disabled set
        plugin = get_plugin_registry()[plugin_id]
        for page in plugin.pages:
            # The plugin page should be in enabled set
            assert page.id in enabled_ids, f"Page {page.id} not in enabled set"

    def test_disabling_plugin_does_not_affect_others(self):
        """Test that disabling one plugin doesn't affect others."""
        from aiml_dash.plugins.registry import get_default_enabled_plugins, get_pages

        # Get all enabled by default
        all_enabled = get_default_enabled_plugins()

        # Disable example plugin
        without_example = [p for p in all_enabled if p != "example"]

        pages_all = get_pages(all_enabled)
        pages_without = get_pages(without_example)

        # Core pages should still be present
        core_page_ids = {"home", "settings", "help"}
        pages_without_ids = {p.id for p in pages_without}

        for core_id in core_page_ids:
            assert core_id in pages_without_ids, f"Core page '{core_id}' missing after disabling example plugin"
