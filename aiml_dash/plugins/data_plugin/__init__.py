"""Data plugin for AIML Dash."""

from aiml_dash.plugins.data_plugin import callbacks
from aiml_dash.plugins.data_plugin.layout import *
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the data plugin definition."""
    
    pages = [
        PluginPage(
            id="manage", label="Manage", icon="carbon:data-table",
            section="Data", order=1, layout=manage_layout,
            description="Manage datasets"
        ),
        PluginPage(
            id="view", label="View", icon="carbon:view",
            section="Data", order=2, layout=view_layout,
            description="View dataset contents"
        ),
        PluginPage(
            id="explore", label="Explore", icon="carbon:explore",
            section="Data", order=3, layout=explore_layout,
            description="Explore data statistics"
        ),
        PluginPage(
            id="transform", label="Transform", icon="carbon:settings-adjust",
            section="Data", order=4, layout=transform_layout,
            description="Transform data"
        ),
        PluginPage(
            id="visualize", label="Visualize", icon="carbon:chart-scatter",
            section="Data", order=5, layout=visualize_layout,
            description="Visualize data"
        ),
        PluginPage(
            id="pivot", label="Pivot", icon="carbon:data-reference",
            section="Data", order=6, layout=pivot_layout,
            description="Pivot tables"
        ),
        PluginPage(
            id="combine", label="Combine", icon="carbon:data-connected",
            section="Data", order=7, layout=combine_layout,
            description="Combine datasets"
        ),
        PluginPage(
            id="report", label="Report", icon="carbon:document",
            section="Data", order=8, layout=report_layout,
            description="Generate reports"
        ),
        PluginPage(
            id="sql-query", label="SQL Query", icon="carbon:data-base",
            section="Data", order=9, layout=sqlquery_layout,
            description="SQL queries"
        ),
    ]
    
    return Plugin(
        id="data",
        name="Data",
        description="Data management and manipulation tools",
        pages=pages,
        version="1.0.0",
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
