"""Layout module for model plugin.

This module provides lazy-loading layout functions that wrap the pages/model layouts.
"""

from typing import Callable

from dash.development.base_component import Component


def _create_lazy_layout(module_path: str, function_name: str = "layout") -> Callable[[], Component]:
    """Create a lazy-loading wrapper for a layout function.
    
    Args:
        module_path: Import path to the module
        function_name: Name of the layout function in the module
        
    Returns:
        Callable that imports and calls the layout function when invoked
    """
    def lazy_layout() -> Component:
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

__all__ = ["collaborativefiltering_layout", "decisionanalysis_layout", "decisiontree_layout", "evaluateclassification_layout", "evaluateregression_layout", "gradientboosting_layout", "linearregression_layout", "logistic_layout", "logisticregression_layout", "multinomiallogit_layout", "naivebayes_layout", "neuralnetwork_layout", "randomforest_layout", "simulator_layout"]
