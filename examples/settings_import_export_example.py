"""
Example usage of settings import/export functionality.

This example demonstrates how to export and import application settings
to/from JSON and YAML files using class methods.
"""

from pathlib import Path

from aiml_dash.utils.settings import Settings, get_settings


def example_basic_export():
    """Example: Export current settings to JSON and YAML files."""
    print("=== Basic Export Example ===")

    settings = get_settings()

    # Export to JSON
    settings.export_to_json("settings_backup.json")
    print("✓ Settings exported to settings_backup.json")

    # Export to YAML
    settings.export_to_yaml("settings_backup.yaml")
    print("✓ Settings exported to settings_backup.yaml")

    # Generic export (format determined by extension)
    settings.export_to("settings_backup.yml")
    print("✓ Settings exported to settings_backup.yml")


def example_custom_settings_export():
    """Example: Export custom settings objects."""
    print("\n=== Custom Settings Export Example ===")

    # Create custom settings
    custom_settings = Settings(
        app_name="My Custom App",
        app_version="2.5.0",
        debug=True,
        host="0.0.0.0",
        port=9000,
        log_level="DEBUG",
        theme="dark",
        page_size=75,
        max_upload_size_mb=500,
        default_confidence_level=0.99,
        plot_template="plotly_dark",
    )

    # Export custom settings
    custom_settings.export_to_json("custom_settings.json")
    print("✓ Custom settings exported to custom_settings.json")


def example_import():
    """Example: Import settings from files."""
    print("\n=== Import Example ===")

    # First, create a file to import
    settings = get_settings()
    settings.export_to_json("temp_settings.json")

    # Import settings
    loaded_settings = Settings.from_json("temp_settings.json")
    print(f"✓ Loaded settings: app_name = {loaded_settings.app_name}")
    print(f"  Loaded settings: theme = {loaded_settings.theme}")

    # Generic import (format determined by extension)
    settings_obj = Settings.from_file("temp_settings.json")
    print("✓ Settings imported using generic function")


def example_modify_and_export():
    """Example: Modify settings and export them."""
    print("\n=== Modify and Export Example ===")

    # Create new settings with modifications
    production_settings = Settings(
        app_name="AIML Dash Production",
        app_version="1.0.0",
        debug=False,  # Production mode
        host="0.0.0.0",
        port=8080,
        log_level="WARNING",
        theme="light",
        page_size=50,
        max_upload_size_mb=100,
        auto_save=True,
        cache_enabled=True,
        enable_compression=True,
    )

    # Export to JSON
    production_settings.export_to_json("production_settings.json")
    print("✓ Production settings exported to production_settings.json")

    # Export to YAML
    production_settings.export_to_yaml("production_settings.yaml")
    print("✓ Production settings exported to production_settings.yaml")


def example_different_environments():
    """Example: Create settings for different environments."""
    print("\n=== Different Environments Example ===")

    # Development settings
    dev_settings = Settings(
        app_name="AIML Dash Dev",
        debug=True,
        host="127.0.0.1",
        port=8050,
        log_level="DEBUG",
        theme="light",
        cache_enabled=False,
        enable_compression=False,
    )
    dev_settings.export_to_yaml("config/dev_settings.yaml")
    print("✓ Development settings exported")

    # Staging settings
    staging_settings = Settings(
        app_name="AIML Dash Staging",
        debug=False,
        host="0.0.0.0",
        port=8080,
        log_level="INFO",
        theme="light",
        cache_enabled=True,
        enable_compression=True,
    )
    staging_settings.export_to_yaml("config/staging_settings.yaml")
    print("✓ Staging settings exported")

    # Production settings
    prod_settings = Settings(
        app_name="AIML Dash",
        debug=False,
        host="0.0.0.0",
        port=80,
        log_level="WARNING",
        theme="light",
        cache_enabled=True,
        enable_compression=True,
        callback_timeout=600,
    )
    prod_settings.export_to_yaml("config/production_settings.yaml")
    print("✓ Production settings exported")


def example_load_environment_specific_settings():
    """Example: Load settings based on environment."""
    print("\n=== Load Environment-Specific Settings Example ===")

    import os

    environment = os.getenv("APP_ENV", "development")
    config_file = f"config/{environment}_settings.yaml"

    if Path(config_file).exists():
        loaded_settings = Settings.from_file(config_file)
        print(f"✓ Loaded {environment} settings from {config_file}")
        print(f"  App Name: {loaded_settings.app_name}")
        print(f"  Debug Mode: {loaded_settings.debug}")
        print(f"  Host: {loaded_settings.host}")
        print(f"  Port: {loaded_settings.port}")
    else:
        print(f"⚠ Config file {config_file} not found, using defaults")


def example_error_handling():
    """Example: Proper error handling."""
    print("\n=== Error Handling Example ===")

    # Handle file not found
    try:
        Settings.from_json("nonexistent.json")
    except FileNotFoundError:
        print("✓ Handled FileNotFoundError for missing file")

    # Handle unsupported format
    try:
        settings = get_settings()
        settings.export_to("settings.txt")
    except ValueError as e:
        print(f"✓ Handled ValueError for unsupported format: {e}")

    # Handle invalid JSON
    Path("invalid.json").write_text("not valid json{")
    try:
        Settings.from_json("invalid.json")
    except Exception as e:
        print(f"✓ Handled exception for invalid JSON: {type(e).__name__}")
    finally:
        Path("invalid.json").unlink(missing_ok=True)


def main():
    """Run all examples."""
    print("Settings Import/Export Examples")
    print("=" * 50)

    # Create config directory if it doesn't exist
    Path("config").mkdir(exist_ok=True)

    try:
        example_basic_export()
        example_custom_settings_export()
        example_import()
        example_modify_and_export()
        example_different_environments()
        example_load_environment_specific_settings()
        example_error_handling()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    finally:
        # Cleanup example files
        print("\n=== Cleanup ===")
        cleanup_files = [
            "settings_backup.json",
            "settings_backup.yaml",
            "settings_backup.yml",
            "custom_settings.json",
            "temp_settings.json",
            "production_settings.json",
            "production_settings.yaml",
        ]
        for file in cleanup_files:
            Path(file).unlink(missing_ok=True)
            print(f"✓ Cleaned up {file}")


if __name__ == "__main__":
    main()
