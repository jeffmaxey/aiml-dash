"""Callback registration for the basics plugin.

This module handles callback registration for the basics plugin.
Callbacks are defined in the individual page modules in pages/basics/.
"""


def register_callbacks(_app: object) -> None:
    """Register callbacks for the basics plugin.

    Args:
        _app: The Dash application instance.

    Note:
        Callbacks are registered automatically when page modules are imported.
        The individual page files in pages/basics/ contain @callback decorators
        that auto-register when imported.
    """
    # Callbacks are auto-registered via @callback decorators in page modules
    pass
