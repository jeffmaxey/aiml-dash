"""Legacy plugin wrapping existing AIML Dash pages."""

from aiml_dash.plugins.legacy import callbacks
from aiml_dash.plugins.legacy.components import LEGACY_PAGE_DEFINITIONS
from aiml_dash.plugins.legacy.layout import PAGE_LAYOUTS
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the legacy pages plugin definition."""

    pages = [
        PluginPage(
            id=definition["id"],
            label=definition["label"],
            icon=definition["icon"],
            section=definition["section"],
            group=definition.get("group"),
            order=definition.get("order", 0),
            group_order=definition.get("group_order", 0),
            description=definition.get("description"),
            layout=PAGE_LAYOUTS[definition["id"]],
        )
        for definition in LEGACY_PAGE_DEFINITIONS
    ]

    return Plugin(
        id="legacy",
        name="Legacy Pages",
        description="Built-in AIML Dash pages from the original application.",
        pages=pages,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
