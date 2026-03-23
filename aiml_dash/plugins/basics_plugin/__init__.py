"""Basics plugin definition."""

from aiml_dash.plugins.basics_plugin import callbacks
from aiml_dash.plugins.basics_plugin.constants import (
    PAGE_DEFINITIONS,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
)
from aiml_dash.plugins.basics_plugin.layout import PAGE_LAYOUTS
from aiml_dash.plugins.factory import build_plugin
from aiml_dash.plugins.models import Plugin


def get_plugin() -> Plugin:
    """Return the basics plugin definition."""
    return build_plugin(
        plugin_id=PLUGIN_ID,
        plugin_name=PLUGIN_NAME,
        plugin_description=PLUGIN_DESCRIPTION,
        plugin_version=PLUGIN_VERSION,
        page_definitions=PAGE_DEFINITIONS,
        page_layouts=PAGE_LAYOUTS,
        register_callbacks=callbacks.register_callbacks,
        default_enabled=True,
        locked=False,
    )
