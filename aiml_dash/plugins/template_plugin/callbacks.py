"""Callback registration for the template plugin.

This module handles callback registration for the template plugin. Callbacks
are optional in plugins and should be defined here when interactivity is needed.

Note:
    The template plugin does not require any callbacks as it displays static
    instructional content. For interactive plugins, define callbacks using the
    @callback decorator and register them in the register_callbacks function.
"""


def register_callbacks(_app: object) -> None:
    """Register callbacks for the template plugin.

    Args:
        _app: The Dash application instance to register callbacks with.

    Note:
        This plugin does not require any callbacks. The function is provided
        as a placeholder for plugins that need interactivity.
    """
    ...
