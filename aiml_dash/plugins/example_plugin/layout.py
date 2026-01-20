"""Layout for the example plugin page.

This module defines the main layout for the example plugin using Dash Mantine
Components. It demonstrates how to structure a plugin page with proper
component organization and styling.

The layout includes:
- Title and description
- Statistic cards showing plugin features
- Informational alert about the template plugin
"""

import dash_mantine_components as dmc

from aiml_dash.plugins.example_plugin.components import create_example_stat
from aiml_dash.plugins.example_plugin.styles import EXAMPLE_CONTAINER_SIZE


def example_layout() -> dmc.Container:
    """Create the example plugin layout.

    Returns:
        dmc.Container: A container with the example plugin layout including
            title, description, feature statistics, and informational content.
    """
    return dmc.Container(
        dmc.Stack(
            [
                dmc.Title("Example Plugin", order=2),
                dmc.Text(
                    "This example plugin demonstrates a lightweight page built with Dash Mantine Components.",
                    c="dimmed",
                ),
                dmc.SimpleGrid(
                    [
                        create_example_stat("Status", "Ready", "carbon:checkmark"),
                        create_example_stat("Layouts", "Separated", "carbon:layers"),
                        create_example_stat("Callbacks", "Optional", "carbon:connection-signal"),
                    ],
                    cols=1,
                    spacing="md",
                ),
                dmc.Alert(
                    "Enable the template plugin to scaffold new experiences.",
                    color="blue",
                    variant="light",
                ),
            ],
            gap="md",
        ),
        size=EXAMPLE_CONTAINER_SIZE,
        py="xl",
    )
