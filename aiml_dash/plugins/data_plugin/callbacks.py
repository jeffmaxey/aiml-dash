"""Callbacks for the data plugin.

This module handles callback registration for the data plugin by importing
the page modules, which triggers their @callback decorators and pre-registers
all interactive callbacks at application startup.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

_PAGE_MODULES = [
    "aiml_dash.pages.data.combine",
    "aiml_dash.pages.data.explore",
    "aiml_dash.pages.data.manage",
    "aiml_dash.pages.data.pivot",
    "aiml_dash.pages.data.report",
    "aiml_dash.pages.data.sql_query",
    "aiml_dash.pages.data.transform",
    "aiml_dash.pages.data.view",
    "aiml_dash.pages.data.visualize",
]


def register_callbacks(_app: object) -> None:
    """Register callbacks for the data plugin.

    Imports each data page module so that their @callback decorators execute
    and register all interactive callbacks with the Dash application.

    Args:
        _app: The Dash application instance (unused; callbacks use global registry).
    """
    for module_path in _PAGE_MODULES:
        try:
            importlib.import_module(module_path)
        except ImportError as exc:
            logger.warning("Could not import %s for callback registration: %s", module_path, exc)
