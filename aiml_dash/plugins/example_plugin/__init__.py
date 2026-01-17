"""Example plugin definition."""

from aiml_dash.plugins.example_plugin import callbacks
from aiml_dash.plugins.example_plugin.layout import example_layout
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the example plugin definition."""

    pages = [
        PluginPage(
            id="example",
            label="Example",
            icon="carbon:apps",
            section="Plugins",
            group="Example Plugin",
            order=1,
            group_order=2,
            layout=example_layout,
        )
    ]

    return Plugin(
        id="example",
        name="Example Plugin",
        description="Sample plugin showcasing a minimal Dash Mantine page.",
        pages=pages,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
