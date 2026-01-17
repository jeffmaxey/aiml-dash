"""Template plugin definition."""

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.template_plugin import callbacks
from aiml_dash.plugins.template_plugin.layout import template_layout


def get_plugin() -> Plugin:
    """Return the template plugin definition."""

    pages = [
        PluginPage(
            id="template",
            label="Template",
            icon="carbon:template",
            section="Plugins",
            group="Template Plugin",
            order=1,
            group_order=1,
            layout=template_layout,
        )
    ]

    return Plugin(
        id="template",
        name="Template Plugin",
        description="Starter template for creating new AIML Dash plugins.",
        pages=pages,
        default_enabled=False,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
