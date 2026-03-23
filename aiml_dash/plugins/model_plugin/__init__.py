"""Model plugin for AIML Dash."""

from aiml_dash.plugins.model_plugin import callbacks
from aiml_dash.plugins.model_plugin.constants import (
    ADVANCED_GROUP, CLASSIFICATION_GROUP, COLLABORATIVE_FILTERING_ID,
    DECISION_ANALYSIS_ID, DECISION_TREE_ID, EVALUATE_CLASSIFICATION_ID,
    EVALUATE_REGRESSION_ID, GRADIENT_BOOSTING_ID, LINEAR_REGRESSION_ID,
    LOGISTIC_ID, LOGISTIC_REGRESSION_ID, MULTINOMIAL_LOGIT_ID, NAIVE_BAYES_ID,
    NEURAL_NETWORK_ID, PLUGIN_DESCRIPTION, PLUGIN_ID, PLUGIN_NAME,
    PLUGIN_VERSION, RANDOM_FOREST_ID, REGRESSION_GROUP, SECTION_NAME,
    SIMULATOR_ID, TREES_GROUP)
from aiml_dash.plugins.model_plugin.layout import (
    collaborativefiltering_layout, decisionanalysis_layout,
    decisiontree_layout, evaluateclassification_layout,
    evaluateregression_layout, gradientboosting_layout,
    linearregression_layout, logistic_layout, logisticregression_layout,
    multinomiallogit_layout, naivebayes_layout, neuralnetwork_layout,
    randomforest_layout, simulator_layout)
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the model plugin definition.

    Returns
    -------
    value : Plugin
        Result produced by this function."""

    pages = [
        PluginPage(
            id=LINEAR_REGRESSION_ID,
            label="Linear Regression",
            icon="carbon:chart-line",
            section=SECTION_NAME,
            group=REGRESSION_GROUP,
            order=1,
            group_order=1,
            layout=linearregression_layout,
            description="Linear regression modeling",
        ),
        PluginPage(
            id=LOGISTIC_REGRESSION_ID,
            label="Logistic Regression",
            icon="carbon:chart-logistic-regression",
            section=SECTION_NAME,
            group=CLASSIFICATION_GROUP,
            order=1,
            group_order=2,
            layout=logisticregression_layout,
            description="Logistic regression modeling",
        ),
        PluginPage(
            id=MULTINOMIAL_LOGIT_ID,
            label="Multinomial Logit",
            icon="carbon:chart-multitype",
            section=SECTION_NAME,
            group=CLASSIFICATION_GROUP,
            order=2,
            group_order=2,
            layout=multinomiallogit_layout,
            description="Multinomial logistic regression",
        ),
        PluginPage(
            id=NAIVE_BAYES_ID,
            label="Naive Bayes",
            icon="carbon:chart-bubble",
            section=SECTION_NAME,
            group=CLASSIFICATION_GROUP,
            order=3,
            group_order=2,
            layout=naivebayes_layout,
            description="Naive Bayes classifier",
        ),
        PluginPage(
            id=DECISION_TREE_ID,
            label="Decision Tree",
            icon="carbon:tree-view",
            section=SECTION_NAME,
            group=TREES_GROUP,
            order=1,
            group_order=3,
            layout=decisiontree_layout,
            description="Decision tree modeling",
        ),
        PluginPage(
            id=RANDOM_FOREST_ID,
            label="Random Forest",
            icon="carbon:network-3",
            section=SECTION_NAME,
            group=TREES_GROUP,
            order=2,
            group_order=3,
            layout=randomforest_layout,
            description="Random forest ensemble",
        ),
        PluginPage(
            id=GRADIENT_BOOSTING_ID,
            label="Gradient Boosting",
            icon="carbon:chart-histogram",
            section=SECTION_NAME,
            group=TREES_GROUP,
            order=3,
            group_order=3,
            layout=gradientboosting_layout,
            description="Gradient boosting machines",
        ),
        PluginPage(
            id=NEURAL_NETWORK_ID,
            label="Neural Network",
            icon="carbon:network-4",
            section=SECTION_NAME,
            group=ADVANCED_GROUP,
            order=1,
            group_order=4,
            layout=neuralnetwork_layout,
            description="Neural network modeling",
        ),
        PluginPage(
            id=COLLABORATIVE_FILTERING_ID,
            label="Collaborative Filtering",
            icon="carbon:user-multiple",
            section=SECTION_NAME,
            group=ADVANCED_GROUP,
            order=2,
            group_order=4,
            layout=collaborativefiltering_layout,
            description="Recommendation systems",
        ),
        PluginPage(
            id=EVALUATE_REGRESSION_ID,
            label="Evaluate Regression",
            icon="carbon:report",
            section=SECTION_NAME,
            order=10,
            layout=evaluateregression_layout,
            description="Evaluate regression models",
        ),
        PluginPage(
            id=EVALUATE_CLASSIFICATION_ID,
            label="Evaluate Classification",
            icon="carbon:chart-evaluation",
            section=SECTION_NAME,
            order=11,
            layout=evaluateclassification_layout,
            description="Evaluate classification models",
        ),
        PluginPage(
            id=SIMULATOR_ID,
            label="Simulator",
            icon="carbon:simulation",
            section=SECTION_NAME,
            order=12,
            layout=simulator_layout,
            description="Monte Carlo simulation",
        ),
        PluginPage(
            id=DECISION_ANALYSIS_ID,
            label="Decision Analysis",
            icon="carbon:decision-tree",
            section=SECTION_NAME,
            order=13,
            layout=decisionanalysis_layout,
            description="Decision tree analysis",
        ),
        PluginPage(
            id=LOGISTIC_ID,
            label="Logistic",
            icon="carbon:chart-area",
            section=SECTION_NAME,
            order=14,
            layout=logistic_layout,
            description="Logistic growth modeling",
        ),
    ]

    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
