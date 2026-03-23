# Python Modules

This repository already includes product and architecture documentation. This page is the Python-oriented entry point for the codebase and maps the MkDocs API reference to the actual package structure.

## Package Overview

The application lives under `aiml_dash` and is organized around a small set of top-level modules plus several focused subpackages:

- `aiml_dash.app`: application factory, app shell layout, and core callbacks
- `aiml_dash.auth`: coarse-grained authorization helpers used by plugins and pages
- `aiml_dash.services`: app-scoped service container and dependency assembly
- `aiml_dash.components`: reusable UI primitives used across pages and plugins
- `aiml_dash.plugins`: plugin models, registry, runtime, loading, and configuration
- `aiml_dash.utils`: configuration, data management, projects, statistics, transforms, logging, and database helpers
- `aiml_dash.pages`: concrete analytical pages exposed through plugins

## Recommended Reading Order

If you are new to the codebase, read the Python modules in this order:

1. [`aiml_dash.__init__`](api-reference/core.md#package-entrypoint)
2. [`aiml_dash.app`](api-reference/core.md#application-factory)
3. [`aiml_dash.services`](api-reference/core.md#service-container)
4. [`aiml_dash.auth`](api-reference/core.md#authorization)
5. [`aiml_dash.plugins.runtime`](api-reference/plugins.md#plugin-runtime)
6. [`aiml_dash.components.common`](api-reference/components.md#common-components)
7. [`aiml_dash.utils.config`](api-reference/utilities.md#configuration)
8. [`aiml_dash.utils.data_manager`](api-reference/utilities.md#data-management)

## Module Map

### Core application

- `aiml_dash.__init__`
- `aiml_dash.app`
- `aiml_dash.auth`
- `aiml_dash.run`
- `aiml_dash.services`

### Reusable UI components

- `aiml_dash.components.__init__`
- `aiml_dash.components.ace_editor`
- `aiml_dash.components.common`
- `aiml_dash.components.shell`

### Plugin framework

- `aiml_dash.plugins.__init__`
- `aiml_dash.plugins.models`
- `aiml_dash.plugins.runtime`
- `aiml_dash.plugins.registry`
- `aiml_dash.plugins.loader`
- `aiml_dash.plugins.dependency_manager`
- `aiml_dash.plugins.config_manager`
- `aiml_dash.plugins.factory`
- `aiml_dash.plugins.hot_reload`
- `aiml_dash.plugins.marketplace`
- `aiml_dash.plugins.standalone`

### Utilities

- `aiml_dash.utils.config`
- `aiml_dash.utils.constants`
- `aiml_dash.utils.data_manager`
- `aiml_dash.utils.database`
- `aiml_dash.utils.logging`
- `aiml_dash.utils.log_manager`
- `aiml_dash.utils.paginate_df`
- `aiml_dash.utils.projects`
- `aiml_dash.utils.statistics`
- `aiml_dash.utils.transforms`

## Notes

- The `pages` directories contain page-level UI and callback implementations. They are intentionally not rendered as one giant API page because the public architecture is plugin-driven, not page-package driven.
- The plugin packages such as `aiml_dash.plugins.model_plugin` and `aiml_dash.plugins.data_plugin` are documented primarily through the plugin system and user/developer guides.
