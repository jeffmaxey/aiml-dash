"""Layout mapping for legacy pages."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module

from dash.development.base_component import Component


def _lazy_layout(module_path: str) -> Callable[[], Component]:
    """Create a lazy layout loader."""

    def _layout() -> Component:
        from typing import cast
        module = import_module(module_path)
        return cast(Component, module.layout())

    return _layout


PAGE_LAYOUTS = {
    "manage": _lazy_layout("aiml_dash.pages.data.manage"),
    "view": _lazy_layout("aiml_dash.pages.data.view"),
    "explore": _lazy_layout("aiml_dash.pages.data.explore"),
    "transform": _lazy_layout("aiml_dash.pages.data.transform"),
    "visualize": _lazy_layout("aiml_dash.pages.data.visualize"),
    "pivot": _lazy_layout("aiml_dash.pages.data.pivot"),
    "combine": _lazy_layout("aiml_dash.pages.data.combine"),
    "report": _lazy_layout("aiml_dash.pages.data.report"),
    "sql-query": _lazy_layout("aiml_dash.pages.data.sql_query"),
    "doe": _lazy_layout("aiml_dash.pages.design.doe"),
    "sampling": _lazy_layout("aiml_dash.pages.design.sampling"),
    "sample_size": _lazy_layout("aiml_dash.pages.design.sample_size"),
    "sample_size_comp": _lazy_layout("aiml_dash.pages.design.sample_size_comp"),
    "randomizer": _lazy_layout("aiml_dash.pages.design.randomizer"),
    "linear-regression": _lazy_layout("aiml_dash.pages.model.linear_regression"),
    "logistic-regression": _lazy_layout("aiml_dash.pages.model.logistic_regression"),
    "multinomial-logit": _lazy_layout("aiml_dash.pages.model.multinomial_logit"),
    "naive-bayes": _lazy_layout("aiml_dash.pages.model.naive_bayes"),
    "neural-network": _lazy_layout("aiml_dash.pages.model.neural_network"),
    "decision-tree": _lazy_layout("aiml_dash.pages.model.decision_tree"),
    "random-forest": _lazy_layout("aiml_dash.pages.model.random_forest"),
    "gradient-boosting": _lazy_layout("aiml_dash.pages.model.gradient_boosting"),
    "evaluate-regression": _lazy_layout("aiml_dash.pages.model.evaluate_regression"),
    "evaluate-classification": _lazy_layout("aiml_dash.pages.model.evaluate_classification"),
    "collaborative-filtering": _lazy_layout("aiml_dash.pages.model.collaborative_filtering"),
    "decision-analysis": _lazy_layout("aiml_dash.pages.model.decision_analysis"),
    "simulator": _lazy_layout("aiml_dash.pages.model.simulator"),
    "pre-factor": _lazy_layout("aiml_dash.pages.multivariate.pre_factor"),
    "full-factor": _lazy_layout("aiml_dash.pages.multivariate.full_factor"),
    "kmeans-cluster": _lazy_layout("aiml_dash.pages.multivariate.kmeans_cluster"),
    "hierarchical-cluster": _lazy_layout("aiml_dash.pages.multivariate.hierarchical_cluster"),
    "perceptual-map": _lazy_layout("aiml_dash.pages.multivariate.perceptual_map"),
    "mds": _lazy_layout("aiml_dash.pages.multivariate.mds"),
    "conjoint": _lazy_layout("aiml_dash.pages.multivariate.conjoint"),
    "single-mean": _lazy_layout("aiml_dash.pages.basics.single_mean"),
    "compare-means": _lazy_layout("aiml_dash.pages.basics.compare_means"),
    "single-prop": _lazy_layout("aiml_dash.pages.basics.single_prop"),
    "compare-props": _lazy_layout("aiml_dash.pages.basics.compare_props"),
    "cross-tabs": _lazy_layout("aiml_dash.pages.basics.cross_tabs"),
    "goodness": _lazy_layout("aiml_dash.pages.basics.goodness"),
    "correlation": _lazy_layout("aiml_dash.pages.basics.correlation"),
    "clt": _lazy_layout("aiml_dash.pages.basics.clt"),
    "prob-calc": _lazy_layout("aiml_dash.pages.basics.prob_calc"),
}
