"""Layout module for design plugin.

This module provides lazy-loading layout functions that wrap
plugin-owned design layouts.
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
doe_layout = _create_lazy_layout("aiml_dash.plugins.design_plugin.pages.doe")
randomizer_layout = _create_lazy_layout(
    "aiml_dash.plugins.design_plugin.pages.randomizer"
)
samplesize_layout = _create_lazy_layout(
    "aiml_dash.plugins.design_plugin.pages.sample_size"
)
samplesizecomp_layout = _create_lazy_layout(
    "aiml_dash.plugins.design_plugin.pages.sample_size_comp"
)
sampling_layout = _create_lazy_layout("aiml_dash.plugins.design_plugin.pages.sampling")

__all__ = [
    "doe_layout",
    "randomizer_layout",
    "samplesize_layout",
    "samplesizecomp_layout",
    "sampling_layout",
]
