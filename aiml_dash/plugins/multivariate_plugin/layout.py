"""Layout module for multivariate plugin.

This module provides lazy-loading layout functions that wrap the pages/multivariate layouts.
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
conjoint_layout = _create_lazy_layout("aiml_dash.pages.multivariate.conjoint")
fullfactor_layout = _create_lazy_layout("aiml_dash.pages.multivariate.full_factor")
hierarchicalcluster_layout = _create_lazy_layout("aiml_dash.pages.multivariate.hierarchical_cluster")
kmeanscluster_layout = _create_lazy_layout("aiml_dash.pages.multivariate.kmeans_cluster")
mds_layout = _create_lazy_layout("aiml_dash.pages.multivariate.mds")
perceptualmap_layout = _create_lazy_layout("aiml_dash.pages.multivariate.perceptual_map")
prefactor_layout = _create_lazy_layout("aiml_dash.pages.multivariate.pre_factor")

__all__ = ["conjoint_layout", "fullfactor_layout", "hierarchicalcluster_layout", "kmeanscluster_layout", "mds_layout", "perceptualmap_layout", "prefactor_layout"]
