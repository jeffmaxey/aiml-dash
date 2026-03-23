"""Layout module for data plugin.

This module provides lazy-loading layout functions that wrap
plugin-owned data layouts.
"""

from collections.abc import Callable
from typing import Any


def _create_lazy_layout(
    module_path: str,
    function_name: str = "layout",
) -> Callable[[], Any]:
    """Create a lazy-loading wrapper for a layout function.

    Parameters
    ----------
    module_path : str
        Dotted import path for the page module.
    function_name : str
        Name of the callable that returns the page layout.

    Returns
    -------
    value : Callable[[], Any]
        Lazily evaluated callable that returns a Dash component tree.
    """

    def lazy_layout() -> Any:
        import importlib

        module = importlib.import_module(module_path)
        layout_func = getattr(module, function_name)
        return layout_func()

    return lazy_layout


# Create lazy-loading layout functions
combine_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.combine")
explore_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.explore")
manage_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.manage")
pivot_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.pivot")
report_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.report")
sqlquery_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.sql_query")
transform_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.transform")
view_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.view")
visualize_layout = _create_lazy_layout("aiml_dash.plugins.data_plugin.pages.visualize")

__all__ = [
    "combine_layout",
    "explore_layout",
    "manage_layout",
    "pivot_layout",
    "report_layout",
    "sqlquery_layout",
    "transform_layout",
    "view_layout",
    "visualize_layout",
]
