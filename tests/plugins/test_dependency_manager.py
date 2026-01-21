"""Tests for plugin dependency management."""

import pytest

from aiml_dash.plugins.dependency_manager import (
    check_dependencies,
    check_version_compatibility,
    parse_version,
    resolve_dependencies,
    validate_plugin,
)
from aiml_dash.plugins.models import Plugin


class TestParseVersion:
    """Tests for version parsing."""

    def test_parse_simple_version(self):
        """Test parsing a simple version string."""
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_parse_two_part_version(self):
        """Test parsing a two-part version string."""
        assert parse_version("1.0") == (1, 0)

    def test_parse_invalid_version(self):
        """Test parsing invalid version returns default."""
        assert parse_version("invalid") == (0, 0, 0)


class TestVersionCompatibility:
    """Tests for version compatibility checking."""

    def test_compatible_version(self):
        """Test plugin with compatible version."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            min_app_version="0.0.1",
            max_app_version="1.0.0",
        )
        is_compat, _ = check_version_compatibility(plugin, "0.5.0")
        assert is_compat is True

    def test_below_minimum_version(self):
        """Test plugin with app version below minimum."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            min_app_version="1.0.0",
        )
        is_compat, error = check_version_compatibility(plugin, "0.5.0")
        assert is_compat is False
        assert "requires app version >=" in error

    def test_above_maximum_version(self):
        """Test plugin with app version above maximum."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            max_app_version="1.0.0",
        )
        is_compat, error = check_version_compatibility(plugin, "2.0.0")
        assert is_compat is False
        assert "requires app version <=" in error


class TestDependencyChecks:
    """Tests for dependency checking."""

    def test_no_dependencies(self):
        """Test plugin with no dependencies."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
        )
        deps_met, _ = check_dependencies(plugin, {})
        assert deps_met is True

    def test_dependencies_met(self):
        """Test plugin with all dependencies available."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            dependencies=["dep1", "dep2"],
        )
        available = {
            "dep1": Plugin(id="dep1", name="Dep1", description="", pages=[]),
            "dep2": Plugin(id="dep2", name="Dep2", description="", pages=[]),
        }
        deps_met, _ = check_dependencies(plugin, available)
        assert deps_met is True

    def test_missing_dependencies(self):
        """Test plugin with missing dependencies."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            dependencies=["dep1", "dep2"],
        )
        available = {
            "dep1": Plugin(id="dep1", name="Dep1", description="", pages=[]),
        }
        deps_met, error = check_dependencies(plugin, available)
        assert deps_met is False
        assert "missing dependencies" in error
        assert "dep2" in error


class TestDependencyResolution:
    """Tests for dependency resolution."""

    def test_no_dependencies(self):
        """Test resolving plugins with no dependencies."""
        plugins = [
            Plugin(id="a", name="A", description="", pages=[]),
            Plugin(id="b", name="B", description="", pages=[]),
        ]
        resolved, errors = resolve_dependencies(plugins)
        assert len(resolved) == 2
        assert len(errors) == 0

    def test_simple_dependency_chain(self):
        """Test resolving a simple dependency chain."""
        plugins = [
            Plugin(id="b", name="B", description="", pages=[], dependencies=["a"]),
            Plugin(id="a", name="A", description="", pages=[]),
        ]
        resolved, errors = resolve_dependencies(plugins)
        assert len(resolved) == 2
        assert len(errors) == 0
        # 'a' should be loaded before 'b'
        assert resolved[0].id == "a"
        assert resolved[1].id == "b"

    def test_circular_dependency(self):
        """Test detecting circular dependencies."""
        plugins = [
            Plugin(id="a", name="A", description="", pages=[], dependencies=["b"]),
            Plugin(id="b", name="B", description="", pages=[], dependencies=["a"]),
        ]
        resolved, errors = resolve_dependencies(plugins)
        assert len(resolved) == 0
        assert len(errors) > 0
        assert "circular" in errors[0].lower()


class TestPluginValidation:
    """Tests for complete plugin validation."""

    def test_valid_plugin(self):
        """Test validating a completely valid plugin."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            version="1.0.0",
            min_app_version="0.0.1",
        )
        available = {}
        is_valid, errors = validate_plugin(plugin, available, "0.5.0")
        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_version(self):
        """Test validating plugin with incompatible version."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            min_app_version="2.0.0",
        )
        available = {}
        is_valid, errors = validate_plugin(plugin, available, "1.0.0")
        assert is_valid is False
        assert len(errors) > 0

    def test_missing_dependency(self):
        """Test validating plugin with missing dependency."""
        plugin = Plugin(
            id="test",
            name="Test",
            description="Test",
            pages=[],
            dependencies=["missing"],
        )
        available = {}
        is_valid, errors = validate_plugin(plugin, available, "1.0.0")
        assert is_valid is False
        assert len(errors) > 0
