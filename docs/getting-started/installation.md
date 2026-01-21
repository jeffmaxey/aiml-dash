# Installation

This guide covers different methods to install and run AIML Dash.

## Prerequisites

- Python 3.12 or higher
- Git (for cloning the repository)
- (Optional) Docker for containerized deployment

## Method 1: Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

### Install UV

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Install dependencies
uv sync

# Run the application
uv run python aiml_dash/run.py
```

The application will be available at `http://127.0.0.1:8050`

## Method 2: Using pip

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

## Method 3: Using Docker

Docker provides an isolated environment for running AIML Dash.

```bash
# Clone the repository
git clone https://github.com/jeffmaxey/aiml-dash.git
cd aiml-dash

# Build the Docker image
docker build -t aiml-dash .

# Run the container
docker run -p 8050:8050 aiml-dash
```

Access the application at `http://127.0.0.1:8050`

### Docker with Volume Mounting

To persist data between container restarts:

```bash
docker run -p 8050:8050 -v $(pwd)/data:/app/data aiml-dash
```

## Development Installation

For development, install with development dependencies:

```bash
# Using UV
uv sync --all-groups

# Using pip
pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install
```

## Verifying Installation

After installation, verify everything is working:

```bash
# Run tests
uv run pytest

# Check code quality
uv run pre-commit run -a

# Start the application
uv run python aiml_dash/run.py
```

## Configuration

AIML Dash can be configured via environment variables or a configuration file. See the [Configuration Guide](configuration.md) for details.

## Troubleshooting

### Port Already in Use

If port 8050 is already in use, you can change it:

```python
# In aiml_dash/run.py
if __name__ == "__main__":
    app.run(debug=True, port=8051)  # Change port here
```

### Missing Dependencies

If you encounter missing dependencies:

```bash
# Using UV
uv sync --reinstall

# Using pip
pip install --force-reinstall -e .
```

### Permission Errors

On Linux/macOS, you may need to use `sudo` or adjust permissions:

```bash
chmod +x aiml_dash/run.py
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Get started with your first analysis
- [Configuration](configuration.md) - Configure AIML Dash for your environment
- [User Guide](../user-guide/overview.md) - Learn about all features
