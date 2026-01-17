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

from aiml_dash.utils.settings import app_settings

# Try to import dash_ace; if unavailable, we'll fallback to a textarea
try:
    import dash_ace  # type: ignore

    _HAS_ACE = True
except Exception:
    _HAS_ACE = False


def get_code_editor(id: str, value: str = "", mode: str = "r", theme: str = "github", height: str = "300px") -> Any:
    """
    Return a code editor component with automatic fallback support.

    Creates a code editor component using dash_ace if available, otherwise
    falls back to a basic dcc.Textarea. The editor supports syntax highlighting
    and basic autocompletion features when dash_ace is available.

    Parameters
    ----------
    id : str
        Unique identifier for the Dash component.
    value : str, optional
        Initial text content to display in the editor (default is "").
    mode : str, optional
        Programming language mode for syntax highlighting. Common values
        include 'r', 'python', 'sql', 'javascript' (default is 'r').
    theme : str, optional
        Visual theme name for the Ace editor (e.g., 'github', 'monokai',
        'twilight'). Ignored when falling back to textarea (default is 'github').
    height : str, optional
        CSS height specification for the editor (e.g., '300px', '50vh')
        (default is '300px').

    Returns
    -------
    dash_ace.Ace or dcc.Textarea
        A Dash component, either dash_ace.Ace if the library is available,
        or dcc.Textarea as a fallback.

    Examples
    --------
    Create a Python code editor:

    >>> editor = get_code_editor(
    ...     id="python-editor",
    ...     value="def hello():\\n    print('Hello, World!')",
    ...     mode="python",
    ...     theme="monokai",
    ...     height="500px"
    ... )

    Create an R code editor with default settings:

    >>> editor = get_code_editor(id="r-editor")

    Notes
    -----
    The function automatically detects if dash_ace is available at the module
    level. If not, it provides a graceful fallback to dcc.Textarea, which has
    reduced functionality but maintains application stability.

    When dash_ace is available, the following features are enabled:

    - Syntax highlighting for the specified language mode
    - Basic autocompletion
    - Configurable themes
    - 2-space tab size
    - Print margin hidden

    See Also
    --------
    dash_ace.Ace : The underlying Ace editor component when available.
    dash.dcc.Textarea : The fallback textarea component.
    """
    if _HAS_ACE:
        # Use Ace editor for richer editing experience
        return dash_ace.Ace(
            id=id,
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
    return dcc.Textarea(id=id, value=value, style={"width": "100%", "height": height}, spellCheck=False)
