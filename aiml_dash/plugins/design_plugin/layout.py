"""Layout module for design plugin.

This module provides lazy-loading layout functions that wrap the pages/design layouts.
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
        module = importlib.import_module(module_path)
        layout_func = getattr(module, function_name)
        return layout_func()
    
    return lazy_layout


# Create lazy-loading layout functions
doe_layout = _create_lazy_layout("aiml_dash.pages.design.doe")
randomizer_layout = _create_lazy_layout("aiml_dash.pages.design.randomizer")
samplesize_layout = _create_lazy_layout("aiml_dash.pages.design.sample_size")
samplesizecomp_layout = _create_lazy_layout("aiml_dash.pages.design.sample_size_comp")
sampling_layout = _create_lazy_layout("aiml_dash.pages.design.sampling")

__all__ = ["doe_layout", "randomizer_layout", "samplesize_layout", "samplesizecomp_layout", "sampling_layout"]
