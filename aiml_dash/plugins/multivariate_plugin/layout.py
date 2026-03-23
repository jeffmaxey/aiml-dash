"""Layout module for multivariate plugin.

This module provides lazy-loading layout functions that wrap
plugin-owned multivariate layouts.
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
conjoint_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.conjoint"
)
fullfactor_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.full_factor"
)
hierarchicalcluster_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.hierarchical_cluster"
)
kmeanscluster_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.kmeans_cluster"
)
mds_layout = _create_lazy_layout("aiml_dash.plugins.multivariate_plugin.pages.mds")
perceptualmap_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.perceptual_map"
)
prefactor_layout = _create_lazy_layout(
    "aiml_dash.plugins.multivariate_plugin.pages.pre_factor"
)

__all__ = [
    "conjoint_layout",
    "fullfactor_layout",
    "hierarchicalcluster_layout",
    "kmeanscluster_layout",
    "mds_layout",
    "perceptualmap_layout",
    "prefactor_layout",
]
