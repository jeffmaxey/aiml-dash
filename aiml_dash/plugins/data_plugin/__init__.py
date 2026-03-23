"""Data plugin definition.

This module defines the data plugin for AIML Dash and its page registry.
"""

from aiml_dash.plugins.data_plugin import callbacks
from aiml_dash.plugins.data_plugin.constants import (COMBINE_ICON, COMBINE_ID,
                                                     EXPLORE_ICON, EXPLORE_ID,
                                                     MANAGE_ICON, MANAGE_ID,
                                                     PIVOT_ICON, PIVOT_ID,
                                                     PLUGIN_DESCRIPTION,
                                                     PLUGIN_ID, PLUGIN_NAME,
                                                     PLUGIN_VERSION,
                                                     REPORT_ICON, REPORT_ID,
                                                     SECTION_NAME,
                                                     SQL_QUERY_ICON,
                                                     SQL_QUERY_ID,
                                                     TRANSFORM_ICON,
                                                     TRANSFORM_ID, VIEW_ICON,
                                                     VIEW_ID, VISUALIZE_ICON,
                                                     VISUALIZE_ID)
from aiml_dash.plugins.data_plugin.layout import (combine_layout,
                                                  explore_layout,
                                                  manage_layout, pivot_layout,
                                                  report_layout,
                                                  sqlquery_layout,
                                                  transform_layout,
                                                  view_layout,
                                                  visualize_layout)
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the data plugin definition.

    Returns
    -------
    value : Plugin
        Result produced by this function."""

    pages = [
        PluginPage(
            id=MANAGE_ID,
            label="Manage",
            icon=MANAGE_ICON,
            section=SECTION_NAME,
            order=1,
            layout=manage_layout,
            description="Manage datasets",
        ),
        PluginPage(
            id=VIEW_ID,
            label="View",
            icon=VIEW_ICON,
            section=SECTION_NAME,
            order=2,
            layout=view_layout,
            description="View dataset contents",
        ),
        PluginPage(
            id=EXPLORE_ID,
            label="Explore",
            icon=EXPLORE_ICON,
            section=SECTION_NAME,
            order=3,
            layout=explore_layout,
            description="Explore data statistics",
        ),
        PluginPage(
            id=TRANSFORM_ID,
            label="Transform",
            icon=TRANSFORM_ICON,
            section=SECTION_NAME,
            order=4,
            layout=transform_layout,
            description="Transform data",
        ),
        PluginPage(
            id=VISUALIZE_ID,
            label="Visualize",
            icon=VISUALIZE_ICON,
            section=SECTION_NAME,
            order=5,
            layout=visualize_layout,
            description="Visualize data",
        ),
        PluginPage(
            id=PIVOT_ID,
            label="Pivot",
            icon=PIVOT_ICON,
            section=SECTION_NAME,
            order=6,
            layout=pivot_layout,
            description="Pivot tables",
        ),
        PluginPage(
            id=COMBINE_ID,
            label="Combine",
            icon=COMBINE_ICON,
            section=SECTION_NAME,
            order=7,
            layout=combine_layout,
            description="Combine datasets",
        ),
        PluginPage(
            id=REPORT_ID,
            label="Report",
            icon=REPORT_ICON,
            section=SECTION_NAME,
            order=8,
            layout=report_layout,
            description="Generate reports",
        ),
        PluginPage(
            id=SQL_QUERY_ID,
            label="SQL Query",
            icon=SQL_QUERY_ICON,
            section=SECTION_NAME,
            order=9,
            layout=sqlquery_layout,
            description="SQL queries",
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
