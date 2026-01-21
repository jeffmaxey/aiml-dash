"""Layout module for data plugin.

This module provides lazy-loading layout functions that wrap the pages/data layouts.
"""

from typing import Callable

from dash.development.base_component import Component


def _create_lazy_layout(module_path: str, function_name: str = "layout") -> Callable[[], Component]:
    """Create a lazy-loading wrapper for a layout function.
    
    Args:
        module_path: Import path to the module
        function_name: Name of the layout function in the module
        
    Returns:
        Callable that imports and calls the layout function when invoked
    """
    def lazy_layout() -> Component:
        import importlib
        from typing import cast
        module = importlib.import_module(module_path)
        layout_func = getattr(module, function_name)
        return cast(Component, layout_func())
    
    return lazy_layout


# Create lazy-loading layout functions
combine_layout = _create_lazy_layout("aiml_dash.pages.data.combine")
explore_layout = _create_lazy_layout("aiml_dash.pages.data.explore")
manage_layout = _create_lazy_layout("aiml_dash.pages.data.manage")
pivot_layout = _create_lazy_layout("aiml_dash.pages.data.pivot")
report_layout = _create_lazy_layout("aiml_dash.pages.data.report")
sqlquery_layout = _create_lazy_layout("aiml_dash.pages.data.sql_query")
transform_layout = _create_lazy_layout("aiml_dash.pages.data.transform")
view_layout = _create_lazy_layout("aiml_dash.pages.data.view")
visualize_layout = _create_lazy_layout("aiml_dash.pages.data.visualize")

__all__ = ["combine_layout", "explore_layout", "manage_layout", "pivot_layout", "report_layout", "sqlquery_layout", "transform_layout", "view_layout", "visualize_layout"]
