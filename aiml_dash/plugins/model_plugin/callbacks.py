"""Callback registration for the model plugin.

This module handles callback registration for the model plugin by importing
the page modules, which triggers their @callback decorators and pre-registers
all interactive callbacks at application startup.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

_PAGE_MODULES = [
    "aiml_dash.pages.model.collaborative_filtering",
    "aiml_dash.pages.model.decision_analysis",
    "aiml_dash.pages.model.decision_tree",
    "aiml_dash.pages.model.evaluate_classification",
    "aiml_dash.pages.model.evaluate_regression",
    "aiml_dash.pages.model.gradient_boosting",
    "aiml_dash.pages.model.linear_regression",
    "aiml_dash.pages.model.logistic",
    "aiml_dash.pages.model.logistic_regression",
    "aiml_dash.pages.model.multinomial_logit",
    "aiml_dash.pages.model.naive_bayes",
    "aiml_dash.pages.model.neural_network",
    "aiml_dash.pages.model.random_forest",
    "aiml_dash.pages.model.simulator",
]


def register_callbacks(_app: object) -> None:
    """Register callbacks for the model plugin.

    Imports each model page module so that their @callback decorators execute
    and register all interactive callbacks with the Dash application.

    Args:
        _app: The Dash application instance (unused; callbacks use global registry).
    """
    for module_path in _PAGE_MODULES:
        try:
            importlib.import_module(module_path)
        except ImportError as exc:
            logger.warning("Could not import %s for callback registration: %s", module_path, exc)
