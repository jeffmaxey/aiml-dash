# Configuration Files

This directory contains centralized configuration files for the aiml-dash project.

## Files

- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration for code quality checks
- **`codecov.yaml`**: Codecov configuration for code coverage reporting
- **`tox.ini`**: Tox configuration for testing across multiple Python versions
- **`mkdocs.yml`**: MkDocs configuration for documentation generation

## Usage

Most tools will reference these files automatically through symlinks or explicit paths in the Makefile and GitHub workflows.

For example:
- Pre-commit hooks: A symlink `.pre-commit-config.yaml` in the root points to this directory
- MkDocs: Use `mkdocs build -f configs/mkdocs.yml` or `make docs`
- Codecov: Referenced in GitHub workflows as `configs/codecov.yaml`
