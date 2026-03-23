"""Lightweight wrapper providing a code editor component for Dash apps.

This module provides a unified interface for code editing in Dash applications.
It attempts to use the dash_ace library for a rich editing experience, but
gracefully falls back to a simple textarea when dash_ace is not available.

Examples
--------
Basic usage in a Dash application:

>>> from aiml_data.shinyace import get_code_editor
>>> editor = get_code_editor(
...     id="my-editor",
...     value="# Enter your code here",
...     mode="python",
...     theme="github",
...     height="400px"
... )

Attributes
----------
_HAS_ACE : bool
    Module-level flag indicating dash_ace availability.

Notes
-----
When dash_ace is not available, the module automatically falls back to
using dcc.Textarea, ensuring the application remains functional even
without the optional dependency.
"""

from __future__ import annotations

from typing import Any

from dash import dcc

# Try to import dash_ace; if unavailable, we'll fallback to a textarea
try:
    import dash_ace  # type: ignore[import-untyped]

    _HAS_ACE = True
except Exception:
    _HAS_ACE = False


def get_code_editor(
    editor_id: str,
    value: str = "",
    mode: str = "r",
    theme: str = "github",
    height: str = "300px",
) -> Any:
    """Return a code editor component with automatic fallback support.

    Parameters
    ----------
    editor_id : str
        Input value for ``editor_id``.
    value : str
        Input value for ``value``.
    mode : str
        Input value for ``mode``.
    theme : str
        Input value for ``theme``.
    height : str
        Input value for ``height``.

    Returns
    -------
    value : Any
        Result produced by this function."""
    if _HAS_ACE:
        # Use Ace editor for richer editing experience
        return dash_ace.Ace(
            id=editor_id,
            value=value,
            mode=mode,
            theme=theme,
            showPrintMargin=False,
            tabSize=2,
            enableBasicAutocompletion=True,
            enableLiveAutocompletion=False,
            style={"width": "100%", "height": height},
        )
    # Fallback: plain textarea (works reliably without extra dependencies)
    return dcc.Textarea(
        id=editor_id,
        value=value,
        style={"width": "100%", "height": height},
        spellCheck=False,
    )
