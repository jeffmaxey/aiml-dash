# Components Module

The `aiml_dash.components` module contains reusable UI components for the Dash application.

## Overview

This module provides custom components that extend Dash's functionality and provide consistent UI patterns across the application.

## Components

### Common Components (`common.py`)

Shared UI components used throughout the application.

**Example:**
```python
from aiml_dash.components.common import create_header, create_footer

# Create standardized header
header = create_header(title="My Page")

# Create footer
footer = create_footer()
```

### ACE Editor (`ace_editor.py`)

Code editor component based on ACE editor.

**Example:**
```python
from aiml_dash.components.ace_editor import create_ace_editor

# Create code editor
editor = create_ace_editor(
    id="code-editor",
    language="python",
    theme="monokai"
)
```

### Shell Component (`shell.py`)

Terminal/shell component for interactive command execution.

**Example:**
```python
from aiml_dash.components.shell import create_shell

# Create shell component
shell = create_shell(id="terminal")
```

## Creating New Components

When creating new reusable components:

1. **Design for Reusability**: Make components configurable and generic
2. **Document Parameters**: Include clear docstrings for all parameters
3. **Type Hints**: Use type hints for better IDE support
4. **Consistent Styling**: Follow the application's design system
5. **Test Thoroughly**: Add tests in `tests/components/`

### Component Template

```python
from dash import html, dcc
from typing import Any

def create_my_component(
    id: str,
    data: Any,
    title: str = "Default Title",
    **kwargs
) -> html.Div:
    """
    Create a custom component.
    
    Args:
        id: Unique identifier for the component
        data: Data to display
        title: Component title
        **kwargs: Additional properties
        
    Returns:
        Dash component
    """
    return html.Div(
        [
            html.H3(title),
            dcc.Graph(id=id, figure=data)
        ],
        **kwargs
    )
```

## Testing

Test your components in `tests/components/`:

```bash
pytest tests/components/
```

## Best Practices

1. **Keep components pure**: Minimize side effects
2. **Use callbacks wisely**: Separate component creation from callback logic
3. **Document thoroughly**: Include usage examples in docstrings
4. **Style consistently**: Use the application's CSS classes and theme
5. **Handle errors gracefully**: Validate inputs and provide fallbacks
