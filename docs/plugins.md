# Plugins Module

The `aiml_dash.plugins` module provides a plugin architecture for extending the application with modular features.

## Overview

The plugin system allows for modular organization of features, making it easy to enable/disable functionality and maintain separation of concerns.

## Architecture

Each plugin consists of several components:

- **Layout**: UI structure and components
- **Callbacks**: Interactive behavior and data processing
- **Components**: Reusable UI elements specific to the plugin
- **Styles**: Custom CSS for the plugin

## Core Components

### Plugin Registry (`registry.py`)

Central registry for managing plugins and navigation.

**Key Functions:**

```python
from aiml_dash.plugins.registry import (
    get_plugins,
    get_plugin_registry,
    get_pages,
    normalize_enabled_plugins
)

# Get all available plugins
plugins = get_plugins()

# Get pages for enabled plugins
pages = get_pages(enabled_plugins=["core", "legacy"])

# Build navigation sections
from aiml_dash.plugins.registry import build_navigation_sections
sections = build_navigation_sections(pages)
```

### Plugin Model (`models.py`)

Defines the plugin structure and data models.

```python
from aiml_dash.plugins.models import Plugin, PluginPage

# Create a plugin
plugin = Plugin(
    id="my_plugin",
    name="My Plugin",
    description="Description",
    version="1.0.0",
    pages=[...],
    locked=False,
    default_enabled=True
)
```

## Available Plugins

### Core Plugin

The main application features including home page and core functionality.

**Location:** `aiml_dash/plugins/core/`

### Legacy Plugin

Support for legacy features and backward compatibility.

**Location:** `aiml_dash/plugins/legacy/`

### Example Plugin

Template and example for creating new plugins.

**Location:** `aiml_dash/plugins/example_plugin/`

### Template Plugin

Starter template for new plugin development.

**Location:** `aiml_dash/plugins/template_plugin/`

## Creating a New Plugin

1. **Create Plugin Directory Structure:**

```
aiml_dash/plugins/my_plugin/
├── __init__.py
├── layout.py
├── callbacks.py
├── components.py
└── styles.py
```

2. **Define Plugin in `__init__.py`:**

```python
from aiml_dash.plugins.models import Plugin, PluginPage

def get_plugin() -> Plugin:
    return Plugin(
        id="my_plugin",
        name="My Plugin",
        description="Plugin description",
        version="1.0.0",
        pages=[
            PluginPage(
                id="my_page",
                path="/my-page",
                name="My Page",
                section="Plugins",
                order=1
            )
        ],
        locked=False,
        default_enabled=False
    )
```

3. **Create Layout in `layout.py`:**

```python
from dash import html

def create_layout():
    return html.Div([
        html.H1("My Plugin Page"),
        html.P("Plugin content")
    ])
```

4. **Register Callbacks in `callbacks.py`:**

```python
from dash import Input, Output

def register_callbacks(app):
    @app.callback(
        Output("output-id", "children"),
        Input("input-id", "value")
    )
    def update_output(value):
        return f"Input: {value}"
```

5. **Register Plugin in `registry.py`:**

```python
from aiml_dash.plugins import my_plugin

def get_plugins() -> Sequence[Plugin]:
    return [
        core.get_plugin(),
        legacy.get_plugin(),
        my_plugin.get_plugin(),  # Add your plugin
        # ...
    ]
```

## Controller/View Separation

Plugins should follow MVC patterns:

- **Controllers** (`callbacks.py`): Handle business logic and data processing
- **Views** (`layout.py`, `components.py`): Handle UI rendering
- **Models** (separate files): Define data structures

**Example:**

```python
# controllers/data_controller.py
def process_data(raw_data):
    # Business logic
    return processed_data

# views/data_view.py
def create_data_display(data):
    # UI rendering
    return html.Div([...])

# callbacks.py
from .controllers.data_controller import process_data
from .views.data_view import create_data_display

def register_callbacks(app):
    @app.callback(...)
    def update_view(input_data):
        processed = process_data(input_data)
        return create_data_display(processed)
```

## Testing Plugins

Create tests in `tests/plugins/`:

```bash
pytest tests/plugins/test_my_plugin.py
```

## Best Practices

1. **Keep plugins independent**: Minimize dependencies between plugins
2. **Use clear naming**: Follow consistent naming conventions
3. **Document thoroughly**: Include docstrings and usage examples
4. **Test comprehensively**: Test all plugin functionality
5. **Follow separation of concerns**: Keep controllers, views, and models separate
6. **Version your plugins**: Use semantic versioning
7. **Handle errors gracefully**: Provide user-friendly error messages
