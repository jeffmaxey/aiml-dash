"""Layouts for core plugin pages."""

import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from aiml_dash.plugins.core.components import (
    create_feature_card,
    create_resource_item,
    create_section_header,
    create_step_card,
)
from aiml_dash.plugins.core.styles import CONTAINER_SIZE, SECTION_GAP


def home_layout() -> dmc.Container:
    """Create the home page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header(
                    "Welcome to AIML Dash",
                    "A plugin-enabled Dash application for predictive analytics and machine learning workflows.",
                ),
                dmc.SimpleGrid(
                    [
                        create_feature_card(
                            "Plugin framework",
                            "Enable or disable pages at runtime and extend the app with new plugins.",
                            "carbon:plugin",
                        ),
                        create_feature_card(
                            "Data workflows",
                            "Load, transform, and visualize datasets with curated tooling.",
                            "carbon:data-table",
                        ),
                        create_feature_card(
                            "Analytics models",
                            "Explore statistical, machine learning, and multivariate techniques.",
                            "carbon:machine-learning",
                        ),
                    ],
                    cols=3,
                    spacing="md",
                    verticalSpacing="md",
                ),
                dmc.Divider(),
                create_section_header("Install", "Set up the app locally in a few steps."),
                dmc.Stack(
                    [
                        create_step_card(
                            "1",
                            "Clone the repository",
                            "Get the code locally before installing dependencies.",
                            "git clone https://github.com/jeffmaxey/aiml-dash.git",
                        ),
                        create_step_card(
                            "2",
                            "Sync dependencies",
                            "Install the runtime and development dependencies with uv.",
                            "uv sync",
                        ),
                        create_step_card(
                            "3",
                            "Run the application",
                            "Start the Dash server and open the browser.",
                            "uv run python -m aiml_dash.app",
                        ),
                    ],
                    gap="md",
                ),
                dmc.Divider(),
                create_section_header("Use", "Navigate the core workflows and plugins."),
                dmc.List(
                    [
                        dmc.ListItem("Start on the Home page to learn the available features."),
                        dmc.ListItem("Use Settings to enable or disable plugins instantly."),
                        dmc.ListItem("Open Data, Basics, Design, Model, or Multivariate sections to work."),
                    ],
                    spacing="xs",
                    size="sm",
                ),
                dmc.Divider(),
                create_section_header("Maintain", "Keep the app healthy over time."),
                dmc.List(
                    [
                        dmc.ListItem("Run `make check` and `make test` before releases."),
                        dmc.ListItem("Use the Settings page to manage plugin availability."),
                        dmc.ListItem("Capture new workflows in template plugins for repeatability."),
                    ],
                    spacing="xs",
                    size="sm",
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )


def help_layout() -> dmc.Container:
    """Create the help page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header("Help & Support", "Guidance for operating and extending AIML Dash."),
                dmc.Card(
                    dmc.Stack(
                        [
                            create_resource_item(
                                "Plugin settings",
                                "Enable, disable, and import plugin configurations from the Settings page.",
                                "carbon:settings",
                            ),
                            create_resource_item(
                                "State management",
                                "Export and import application state using the header menu.",
                                "carbon:save",
                            ),
                            create_resource_item(
                                "Documentation",
                                "Review README.md and docs/ for deeper technical details.",
                                "carbon:book",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                dmc.Alert(
                    "Need more help? File an issue on GitHub with logs and screenshots.",
                    title="Support",
                    color="blue",
                    icon=DashIconify(icon="carbon:chat"),
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )


def settings_layout() -> dmc.Container:
    """Create the plugin settings page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header("Settings", "Manage plugins and import configurations."),
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Enabled plugins", fw=600),
                            dmc.Stack(id="plugin-toggle-container", gap="sm"),
                        ],
                        gap="sm",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Import plugin configuration", fw=600),
                            dmc.Text(
                                "Upload a JSON file with an enabled_plugins list to update active plugins.",
                                size="sm",
                                c="dimmed",
                            ),
                            dcc.Upload(
                                id="plugin-import-upload",
                                children=dmc.Button(
                                    "Upload plugin config",
                                    leftSection=DashIconify(icon="carbon:upload"),
                                    variant="light",
                                ),
                                multiple=False,
                            ),
                            dmc.Stack(id="plugin-import-status"),
                        ],
                        gap="sm",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )
