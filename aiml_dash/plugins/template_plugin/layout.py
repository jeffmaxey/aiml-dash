"""Layout for the template plugin page.

This module defines the main layout for the template plugin using Dash Mantine
Components. It serves as a guide for developers creating new plugins.

The layout includes:
- Hero header introducing the template
- Step-by-step guide for creating a new plugin
- Module cards explaining each file's purpose
- Quick-reference code snippets
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from aiml_dash.plugins.template_plugin.components import (
    create_step_card,
    create_template_card,
)
from aiml_dash.plugins.template_plugin.styles import (
    SECTION_GAP,
    TEMPLATE_CONTAINER_SIZE,
)


def template_layout() -> dmc.Container:
    """Create the template plugin layout.

    Returns
    -------
    dmc.Container
        The complete template plugin page layout.
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
                                        icon="carbon:template",
                                        width=40,
                                        color="#339af0",
                                    ),
                                    dmc.Title("Plugin Starter Template", order=2),
                                ],
                                gap="md",
                            ),
                            dmc.Text(
                                "Use this template as a starting point for new plugin "
                                "development. Copy the template_plugin directory, rename "
                                "it, and customise each module.",
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
                # --- Getting started steps ---
                dmc.Stack(
                    [
                        dmc.Title("Getting Started", order=3),
                        dmc.Text(
                            "Follow these steps to create your own plugin:",
                            c="dimmed",
                            size="sm",
                        ),
                    ],
                    gap="xs",
                ),
                dmc.SimpleGrid(
                    [
                        create_step_card(
                            "1",
                            "Copy the Template",
                            "Duplicate the template_plugin/ directory and rename it "
                            "to your plugin name (e.g. my_plugin/).",
                        ),
                        create_step_card(
                            "2",
                            "Update Constants",
                            "Edit constants.py to set your PLUGIN_ID, PLUGIN_NAME, "
                            "PAGE_DEFINITIONS, and other metadata.",
                        ),
                        create_step_card(
                            "3",
                            "Build the Layout",
                            "Design your page layout in layout.py using Dash Mantine "
                            "Components and export PAGE_LAYOUTS.",
                        ),
                        create_step_card(
                            "4",
                            "Register in Runtime",
                            "Add your plugin module path to _STATIC_PLUGIN_MODULES "
                            "in runtime.py to make it load automatically.",
                        ),
                    ],
                    cols={"base": 1, "sm": 2},
                    spacing="md",
                ),
                # --- Module reference cards ---
                dmc.Stack(
                    [
                        dmc.Title("Module Reference", order=3),
                        dmc.Text(
                            "Each plugin consists of the following standard modules:",
                            c="dimmed",
                            size="sm",
                        ),
                    ],
                    gap="xs",
                ),
                dmc.SimpleGrid(
                    [
                        create_template_card(
                            "constants.py",
                            "Define PLUGIN_ID, PLUGIN_NAME, PLUGIN_VERSION, "
                            "PAGE_DEFINITIONS, icons, and section ordering.",
                            "carbon:catalog",
                            "blue",
                        ),
                        create_template_card(
                            "layout.py",
                            "Build page layouts with DMC components. Export "
                            "PAGE_LAYOUTS mapping page IDs to layout callables.",
                            "carbon:layout",
                            "teal",
                        ),
                        create_template_card(
                            "components.py",
                            "Extract reusable UI elements (cards, charts, forms) that can be shared across pages.",
                            "carbon:component",
                            "violet",
                        ),
                        create_template_card(
                            "callbacks.py",
                            "Register Dash callbacks for interactivity. Expose "
                            "register_callbacks(app) for the framework.",
                            "carbon:connection-signal",
                            "orange",
                        ),
                        create_template_card(
                            "styles.py",
                            "Centralise style constants (sizes, gaps, colours) "
                            "for consistent theming across the plugin.",
                            "carbon:paint-brush",
                            "pink",
                        ),
                        create_template_card(
                            "__init__.py",
                            "Wire everything together with build_plugin() and expose "
                            "get_plugin() for the plugin runtime.",
                            "carbon:application",
                            "gray",
                        ),
                    ],
                    cols={"base": 1, "sm": 2, "lg": 3},
                    spacing="md",
                ),
                # --- Tip alert ---
                dmc.Alert(
                    dmc.Text(
                        "Check the Example Plugin page to see a working plugin in "
                        "action, or refer to the docs/PLUGIN_DEVELOPMENT.md guide "
                        "for detailed documentation.",
                        size="sm",
                    ),
                    title="Tip",
                    color="teal",
                    variant="light",
                    icon=DashIconify(icon="carbon:information", width=20),
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=TEMPLATE_CONTAINER_SIZE,
        py="xl",
    )


PAGE_LAYOUTS = {
    "template": template_layout,
}
