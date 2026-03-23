"""Constants for the basics plugin.

This module defines plugin-specific constants used throughout the basics plugin,
including page IDs, default values, and configuration settings.
"""

# Plugin metadata
PLUGIN_ID = "basics"
PLUGIN_NAME = "Basics"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Basic statistical analysis tools including means, proportions, and probability calculations."

# Section and ordering
SECTION_NAME = "Basics"

# Icons
SINGLE_MEAN_ICON = "carbon:chart-average"
COMPARE_MEANS_ICON = "carbon:compare"
SINGLE_PROP_ICON = "carbon:percentage"
COMPARE_PROPS_ICON = "carbon:chart-bar-stacked"
CROSS_TABS_ICON = "carbon:table-split"
GOODNESS_ICON = "carbon:chart-pie"
CORRELATION_ICON = "carbon:chart-line"
PROB_CALC_ICON = "carbon:calculator"
CLT_ICON = "mdi:chart-bell-curve-cumulative"

# Page IDs
SINGLE_MEAN_ID = "single-mean"
COMPARE_MEANS_ID = "compare-means"
SINGLE_PROP_ID = "single-prop"
COMPARE_PROPS_ID = "compare-props"
CROSS_TABS_ID = "cross-tabs"
GOODNESS_ID = "goodness"
CORRELATION_ID = "correlation"
PROB_CALC_ID = "prob-calc"
CLT_ID = "clt"

# Group names
MEANS_GROUP = "Means"
PROPORTIONS_GROUP = "Proportions"
TABLES_GROUP = "Tables"

# Group ordering
MEANS_GROUP_ORDER = 1
PROPORTIONS_GROUP_ORDER = 2
TABLES_GROUP_ORDER = 3

# Page ordering
SINGLE_MEAN_ORDER = 1
COMPARE_MEANS_ORDER = 2
SINGLE_PROP_ORDER = 1
COMPARE_PROPS_ORDER = 2
CROSS_TABS_ORDER = 1
GOODNESS_ORDER = 2
CORRELATION_ORDER = 7
PROB_CALC_ORDER = 8
CLT_ORDER = 9

# Container size
CONTAINER_SIZE = "fluid"

PAGE_DEFINITIONS = [
    {"id": SINGLE_MEAN_ID, "label": "Single Mean", "icon": SINGLE_MEAN_ICON, "section": SECTION_NAME, "group": MEANS_GROUP, "order": SINGLE_MEAN_ORDER, "group_order": MEANS_GROUP_ORDER, "description": "Test a single population mean"},
    {"id": COMPARE_MEANS_ID, "label": "Compare Means", "icon": COMPARE_MEANS_ICON, "section": SECTION_NAME, "group": MEANS_GROUP, "order": COMPARE_MEANS_ORDER, "group_order": MEANS_GROUP_ORDER, "description": "Compare two population means"},
    {"id": SINGLE_PROP_ID, "label": "Single Proportion", "icon": SINGLE_PROP_ICON, "section": SECTION_NAME, "group": PROPORTIONS_GROUP, "order": SINGLE_PROP_ORDER, "group_order": PROPORTIONS_GROUP_ORDER, "description": "Test a single population proportion"},
    {"id": COMPARE_PROPS_ID, "label": "Compare Proportions", "icon": COMPARE_PROPS_ICON, "section": SECTION_NAME, "group": PROPORTIONS_GROUP, "order": COMPARE_PROPS_ORDER, "group_order": PROPORTIONS_GROUP_ORDER, "description": "Compare two population proportions"},
    {"id": CROSS_TABS_ID, "label": "Cross-tabs", "icon": CROSS_TABS_ICON, "section": SECTION_NAME, "group": TABLES_GROUP, "order": CROSS_TABS_ORDER, "group_order": TABLES_GROUP_ORDER, "description": "Cross-tabulation and chi-square tests"},
    {"id": GOODNESS_ID, "label": "Goodness of Fit", "icon": GOODNESS_ICON, "section": SECTION_NAME, "group": TABLES_GROUP, "order": GOODNESS_ORDER, "group_order": TABLES_GROUP_ORDER, "description": "Chi-square goodness of fit test"},
    {"id": CORRELATION_ID, "label": "Correlation", "icon": CORRELATION_ICON, "section": SECTION_NAME, "order": CORRELATION_ORDER, "description": "Correlation analysis"},
    {"id": PROB_CALC_ID, "label": "Probability Calculator", "icon": PROB_CALC_ICON, "section": SECTION_NAME, "order": PROB_CALC_ORDER, "description": "Calculate probabilities from distributions"},
    {"id": CLT_ID, "label": "CLT Simulation", "icon": CLT_ICON, "section": SECTION_NAME, "order": CLT_ORDER, "description": "Central Limit Theorem demonstration"},
]
