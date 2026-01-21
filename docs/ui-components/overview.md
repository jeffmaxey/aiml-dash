# UI Components Overview

AIML Dash uses [dash-mantine-components](https://www.dash-mantine-components.com/) (DMC) as its primary UI component library, providing a modern, professional interface with over 120 customizable components.

## Why Dash Mantine Components?

### Key Advantages

- **Modern Design System**: Consistent, professional look and feel
- **Rich Component Library**: Everything from basic buttons to complex data tables
- **Theme Customization**: Extensive theming with full dark mode support
- **Responsive Layout**: Mobile-first design with built-in breakpoints
- **AppShell Pattern**: Complete application shell structure
- **Accessibility**: Built with WCAG standards in mind
- **Active Development**: Regular updates and excellent documentation
- **TypeScript Support**: Full type definitions for better development

## Component Categories

### Layout Components

Used for page structure and organization:

- **Container**: Max-width containers with responsive sizing
- **Stack**: Vertical layout with consistent spacing
- **Group**: Horizontal layout with flexible alignment
- **Grid**: Responsive grid system
- **SimpleGrid**: Equal-width grid columns
- **Card**: Bordered containers for grouping content
- **Paper**: Surface with shadow and background
- **Center**: Centering content horizontally and vertically
- **Space**: Flexible spacing element

### Navigation Components

For app navigation and menus:

- **AppShell**: Complete application shell with header, navbar, aside, footer
- **Accordion**: Collapsible sections
- **NavLink**: Navigation links with icons and active states
- **Tabs**: Tabbed interfaces
- **Menu**: Dropdown menus
- **Breadcrumbs**: Hierarchical navigation

### Form Components

For user input:

- **TextInput**: Single-line text input
- **Textarea**: Multi-line text input
- **Select**: Dropdown selector
- **MultiSelect**: Multiple selection dropdown
- **NumberInput**: Numeric input with increment/decrement
- **Checkbox**: Single checkbox
- **CheckboxGroup**: Multiple checkboxes
- **Radio**: Radio button group
- **Switch**: Toggle switch
- **Slider**: Range slider
- **DatePicker**: Date selection
- **ColorPicker**: Color selection
- **FileInput**: File upload

### Display Components

For showing information:

- **Text**: Typography with size, weight, color options
- **Title**: Heading components (h1-h6)
- **Badge**: Status indicators
- **Code**: Code display with syntax highlighting
- **Alert**: Notification messages
- **Table**: Simple data tables
- **List**: Ordered and unordered lists
- **Timeline**: Timeline/stepper component
- **Avatar**: User avatars
- **Image**: Responsive images

### Action Components

For user interactions:

- **Button**: Action buttons with variants
- **ActionIcon**: Icon-only buttons
- **CloseButton**: Close/dismiss button
- **CopyButton**: Copy to clipboard
- **FileButton**: File upload trigger

### Feedback Components

For user feedback:

- **Modal**: Dialog windows
- **Drawer**: Side panel
- **Notification**: Toast notifications
- **LoadingOverlay**: Loading indicators
- **Progress**: Progress bars
- **Skeleton**: Loading placeholders
- **Tooltip**: Hover tooltips
- **Popover**: Popup content

### Data Display

For displaying data:

- **Table**: Simple data tables
- **JsonInput**: JSON editor
- **Prism**: Code highlighting
- **Highlight**: Text highlighting

## Theme System

### Default Theme

AIML Dash uses a custom theme configuration:

```python
{
    "fontFamily": "'Inter', sans-serif",
    "primaryColor": "blue",
    "components": {
        "Button": {"defaultProps": {"fw": 400}},
        "Alert": {"styles": {"title": {"fontWeight": 500}}},
    },
}
```

### Color Palette

Available color schemes:

- **blue** (primary)
- **red**
- **pink**
- **grape**
- **violet**
- **indigo**
- **cyan**
- **teal**
- **green**
- **lime**
- **yellow**
- **orange**

### Dark Mode

Full support for light and dark themes:

- Automatic theme detection based on system preferences
- Manual toggle via theme switch in header
- Persists user preference in local storage
- All components adapt automatically

## Responsive Design

### Breakpoints

DMC uses standard breakpoints:

- **xs**: 576px - Mobile
- **sm**: 768px - Tablet
- **md**: 992px - Desktop
- **lg**: 1200px - Large desktop
- **xl**: 1400px - Extra large desktop

### Responsive Utilities

```python
# Hide on mobile
dmc.Box(display={"base": "none", "sm": "block"})

# Responsive widths
dmc.Container(size={"base": "xs", "md": "md", "lg": "lg"})

# Responsive grid
dmc.SimpleGrid(cols={"base": 1, "sm": 2, "md": 3})
```

## Component Composition

### Example: Form with Validation

```python
import dash_mantine_components as dmc
from dash import callback, Input, Output

def create_form():
    return dmc.Stack([
        dmc.TextInput(
            id="name-input",
            label="Name",
            placeholder="Enter your name",
            required=True,
            error="",
        ),
        dmc.Select(
            id="role-select",
            label="Role",
            data=[
                {"label": "Admin", "value": "admin"},
                {"label": "User", "value": "user"},
            ],
            required=True,
        ),
        dmc.Button(
            "Submit",
            id="submit-button",
            fullWidth=True,
        ),
    ], gap="md")

@callback(
    Output("name-input", "error"),
    Input("submit-button", "n_clicks"),
    Input("name-input", "value"),
    prevent_initial_call=True,
)
def validate_name(n_clicks, value):
    if not value or len(value) < 3:
        return "Name must be at least 3 characters"
    return ""
```

### Example: Data Card

```python
def create_data_card(title, value, icon, color):
    return dmc.Card([
        dmc.Group([
            dmc.ThemeIcon(
                DashIconify(icon=icon, width=20),
                size="lg",
                radius="md",
                variant="light",
                color=color,
            ),
            dmc.Stack([
                dmc.Text(title, size="sm", c="dimmed"),
                dmc.Text(value, size="xl", fw=700),
            ], gap=0),
        ]),
    ], withBorder=True, radius="md", p="md")
```

## Integration with Dash

### Dash Core Components

DMC works alongside standard Dash components:

```python
from dash import dcc, html
import dash_mantine_components as dmc

layout = dmc.Container([
    # DMC components
    dmc.Title("My App"),
    
    # Dash Core Components
    dcc.Store(id="data-store"),
    dcc.Location(id="url"),
    dcc.Download(id="download"),
    
    # Plotly graphs
    dcc.Graph(id="my-graph"),
])
```

### AG Grid Integration

For high-performance data tables:

```python
import dash_ag_grid as dag

dmc.Card([
    dmc.Title("Data Table", order=3),
    dag.AgGrid(
        id="data-table",
        columnDefs=[...],
        rowData=[...],
        dashGridOptions={"pagination": True},
    ),
])
```

## Styling

### Inline Styles

```python
dmc.Text(
    "Styled text",
    c="blue",        # color
    fw=700,          # font weight
    fs="italic",     # font style
    td="underline",  # text decoration
    ta="center",     # text align
)
```

### System Props

```python
dmc.Box(
    p="md",     # padding
    m="lg",     # margin
    bg="blue",  # background
    c="white",  # color
)
```

### Custom Styles

```python
dmc.Box(
    style={
        "border": "1px solid #ccc",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    }
)
```

## Best Practices

1. **Use Semantic Components**: Choose components based on their semantic meaning
2. **Consistent Spacing**: Use the spacing scale (`xs`, `sm`, `md`, `lg`, `xl`)
3. **Responsive by Default**: Test on multiple screen sizes
4. **Accessible**: Use proper labels, ARIA attributes, and keyboard navigation
5. **Theme-Aware**: Avoid hardcoded colors, use theme colors
6. **Composition**: Build complex UIs from simple components
7. **Performance**: Use `prevent_initial_call` and memoization for callbacks

## Next Steps

- [Layout System](layout-system.md) - Detailed layout guide
- [Common Components](common-components.md) - Component examples
- [Theming](theming.md) - Customizing the theme
- [Plugin Development](../plugin-development/overview.md) - Build custom pages

## Resources

- [DMC Documentation](https://www.dash-mantine-components.com/)
- [Mantine UI](https://mantine.dev/) - Original React library
- [Iconify](https://iconify.design/) - Icon library
