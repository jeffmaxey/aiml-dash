# Copilot Cloud Agent — Onboarding Instructions

## Project Overview

**AIML Dash** is a Python 3.14+ web application built with Plotly Dash 4 and dash-mantine-components for interactive predictive analytics and machine learning. It ships **two top-level packages**:

| Package | Purpose |
|---|---|
| `aiml_dash/` | The Dash web application (UI, plugins, API, services, utils) |
| `aiml/` | A standalone ML library (supervised, unsupervised, deep learning, experiments) wrapping scikit-learn |

Both packages are built and installed from a single `pyproject.toml` using **Hatchling** as the build backend.

---

## Quick Reference — Commands

| Task | Command |
|---|---|
| **Install (recommended)** | `uv sync` (or `pip install -e . --ignore-requires-python`) |
| **Run tests** | `PYTHONPATH=. python3 -m pytest tests/ -q` |
| **Run tests with coverage** | `PYTHONPATH=. python3 -m pytest tests/ --cov --cov-config=pyproject.toml --cov-report=xml` |
| **Lint / format** | `ruff check . --fix && ruff format .` |
| **Full quality check** | `make check` (runs pre-commit, mypy, deptry, docstring quality) |
| **Build wheel** | `make build` (or `uvx --from build pyproject-build --installer uv`) |
| **Build docs** | `uv run mkdocs build -s` |
| **Run the application** | `python aiml_dash/run.py` (dev server at `http://127.0.0.1:8050`) |

### Known Workarounds

* **`requires-python = ">=3.14"`**: When installing with pip on Python 3.12, add `--ignore-requires-python`.
* **`pyarrow` not in dependencies**: Tests in `tests/utils/test_data_persistence.py` fail because `pyarrow` is not listed as a dependency. These ~25 failures are pre-existing and unrelated to most tasks.
* **`unixodbc-dev` needed for `pyodbc`**: On Debian/Ubuntu systems, install `unixodbc-dev` (`apt-get install unixodbc-dev`) before `pip install`. The Dockerfile handles this already. If `pyodbc` installation fails in the sandbox, ignore it — the rest of the app works without it.

---

## Repository Layout

```
aiml-dash/
├── aiml_dash/                # Dash web application package
│   ├── app.py                # create_app() factory — builds layout, registers callbacks
│   ├── run.py                # CLI entry point (loads AppSettings, calls create_app)
│   ├── auth.py               # UserContext (frozen dataclass) + AuthorizationService (RBAC)
│   ├── services.py           # AppServices container (auth, plugins, data, projects)
│   ├── check_setup.py        # Startup validation
│   ├── api/                  # REST API blueprint (/api/v1, auth via X-API-Key header)
│   │   └── blueprint.py
│   ├── components/           # Reusable UI: shell.py (AppShell), common.py, ace_editor.py
│   ├── pages/                # Legacy page structure (being replaced by plugins)
│   ├── utils/                # config.py (Pydantic AppSettings), data_manager.py,
│   │                         #   database.py, logging.py, statistics.py, transforms.py,
│   │                         #   user_store.py, paginate_df.py
│   └── plugins/              # ★ Plugin framework (see "Plugin System" below)
│       ├── models.py         # Plugin + PluginPage frozen dataclasses
│       ├── factory.py        # build_plugin() / build_plugin_pages() helpers
│       ├── registry.py       # Central registry + navigation builder
│       ├── runtime.py        # PluginRuntime — lifecycle, discovery, RBAC filtering
│       ├── loader.py         # Dynamic plugin discovery
│       ├── dependency_manager.py
│       ├── config_manager.py
│       ├── hot_reload.py     # Dev hot-reloading via watchdog
│       ├── standalone.py     # Run a single plugin in isolation
│       ├── marketplace.py    # Plugin marketplace
│       ├── core/             # Home, settings, help (locked, always on)
│       ├── data_plugin/      # Data import / exploration / transformation
│       ├── basics_plugin/    # Statistics & hypothesis testing
│       ├── design_plugin/    # Experimental design & sampling
│       ├── model_plugin/     # ML model building
│       ├── multivariate_plugin/  # PCA, clustering
│       ├── legacy/           # Legacy analysis tools
│       ├── example_plugin/   # Reference implementation
│       └── template_plugin/  # Starter template for new plugins
├── aiml/                     # Standalone ML library
│   ├── base.py               # BaseModel ABC (fit/predict/evaluate/summary/get_params)
│   ├── supervised/           # linear.py, glm.py, trees.py
│   ├── unsupervised/         # pca.py, clustering.py
│   ├── deep_learning/        # neural_network.py
│   ├── experiments/          # Experiment + ExperimentRegistry
│   └── model_selection.py    # cross_validate, grid_search, compare_models
├── tests/                    # Pytest suite (1100+ tests)
│   ├── test_app.py           # App factory, Flask integration
│   ├── test_auth.py, test_services.py, test_check_setup.py, ...
│   ├── aiml/                 # Tests for the aiml library
│   ├── api/                  # REST API tests
│   ├── components/           # UI component tests
│   ├── pages/                # Legacy page tests
│   ├── plugins/              # Plugin-specific tests (one subdir per plugin)
│   └── utils/                # Utility tests
├── docs/                     # MkDocs + Material for documentation
├── scripts/                  # check_docstring_quality.py, profile_hotspots.py, run_ruff_format.py
├── pyproject.toml            # Single source of truth for deps, build, tools config
├── Makefile                  # install, check, test, build, docs targets
├── tox.ini                   # tox config for CI (Python 3.14)
├── Dockerfile                # Multi-stage Docker build (Python 3.14-slim, Gunicorn)
├── .pre-commit-config.yaml   # pre-commit hooks (pre-commit-hooks, ruff)
└── .github/
    ├── workflows/            # CI: main.yml (quality + test + docs), on-release-main.yml, etc.
    └── actions/setup-python-env/  # Shared action for CI setup
```

---

## Architecture — Key Concepts

### Application Factory Pattern

`aiml_dash/app.py` → `create_app(settings, services)` returns a `dash.Dash` instance:

1. Builds `AppServices` via `build_services(settings)` — wires auth, plugins, data, projects.
2. Loads static plugins from `_STATIC_PLUGIN_MODULES` list in `runtime.py`.
3. Constructs a `dmc.MantineProvider` → `dmc.AppShell` layout (header, navbar, aside, main, footer).
4. Registers Dash callbacks for routing, theme, state, and per-plugin callbacks.

Module-level singletons `app` and `server` are created at import time. `server` is the Flask instance (used by Gunicorn: `gunicorn aiml_dash:server`).

### Configuration

All settings live in `AppSettings` (Pydantic `BaseSettings`). Environment variable prefix: `AIML_DASH_`. Supports `.env` files. Key settings: `AIML_DASH_HOST`, `AIML_DASH_PORT`, `AIML_DASH_DEBUG`, `AIML_DASH_ENVIRONMENT`.

### Plugin System

**This is the most important architectural concept.** Every feature area (data import, statistics, ML models, etc.) is a plugin.

Each plugin module contains:
- `constants.py` — `PLUGIN_ID`, `PAGE_DEFINITIONS` (list of metadata dicts)
- `layout.py` — `PAGE_LAYOUTS` dict mapping `page_id → layout callable`
- `components.py` — Reusable UI components
- `callbacks.py` — `register_callbacks(app)` for Dash interactivity
- `styles.py` — Style constants
- `__init__.py` — Calls `build_plugin()` from `factory.py` and exposes `get_plugin()`

Plugin data models are **frozen dataclasses** (`Plugin`, `PluginPage`) defined in `plugins/models.py`.

Plugin lifecycle: Discovery → Loading → Registration (in `PluginRuntime`) → Callback registration → Runtime enable/disable.

To create a new plugin, copy `template_plugin/` and follow the same structure.

### The `aiml` Library

A separate pure-Python ML library. All models inherit from `aiml.base.BaseModel` (ABC with `fit`, `predict`, `evaluate`, `summary`, `get_params`, `set_params`). Models wrap scikit-learn estimators. The library is independent of the Dash app and can be used standalone.

### REST API

`aiml_dash/api/blueprint.py` — Flask Blueprint at `/api/v1`. Auth via `X-API-Key` header (set `AIML_DASH_API_KEY` env var). Endpoints for health, dataset CRUD.

### Auth & RBAC

- `UserContext` is a frozen dataclass with `user_id` and `roles`.
- `AuthorizationService` checks `can_access(user, allowed_roles)`.
- Per-page `allowed_roles` in `PluginPage` controls visibility.
- Default anonymous user has role `("viewer",)`.
- `UserStore` (in `utils/user_store.py`) handles credential storage.

---

## Testing Conventions

- **Framework**: pytest (configured in `pyproject.toml` under `[tool.pytest.ini_options]`).
- **Test directory**: `tests/` mirrors the source structure.
- **Run all tests**: `PYTHONPATH=. python3 -m pytest tests/ -q`
- **Dash callbacks are testable as pure functions**: Import and call directly with positional args matching the callback signature — no running Dash server needed.
- **Test style**: Class-based grouping (e.g., `class TestBuildProjectSnapshot:`) with descriptive docstrings.
- **Assertions**: Standard `assert` statements (Ruff ignores `S101` in test files).
- **Fixtures**: Defined per-file or in `conftest.py`; common fixtures include `services()` (builds `AppServices`) and `flask_client()`.

### Pre-existing Test Failures

~25 tests in `tests/utils/test_data_persistence.py` fail due to missing `pyarrow` dependency. These are known and unrelated to most tasks.

---

## Code Style & Linting

- **Formatter & Linter**: [Ruff](https://docs.astral.sh/ruff/) — configured in `pyproject.toml`.
  - `target-version = "py314"`, `line-length = 120`, `fix = true`.
  - Select rules: `YTT, S, B, A, C4, T10, SIM, I, C90, E, W, F, PGH, UP, RUF, TRY`.
  - Ignored: `E501` (line too long), `E731` (lambda assignment).
  - Test files ignore `S101` (use of assert).
- **Type checking**: mypy (configured in `pyproject.toml`; targets `aiml_dash/`).
- **Pre-commit**: Runs ruff-check, ruff-format, and standard hooks (trailing whitespace, TOML/YAML/JSON checks, end-of-file fixer).
- **Docstrings**: NumPy-style (or Google-style for mkdocstrings). Quality checked by `scripts/check_docstring_quality.py`.
- **Imports**: Sorted by `isort` rules (via Ruff `I` selector). Use `from __future__ import annotations` at top of files.
- **Type hints**: Required on all functions. Use modern syntax (`str | None`, `dict[str, Any]`, `list[str]`).

---

## CI/CD (GitHub Actions)

**Primary workflow**: `.github/workflows/main.yml` — runs on push to `main` and all PRs.

Three jobs:
1. **`quality`** — `make check` (pre-commit, docstring quality, mypy, deptry)
2. **`test`** — `uv run python -m pytest tests --cov --cov-config=pyproject.toml --cov-report=xml` (Python 3.14 matrix)
3. **`check-docs`** — `uv run mkdocs build -s`

Other workflows: `on-release-main.yml` (publish), `pylint.yml`, `python-package.yml`, `python-publish.yml`, `validate-codecov-config.yml`.

---

## Important Patterns & Conventions

1. **Frozen dataclasses** for data models (`Plugin`, `PluginPage`, `UserContext`, `ProjectRecord`).
2. **Service layer pattern**: `AppServices` container bundles all singletons; injected via `create_app()`.
3. **Factory functions**: `build_plugin()`, `build_services()`, `create_app()`, `create_data_manager()`.
4. **Pydantic for config**: `AppSettings(BaseSettings)` with `AIML_DASH_` env prefix.
5. **`dcc.Store` for state**: `color-scheme-storage` (local), `enabled-plugins` (local), `app-state` (session), `user-context` (session).
6. **Plugin callback split**: Large plugins (e.g., `basics_plugin`) split callbacks into sub-modules (`callbacks_single_mean.py`, `callbacks_compare_means.py`, etc.) imported from a `callbacks.py` aggregator.
7. **Icons**: Use Iconify identifiers (e.g., `"carbon:home"`, `"carbon:calculator"`).
8. **UI**: dash-mantine-components (DMC) — AppShell pattern with header, navbar, aside, main, footer.

---

## Tips for Efficient Agent Work

- **Start with `pyproject.toml`** to understand dependencies and tool config.
- **Test changes quickly** with `PYTHONPATH=. python3 -m pytest tests/ -q` — no `uv` needed if pytest is installed.
- **Plugin changes**: Each plugin is self-contained in its own directory under `aiml_dash/plugins/`. Edit only the relevant plugin modules.
- **Callback testing**: Import the callback function directly and call it with positional arguments — no Dash server required.
- **The `aiml` library is independent**: Changes to `aiml/` do not affect the Dash app and vice versa (except at the top-level `__init__.py` re-exports).
- **`app.py` is large (~44KB)**: Use grep or view_range to navigate — it contains the layout builder and all core callbacks.
- **Avoid modifying `_STATIC_PLUGIN_MODULES`** in `runtime.py` unless adding/removing a built-in plugin.
- **Pre-commit is configured**: Run `ruff check . --fix && ruff format .` before committing to avoid CI lint failures.
- **Docker**: Multi-stage build in `Dockerfile`; production runs via Gunicorn (`gunicorn aiml_dash:server`).
