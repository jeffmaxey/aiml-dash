"""Layout module for model plugin.

This module provides lazy-loading layout functions that wrap
plugin-owned model layouts.
"""

from collections.abc import Callable
from typing import Any


def _create_lazy_layout(
    module_path: str,
    function_name: str = "layout",
) -> Callable[[], Any]:
    """Create a lazy-loading wrapper for a layout function.

    Parameters
    ----------
    module_path : str
        Dotted import path for the page module.
    function_name : str
        Name of the callable that returns the page layout.

    Returns
    -------
    value : Callable[[], Any]
        Lazily evaluated callable that returns a Dash component tree.
    """

    def lazy_layout() -> Any:
        import importlib

        module = importlib.import_module(module_path)
        layout_func = getattr(module, function_name)
        return layout_func()

    return lazy_layout


# Create lazy-loading layout functions
collaborativefiltering_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.collaborative_filtering"
)
decisionanalysis_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.decision_analysis"
)
decisiontree_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.decision_tree"
)
evaluateclassification_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.evaluate_classification"
)
evaluateregression_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.evaluate_regression"
)
gradientboosting_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.gradient_boosting"
)
linearregression_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.linear_regression"
)
logistic_layout = _create_lazy_layout("aiml_dash.plugins.model_plugin.pages.logistic")
logisticregression_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.logistic_regression"
)
multinomiallogit_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.multinomial_logit"
)
naivebayes_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.naive_bayes"
)
neuralnetwork_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.neural_network"
)
randomforest_layout = _create_lazy_layout(
    "aiml_dash.plugins.model_plugin.pages.random_forest"
)
simulator_layout = _create_lazy_layout("aiml_dash.plugins.model_plugin.pages.simulator")

__all__ = [
    "collaborativefiltering_layout",
    "decisionanalysis_layout",
    "decisiontree_layout",
    "evaluateclassification_layout",
    "evaluateregression_layout",
    "gradientboosting_layout",
    "linearregression_layout",
    "logistic_layout",
    "logisticregression_layout",
    "multinomiallogit_layout",
    "naivebayes_layout",
    "neuralnetwork_layout",
    "randomforest_layout",
    "simulator_layout",
]
