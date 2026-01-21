"""Layout module for basics plugin.

This module provides lazy-loading layout functions that wrap the pages/basics layouts.
"""

from typing import Callable

from dash.development.base_component import Component


def _create_lazy_layout(module_path: str, function_name: str = "layout") -> Callable[[], Component]:
    """Create a lazy-loading wrapper for a layout function.
    
    Args:
        module_path: Import path to the module (e.g., "aiml_dash.pages.basics.clt")
        function_name: Name of the layout function in the module
        
    Returns:
        Callable that imports and calls the layout function when invoked
    """
    def lazy_layout() -> Component:
        import importlib
        module = importlib.import_module(module_path)
        layout_func = getattr(module, function_name)
        return layout_func()
    
    return lazy_layout


# Create lazy-loading layout functions
clt_layout = _create_lazy_layout("aiml_dash.pages.basics.clt")
compare_means_layout = _create_lazy_layout("aiml_dash.pages.basics.compare_means")
compare_props_layout = _create_lazy_layout("aiml_dash.pages.basics.compare_props")
correlation_layout = _create_lazy_layout("aiml_dash.pages.basics.correlation")
cross_tabs_layout = _create_lazy_layout("aiml_dash.pages.basics.cross_tabs")
goodness_layout = _create_lazy_layout("aiml_dash.pages.basics.goodness")
prob_calc_layout = _create_lazy_layout("aiml_dash.pages.basics.prob_calc")
single_mean_layout = _create_lazy_layout("aiml_dash.pages.basics.single_mean")
single_prop_layout = _create_lazy_layout("aiml_dash.pages.basics.single_prop")

__all__ = [
    "clt_layout",
    "compare_means_layout",
    "compare_props_layout",
    "correlation_layout",
    "cross_tabs_layout",
    "goodness_layout",
    "prob_calc_layout",
    "single_mean_layout",
    "single_prop_layout",
]
