# Contributing to aiml-dash

Thank you for your interest in contributing to aiml-dash! This guide will help you get started.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/aiml-dash.git
cd aiml-dash
```

### 2. Set Up Development Environment

```bash
make install
```

This will:
- Create a virtual environment using `uv`
- Install all dependencies
- Set up pre-commit hooks

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Running the Application

```bash
python aiml_dash/run.py
```

The application will be available at `http://127.0.0.1:8050`

### Code Quality

Before committing, run code quality checks:

```bash
make check
```

This runs:
- Pre-commit hooks (linting, formatting)
- Type checking with mypy
- Dependency checks with deptry

### Testing

Run tests with coverage:

```bash
make test
```

Run specific test files:

```bash
uv run pytest tests/utils/test_constants.py
```

### Documentation

Build and serve documentation:

```bash
make docs
```

Test documentation build:

```bash
make docs-test
```

## Project Structure

```
aiml-dash/
├── aiml_dash/          # Main package
│   ├── components/     # Reusable UI components
│   ├── pages/          # Application pages
│   │   ├── basics/     # Basic statistics
│   │   ├── data/       # Data management
│   │   ├── design/     # Experimental design
│   │   ├── model/      # ML models
│   │   └── multivariate/  # Multivariate analysis
│   ├── plugins/        # Plugin system
│   │   ├── core/       # Core plugin
│   │   ├── legacy/     # Legacy features
│   │   └── ...         # Other plugins
│   └── utils/          # Utility modules
├── configs/            # Configuration files
│   ├── .pre-commit-config.yaml
│   ├── codecov.yaml
│   ├── mkdocs.yml
│   └── tox.ini
├── docs/               # Documentation
├── tests/              # Test suite
└── pyproject.toml      # Project configuration
```

## Contributing Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 120 characters
- Use meaningful variable names
- Add docstrings to functions and classes

**Example:**

```python
def calculate_statistics(data: pd.DataFrame, column: str) -> dict[str, float]:
    """
    Calculate descriptive statistics for a column.
    
    Args:
        data: Input dataframe
        column: Column name to analyze
        
    Returns:
        Dictionary containing mean, median, std, etc.
        
    Raises:
        ValueError: If column doesn't exist
    """
    if column not in data.columns:
        raise ValueError(f"Column {column} not found")
        
    return {
        "mean": data[column].mean(),
        "median": data[column].median(),
        "std": data[column].std(),
    }
```

### Adding New Features

#### 1. Adding a Utility Function

Create in `aiml_dash/utils/`:

```python
# aiml_dash/utils/my_util.py
def my_utility_function(param: str) -> str:
    """Description of function."""
    return param.upper()
```

Add tests:

```python
# tests/utils/test_my_util.py
from aiml_dash.utils.my_util import my_utility_function

def test_my_utility_function():
    assert my_utility_function("hello") == "HELLO"
```

#### 2. Adding a Component

Create in `aiml_dash/components/`:

```python
# aiml_dash/components/my_component.py
from dash import html

def create_my_component(title: str) -> html.Div:
    """Create a custom component."""
    return html.Div([
        html.H3(title),
        html.P("Component content")
    ])
```

#### 3. Adding a Page

1. Choose category (basics, data, design, model, multivariate)
2. Create page file
3. Register in plugin system
4. Add tests

See [Pages Documentation](pages.md) for details.

#### 4. Adding a Plugin

1. Create plugin directory in `aiml_dash/plugins/`
2. Implement plugin structure (layout, callbacks, components)
3. Register in `registry.py`
4. Add documentation

See [Plugins Documentation](plugins.md) for details.

### Testing Guidelines

- Write tests for all new functionality
- Aim for >80% code coverage
- Test edge cases and error conditions
- Use descriptive test names

**Example:**

```python
def test_calculate_statistics_with_valid_data():
    """Test statistics calculation with valid input."""
    df = pd.DataFrame({"col": [1, 2, 3, 4, 5]})
    result = calculate_statistics(df, "col")
    assert result["mean"] == 3.0

def test_calculate_statistics_with_missing_column():
    """Test that ValueError is raised for missing column."""
    df = pd.DataFrame({"col": [1, 2, 3]})
    with pytest.raises(ValueError):
        calculate_statistics(df, "missing")
```

### Documentation Guidelines

- Update relevant documentation files
- Include code examples
- Add docstrings to all public functions
- Update the changelog

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add new statistical test for normality
fix: Resolve issue with data loading
docs: Update contributing guide
test: Add tests for data transforms
refactor: Separate controller and view logic
```

### Pull Request Process

1. **Ensure tests pass**: `make test`
2. **Run code quality checks**: `make check`
3. **Update documentation**: Add/update relevant docs
4. **Create PR**: With clear description of changes
5. **Address feedback**: Respond to review comments
6. **Squash commits**: Before merging (if requested)

## Common Tasks

### Adding a New Dependency

1. Add to `pyproject.toml` under `dependencies`
2. Run `uv sync` to update lock file
3. Document why the dependency is needed

### Updating Configuration

Configuration files are in `configs/`:
- Pre-commit: `configs/.pre-commit-config.yaml`
- Codecov: `configs/codecov.yaml`
- MkDocs: `configs/mkdocs.yml`
- Tox: `configs/tox.ini`

### Working with Pre-commit

Skip pre-commit hooks (not recommended):
```bash
git commit --no-verify
```

Update hooks:
```bash
uv run pre-commit autoupdate
```

## Getting Help

- Check existing [documentation](https://jeffmaxey.github.io/aiml-dash/)
- Review [issues](https://github.com/jeffmaxey/aiml-dash/issues)
- Ask questions in pull requests
- Read the [README](../README.md)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
