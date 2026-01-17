"""Core plugin providing home, help, and settings pages."""

from aiml_dash.plugins.core import callbacks
from aiml_dash.plugins.core.layout import help_layout, home_layout, settings_layout
from aiml_dash.plugins.models import HOME_PAGE_ID, Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the core plugin definition."""

    pages = [
        PluginPage(
            id=HOME_PAGE_ID,
            label="Home",
            icon="carbon:home",
            section="Core",
            order=1,
            layout=home_layout,
        ),
        PluginPage(
            id="settings",
            label="Settings",
            icon="carbon:settings",
            section="Core",
            order=2,
            layout=settings_layout,
        ),
        PluginPage(
            id="help",
            label="Help",
            icon="carbon:help",
            section="Core",
            order=3,
            layout=help_layout,
        ),
    ]

    return Plugin(
        id="core",
        name="Core Pages",
        description="Home, settings, and help documentation for AIML Dash.",
        pages=pages,
        default_enabled=True,
        locked=True,
        register_callbacks=callbacks.register_callbacks,
    )
