"""Tests for settings import/export functionality."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from aiml_dash.utils.settings import Settings, get_settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_settings():
    """Create sample settings for testing."""
    settings = Settings(
        app_name="Test App",
        app_version="2.0.0",
        debug=True,
        host="0.0.0.0",
        port=8080,
    )
    return settings


class TestExportJSON:
    """Tests for JSON export functionality."""

    def test_export_to_json_default_settings(self, temp_dir):
        """Test exporting default settings to JSON."""
        settings = get_settings()
        filepath = temp_dir / "settings.json"
        settings.export_to_json(filepath)

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "app_name" in data

    def test_export_to_json_custom_settings(self, temp_dir, sample_settings):
        """Test exporting custom settings to JSON."""
        filepath = temp_dir / "custom_settings.json"
        sample_settings.export_to_json(filepath)

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert data["app_name"] == "Test App"
        assert data["app_version"] == "2.0.0"
        assert data["debug"] is True
        assert data["port"] == 8080

    def test_export_to_json_with_custom_indent(self, temp_dir):
        """Test JSON export with custom indentation."""
        settings = get_settings()
        filepath = temp_dir / "settings_indent.json"
        settings.export_to_json(filepath, indent=4)

        with open(filepath) as f:
            content = f.read()

        # Check that indentation is applied (4 spaces)
        assert "    " in content


class TestExportYAML:
    """Tests for YAML export functionality."""

    def test_export_to_yaml_default_settings(self, temp_dir):
        """Test exporting default settings to YAML."""
        settings = get_settings()
        filepath = temp_dir / "settings.yaml"
        settings.export_to_yaml(filepath)

        assert filepath.exists()

        with open(filepath) as f:
            data = yaml.safe_load(f)

        assert isinstance(data, dict)
        assert "app_name" in data

    def test_export_to_yaml_custom_settings(self, temp_dir, sample_settings):
        """Test exporting custom settings to YAML."""
        filepath = temp_dir / "custom_settings.yml"
        sample_settings.export_to_yaml(filepath)

        assert filepath.exists()

        with open(filepath) as f:
            data = yaml.safe_load(f)

        assert data["app_name"] == "Test App"
        assert data["app_version"] == "2.0.0"
        assert data["debug"] is True
        assert data["port"] == 8080


class TestImportJSON:
    """Tests for JSON import functionality."""

    def test_import_from_json(self, temp_dir, sample_settings):
        """Test importing settings from JSON."""
        filepath = temp_dir / "import_test.json"

        # First export
        sample_settings.export_to_json(filepath)

        # Then import
        loaded_settings = Settings.from_json(filepath)

        assert loaded_settings.app_name == "Test App"
        assert loaded_settings.app_version == "2.0.0"
        assert loaded_settings.debug is True
        assert loaded_settings.port == 8080

    def test_import_from_json_file_not_found(self, temp_dir):
        """Test importing from non-existent JSON file."""
        filepath = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            Settings.from_json(filepath)

    def test_import_from_json_invalid_json(self, temp_dir):
        """Test importing invalid JSON."""
        filepath = temp_dir / "invalid.json"
        with open(filepath, "w") as f:
            f.write("not valid json{")

        with pytest.raises(json.JSONDecodeError):
            Settings.from_json(filepath)

    def test_import_from_json_invalid_structure(self, temp_dir):
        """Test importing JSON with invalid structure."""
        filepath = temp_dir / "invalid_structure.json"
        with open(filepath, "w") as f:
            json.dump([], f)  # Array instead of object

        with pytest.raises(TypeError, match="must contain an object"):
            Settings.from_json(filepath)

    def test_import_from_json_partial_data(self, temp_dir):
        """Test importing JSON with partial data."""
        filepath = temp_dir / "partial.json"
        data = {"app_name": "Partial App"}
        with open(filepath, "w") as f:
            json.dump(data, f)

        loaded_settings = Settings.from_json(filepath)

        assert loaded_settings.app_name == "Partial App"
        # Should use defaults for missing fields
        assert loaded_settings.theme == "light"


class TestImportYAML:
    """Tests for YAML import functionality."""

    def test_import_from_yaml(self, temp_dir, sample_settings):
        """Test importing settings from YAML."""
        filepath = temp_dir / "import_test.yaml"

        # First export
        sample_settings.export_to_yaml(filepath)

        # Then import
        loaded_settings = Settings.from_yaml(filepath)

        assert loaded_settings.app_name == "Test App"
        assert loaded_settings.app_version == "2.0.0"
        assert loaded_settings.debug is True
        assert loaded_settings.port == 8080

    def test_import_from_yaml_file_not_found(self, temp_dir):
        """Test importing from non-existent YAML file."""
        filepath = temp_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            Settings.from_yaml(filepath)

    def test_import_from_yaml_invalid_yaml(self, temp_dir):
        """Test importing invalid YAML."""
        filepath = temp_dir / "invalid.yaml"
        with open(filepath, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            Settings.from_yaml(filepath)

    def test_import_from_yaml_invalid_structure(self, temp_dir):
        """Test importing YAML with invalid structure."""
        filepath = temp_dir / "invalid_structure.yaml"
        with open(filepath, "w") as f:
            f.write("- item1\n- item2")  # List instead of mapping

        with pytest.raises(TypeError, match="must contain a mapping"):
            Settings.from_yaml(filepath)


class TestGenericImportExport:
    """Tests for generic import/export methods."""

    def test_export_json_by_extension(self, temp_dir):
        """Test generic export method with .json extension."""
        settings = get_settings()
        filepath = temp_dir / "test.json"
        settings.export_to(filepath)

        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert "app_name" in data

    def test_export_yaml_by_extension(self, temp_dir):
        """Test generic export method with .yaml extension."""
        settings = get_settings()
        filepath = temp_dir / "test.yaml"
        settings.export_to(filepath)

        assert filepath.exists()
        with open(filepath) as f:
            data = yaml.safe_load(f)
        assert "app_name" in data

    def test_export_yml_by_extension(self, temp_dir):
        """Test generic export method with .yml extension."""
        settings = get_settings()
        filepath = temp_dir / "test.yml"
        settings.export_to(filepath)

        assert filepath.exists()
        with open(filepath) as f:
            data = yaml.safe_load(f)
        assert "app_name" in data

    def test_export_unsupported_extension(self, temp_dir):
        """Test export with unsupported file extension."""
        settings = get_settings()
        filepath = temp_dir / "test.txt"

        with pytest.raises(ValueError, match="Unsupported file extension"):
            settings.export_to(filepath)

    def test_import_json_by_extension(self, temp_dir, sample_settings):
        """Test generic import method with .json extension."""
        filepath = temp_dir / "test.json"
        sample_settings.export_to_json(filepath)

        loaded_settings = Settings.from_file(filepath)
        assert loaded_settings.app_name == sample_settings.app_name

    def test_import_yaml_by_extension(self, temp_dir, sample_settings):
        """Test generic import method with .yaml extension."""
        filepath = temp_dir / "test.yaml"
        sample_settings.export_to_yaml(filepath)

        loaded_settings = Settings.from_file(filepath)
        assert loaded_settings.app_name == sample_settings.app_name

    def test_import_yml_by_extension(self, temp_dir, sample_settings):
        """Test generic import method with .yml extension."""
        filepath = temp_dir / "test.yml"
        sample_settings.export_to_yaml(filepath)

        loaded_settings = Settings.from_file(filepath)
        assert loaded_settings.app_name == sample_settings.app_name

    def test_import_unsupported_extension(self, temp_dir):
        """Test import with unsupported file extension."""
        filepath = temp_dir / "test.txt"
        filepath.touch()

        with pytest.raises(ValueError, match="Unsupported file extension"):
            Settings.from_file(filepath)


class TestRoundTrip:
    """Tests for complete export-import cycles."""

    def test_json_roundtrip(self, temp_dir, sample_settings):
        """Test complete JSON export-import cycle."""
        filepath = temp_dir / "roundtrip.json"

        # Export
        sample_settings.export_to_json(filepath)

        # Import
        loaded_settings = Settings.from_json(filepath)

        # Verify all fields match
        assert loaded_settings.model_dump() == sample_settings.model_dump()

    def test_yaml_roundtrip(self, temp_dir, sample_settings):
        """Test complete YAML export-import cycle."""
        filepath = temp_dir / "roundtrip.yaml"

        # Export
        sample_settings.export_to_yaml(filepath)

        # Import
        loaded_settings = Settings.from_yaml(filepath)

        # Verify all fields match
        assert loaded_settings.model_dump() == sample_settings.model_dump()


class TestSettingsProperties:
    """Tests for Settings properties."""

    def test_base_dir_property(self):
        """Test base_dir property."""
        settings = get_settings()
        assert settings.base_dir.exists()
        assert settings.base_dir.is_dir()

    def test_assets_dir_property(self):
        """Test assets_dir property."""
        settings = get_settings()
        assert "assets" in str(settings.assets_dir)

    def test_data_dir_property(self):
        """Test data_dir property creates directory."""
        settings = get_settings()
        data_dir = settings.data_dir
        assert "data" in str(data_dir)
