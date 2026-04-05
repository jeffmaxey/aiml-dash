# AIML Dash

[![Release](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jeffmaxey/aiml-dash/main.yml?branch=main)](https://github.com/jeffmaxey/aiml-dash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jeffmaxey/aiml-dash/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffmaxey/aiml-dash)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)
[![License](https://img.shields.io/github/license/jeffmaxey/aiml-dash)](https://img.shields.io/github/license/jeffmaxey/aiml-dash)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/downloads/)

A comprehensive Dash application for Predictive Analytics and Machine Learning with a powerful plugin framework.

## 🌟 Overview

AIML Dash is a modern, extensible web application built with Plotly Dash that provides interactive tools for data analysis, machine learning, and statistical modeling. Designed with a modular plugin architecture, it offers a professional interface for data scientists, analysts, and researchers to explore data and build predictive models.

- **📚 Documentation**: <https://jeffmaxey.github.io/aiml-dash/>
- **💻 GitHub Repository**: <https://github.com/jeffmaxey/aiml-dash/>
- **🐛 Issue Tracker**: <https://github.com/jeffmaxey/aiml-dash/issues>

## ✨ Key Features

- **🎨 Modern UI**: Built with [dash-mantine-components](https://www.dash-mantine-components.com/) for a professional, responsive interface
- **🔌 Plugin Framework**: Extensible architecture allowing easy addition of new features and pages
- **📊 Data Management**: Comprehensive tools for data import, transformation, visualization, and export
- **🤖 Machine Learning**: Built-in support for various ML algorithms including regression, classification, clustering, and neural networks
- **📈 Statistical Analysis**: Tools for hypothesis testing, correlation analysis, and experimental design
- **🎯 Interactive Visualizations**: Rich, interactive charts and plots powered by Plotly
- **💾 State Management**: Save and restore application state for reproducible analysis
- **🌓 Dark Mode**: Full support for light and dark themes
- **🐳 Docker Support**: Containerized deployment for easy setup and scaling

## 🚀 Quick Start

### Option 1: Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the application
uv run python aiml_dash/run.py
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the application
python aiml_dash/run.py
```

### Option 3: Using Docker

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Build the Docker image
docker build -t aiml-dash .

# Run the container
docker run -p 8050:8050 aiml-dash
```

Once running, open your browser and navigate to `http://127.0.0.1:8050`

## 📦 Installation for Development

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Install with development dependencies
uv sync --all-groups

# Install pre-commit hooks
uv run pre-commit install
```

## 🛠️ Technology Stack

| Layer | Libraries |
|---|---|
| **Web framework** | Plotly Dash 4.0+, Flask |
| **UI components** | dash-mantine-components 2.6+, dash-ag-grid 32.3+, dash-iconify |
| **Data / ML** | pandas 2.1+, numpy 1.24+, scipy 1.11+, scikit-learn 1.3+ |
| **Config / Validation** | pydantic 2.7+, pydantic-settings |
| **Security / Perf** | flask-talisman, flask-caching, flask-compress, brotli |
| **Database** | SQLAlchemy, pyodbc |
| **Dev tooling** | pytest, ruff, mypy, tox, MkDocs, pre-commit, watchdog |
| **Deployment** | Docker, Gunicorn |

## 🏗️ Architecture

AIML Dash uses a modular architecture with several key components:

- **Core Application**: Built with Plotly Dash and Flask
- **Plugin System**: Dynamic plugin discovery and registration with RBAC filtering
- **Service Layer**: `AppServices` singleton that bundles plugins, auth, data, and projects
- **Data Manager**: Centralized in-memory dataset management
- **Component Library**: Reusable UI components built with dash-mantine-components
- **Utilities**: Helper functions for statistics, transforms, and database operations

### Directory Structure

```
aiml-dash/
├── aiml_dash/
│   ├── app.py              # Main create_app() factory
│   ├── run.py              # CLI entry point
│   ├── auth.py             # UserContext + RBAC (AuthorizationService)
│   ├── services.py         # AppServices container (plugins, data, auth, projects)
│   ├── check_setup.py      # Setup validation
│   ├── components/         # Reusable Dash UI components (shell, editor, common)
│   ├── pages/              # Legacy page structure
│   ├── utils/              # config, logging, data_manager, statistics,
│   │                       #   transforms, database, pagination helpers
│   └── plugins/            # Plugin system core + all built-in plugins
│       ├── models.py           # Plugin + PluginPage frozen dataclasses
│       ├── registry.py         # Central registry, navigation builder
│       ├── runtime.py          # PluginRuntime lifecycle manager
│       ├── factory.py          # build_plugin() / build_plugin_pages() helpers
│       ├── loader.py           # Dynamic plugin discovery
│       ├── dependency_manager.py
│       ├── config_manager.py
│       ├── hot_reload.py       # Dev hot-reloading via watchdog
│       ├── standalone.py       # Run a single plugin in isolation
│       ├── core/               # Home, settings, help (locked, always on)
│       ├── data_plugin/        # Data import / exploration / transformation
│       ├── basics_plugin/      # Statistics & hypothesis testing
│       ├── design_plugin/      # Experimental design & sampling
│       ├── model_plugin/       # ML model building
│       ├── multivariate_plugin/
│       ├── legacy/             # Legacy analysis tools
│       ├── example_plugin/     # Reference implementation
│       └── template_plugin/    # Starter template for new plugins
├── tests/                  # Pytest suite (317 tests)
├── docs/                   # MkDocs documentation
├── Dockerfile
├── pyproject.toml
└── Makefile
```

### Startup Flow

1. `run.py` loads `AppSettings` from environment variables (prefix `AIML_DASH_`, e.g. `AIML_DASH_PORT=8050`)
2. `create_app(settings)` in `app.py`:
   - Instantiates `AppServices` (plugins, auth, data, projects)
   - Loads all static plugins from `_STATIC_PLUGIN_MODULES`
   - Builds the `dmc.AppShell` layout (header + navbar + aside + main + footer)
   - Registers all Dash callbacks (routing, theme, state, per-plugin callbacks)
3. Flask dev server starts at `http://127.0.0.1:8050` (Gunicorn in production)

If `AIML_DASH_DEBUG=true`, a `watchdog`-based hot-reloader automatically restarts the app when plugin files change.

## 🔌 Plugin Framework

AIML Dash features a powerful plugin framework that makes it easy to extend the application with new pages and functionality. Each plugin is a self-contained module that follows a standardized structure.

### Plugin Architecture

- **🔍 Dynamic Discovery**: Plugins are automatically discovered from the `plugins/` directory
- **⚙️ Enable/Disable**: Runtime plugin management through the settings page
- **📦 Modular Structure**: Consistent structure with separate modules for layout, components, callbacks, styles, and constants
- **📖 Well-Documented**: Comprehensive docstrings and type hints throughout
- **🧪 Standalone Testing**: Plugins can be run independently for development and testing
- **🔒 Type-Safe**: Full type hints throughout the plugin framework
- **🛡️ RBAC**: Per-page `allowed_roles` filtering via `UserContext`

### Plugin Data Models

All plugin objects use immutable, type-safe frozen dataclasses:

```python
@dataclass(frozen=True)
class PluginPage:
    id: str                      # Unique page identifier
    label: str                   # Display name in navigation
    icon: str                    # Iconify icon (e.g. "carbon:home")
    layout: Callable[[], Component]  # Callable that returns the Dash layout
    section: str                 # Nav section (Core, Data, Basics, …)
    group: str | None            # Optional sub-grouping within a section
    order: int                   # Sort order within the group
    group_order: int             # Sort order for the group itself
    description: str | None
    allowed_roles: Sequence[str] # RBAC role list; empty = unrestricted

@dataclass(frozen=True)
class Plugin:
    id: str
    name: str
    description: str
    pages: Sequence[PluginPage]
    version: str                 # Semantic version string
    default_enabled: bool
    locked: bool                 # If True, cannot be disabled by users
    register_callbacks: Callable[[object], None] | None
    dependencies: Sequence[str]  # IDs of required plugins
    min_app_version: str | None
    config_schema: dict | None   # JSON schema for plugin config
```

### Plugin Lifecycle

1. **Discovery** — Static list in `_STATIC_PLUGIN_MODULES` (+ optional dynamic loading)
2. **Loading** — Import module → call `get_plugin()` → validate dependencies/versions
3. **Registration** — Store in `PluginRuntime`, build navigation structure
4. **Callback Registration** — Call `plugin.register_callbacks(app)` for each plugin
5. **Runtime Management** — Enable/disable via `enabled-plugins` store; filter by user roles

### Plugin Components

Each plugin consists of these modules:

- `__init__.py` - Plugin registration; calls `build_plugin()` from `factory.py`
- `constants.py` - `PLUGIN_ID`, `PAGE_DEFINITIONS` list (metadata only, no logic)
- `layout.py` - `PAGE_LAYOUTS` dict mapping `page_id → layout callable`
- `components.py` - Reusable UI components scoped to this plugin
- `callbacks.py` - `register_callbacks(app)` — optional Dash interactivity
- `styles.py` - Style constants and configuration

### Available Plugin Categories

- **Core**: Essential pages (home, settings, help) - locked, cannot be disabled
- **Data**: Data management, exploration, transformation, and visualization
- **Basics**: Statistical analysis and hypothesis testing
- **Design**: Experimental design, sampling, and randomization
- **Model**: Machine learning models and evaluation
- **Multivariate**: Advanced multivariate analysis
- **Legacy**: Legacy analysis tools
- **Example**: Demonstration plugin showing best practices
- **Template**: Starter template for creating new plugins

### Creating a New Plugin

1. **Copy the template**:
   ```bash
   cp -r aiml_dash/plugins/template_plugin aiml_dash/plugins/my_plugin
   ```

2. **Update constants.py** with your plugin's metadata

3. **Modify layout.py** to define your page structure

4. **Test standalone**:
   ```bash
   python -m aiml_dash.plugins.standalone my_plugin
   ```

For detailed instructions, see the [Plugin Development Guide](https://jeffmaxey.github.io/aiml-dash/plugin-development/).

## 🎨 UI Framework - Dash Mantine Components

AIML Dash uses [dash-mantine-components](https://www.dash-mantine-components.com/) (DMC) as its primary UI component library, providing:

- **Modern Design**: Professional, consistent look and feel
- **Rich Components**: 120+ customizable components
- **Theme Support**: Extensive theming with light/dark mode
- **Responsive Layout**: Mobile-first responsive design
- **AppShell Pattern**: Complete application shell structure
- **Accessibility**: WCAG accessibility standards

### Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  Header (60px)                                          │
│  - Branding, navigation, theme switcher                │
├──────────┬──────────────────────────┬───────────────────┤
│  Navbar  │    Main Content Area     │   Aside (300px)   │
│  (250px) │                          │                   │
│  - Page  │    Dynamic page content  │   - Dataset       │
│    Nav   │    loaded based on       │     Selector      │
│  - Links │    active page           │   - Quick Stats   │
├──────────┴──────────────────────────┴───────────────────┤
│  Footer (50px)                                          │
│  - Credits, documentation, links                       │
└─────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

All settings are managed via Pydantic with environment variable overrides using the `AIML_DASH_` prefix. You can also use a `.env` file in the project root.

| Environment Variable | Default | Description |
|---|---|---|
| `AIML_DASH_HOST` | `127.0.0.1` | Bind address |
| `AIML_DASH_PORT` | `8050` | Port to listen on |
| `AIML_DASH_DEBUG` | `false` | Enable debug mode + hot reload |

Example `.env`:

```env
AIML_DASH_HOST=0.0.0.0
AIML_DASH_PORT=8000
AIML_DASH_DEBUG=true
```

## 💾 State Management

AIML Dash persists UI and data state in the browser using Dash `dcc.Store` components:

| Store ID | Storage | Contents |
|---|---|---|
| `color-scheme-storage` | `local` | Light / dark theme preference |
| `enabled-plugins` | `local` | Which plugins the user has enabled |
| `app-state` | `session` | Active page, sidebar state |
| `user-context` | `session` | Current user ID and roles |

The **Project Snapshot** feature serializes all stores plus in-memory datasets to a single JSON file that can be saved and restored to reproduce any analysis workflow.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes** and commit: `git commit -m 'Add new feature'`
4. **Run tests**: `uv run pytest`
5. **Run linting**: `uv run pre-commit run -a`
6. **Push to your fork**: `git push origin feature/my-feature`
7. **Create a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines (enforced by Ruff)
- Write tests for new features
- Update documentation as needed
- Add type hints to all functions
- Write descriptive commit messages

### Plugin Development

See the [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) for detailed instructions on creating plugins.

## 🧪 Testing

```bash
# Run all tests (recommended)
uv run pytest

# Run all tests using explicit PYTHONPATH
PYTHONPATH=. python3 -m pytest tests/ -q

# Run with coverage
uv run pytest --cov=aiml_dash

# Run specific test file
uv run pytest tests/test_data_manager.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Plotly Dash](https://dash.plotly.com/)
- UI components from [dash-mantine-components](https://www.dash-mantine-components.com/)
- Icons from [Iconify](https://iconify.design/)
- Inspired by the R Shiny AIML package

## 📧 Contact

- **Author**: Jeff A. Maxey
- **Email**: aiml-dash@proton.me
- **GitHub**: [@jeffmaxey](https://github.com/jeffmaxey)

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).

