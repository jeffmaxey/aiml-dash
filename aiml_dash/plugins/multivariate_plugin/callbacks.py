"""Callbacks for the multivariate plugin.

This module handles callback registration for the multivariate plugin by
importing the page modules, which triggers their @callback decorators and
pre-registers all interactive callbacks at application startup.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

_PAGE_MODULES = [
    "aiml_dash.pages.multivariate.conjoint",
    "aiml_dash.pages.multivariate.full_factor",
    "aiml_dash.pages.multivariate.hierarchical_cluster",
    "aiml_dash.pages.multivariate.kmeans_cluster",
    "aiml_dash.pages.multivariate.mds",
    "aiml_dash.pages.multivariate.perceptual_map",
    "aiml_dash.pages.multivariate.pre_factor",
]


def register_callbacks(_app: object) -> None:
    """Register callbacks for the multivariate plugin.

    Imports each multivariate page module so that their @callback decorators
    execute and register all interactive callbacks with the Dash application.

    Args:
        _app: The Dash application instance (unused; callbacks use global registry).
    """
    for module_path in _PAGE_MODULES:
        try:
            importlib.import_module(module_path)
        except ImportError as exc:
            logger.warning("Could not import %s for callback registration: %s", module_path, exc)
