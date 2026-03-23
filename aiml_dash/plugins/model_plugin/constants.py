"""Constants for the model plugin.

This module defines plugin-specific constants used throughout the model plugin.
"""

# Plugin metadata
PLUGIN_ID = "model"
PLUGIN_NAME = "Model"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Machine learning and statistical modeling tools."

# Section and ordering
SECTION_NAME = "Model"

# Group names
REGRESSION_GROUP = "Regression"
CLASSIFICATION_GROUP = "Classification"
TREES_GROUP = "Trees"
ADVANCED_GROUP = "Advanced"

# Page identifiers
LINEAR_REGRESSION_ID = "linear-regression"
LOGISTIC_REGRESSION_ID = "logistic-regression"
MULTINOMIAL_LOGIT_ID = "multinomial-logit"
NAIVE_BAYES_ID = "naive-bayes"
DECISION_TREE_ID = "decision-tree"
RANDOM_FOREST_ID = "random-forest"
GRADIENT_BOOSTING_ID = "gradient-boosting"
NEURAL_NETWORK_ID = "neural-network"
COLLABORATIVE_FILTERING_ID = "collaborative-filtering"
EVALUATE_REGRESSION_ID = "evaluate-regression"
EVALUATE_CLASSIFICATION_ID = "evaluate-classification"
SIMULATOR_ID = "simulator"
DECISION_ANALYSIS_ID = "decision-analysis"
LOGISTIC_ID = "logistic"

# Container size
CONTAINER_SIZE = "fluid"

PAGE_DEFINITIONS = [
    {"id": LINEAR_REGRESSION_ID, "label": "Linear Regression", "icon": "carbon:chart-line", "section": SECTION_NAME, "group": REGRESSION_GROUP, "order": 1, "group_order": 1, "description": "Linear regression modeling"},
    {"id": LOGISTIC_REGRESSION_ID, "label": "Logistic Regression", "icon": "carbon:chart-logistic-regression", "section": SECTION_NAME, "group": CLASSIFICATION_GROUP, "order": 1, "group_order": 2, "description": "Logistic regression modeling"},
    {"id": MULTINOMIAL_LOGIT_ID, "label": "Multinomial Logit", "icon": "carbon:chart-multitype", "section": SECTION_NAME, "group": CLASSIFICATION_GROUP, "order": 2, "group_order": 2, "description": "Multinomial logistic regression"},
    {"id": NAIVE_BAYES_ID, "label": "Naive Bayes", "icon": "carbon:chart-bubble", "section": SECTION_NAME, "group": CLASSIFICATION_GROUP, "order": 3, "group_order": 2, "description": "Naive Bayes classifier"},
    {"id": DECISION_TREE_ID, "label": "Decision Tree", "icon": "carbon:tree-view", "section": SECTION_NAME, "group": TREES_GROUP, "order": 1, "group_order": 3, "description": "Decision tree modeling"},
    {"id": RANDOM_FOREST_ID, "label": "Random Forest", "icon": "carbon:network-3", "section": SECTION_NAME, "group": TREES_GROUP, "order": 2, "group_order": 3, "description": "Random forest ensemble"},
    {"id": GRADIENT_BOOSTING_ID, "label": "Gradient Boosting", "icon": "carbon:chart-histogram", "section": SECTION_NAME, "group": TREES_GROUP, "order": 3, "group_order": 3, "description": "Gradient boosting machines"},
    {"id": NEURAL_NETWORK_ID, "label": "Neural Network", "icon": "carbon:network-4", "section": SECTION_NAME, "group": ADVANCED_GROUP, "order": 1, "group_order": 4, "description": "Neural network modeling"},
    {"id": COLLABORATIVE_FILTERING_ID, "label": "Collaborative Filtering", "icon": "carbon:user-multiple", "section": SECTION_NAME, "group": ADVANCED_GROUP, "order": 2, "group_order": 4, "description": "Recommendation systems"},
    {"id": EVALUATE_REGRESSION_ID, "label": "Evaluate Regression", "icon": "carbon:report", "section": SECTION_NAME, "order": 10, "description": "Evaluate regression models"},
    {"id": EVALUATE_CLASSIFICATION_ID, "label": "Evaluate Classification", "icon": "carbon:chart-evaluation", "section": SECTION_NAME, "order": 11, "description": "Evaluate classification models"},
    {"id": SIMULATOR_ID, "label": "Simulator", "icon": "carbon:chart-line-data", "section": SECTION_NAME, "order": 12, "description": "Monte Carlo simulation"},
    {"id": DECISION_ANALYSIS_ID, "label": "Decision Analysis", "icon": "carbon:decision-tree", "section": SECTION_NAME, "order": 13, "description": "Decision tree analysis"},
    {"id": LOGISTIC_ID, "label": "Logistic", "icon": "carbon:chart-area", "section": SECTION_NAME, "order": 14, "description": "Logistic growth modeling"},
]
