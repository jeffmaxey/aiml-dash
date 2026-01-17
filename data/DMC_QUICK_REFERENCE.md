# Dash Mantine Components Quick Reference

## Common Conversions from Bootstrap to Mantine

### Layout Components

```python
# Bootstrap
dbc.Container(fluid=True)
# Mantine
dmc.Container(fluid=True)  # Same prop name!

# Bootstrap
dbc.Row(className="g-3")
# Mantine
dmc.Grid(gutter="md")

# Bootstrap
dbc.Col(width=6)
# Mantine
dmc.GridCol(span=6)
```

### Cards

```python
# Bootstrap
dbc.Card([
    dbc.CardHeader("Title"),
    dbc.CardBody([...])
])

# Mantine
dmc.Card([
    dmc.Text("Title", fw=700, size="lg"),
    dmc.Stack([...], gap="sm")
])
```

### Forms

```python
# Bootstrap
dbc.Label("Field")
dbc.Input(id="field")

# Mantine
dmc.Text("Field", size="sm", fw=500)
dmc.TextInput(id="field")
```

### Buttons

```python
# Bootstrap
dbc.Button("Click", color="primary", size="md")

# Mantine
dmc.Button("Click", color="blue", size="md")
```

### Switches

```python
# Bootstrap
dbc.Switch(id="sw", value=False, label="Toggle")

# Mantine
dmc.Switch(id="sw", checked=False, label="Toggle")
```

### Tabs

```python
# Bootstrap (dcc)
dcc.Tabs([
    dcc.Tab(label="Tab 1", value="tab-1", children=[...]),
    dcc.Tab(label="Tab 2", value="tab-2", children=[...])
], value="tab-1")

# Mantine
dmc.Tabs([
    dmc.TabsList([
        dmc.TabsTab("Tab 1", value="tab-1"),
        dmc.TabsTab("Tab 2", value="tab-2"),
    ]),
    dmc.TabsPanel([...], value="tab-1"),
    dmc.TabsPanel([...], value="tab-2"),
], value="tab-1")
```

## Spacing Props

### Mantine Spacing Scale
- `xs` = 10px
- `sm` = 12px
- `md` = 16px
- `lg` = 20px
- `xl` = 32px

### Common Props
```python
# Margin
mt="md"    # margin-top
mb="lg"    # margin-bottom
ml="sm"    # margin-left
mr="xs"    # margin-right
m="md"     # all margins

# Padding
pt="md"    # padding-top
pb="lg"    # padding-bottom
pl="sm"    # padding-left
pr="xs"    # padding-right
p="md"     # all padding

# Gap (for Stack/Group)
gap="sm"   # space between children
```

## Text Styling

```python
# Font weight
fw=400     # normal
fw=500     # medium
fw=700     # bold

# Text size
size="xs"  # extra small
size="sm"  # small
size="md"  # medium (default)
size="lg"  # large
size="xl"  # extra large

# Text align
ta="left"
ta="center"
ta="right"

# Color
c="blue"
c="red"
c="gray"
```

## Common Patterns

### Centered Content
```python
# Bootstrap
html.Div(className="d-flex justify-content-center")

# Mantine
dmc.Center([...])
# or
dmc.Group([...], justify="center")
```

### Vertical Stack
```python
# Bootstrap
html.Div([child1, child2], className="d-flex flex-column")

# Mantine
dmc.Stack([child1, child2], gap="md")
```

### Horizontal Group
```python
# Bootstrap
html.Div([item1, item2], className="d-flex")

# Mantine
dmc.Group([item1, item2], gap="sm")
```

### Card with Shadow
```python
# Bootstrap
dbc.Card(style={"box-shadow": "1px 2px 7px 0px grey"})

# Mantine
dmc.Card(shadow="sm", withBorder=True)
```

## Grid System

Both use 12-column grid:

```python
# Bootstrap
dbc.Row([
    dbc.Col([...], width=4),   # 4/12 = 33%
    dbc.Col([...], width=8),   # 8/12 = 67%
])

# Mantine
dmc.Grid([
    dmc.GridCol([...], span=4),  # 4/12 = 33%
    dmc.GridCol([...], span=8),  # 8/12 = 67%
])
```

## Color Names

Bootstrap → Mantine:
- `primary` → `blue`
- `secondary` → `gray`
- `success` → `green`
- `danger` → `red`
- `warning` → `yellow`
- `info` → `cyan`

## Key Differences

1. **No CardHeader/CardBody**: Mantine cards have flat children
2. **checked vs value**: Switches use `checked` instead of `value`
3. **span vs width**: Grid columns use `span` instead of `width`
4. **Built-in props**: Mantine has props like `withBorder`, `shadow`, `radius`
5. **Size tokens**: Use 'xs', 'sm', 'md' instead of pixel values
6. **Tabs structure**: More explicit with TabsList, TabsTab, TabsPanel

## Tips

1. **Use Stack liberally** - It's great for vertical layouts
2. **Group for horizontal** - Replaces d-flex with better control
3. **Grid for complex layouts** - Full responsive control
4. **Props over className** - Use built-in props when possible
5. **Consistent spacing** - Stick to the size scale (xs, sm, md, lg, xl)
