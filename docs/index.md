# Welcome to AIML Dash

[![Release](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)](https://img.shields.io/github/v/release/jeffmaxey/aiml-dash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jeffmaxey/aiml-dash/main.yml?branch=main)](https://github.com/jeffmaxey/aiml-dash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jeffmaxey/aiml-dash/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffmaxey/aiml-dash)
[![License](https://img.shields.io/github/license/jeffmaxey/aiml-dash)](https://img.shields.io/github/license/jeffmaxey/aiml-dash)

A comprehensive Dash application for Predictive Analytics and Machine Learning with a powerful plugin framework.

## Overview

AIML Dash is a modern, extensible web application built with Plotly Dash that provides interactive tools for data analysis, machine learning, and statistical modeling. Designed with a modular plugin architecture, it offers a professional interface for data scientists, analysts, and researchers to explore data and build predictive models.

## Key Features

### 🎨 Modern UI
Built with [dash-mantine-components](https://www.dash-mantine-components.com/) for a professional, responsive interface with full dark mode support.

### 🔌 Plugin Framework
Extensible architecture allowing easy addition of new features and pages. Plugins can be dynamically enabled or disabled at runtime.

### 📊 Data Management
- Import data from CSV, Excel, SQL databases
- Transform and filter datasets
- Combine multiple datasets
- Export results in various formats

### 🤖 Machine Learning
- Linear and Logistic Regression
- Decision Trees and Random Forests
- Neural Networks
- Gradient Boosting
- Model evaluation and comparison

### 📈 Statistical Analysis
- Hypothesis testing (t-tests, ANOVA, chi-square)
- Correlation and regression analysis
- Experimental design
- Sample size calculation

### 🎯 Interactive Visualizations
Rich, interactive charts and plots powered by Plotly:
- Scatter plots, line charts, bar charts
- Box plots, violin plots, histograms
- Correlation matrices, heatmaps
- 3D visualizations

### 💾 State Management
Save and restore application state for reproducible analysis. Export and share your work with colleagues.

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quick-start.md)
- [Plugin Development Guide](plugin-development/overview.md)
- [API Reference](api-reference/core.md)
- [GitHub Repository](https://github.com/jeffmaxey/aiml-dash)

## Architecture

AIML Dash uses a modular architecture with several key components:

- **Core Application**: Built with Plotly Dash and Flask
- **Plugin System**: Dynamic plugin discovery and registration
- **Data Manager**: Centralized data storage and management
- **Component Library**: Reusable UI components
- **Utilities**: Helper functions for statistics and transforms

## Getting Started

```bash
# Install using UV (recommended)
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash
uv sync
uv run python aiml_dash/run.py
```

Open your browser and navigate to `http://127.0.0.1:8050`

See the [Installation Guide](getting-started/installation.md) for more options.

## Support

- **Documentation**: <https://jeffmaxey.github.io/aiml-dash/>
- **GitHub Issues**: <https://github.com/jeffmaxey/aiml-dash/issues>
- **Email**: aiml-dash@proton.me

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/jeffmaxey/aiml-dash/blob/main/LICENSE) file for details.
