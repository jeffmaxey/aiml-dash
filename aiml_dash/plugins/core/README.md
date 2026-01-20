# Core Plugin - Controller/View Architecture

This plugin follows a Model-View-Controller (MVC) pattern for clean separation of concerns.

## Directory Structure

```
core/
├── __init__.py           # Plugin definition and registration
├── callbacks.py          # Dash callbacks (Controller coordination)
├── components.py         # Reusable UI components
├── layout.py             # Page layouts (View)
├── styles.py             # CSS styles and constants
├── controllers/          # Business logic layer
│   ├── __init__.py
│   └── plugin_controller.py  # Plugin management logic
└── views/                # Presentation layer
    ├── __init__.py
    └── plugin_view.py    # UI rendering functions
```

## Architecture Pattern

### Controllers (Business Logic)

Controllers contain pure business logic with no UI dependencies:

```python
# controllers/plugin_controller.py
def get_locked_plugins(metadata):
    """Pure function that processes data."""
    # Business logic only
    return locked_plugins
```

**Responsibilities:**
- Data validation and processing
- Business rule enforcement
- State management
- Data transformation

**Guidelines:**
- No UI component imports
- Return data structures, not UI components
- Pure functions when possible
- Comprehensive error handling

### Views (Presentation)

Views handle UI rendering and visual representation:

```python
# views/plugin_view.py
def render_plugin_toggles(metadata, enabled_plugins):
    """Create UI components from data."""
    # Render components
    return [component1, component2, ...]
```

**Responsibilities:**
- UI component creation
- Visual formatting
- Layout composition
- User feedback messages

**Guidelines:**
- Import and use Dash components
- Accept processed data from controllers
- Return UI components
- Keep logic minimal (only UI-related)

### Callbacks (Coordination)

Callbacks coordinate between controllers and views:

```python
# callbacks.py
from .controllers import get_locked_plugins
from .views import render_plugin_toggles

@callback(...)
def update_view(input_data):
    # 1. Use controller to process data
    processed_data = get_locked_plugins(input_data)
    
    # 2. Use view to render UI
    return render_plugin_toggles(processed_data)
```

**Responsibilities:**
- Connect Dash inputs to outputs
- Coordinate between controllers and views
- Handle Dash-specific logic
- Manage callback state

## Example Workflow

1. **User Action**: User clicks a toggle
2. **Callback Triggered**: `update_enabled_plugins` callback fires
3. **Controller Processing**: `get_locked_plugins` validates and processes the data
4. **View Rendering**: `render_plugin_toggles` creates the updated UI
5. **UI Update**: Dash updates the interface

## Benefits

1. **Testability**: Business logic can be tested without UI
2. **Reusability**: Controllers can be used by multiple views
3. **Maintainability**: Clear separation makes changes easier
4. **Scalability**: Easy to add new features
5. **Clarity**: Each layer has a single responsibility

## Testing Strategy

### Controller Tests
```python
def test_get_locked_plugins():
    metadata = [{"id": "core", "locked": True}]
    result = get_locked_plugins(metadata)
    assert "core" in result
```

### View Tests
```python
def test_render_plugin_toggles():
    result = render_plugin_toggles([], [])
    assert isinstance(result, dmc.Alert)
```

### Integration Tests
```python
def test_callback_integration():
    # Test full callback workflow
    pass
```

## Migration Guide

To refactor existing code:

1. **Identify Business Logic**: Find data processing code
2. **Extract to Controller**: Move to `controllers/`
3. **Identify UI Code**: Find component creation
4. **Extract to View**: Move to `views/`
5. **Update Callbacks**: Import from new modules
6. **Add Tests**: Test controllers and views separately
7. **Document**: Update docstrings

## Best Practices

1. **Keep Controllers Pure**: No side effects when possible
2. **Views Only Render**: Minimal logic in views
3. **Single Responsibility**: Each function does one thing
4. **Type Hints**: Use type hints for clarity
5. **Documentation**: Clear docstrings for all functions
6. **Error Handling**: Handle errors appropriately in each layer
7. **Naming**: Use clear, descriptive names

## Future Improvements

- Add data models/schemas for type safety
- Implement dependency injection
- Add caching layer for performance
- Create base controller/view classes
- Add validation layer
