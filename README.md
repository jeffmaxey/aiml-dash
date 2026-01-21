# AIML Dash

[![Release](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jeffmaxey/aiml-dash/main.yml?branch=main)](https://github.com/jeffmaxey/aiml-dash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jeffmaxey/aiml-dash/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffmaxey/aiml-dash)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)](https://img.shields.io/github/commit-activity/m/jeffmaxey/aiml-dash)
[![License](https://img.shields.io/github/license/jeffmaxey/aiml-dash)](https://img.shields.io/github/license/jeffmaxey/aiml-dash)

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

## 🏗️ Architecture

AIML Dash uses a modular architecture with several key components:

- **Core Application**: Built with Plotly Dash and Flask
- **Plugin System**: Dynamic plugin discovery and registration
- **Data Manager**: Centralized data storage and management
- **Component Library**: Reusable UI components built with dash-mantine-components
- **Utilities**: Helper functions for statistics, transforms, and database operations

## 🔌 Plugin Framework

AIML Dash features a powerful plugin framework that makes it easy to extend the application with new pages and functionality. Each plugin is a self-contained module that follows a standardized structure.

### Plugin Architecture

- **🔍 Dynamic Discovery**: Plugins are automatically discovered from the `plugins/` directory
- **⚙️ Enable/Disable**: Runtime plugin management through the settings page
- **📦 Modular Structure**: Consistent structure with separate modules for layout, components, callbacks, styles, and constants
- **📖 Well-Documented**: Comprehensive docstrings and type hints throughout
- **🧪 Standalone Testing**: Plugins can be run independently for development and testing
- **🔒 Type-Safe**: Full type hints throughout the plugin framework

### Plugin Components

Each plugin consists of these modules:

- `__init__.py` - Plugin registration and metadata
- `layout.py` - Page layout definitions using Dash Mantine Components
- `components.py` - Reusable UI components
- `callbacks.py` - Dash callbacks for interactivity (optional)
- `styles.py` - Style constants and configuration
- `constants.py` - Plugin-specific constants

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
# Run all tests
uv run pytest

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

For more details, see the [UI Components documentation](https://jeffmaxey.github.io/aiml-dash/ui-components/).

## 🤝 Contributing
Contributions are welcome! If you would like to contribute to the `aiml_dash` project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## 📧 Contact

- **Author**: Jeff A. Maxey
- **Email**: aiml-dash@proton.me
- **GitHub**: [@jeffmaxey](https://github.com/jeffmaxey)

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
