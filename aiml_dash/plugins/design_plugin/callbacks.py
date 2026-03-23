"""Callbacks for the design plugin.

This module handles callback registration for the design plugin by importing
the page modules, which triggers their @callback decorators and pre-registers
all interactive callbacks at application startup.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

_PAGE_MODULES = [
    "aiml_dash.pages.design.doe",
    "aiml_dash.pages.design.randomizer",
    "aiml_dash.pages.design.sample_size",
    "aiml_dash.pages.design.sample_size_comp",
    "aiml_dash.pages.design.sampling",
]


def register_callbacks(_app: object) -> None:
    """Register callbacks for the design plugin.

    Imports each design page module so that their @callback decorators execute
    and register all interactive callbacks with the Dash application.

    Args:
        _app: The Dash application instance (unused; callbacks use global registry).
    """
    for module_path in _PAGE_MODULES:
        try:
            importlib.import_module(module_path)
        except ImportError as exc:
            logger.warning("Could not import %s for callback registration: %s", module_path, exc)
