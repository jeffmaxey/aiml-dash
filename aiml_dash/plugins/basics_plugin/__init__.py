"""Basics plugin definition.

This module defines the basics plugin for AIML Dash, providing statistical
analysis pages for means, proportions, correlations, and probability calculations.

The plugin follows the standard AIML Dash plugin structure:
- layout.py: Page layout imports from pages/basics
- components.py: Shared UI components
- callbacks.py: Callback registration
- styles.py: Plugin-specific styles
- constants.py: Plugin constants and metadata
"""

from aiml_dash.plugins.basics_plugin import callbacks
from aiml_dash.plugins.basics_plugin.constants import (
    CLT_ICON,
    CLT_ID,
    COMPARE_MEANS_ICON,
    COMPARE_MEANS_ID,
    COMPARE_PROPS_ICON,
    COMPARE_PROPS_ID,
    CORRELATION_ICON,
    CORRELATION_ID,
    CROSS_TABS_ICON,
    CROSS_TABS_ID,
    GOODNESS_ICON,
    GOODNESS_ID,
    MEANS_GROUP,
    PLUGIN_DESCRIPTION,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PROB_CALC_ICON,
    PROB_CALC_ID,
    PROPORTIONS_GROUP,
    SECTION_NAME,
    SINGLE_MEAN_ICON,
    SINGLE_MEAN_ID,
    SINGLE_PROP_ICON,
    SINGLE_PROP_ID,
    TABLES_GROUP,
)
from aiml_dash.plugins.basics_plugin.layout import (
    clt_layout,
    compare_means_layout,
    compare_props_layout,
    correlation_layout,
    cross_tabs_layout,
    goodness_layout,
    prob_calc_layout,
    single_mean_layout,
    single_prop_layout,
)
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the basics plugin definition.

    Returns:
        Plugin: The basics plugin containing statistical analysis pages.
    """
    pages = [
        # Means group
        PluginPage(
            id=SINGLE_MEAN_ID,
            label="Single Mean",
            icon=SINGLE_MEAN_ICON,
            section=SECTION_NAME,
            group=MEANS_GROUP,
            order=1,
            group_order=1,
            layout=single_mean_layout,
            description="Test a single population mean",
        ),
        PluginPage(
            id=COMPARE_MEANS_ID,
            label="Compare Means",
            icon=COMPARE_MEANS_ICON,
            section=SECTION_NAME,
            group=MEANS_GROUP,
            order=2,
            group_order=1,
            layout=compare_means_layout,
            description="Compare two population means",
        ),
        # Proportions group
        PluginPage(
            id=SINGLE_PROP_ID,
            label="Single Proportion",
            icon=SINGLE_PROP_ICON,
            section=SECTION_NAME,
            group=PROPORTIONS_GROUP,
            order=1,
            group_order=2,
            layout=single_prop_layout,
            description="Test a single population proportion",
        ),
        PluginPage(
            id=COMPARE_PROPS_ID,
            label="Compare Proportions",
            icon=COMPARE_PROPS_ICON,
            section=SECTION_NAME,
            group=PROPORTIONS_GROUP,
            order=2,
            group_order=2,
            layout=compare_props_layout,
            description="Compare two population proportions",
        ),
        # Tables group
        PluginPage(
            id=CROSS_TABS_ID,
            label="Cross-tabs",
            icon=CROSS_TABS_ICON,
            section=SECTION_NAME,
            group=TABLES_GROUP,
            order=1,
            group_order=3,
            layout=cross_tabs_layout,
            description="Cross-tabulation and chi-square tests",
        ),
        PluginPage(
            id=GOODNESS_ID,
            label="Goodness of Fit",
            icon=GOODNESS_ICON,
            section=SECTION_NAME,
            group=TABLES_GROUP,
            order=2,
            group_order=3,
            layout=goodness_layout,
            description="Chi-square goodness of fit test",
        ),
        # Other basics pages
        PluginPage(
            id=CORRELATION_ID,
            label="Correlation",
            icon=CORRELATION_ICON,
            section=SECTION_NAME,
            order=7,
            layout=correlation_layout,
            description="Correlation analysis",
        ),
        PluginPage(
            id=PROB_CALC_ID,
            label="Probability Calculator",
            icon=PROB_CALC_ICON,
            section=SECTION_NAME,
            order=8,
            layout=prob_calc_layout,
            description="Calculate probabilities from distributions",
        ),
        PluginPage(
            id=CLT_ID,
            label="CLT Simulation",
            icon=CLT_ICON,
            section=SECTION_NAME,
            order=9,
            layout=clt_layout,
            description="Central Limit Theorem demonstration",
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
