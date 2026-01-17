"""Layout for the template plugin page."""

import dash_mantine_components as dmc

from aiml_dash.plugins.template_plugin.components import create_template_card
from aiml_dash.plugins.template_plugin.styles import TEMPLATE_CONTAINER_SIZE


def template_layout() -> dmc.Container:
    """Create the template plugin layout."""

    return dmc.Container(
        dmc.Stack(
            [
                dmc.Title("Template Plugin", order=2),
                dmc.Text(
                    "Use this page as a starting point for new plugin development.",
                    c="dimmed",
                ),
                dmc.SimpleGrid(
                    [
                        create_template_card(
                            "Layout",
                            "Define layout components in layout.py using Dash Mantine Components.",
                            "carbon:layout",
                        ),
                        create_template_card(
                            "Components",
                            "Extract reusable UI bits into components.py for clarity.",
                            "carbon:component",
                        ),
                        create_template_card(
                            "Callbacks",
                            "Register callbacks in callbacks.py to keep logic scoped.",
                            "carbon:connection-signal",
                        ),
                    ],
                    cols=1,
                    spacing="md",
                ),
            ],
            gap="md",
        ),
        size=TEMPLATE_CONTAINER_SIZE,
        py="xl",
    )
