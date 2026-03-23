"""Legacy plugin wrapping existing AIML Dash pages."""

from aiml_dash.plugins.factory import build_plugin_pages
from aiml_dash.plugins.legacy import callbacks
from aiml_dash.plugins.legacy.components import LEGACY_PAGE_DEFINITIONS
from aiml_dash.plugins.legacy.constants import (
    PAGE_DEFINITIONS,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
)
from aiml_dash.plugins.legacy.layout import PAGE_LAYOUTS
from aiml_dash.plugins.models import Plugin


def get_plugin() -> Plugin:
    """Return the legacy pages plugin definition."""
    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=build_plugin_pages(PAGE_DEFINITIONS or LEGACY_PAGE_DEFINITIONS, PAGE_LAYOUTS),
        version=PLUGIN_VERSION,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
