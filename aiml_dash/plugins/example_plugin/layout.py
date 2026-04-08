"""Layout for the example plugin page.

This module defines the main layout for the example plugin using Dash Mantine
Components. It demonstrates how to structure a plugin page with proper
component organization and styling.

The layout includes:
- Hero header with plugin branding
- Statistic cards summarising the plugin architecture
- Feature grid highlighting key capabilities
- Architecture overview of the plugin module structure
- Informational alert about the template plugin
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.example_plugin.components import (
    create_architecture_item,
    create_example_stat,
    create_feature_card,
)
from aiml_dash.plugins.example_plugin.styles import (
    EXAMPLE_CONTAINER_SIZE,
    SECTION_GAP,
)


def example_layout() -> dmc.Container:
    """Create the example plugin layout.

    Returns
    -------
    dmc.Container
        The complete example plugin page layout.
    """
    return dmc.Container(
        dmc.Stack(
            [
                # --- Hero section ---
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    DashIconify(
                                        icon="carbon:apps",
                                        width=40,
                                        color="#339af0",
                                    ),
                                    dmc.Title("Example Plugin", order=2),
                                ],
                                gap="md",
                            ),
                            dmc.Text(
                                "A reference implementation demonstrating how to build "
                                "a full-featured plugin for AIML Dash using Dash Mantine "
                                "Components.",
                                size="md",
                                c="dimmed",
                            ),
                        ],
                        gap="xs",
                    ),
                    withBorder=True,
                    radius="md",
                    p="xl",
                ),
                # --- Statistics row ---
                dmc.SimpleGrid(
                    [
                        create_example_stat("Status", "Active", "carbon:checkmark-filled", "green"),
                        create_example_stat("Version", "1.0.0", "carbon:version", "blue"),
                        create_example_stat("Modules", "6 files", "carbon:document", "violet"),
                        create_example_stat("Callbacks", "Optional", "carbon:connection-signal", "orange"),
                    ],
                    cols={"base": 2, "sm": 4},
                    spacing="md",
                ),
                # --- Feature cards ---
                dmc.Stack(
                    [
                        dmc.Title("Plugin Capabilities", order=3),
                        dmc.Text(
                            "Each plugin in AIML Dash is a self-contained package that follows a standard structure.",
                            c="dimmed",
                            size="sm",
                        ),
                    ],
                    gap="xs",
                ),
                dmc.SimpleGrid(
                    [
                        create_feature_card(
                            "Modular Layouts",
                            "Define page layouts in layout.py with Dash Mantine "
                            "Components for a consistent, responsive UI.",
                            "carbon:layout",
                            "blue",
                        ),
                        create_feature_card(
                            "Reusable Components",
                            "Extract shared UI elements into components.py so they "
                            "can be reused across pages and plugins.",
                            "carbon:component",
                            "teal",
                        ),
                        create_feature_card(
                            "Scoped Callbacks",
                            "Register callbacks in callbacks.py to keep interactivity scoped and easy to test.",
                            "carbon:connection-signal",
                            "violet",
                        ),
                        create_feature_card(
                            "Declarative Constants",
                            "Centralise page IDs, metadata, and config in constants.py for a single source of truth.",
                            "carbon:settings",
                            "orange",
                        ),
                        create_feature_card(
                            "RBAC Integration",
                            "Control page visibility with per-page allowed_roles using "
                            "the built-in authorisation service.",
                            "carbon:locked",
                            "red",
                        ),
                        create_feature_card(
                            "Hot Reloading",
                            "Edit plugin files during development and see changes "
                            "reflected instantly with watchdog integration.",
                            "carbon:restart",
                            "cyan",
                        ),
                    ],
                    cols={"base": 1, "sm": 2, "lg": 3},
                    spacing="md",
                ),
                # --- Architecture overview ---
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Title("Plugin Architecture", order=4),
                            dmc.Text(
                                "Every plugin follows the same module structure:",
                                size="sm",
                                c="dimmed",
                                mb="sm",
                            ),
                            dmc.Divider(),
                            create_architecture_item(
                                "__init__.py",
                                "Plugin entry point — exposes get_plugin() factory",
                                "carbon:application",
                            ),
                            dmc.Divider(variant="dashed"),
                            create_architecture_item(
                                "constants.py",
                                "Plugin ID, name, version, page definitions",
                                "carbon:catalog",
                            ),
                            dmc.Divider(variant="dashed"),
                            create_architecture_item(
                                "layout.py",
                                "Page layouts built with Dash Mantine Components",
                                "carbon:layout",
                            ),
                            dmc.Divider(variant="dashed"),
                            create_architecture_item(
                                "components.py",
                                "Reusable UI components shared across pages",
                                "carbon:component",
                            ),
                            dmc.Divider(variant="dashed"),
                            create_architecture_item(
                                "callbacks.py",
                                "Dash callback registration for interactivity",
                                "carbon:connection-signal",
                            ),
                            dmc.Divider(variant="dashed"),
                            create_architecture_item(
                                "styles.py",
                                "Style constants for consistent theming",
                                "carbon:paint-brush",
                            ),
                        ],
                        gap="sm",
                    ),
                    withBorder=True,
                    radius="md",
                    p="lg",
                ),
                # --- Call to action ---
                dmc.Alert(
                    dmc.Text(
                        "Ready to build your own plugin? Enable the Template Plugin "
                        "from the Settings page to get started with a scaffolded structure.",
                        size="sm",
                    ),
                    title="Get Started",
                    color="blue",
                    variant="light",
                    icon=DashIconify(icon="carbon:lightbulb", width=20),
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=EXAMPLE_CONTAINER_SIZE,
        py="xl",
    )


PAGE_LAYOUTS = {
    "example": example_layout,
}
