"""Layout for the template plugin page.

This module defines the main layout for the template plugin using Dash Mantine
Components. It serves as a guide for developers creating new plugins.

The layout includes:
- Title and introductory description
- Instruction cards for each plugin component
- Examples of proper component organization
"""

import dash_mantine_components as dmc

from aiml_dash.plugins.template_plugin.components import create_template_card
from aiml_dash.plugins.template_plugin.styles import TEMPLATE_CONTAINER_SIZE


def template_layout() -> dmc.Container:
    """Create the template plugin layout.

    Returns:
        dmc.Container: A container with the template plugin layout including
            title, description, and instructional cards for plugin development.
    """
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
