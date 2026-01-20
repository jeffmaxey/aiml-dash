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
- Modular plugin architecture for easy extensibility.

## Project Structure

The project is organized into modular directories for improved maintainability:

```
aiml-dash/
├── aiml_dash/              # Main package
│   ├── components/         # Reusable UI components
│   ├── pages/              # Application pages by category
│   │   ├── basics/         # Basic statistical analyses
│   │   ├── data/           # Data management and exploration
│   │   ├── design/         # Experimental design
│   │   ├── model/          # Machine learning models
│   │   └── multivariate/   # Multivariate analysis
│   ├── plugins/            # Plugin system
│   │   ├── core/           # Core plugin with MVC architecture
│   │   │   ├── controllers/  # Business logic
│   │   │   └── views/        # UI rendering
│   │   ├── legacy/         # Legacy features
│   │   └── ...             # Additional plugins
│   └── utils/              # Utility modules
│       ├── constants.py    # Application constants
│       ├── transforms.py   # Data transformations
│       ├── data_manager.py # Data management
│       └── ...             # Other utilities
├── configs/                # Configuration files
│   ├── .pre-commit-config.yaml
│   ├── codecov.yaml
│   ├── mkdocs.yml
│   └── tox.ini
├── docs/                   # Documentation
│   ├── components.md       # Component documentation
│   ├── plugins.md          # Plugin development guide
│   ├── pages.md            # Pages documentation
│   ├── utils.md            # Utilities documentation
│   └── contributing.md     # Contribution guidelines
└── tests/                  # Test suite
```

For detailed information about each module, see the [documentation](https://jeffmaxey.github.io/aiml-dash/).

## Architecture

The project follows a modular architecture with clear separation of concerns:

- **Utils**: Reusable utility functions and data management
- **Components**: UI components shared across pages
- **Pages**: Application pages organized by functional area
- **Plugins**: Modular features with MVC pattern
  - **Controllers**: Business logic and data processing
  - **Views**: UI rendering and presentation
  - **Callbacks**: Coordination between controllers and views

See [docs/plugins.md](docs/plugins.md) for detailed plugin architecture documentation.

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
