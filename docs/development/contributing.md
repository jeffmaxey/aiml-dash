# Contributing to AIML Dash

Thank you for your interest in contributing to AIML Dash! This guide will help you get started.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/aiml-dash.git
cd aiml-dash
```

### 2. Set Up Development Environment

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with development tools
uv sync --all-groups

# Install pre-commit hooks
uv run pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

## Development Workflow

### Running the Application

```bash
# Start in development mode
uv run python aiml_dash/run.py
```

The app will run at `http://127.0.0.1:8050` with hot reloading enabled.

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

Pre-commit hooks will automatically run these checks.

### Type Checking

We use [mypy](https://mypy.readthedocs.io/) for type checking:

```bash
uv run mypy aiml_dash
```

### Testing

Write tests for new features and bug fixes:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=aiml_dash --cov-report=html

# Run specific test file
uv run pytest tests/test_data_manager.py

# Run tests matching a pattern
uv run pytest -k "test_data"
```

### Documentation

Update documentation for user-facing changes:

```bash
# Build documentation locally
uv run mkdocs serve

# View at http://127.0.0.1:8000
```

## Making Changes

### Adding a New Feature

1. **Discuss First**: Open an issue to discuss the feature
2. **Create Plugin**: For new pages, create a plugin
3. **Write Tests**: Add tests for new functionality
4. **Update Docs**: Document the new feature
5. **Submit PR**: Create a pull request

### Fixing a Bug

1. **Create Issue**: Report the bug (if not already reported)
2. **Write Test**: Add a test that reproduces the bug
3. **Fix Bug**: Make the fix
4. **Verify**: Ensure the test passes
5. **Submit PR**: Create a pull request

### Plugin Development

See the [Plugin Development Guide](../plugin-development/overview.md) for creating plugins.

### Adding Tests

Tests are located in the `tests/` directory:

```
tests/
├── components/
│   └── test_common.py
├── plugins/
│   ├── test_loader.py
│   └── test_registry.py
└── utils/
    ├── test_data_manager.py
    └── test_statistics.py
```

Example test:

```python
import pytest
from aiml_dash.utils.data_manager import DataManager


def test_add_data():
    """Test adding data to the DataManager."""
    dm = DataManager()
    df = pd.DataFrame({"a": [1, 2, 3]})
    
    dm.add_data("test", df, "Test Dataset")
    
    assert "test" in dm.list_datasets()
    assert dm.get_data("test").equals(df)
```

## Pull Request Process

### 1. Update Your Branch

```bash
# Fetch latest changes
git fetch upstream
git rebase upstream/main
```

### 2. Run All Checks

```bash
# Format code
uv run ruff format .

# Run linting
uv run ruff check --fix .

# Run type checking
uv run mypy aiml_dash

# Run tests
uv run pytest

# Run pre-commit hooks
uv run pre-commit run -a
```

### 3. Commit Your Changes

Follow conventional commit format:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in data loader"
git commit -m "docs: update installation guide"
git commit -m "test: add tests for statistics module"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### 4. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a pull request on GitHub.

### 5. PR Description

Include in your PR description:

- **What**: What does this PR do?
- **Why**: Why is this change needed?
- **How**: How does it work?
- **Testing**: How did you test it?
- **Screenshots**: For UI changes
- **Related Issues**: Link related issues

Example:

```markdown
## Description
Adds a new scatter plot visualization option to the Data Visualize page.

## Motivation
Users requested the ability to create scatter plots with trend lines.

## Changes
- Added scatter plot component
- Added trend line calculation
- Updated documentation
- Added tests

## Testing
- Tested with sample datasets
- Verified trend line calculation
- Checked responsive behavior

## Screenshots
[Add screenshots here]

Fixes #123
```

## Code Review

### What to Expect

- Reviewers may suggest changes
- Be open to feedback
- Respond to comments promptly
- Make requested changes

### Review Checklist

Reviewers will check:

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear
- [ ] PR description is complete

## Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions small and focused
- Use meaningful variable names

Example:

```python
def calculate_mean(values: list[float]) -> float:
    """Calculate the arithmetic mean of a list of values.
    
    Args:
        values: A list of numeric values.
        
    Returns:
        The arithmetic mean of the values.
        
    Raises:
        ValueError: If the values list is empty.
    """
    if not values:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(values) / len(values)
```

### Component Guidelines

- Use dash-mantine-components for UI
- Follow existing component patterns
- Support both light and dark themes
- Make components responsive
- Add proper accessibility attributes

### Plugin Guidelines

- Follow plugin structure conventions
- Use consistent naming
- Document plugin functionality
- Test standalone
- Handle errors gracefully

## Community

### Getting Help

- **GitHub Issues**: Report bugs, request features
- **Discussions**: Ask questions, share ideas
- **Email**: aiml-dash@proton.me

### Recognition

Contributors will be recognized in:

- Release notes
- Contributors section
- Commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask! Open an issue or reach out via email.

Thank you for contributing to AIML Dash! 🎉
