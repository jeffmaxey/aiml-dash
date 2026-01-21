"""Model plugin for AIML Dash."""

from aiml_dash.plugins.model_plugin import callbacks
from aiml_dash.plugins.model_plugin.layout import (
    collaborativefiltering_layout,
    decisionanalysis_layout,
    decisiontree_layout,
    evaluateclassification_layout,
    evaluateregression_layout,
    gradientboosting_layout,
    linearregression_layout,
    logistic_layout,
    logisticregression_layout,
    multinomiallogit_layout,
    naivebayes_layout,
    neuralnetwork_layout,
    randomforest_layout,
    simulator_layout,
)
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the model plugin definition."""
    
    pages = [
        PluginPage(
            id="linear-regression", label="Linear Regression", icon="carbon:chart-line",
            section="Model", group="Regression", order=1, group_order=1,
            layout=linearregression_layout, description="Linear regression modeling"
        ),
        PluginPage(
            id="logistic-regression", label="Logistic Regression", icon="carbon:chart-logistic-regression",
            section="Model", group="Classification", order=1, group_order=2,
            layout=logisticregression_layout, description="Logistic regression modeling"
        ),
        PluginPage(
            id="multinomial-logit", label="Multinomial Logit", icon="carbon:chart-multitype",
            section="Model", group="Classification", order=2, group_order=2,
            layout=multinomiallogit_layout, description="Multinomial logistic regression"
        ),
        PluginPage(
            id="naive-bayes", label="Naive Bayes", icon="carbon:chart-bubble",
            section="Model", group="Classification", order=3, group_order=2,
            layout=naivebayes_layout, description="Naive Bayes classifier"
        ),
        PluginPage(
            id="decision-tree", label="Decision Tree", icon="carbon:tree-view",
            section="Model", group="Trees", order=1, group_order=3,
            layout=decisiontree_layout, description="Decision tree modeling"
        ),
        PluginPage(
            id="random-forest", label="Random Forest", icon="carbon:network-3",
            section="Model", group="Trees", order=2, group_order=3,
            layout=randomforest_layout, description="Random forest ensemble"
        ),
        PluginPage(
            id="gradient-boosting", label="Gradient Boosting", icon="carbon:chart-histogram",
            section="Model", group="Trees", order=3, group_order=3,
            layout=gradientboosting_layout, description="Gradient boosting machines"
        ),
        PluginPage(
            id="neural-network", label="Neural Network", icon="carbon:network-4",
            section="Model", group="Advanced", order=1, group_order=4,
            layout=neuralnetwork_layout, description="Neural network modeling"
        ),
        PluginPage(
            id="collaborative-filtering", label="Collaborative Filtering", icon="carbon:user-multiple",
            section="Model", group="Advanced", order=2, group_order=4,
            layout=collaborativefiltering_layout, description="Recommendation systems"
        ),
        PluginPage(
            id="evaluate-regression", label="Evaluate Regression", icon="carbon:report",
            section="Model", order=10,
            layout=evaluateregression_layout, description="Evaluate regression models"
        ),
        PluginPage(
            id="evaluate-classification", label="Evaluate Classification", icon="carbon:chart-evaluation",
            section="Model", order=11,
            layout=evaluateclassification_layout, description="Evaluate classification models"
        ),
        PluginPage(
            id="simulator", label="Simulator", icon="carbon:simulation",
            section="Model", order=12,
            layout=simulator_layout, description="Monte Carlo simulation"
        ),
        PluginPage(
            id="decision-analysis", label="Decision Analysis", icon="carbon:decision-tree",
            section="Model", order=13,
            layout=decisionanalysis_layout, description="Decision tree analysis"
        ),
        PluginPage(
            id="logistic", label="Logistic", icon="carbon:chart-area",
            section="Model", order=14,
            layout=logistic_layout, description="Logistic growth modeling"
        ),
    ]
    
    return Plugin(
        id="model",
        name="Model",
        description="Machine learning and statistical modeling tools",
        pages=pages,
        version="1.0.0",
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
