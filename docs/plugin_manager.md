# PluginManager Documentation

## Overview

The `PluginManager` class provides centralized management of plugins in the AIML Dash application. It handles automatic plugin discovery, registration, initialization, and configuration management.

## Features

### 1. Automatic Plugin Discovery

The PluginManager automatically discovers plugins from the `aiml_dash/plugins/` directory:

```python
from aiml_dash.plugins.plugin_manager import PluginManager

# Automatic discovery on initialization
manager = PluginManager()
```

Plugin discovery works by:
- Scanning all subdirectories in the `plugins/` package
- Looking for modules with a `get_plugin()` function
- Automatically registering discovered plugins
- Gracefully handling plugins that fail to load

### 2. Manual Plugin Registration

You can also manually register plugins:

```python
from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.plugin_manager import PluginManager

# Create a custom plugin
custom_plugin = Plugin(
    id="custom",
    name="Custom Plugin",
    description="My custom plugin",
    pages=[],
    version="1.0",
    default_enabled=True,
)

# Initialize with manual plugins
manager = PluginManager(plugins=[custom_plugin])

# Or register after initialization
manager.register_plugin(custom_plugin)
```

### 3. Plugin Configuration Management

The PluginManager handles various plugin configurations:

```python
# Get all registered plugins
plugins = manager.get_plugins()

# Get plugin registry (dict of plugin_id -> Plugin)
registry = manager.get_plugin_registry()

# Get default enabled plugins
defaults = manager.get_default_enabled_plugins()

# Normalize enabled plugins (includes locked plugins)
enabled = manager.normalize_enabled_plugins(["core", "example"])

# Get plugin metadata for UI rendering
metadata = manager.get_plugin_metadata()
```

### 4. Callback Registration

Register callbacks for all plugins:

```python
from dash import Dash

app = Dash(__name__)
manager.register_callbacks(app)
```

## Using the Global Singleton

For backward compatibility and convenience, a global singleton instance is available:

```python
from aiml_dash.plugins.plugin_manager import get_default_manager

# Get the default manager instance (created on first call)
manager = get_default_manager()

# All subsequent calls return the same instance
manager2 = get_default_manager()
assert manager is manager2  # True
```

## Backward Compatibility with registry.py

The existing `registry.py` module continues to work and delegates to the PluginManager:

```python
from aiml_dash.plugins.registry import (
    get_plugins,
    get_plugin_registry,
    get_plugin_metadata,
    get_default_enabled_plugins,
    normalize_enabled_plugins,
    register_plugin_callbacks,
)

# All these functions now delegate to the global PluginManager
plugins = get_plugins()  # Calls get_default_manager().get_plugins()
```

## Separation of Concerns

The PluginManager focuses on **backend plugin operations**:
- Plugin discovery and registration
- Plugin configuration management
- Callback registration
- Plugin metadata generation

The `registry.py` module continues to handle **UI-related operations**:
- `build_navigation_sections()` - Creates navigation UI structure
- `get_pages()` - Gets pages for enabled plugins
- `get_page_registry()` - Gets page registry for routing

## Creating a Custom Plugin

To create a new plugin that will be automatically discovered:

1. Create a new directory in `aiml_dash/plugins/`
2. Add an `__init__.py` file with a `get_plugin()` function:

```python
# aiml_dash/plugins/my_plugin/__init__.py
from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.my_plugin.layout import my_layout

def get_plugin() -> Plugin:
    """Return the plugin definition."""
    pages = [
        PluginPage(
            id="my_page",
            label="My Page",
            icon="carbon:apps",
            section="Plugins",
            order=1,
            layout=my_layout,
        )
    ]
    
    return Plugin(
        id="my_plugin",
        name="My Plugin",
        description="My custom plugin",
        pages=pages,
        version="1.0",
        default_enabled=True,
        locked=False,
    )
```

3. The PluginManager will automatically discover and register it on next startup.

## Testing

The PluginManager includes comprehensive unit tests:

```bash
# Run PluginManager tests
pytest tests/plugins/test_plugin_manager.py -v

# Run all plugin tests
pytest tests/plugins/ -v
```

## API Reference

### PluginManager

#### `__init__(plugins: Sequence[Plugin] | None = None)`
Initialize the PluginManager. If `plugins` is None, uses automatic discovery.

#### `register_plugin(plugin: Plugin) -> None`
Manually register a plugin.

#### `discover_plugins() -> None`
Discover and register plugins from the plugins package.

#### `get_plugins() -> Sequence[Plugin]`
Return the ordered list of registered plugins.

#### `get_plugin_registry() -> dict[str, Plugin]`
Return plugins keyed by their identifier.

#### `get_plugin_metadata() -> list[dict[str, object]]`
Return plugin metadata for UI rendering.

#### `get_default_enabled_plugins() -> list[str]`
Return the list of plugins enabled by default, including locked plugins.

#### `normalize_enabled_plugins(enabled_plugins: Iterable[str] | None) -> list[str]`
Normalize enabled plugins to include locked entries and filter invalid IDs.

#### `register_callbacks(app: object) -> None`
Register callbacks defined by all plugins.

### Global Functions

#### `get_default_manager() -> PluginManager`
Get or create the default global PluginManager instance.

## Best Practices

1. **Use the singleton for application code**: Use `get_default_manager()` in your application code for consistency.

2. **Use explicit instances for testing**: Create new `PluginManager` instances in tests to avoid side effects.

3. **Let automatic discovery work**: Unless you have specific needs, let the PluginManager discover plugins automatically.

4. **Keep UI logic in registry.py**: UI-related functions like `build_navigation_sections()` remain in `registry.py`.

5. **Handle plugin loading errors gracefully**: The PluginManager silently skips plugins that fail to load, allowing the application to continue.
