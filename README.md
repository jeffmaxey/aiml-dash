# aiml-dash

[![Release](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jeffmaxey/aiml-dash/main.yml?branch=main)](https://github.com/jeffmaxey/aiml-dash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jeffmaxey/aiml-dash/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffmaxey/aiml-dash)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)
[![License](https://img.shields.io/github/license/jeffmaxey/aiml-dash)](https://img.shields.io/github/license/jeffmaxey/aiml-dash)

A Dash application for Predictive Analytics and Machine Learning.

## Overview
`aiml_dash` is a Dash application designed to provide interactive insights into predictive analytics and machine learning. 
This application serves as a platform for users to explore and visualize datasets, perform machine learning experiments 
and develop insights through an intuitive web interface.

- **Github repository**: <https://github.com/jeffmaxey/aiml-dash/>
- **Documentation** <https://jeffmaxey.github.io/aiml-dash/>

## Installation
To install the `aiml_dash` application, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aiml_dash.git
   cd aiml_dash
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the Dash application, execute the following command:

```bash
python src/aiml_dash/app.py
```

Once the application is running, open your web browser and navigate to `http://127.0.0.1:8050` to access the application.

## Features
- Interactive visualizations of AI and machine learning datasets.
- User-friendly interface for data exploration.
- Customizable components for enhanced user experience.

## UI Framework - dash-mantine-components

### Overview
AIML Dash uses [dash-mantine-components](https://www.dash-mantine-components.com/) (DMC) as its primary UI component library. DMC is a Dash wrapper for the [Mantine UI](https://mantine.dev/) library, providing over 120 customizable components with a modern, professional design system.

### Why dash-mantine-components?
We chose dash-mantine-components for several key reasons:

- **Modern Design System**: Provides a consistent, professional look and feel across the entire application
- **Rich Component Library**: Includes everything from basic elements (buttons, inputs) to complex components (data tables, accordions, modals)
- **Theme Customization**: Supports extensive theming capabilities for colors, fonts, spacing, and component defaults
- **Responsive Layout**: Built-in support for responsive design with breakpoints and mobile-first approach
- **AppShell Pattern**: Provides a complete application shell structure with header, navbar, aside, main content, and footer
- **Accessibility**: Components are built with WCAG accessibility standards in mind
- **Active Development**: Regular updates and excellent documentation

### Theme Customization

The application uses a custom Mantine theme configured in `app.py`:

```python
dmc.MantineProvider(
    theme={
        "fontFamily": "'Inter', sans-serif",
        "primaryColor": "blue",
        "components": {
            "Button": {"defaultProps": {"fw": 400}},
            "Alert": {"styles": {"title": {"fontWeight": 500}}},
            "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
        },
    }
)
```

**Key Theme Features:**
- **Font Family**: Uses Inter font from Google Fonts for clean, modern typography
- **Primary Color**: Blue color scheme for buttons, links, and accent elements
- **Component Defaults**: Customized button font weight (400) and alert title styling
- **Consistent Styling**: Ensures all components follow the same design language

### AppShell Layout Structure

AIML Dash implements a comprehensive layout using DMC's AppShell component:

```
┌─────────────────────────────────────────────────────────┐
│  Header (60px height)                                   │
│  - Branding, navigation toggle, theme switcher         │
│  - Dataset info, state export/import menu              │
├──────────┬──────────────────────────┬───────────────────┤
│          │                          │                   │
│  Navbar  │    Main Content Area     │   Aside (300px)   │
│  (250px) │                          │                   │
│          │                          │   Dataset         │
│  Page    │    Dynamic page content  │   Selector        │
│  Nav     │    loaded based on       │                   │
│  Links   │    active page           │   Quick Stats     │
│          │                          │                   │
│          │                          │                   │
├──────────┴──────────────────────────┴───────────────────┤
│  Footer (50px height)                                   │
│  - App credits, documentation, GitHub links            │
└─────────────────────────────────────────────────────────┘
```

**Layout Components:**
- **AppShellHeader**: Contains app branding, theme toggle, and navigation controls
- **AppShellNavbar**: Collapsible sidebar with accordion-based navigation (250px width)
- **AppShellAside**: Dataset selector and statistics panel (300px width)
- **AppShellMain**: Dynamic content area that loads different pages
- **AppShellFooter**: Application footer with links and credits

**Responsive Behavior:**
- Navbar collapses on mobile devices (breakpoint: "sm")
- Aside collapses on tablets (breakpoint: "md")
- Both panels can be manually toggled using header buttons

### Common Components

The application leverages numerous DMC components throughout. Here are key examples:

#### Navigation Components
- **`dmc.Accordion`**: Collapsible navigation sections in the sidebar
- **`dmc.NavLink`**: Individual navigation links with icons and active states
- **`dmc.Menu`**: Dropdown menus for actions like export/import state

#### Layout Components
- **`dmc.Container`**: Page containers with max-width constraints
- **`dmc.Stack`**: Vertical layout with consistent spacing between elements
- **`dmc.Group`**: Horizontal layout with flexible alignment options
- **`dmc.Card`**: Bordered containers for grouping related content
- **`dmc.Center`**: Centered content for empty states and loading indicators

#### Form Components
- **`dmc.Select`**: Dropdown selector (e.g., dataset selector)
- **`dmc.MultiSelect`**: Multiple selection dropdowns for variables and functions
- **`dmc.TextInput`**: Single-line text inputs
- **`dmc.Textarea`**: Multi-line text inputs for filters and queries
- **`dmc.Button`**: Action buttons with icons and variants (filled, light, outline)
- **`dmc.Switch`**: Toggle switches for settings like theme switching

#### Display Components
- **`dmc.Badge`**: Status indicators (e.g., row counts, column counts)
- **`dmc.Text`**: Typography with size, weight, and color options
- **`dmc.Title`**: Heading components with hierarchical orders
- **`dmc.Code`**: Code display blocks with syntax highlighting support
- **`dmc.Alert`**: Notification messages for success, error, warning states
- **`dmc.Modal`**: Dialog windows for actions like state import

#### Navigation Components
- **`dmc.Tabs`**: Tabbed interfaces for organizing related content
- **`dmc.Accordion`**: Collapsible sections for filters and grouped content

### Reusable Component Patterns

The application defines reusable component patterns in `components/common.py`:

1. **Page Headers** (`create_page_header`): Consistent title and description formatting with icons
2. **Variable Selectors** (`create_variable_selector`): Standardized dropdowns for column selection
3. **Filter Sections** (`create_filter_section`): Collapsible filter controls with query syntax
4. **Download Buttons** (`create_download_button`): Export buttons with consistent styling
5. **Info Cards** (`create_info_card`): Statistics display cards with icons and colors
6. **Tabs** (`create_tabs`): Dynamic tab creation with icons and panels

### Integration with Other Libraries

DMC is integrated alongside other Dash components:

- **Dash Core Components (dcc)**: Used for Location, Store, Download components
- **dash-ag-grid**: High-performance data tables for viewing and editing large datasets
- **dash-iconify**: Icon library integrated into DMC components for visual indicators
- **Plotly**: Chart library for data visualization within DMC containers

### Notable Configurations

1. **Persistent Storage**: DMC components use `dcc.Store` with local/session storage for:
   - Color scheme preferences
   - Plugin configuration
   - Application state
   - Active page and navigation state

2. **Dark Mode Support**: Theme toggle using DMC Switch component
   - Persists user preference across sessions
   - Icon changes based on theme (sun/moon icons)

3. **Collapsible Panels**: AppShell navbar and aside can be toggled
   - State stored in `dcc.Store` components
   - Smooth transitions and responsive behavior

4. **Dynamic Navigation**: Navigation menu is built dynamically based on:
   - Enabled plugins
   - Page registry
   - User permissions (future enhancement)

5. **Notification System**: Uses `dmc.NotificationContainer` for:
   - Success messages
   - Error alerts
   - Import/export status updates

### Getting Started with dash-mantine-components

To use DMC components in new pages:

```python
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def layout():
    return dmc.Container([
        dmc.Stack([
            dmc.Title("My Page", order=2),
            dmc.Card([
                dmc.Text("Content here"),
                dmc.Button(
                    "Action",
                    leftSection=DashIconify(icon="carbon:play"),
                    variant="light",
                ),
            ], withBorder=True, radius="md", p="md"),
        ], gap="md"),
    ])
```

For more information, visit the [dash-mantine-components documentation](https://www.dash-mantine-components.com/).

## Contributing
Contributions are welcome! If you would like to contribute to the `aiml_dash` project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Getting started with your project

### 1. Create a New Repository

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:jeffmaxey/aiml-dash.git
git push -u origin main
```

### 2. Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file

### 3. Run the pre-commit hooks

Initially, the CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
uv run pre-commit run -a
```

### 4. Commit the changes

Lastly, commit the changes made by the two steps above to your repository.

```bash
git add .
git commit -m 'Fix formatting issues'
git push origin main
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/codecov/).

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/jeffmaxey/aiml-dash/settings/secrets/actions/new).
- Create a [new release](https://github.com/jeffmaxey/aiml-dash/releases/new) on Github.
- Create a new tag in the form `*.*.*`.

For more details, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/cicd/#how-to-trigger-a-release).

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
