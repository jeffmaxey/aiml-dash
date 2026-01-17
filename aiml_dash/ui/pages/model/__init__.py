"""
Model Pages Module
==================

This module contains all model-related pages for the AIML Dash application.
"""

from . import (
    linear_regression,
    logistic_regression,
    multinomial_logit,
    naive_bayes,
    neural_network,
    decision_tree,
    random_forest,
    gradient_boosting,
    evaluate_regression,
    evaluate_classification,
    collaborative_filtering,
    decision_analysis,
    simulator,
)

__all__ = [
    "linear_regression",
    "logistic_regression",
    "multinomial_logit",
    "naive_bayes",
    "neural_network",
    "decision_tree",
    "random_forest",
    "gradient_boosting",
    "evaluate_regression",
    "evaluate_classification",
    "collaborative_filtering",
    "decision_analysis",
    "simulator",
]
