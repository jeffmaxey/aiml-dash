"""
Example demonstrating PluginManager usage.

This example shows how to:
1. Use the PluginManager with automatic discovery
2. Create custom plugins
3. Access plugin information
4. Use the backward-compatible registry API
"""

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.plugin_manager import PluginManager, get_default_manager
from aiml_dash.plugins.registry import get_plugins, get_plugin_metadata


def example_basic_usage():
    """Example 1: Basic usage with automatic discovery."""
    print("=" * 60)
    print("Example 1: Basic Usage with Automatic Discovery")
    print("=" * 60)

    # Create a PluginManager with automatic discovery
    manager = PluginManager()

    # Get all discovered plugins
    plugins = manager.get_plugins()
    print(f"\nDiscovered {len(plugins)} plugins:")
    for plugin in plugins:
        print(f"  - {plugin.id}: {plugin.name}")
        print(f"    Description: {plugin.description}")
        print(f"    Version: {plugin.version}")
        print(f"    Default Enabled: {plugin.default_enabled}")
        print(f"    Locked: {plugin.locked}")
        print(f"    Pages: {len(plugin.pages)}")
        print()


def example_custom_plugin():
    """Example 2: Creating and registering a custom plugin."""
    print("=" * 60)
    print("Example 2: Custom Plugin Registration")
    print("=" * 60)

    # Create a custom plugin
    custom_plugin = Plugin(
        id="custom_example",
        name="Custom Example Plugin",
        description="A plugin created for demonstration purposes",
        pages=[
            PluginPage(
                id="custom_page",
                label="Custom Page",
                icon="carbon:star",
                section="Plugins",
                order=1,
                layout=lambda: None,  # Placeholder layout
            )
        ],
        version="1.0.0",
        default_enabled=False,
        locked=False,
    )

    # Initialize manager with explicit plugins
    manager = PluginManager(plugins=[custom_plugin])

    print(f"\nRegistered custom plugin: {custom_plugin.name}")
    print(f"Plugin ID: {custom_plugin.id}")
    print(f"Number of pages: {len(custom_plugin.pages)}")


def example_plugin_configuration():
    """Example 3: Working with plugin configuration."""
    print("=" * 60)
    print("Example 3: Plugin Configuration Management")
    print("=" * 60)

    manager = get_default_manager()

    # Get default enabled plugins
    defaults = manager.get_default_enabled_plugins()
    print(f"\nDefault enabled plugins: {defaults}")

    # Normalize a list of enabled plugins
    enabled = manager.normalize_enabled_plugins(["core", "example"])
    print(f"Normalized plugins (includes locked): {enabled}")

    # Get plugin metadata for UI
    metadata = manager.get_plugin_metadata()
    print(f"\nPlugin metadata for UI:")
    for meta in metadata:
        print(f"  {meta['id']}: enabled={meta['default_enabled']}, locked={meta['locked']}")


def example_backward_compatibility():
    """Example 4: Using backward-compatible registry API."""
    print("=" * 60)
    print("Example 4: Backward Compatibility via registry.py")
    print("=" * 60)

    # Use the familiar registry functions
    plugins = get_plugins()
    print(f"\nUsing get_plugins(): {len(plugins)} plugins")

    metadata = get_plugin_metadata()
    print(f"Using get_plugin_metadata(): {len(metadata)} plugins")

    print("\nBoth APIs provide the same data:")
    print(f"  Direct: {len(get_default_manager().get_plugins())} plugins")
    print(f"  Registry: {len(get_plugins())} plugins")


def example_singleton_pattern():
    """Example 5: Demonstrating the singleton pattern."""
    print("=" * 60)
    print("Example 5: Global Singleton Pattern")
    print("=" * 60)

    # Get multiple references to the default manager
    manager1 = get_default_manager()
    manager2 = get_default_manager()

    print(f"\nManager 1 ID: {id(manager1)}")
    print(f"Manager 2 ID: {id(manager2)}")
    print(f"Same instance: {manager1 is manager2}")

    # Register a plugin in one reference
    test_plugin = Plugin(
        id="singleton_test",
        name="Singleton Test",
        description="Testing singleton behavior",
        pages=[],
    )
    manager1.register_plugin(test_plugin)

    # Verify it's available in the other reference
    registry = manager2.get_plugin_registry()
    print(f"\nPlugin registered via manager1")
    print(f"Available in manager2: {'singleton_test' in registry}")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    print("\n")

    example_custom_plugin()
    print("\n")

    example_plugin_configuration()
    print("\n")

    example_backward_compatibility()
    print("\n")

    example_singleton_pattern()
    print("\n")

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
