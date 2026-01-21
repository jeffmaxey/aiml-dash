# Plugin Development Overview

AIML Dash features a powerful plugin framework that allows you to extend the application with new pages, features, and functionality. This guide provides an overview of the plugin system and how to get started with plugin development.

## What is a Plugin?

A plugin in AIML Dash is a self-contained module that adds one or more pages to the application. Plugins follow a standardized structure that makes them easy to develop, test, and maintain.

### Key Benefits

- **Modular Architecture**: Plugins are independent and don't interfere with each other
- **Dynamic Discovery**: Plugins are automatically discovered at runtime
- **Hot Reload**: Changes to plugins are immediately reflected (in debug mode)
- **Enable/Disable**: Users can enable or disable plugins through the settings page
- **Standalone Testing**: Plugins can be tested independently of the main application
- **Type Safety**: Full type hints throughout for better IDE support

## Plugin Architecture

### Plugin Structure

Each plugin follows this directory structure:

```
plugins/
└── your_plugin/
    ├── __init__.py       # Plugin registration
    ├── constants.py      # Plugin metadata and constants
    ├── styles.py         # Style constants
    ├── components.py     # Reusable UI components
    ├── layout.py         # Page layouts
    └── callbacks.py      # Dash callbacks (optional)
```

### Plugin Lifecycle

1. **Discovery**: Plugins are discovered from the `plugins/` directory
2. **Registration**: Plugin metadata is registered with the plugin registry
3. **Initialization**: Plugin pages are added to the Dash app
4. **Callback Registration**: Plugin callbacks are registered
5. **Runtime**: Plugin can be enabled/disabled through settings

## Quick Start

### 1. Create from Template

The fastest way to create a new plugin is to copy the template:

```bash
cp -r aiml_dash/plugins/template_plugin aiml_dash/plugins/my_plugin
```

### 2. Update Constants

Edit `my_plugin/constants.py`:

```python
"""Constants for my_plugin."""

# Page identifiers
MY_PAGE_ID = "my_page"

# Plugin metadata
PLUGIN_ID = "my_plugin"
PLUGIN_NAME = "My Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Description of what my plugin does."

# Navigation
SECTION_NAME = "Custom"  # Sidebar section
GROUP_NAME = "My Plugin"  # Group within section
PAGE_ORDER = 1           # Order within group
GROUP_ORDER = 1          # Order of group

# Icons (from Iconify)
MY_ICON = "carbon:app"
```

### 3. Create Layout

Edit `my_plugin/layout.py`:

```python
"""Layout for my_plugin."""

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from my_plugin.constants import MY_PAGE_ID, MY_ICON


def layout() -> html.Div:
    """Create the layout for my page."""
    return dmc.Container(
        [
            dmc.Stack(
                [
                    # Page header
                    dmc.Group(
                        [
                            DashIconify(icon=MY_ICON, width=30),
                            dmc.Title("My Page", order=2),
                        ],
                        gap="sm",
                    ),
                    
                    # Page content
                    dmc.Card(
                        [
                            dmc.Text("Welcome to my plugin!"),
                            dmc.Button(
                                "Click Me",
                                id=f"{MY_PAGE_ID}-button",
                                leftSection=DashIconify(icon="carbon:play"),
                            ),
                        ],
                        withBorder=True,
                        p="md",
                    ),
                ],
                gap="md",
            )
        ],
        size="md",
        mt="md",
    )
```

### 4. Register Plugin

Edit `my_plugin/__init__.py`:

```python
"""My Plugin."""

from aiml_dash.plugins.models import Page

from .constants import (
    GROUP_NAME,
    GROUP_ORDER,
    MY_ICON,
    MY_PAGE_ID,
    PAGE_ORDER,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SECTION_NAME,
)
from .layout import layout

# Define pages
PAGES = [
    Page(
        page_id=MY_PAGE_ID,
        name="My Page",
        path=f"/{MY_PAGE_ID}",
        layout=layout,
        icon=MY_ICON,
        section=SECTION_NAME,
        group=GROUP_NAME,
        order=PAGE_ORDER,
        group_order=GROUP_ORDER,
    )
]

# Plugin metadata
__plugin_id__ = PLUGIN_ID
__plugin_name__ = PLUGIN_NAME
__version__ = PLUGIN_VERSION
__description__ = PLUGIN_DESCRIPTION
__pages__ = PAGES
```

### 5. Test Standalone

Test your plugin independently:

```bash
python -m aiml_dash.plugins.standalone my_plugin
```

This starts a minimal Dash app with only your plugin loaded.

### 6. Enable in Main App

Your plugin will be automatically discovered. Enable it through the Settings page or add it to the default enabled plugins in `plugins/registry.py`.

## Plugin Categories

### Core Plugins
- **Locked**: Cannot be disabled
- **Essential functionality**: Home, Settings, Help
- **Section**: "Core"

### Data Plugins
- **Data management**: Import, export, transform
- **Section**: "Data"
- **Examples**: Data View, Data Explorer, Data Transform

### Analysis Plugins
- **Statistical analysis**: Hypothesis testing, correlation
- **Section**: "Basics" or "Multivariate"
- **Examples**: t-tests, ANOVA, PCA

### Model Plugins
- **Machine learning**: Regression, classification, clustering
- **Section**: "Model"
- **Examples**: Linear Regression, Decision Trees

### Design Plugins
- **Experimental design**: Sample size, randomization
- **Section**: "Design"
- **Examples**: DOE, Sample Size Calculator

## Plugin Features

### Multiple Pages

A plugin can provide multiple pages:

```python
PAGES = [
    Page(
        page_id="my_page_1",
        name="Page 1",
        path="/my_page_1",
        layout=layout_1,
        icon="carbon:app",
        section="Custom",
        group="My Plugin",
        order=1,
    ),
    Page(
        page_id="my_page_2",
        name="Page 2",
        path="/my_page_2",
        layout=layout_2,
        icon="carbon:document",
        section="Custom",
        group="My Plugin",
        order=2,
    ),
]
```

### Callbacks

Add interactivity with callbacks in `callbacks.py`:

```python
"""Callbacks for my_plugin."""

from dash import Input, Output, callback

from my_plugin.constants import MY_PAGE_ID


@callback(
    Output(f"{MY_PAGE_ID}-output", "children"),
    Input(f"{MY_PAGE_ID}-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_button_click(n_clicks):
    """Handle button click."""
    return f"Button clicked {n_clicks} times!"
```

### Data Access

Access shared data through the DataManager:

```python
from utils.data_manager import data_manager

# Get active dataset
df = data_manager.get_active_data()

# Get specific dataset
df = data_manager.get_data("my_dataset")

# Add new dataset
data_manager.add_data("new_dataset", df, "New Dataset")
```

## Best Practices

1. **Use Type Hints**: Add type hints to all functions
2. **Document Everything**: Use docstrings for modules, classes, and functions
3. **Follow Naming Conventions**: Use consistent naming for IDs and variables
4. **Test Thoroughly**: Test both standalone and integrated
5. **Handle Errors**: Provide user-friendly error messages
6. **Be Responsive**: Use DMC's responsive features
7. **Support Dark Mode**: Test in both light and dark themes

## Next Steps

- [Plugin Structure](structure.md) - Detailed structure explanation
- [Creating Plugins](creating-plugins.md) - Step-by-step guide
- [Components & Layouts](components-layouts.md) - UI development
- [Callbacks](callbacks.md) - Adding interactivity
- [Testing](testing.md) - Testing strategies
- [Best Practices](best-practices.md) - Advanced patterns

## Examples

### Minimal Plugin

See `plugins/example_plugin/` for a minimal working example.

### Complete Plugin

See `plugins/data_plugin/` for a full-featured plugin with multiple pages and callbacks.

### Template

Use `plugins/template_plugin/` as a starting point for new plugins.
