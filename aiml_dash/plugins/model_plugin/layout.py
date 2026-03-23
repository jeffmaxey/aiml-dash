"""Layout module for model plugin.

This module provides lazy-loading layout functions that wrap the canonical
application page modules under ``aiml_dash.pages.model``.
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
collaborativefiltering_layout = _create_lazy_layout("aiml_dash.pages.model.collaborative_filtering")
decisionanalysis_layout = _create_lazy_layout("aiml_dash.pages.model.decision_analysis")
decisiontree_layout = _create_lazy_layout("aiml_dash.pages.model.decision_tree")
evaluateclassification_layout = _create_lazy_layout("aiml_dash.pages.model.evaluate_classification")
evaluateregression_layout = _create_lazy_layout("aiml_dash.pages.model.evaluate_regression")
gradientboosting_layout = _create_lazy_layout("aiml_dash.pages.model.gradient_boosting")
linearregression_layout = _create_lazy_layout("aiml_dash.pages.model.linear_regression")
logistic_layout = _create_lazy_layout("aiml_dash.pages.model.logistic")
logisticregression_layout = _create_lazy_layout("aiml_dash.pages.model.logistic_regression")
multinomiallogit_layout = _create_lazy_layout("aiml_dash.pages.model.multinomial_logit")
naivebayes_layout = _create_lazy_layout("aiml_dash.pages.model.naive_bayes")
neuralnetwork_layout = _create_lazy_layout("aiml_dash.pages.model.neural_network")
randomforest_layout = _create_lazy_layout("aiml_dash.pages.model.random_forest")
simulator_layout = _create_lazy_layout("aiml_dash.pages.model.simulator")

PAGE_LAYOUTS = {
    "collaborative-filtering": collaborativefiltering_layout,
    "decision-analysis": decisionanalysis_layout,
    "decision-tree": decisiontree_layout,
    "evaluate-classification": evaluateclassification_layout,
    "evaluate-regression": evaluateregression_layout,
    "gradient-boosting": gradientboosting_layout,
    "linear-regression": linearregression_layout,
    "logistic": logistic_layout,
    "logistic-regression": logisticregression_layout,
    "multinomial-logit": multinomiallogit_layout,
    "naive-bayes": naivebayes_layout,
    "neural-network": neuralnetwork_layout,
    "random-forest": randomforest_layout,
    "simulator": simulator_layout,
}

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
    "PAGE_LAYOUTS",
]
