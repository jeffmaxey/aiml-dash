# Plugin Development Guide

## Overview

AIML Dash uses a dynamic plugin framework that allows you to extend the application with new pages and functionality. Plugins are self-contained modules that follow a standardized structure, making them easy to develop, test, and maintain.

## Plugin Structure

Each plugin must follow this directory structure:

```
plugins/
└── your_plugin/
    ├── __init__.py       # Plugin registration and metadata
    ├── layout.py         # Page layout definitions
    ├── components.py     # Reusable UI components
    ├── callbacks.py      # Dash callbacks for interactivity
    ├── styles.py         # Style constants and configuration
    └── constants.py      # Plugin-specific constants
```

### Required Files

#### 1. `constants.py`
Define all plugin-specific constants here:

```python
"""Constants for the your_plugin plugin."""

# Page identifiers
YOUR_PAGE_ID = "your_page"

# Plugin metadata
PLUGIN_ID = "your_plugin"
PLUGIN_NAME = "Your Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Description of what your plugin does."

# Section and ordering
SECTION_NAME = "Plugins"  # or "Core", "Data", "Basics", etc.
GROUP_NAME = "Your Plugin Group"  # Optional grouping
PAGE_ORDER = 1
GROUP_ORDER = 1

# Icons (using Iconify)
YOUR_ICON = "carbon:app"

# Layout configuration
CONTAINER_SIZE = "md"  # "xs", "sm", "md", "lg", "xl"
```

#### 2. `styles.py`
Define style constants and configuration:

```python
"""Styles for the your_plugin plugin."""

from your_plugin.constants import CONTAINER_SIZE

# Layout configuration
YOUR_CONTAINER_SIZE = CONTAINER_SIZE

# Additional style constants
CARD_PADDING = "md"
GRID_SPACING = "lg"
```

#### 3. `components.py`
Create reusable UI components:

```python
"""Reusable components for the your_plugin plugin."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_info_card(title: str, content: str, icon: str) -> dmc.Card:
    """Create an information card.
    
    Args:
        title: The card title.
        content: The card content.
        icon: The Iconify icon identifier.
        
    Returns:
        dmc.Card: A styled card component.
    """
    return dmc.Card(
        [
            dmc.Group([
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=20),
                    radius="xl",
                    variant="light"
                ),
                dmc.Text(title, fw=600),
            ]),
            dmc.Text(content, size="sm", c="dimmed", mt="xs"),
        ],
        withBorder=True,
        radius="md",
        p="md",
    )
```

#### 4. `layout.py`
Define the page layout:

```python
"""Layout for the your_plugin page."""

import dash_mantine_components as dmc

from your_plugin.components import create_info_card
from your_plugin.styles import YOUR_CONTAINER_SIZE


def your_page_layout() -> dmc.Container:
    """Create the your_plugin page layout.
    
    Returns:
        dmc.Container: The page layout container.
    """
    return dmc.Container(
        dmc.Stack(
            [
                dmc.Title("Your Plugin", order=2),
                dmc.Text("Plugin description goes here.", c="dimmed"),
                dmc.SimpleGrid(
                    [
                        create_info_card(
                            "Feature 1",
                            "Description of feature 1",
                            "carbon:checkmark"
                        ),
                        create_info_card(
                            "Feature 2", 
                            "Description of feature 2",
                            "carbon:star"
                        ),
                    ],
                    cols=2,
                    spacing="md",
                ),
            ],
            gap="md",
        ),
        size=YOUR_CONTAINER_SIZE,
        py="xl",
    )
```

#### 5. `callbacks.py`
Register Dash callbacks (optional):

```python
"""Callback registration for the your_plugin plugin."""

from dash import Input, Output, callback


def register_callbacks(app: object) -> None:
    """Register callbacks for the your_plugin plugin.
    
    Args:
        app: The Dash application instance.
    """
    # Example callback (remove if not needed)
    @callback(
        Output("your-output-id", "children"),
        Input("your-input-id", "value"),
    )
    def update_output(value):
        """Update output based on input."""
        return f"You entered: {value}"
```

#### 6. `__init__.py`
Register the plugin:

```python
"""Your plugin definition."""

from your_plugin import callbacks
from your_plugin.constants import (
    GROUP_NAME,
    GROUP_ORDER,
    PAGE_ORDER,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SECTION_NAME,
    YOUR_ICON,
    YOUR_PAGE_ID,
)
from your_plugin.layout import your_page_layout
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the your_plugin definition.
    
    Returns:
        Plugin: The plugin configuration and metadata.
    """
    pages = [
        PluginPage(
            id=YOUR_PAGE_ID,
            label="Your Page",
            icon=YOUR_ICON,
            section=SECTION_NAME,
            group=GROUP_NAME,
            order=PAGE_ORDER,
            group_order=GROUP_ORDER,
            layout=your_page_layout,
            description="Your page description",
        )
    ]
    
    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=True,  # Set to False to disable by default
        locked=False,  # Set to True to prevent disabling
        register_callbacks=callbacks.register_callbacks,
    )
```

## Creating a New Plugin

### Quick Start

1. **Copy the template plugin**:
   ```bash
   cp -r aiml_dash/plugins/template_plugin aiml_dash/plugins/your_plugin
   ```

2. **Update constants.py** with your plugin's metadata

3. **Modify layout.py** to define your page structure

4. **Add components** to components.py as needed

5. **Implement callbacks** in callbacks.py if interactivity is required

6. **Update styles.py** with any custom styling

7. **Register the plugin** in __init__.py

### Testing Your Plugin

#### Run Standalone
Test your plugin independently:

```bash
python -m aiml_dash.plugins.standalone your_plugin
```

This creates a minimal app with just your plugin's page.

#### Run with Main App
The plugin will be automatically discovered if placed in the plugins directory.

### Best Practices

1. **Documentation**: Add comprehensive docstrings to all functions and classes
2. **Type Hints**: Use type hints for better code clarity
3. **Constants**: Use constants instead of hardcoded values
4. **Reusability**: Extract common UI patterns into components
5. **Independence**: Ensure your plugin doesn't depend on other plugins
6. **Testing**: Write tests for your plugin's functionality

## Dynamic Plugin Loading

Plugins can be loaded dynamically at runtime. The framework will:

1. Scan the `plugins/` directory
2. Import modules with valid structure
3. Register plugins with the main application
4. Make pages available based on enabled state

### Plugin Discovery

The loader looks for directories with:
- An `__init__.py` file
- A `get_plugin()` function that returns a `Plugin` object
- Required module files (layout.py, components.py, etc.)

## Plugin Configuration

### Sections

Available navigation sections (in order):
- Core
- Data
- Basics
- Design
- Model
- Multivariate
- Plugins

### Icons

Use [Iconify](https://icon-sets.iconify.design/) icons with the `carbon` prefix:
- `carbon:home`
- `carbon:data-base`
- `carbon:chart-line`
- `carbon:app`

### Locked vs Unlocked

- **Locked plugins** (e.g., core): Cannot be disabled by users
- **Unlocked plugins**: Can be enabled/disabled through settings

## Example: Complete Plugin

See the `example_plugin` or `template_plugin` directories for complete, working examples that demonstrate:
- Proper file organization
- Documentation standards
- Component creation
- Layout structure
- Callback registration (if needed)

## Troubleshooting

### Plugin not appearing
- Verify `__init__.py` has a `get_plugin()` function
- Check that all required files exist
- Ensure plugin ID is unique
- Check console for import errors

### Callbacks not working
- Verify `register_callbacks()` is defined
- Check that IDs match between layout and callbacks
- Ensure callbacks are registered in plugin definition

### Layout issues
- Verify imports from `dash_mantine_components`
- Check that layout function returns a valid component
- Ensure component IDs are unique across the application

## Advanced Topics

### Multiple Pages per Plugin

A plugin can provide multiple pages:

```python
pages = [
    PluginPage(
        id="page1",
        label="Page 1",
        # ...
    ),
    PluginPage(
        id="page2",
        label="Page 2",
        # ...
    ),
]
```

### Grouped Pages

Group related pages within a section:

```python
PluginPage(
    id="analysis1",
    label="Analysis 1",
    section="Model",
    group="My Analysis Tools",
    group_order=1,
    order=1,
    # ...
)
```

### Custom Callbacks

For complex interactivity, use Dash callbacks:

```python
@callback(
    Output("output-id", "children"),
    Input("input-id", "value"),
    State("state-id", "data"),
)
def my_callback(input_value, state_data):
    # Process and return result
    return result
```

## Resources

- [Dash Documentation](https://dash.plotly.com/)
- [Dash Mantine Components](https://www.dash-mantine-components.com/)
- [Iconify Icons](https://icon-sets.iconify.design/)
- [AIML Dash Repository](https://github.com/jeffmaxey/aiml-dash)
