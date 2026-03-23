"""Callback registration for the example plugin.

This module handles callback registration for the example plugin. Callbacks
are optional in plugins and should be defined here when interactivity is needed.

Note:
    The example plugin does not require any callbacks as it displays static
    content. For interactive plugins, define callbacks using the @callback
    decorator and register them in the register_callbacks function.
"""


def register_callbacks(_app: object) -> None:
    """Register callbacks for the example plugin.

    Parameters
    ----------
    _app : object
        Value provided for this parameter."""
    ...
