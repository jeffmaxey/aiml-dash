"""Login page for AIML Dash.

Provides a simple username/password form backed by :class:`UserStore`.  On
successful authentication the user is redirected to ``/home``; on failure an
inline error alert is displayed.

Functions:
    layout: Return the Dash component tree for the login page.
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html, no_update

from aiml_dash.auth import AuthorizationService
from aiml_dash.utils.config import get_settings
from aiml_dash.utils.data_manager import data_manager  # noqa: F401 – singleton import
from aiml_dash.utils.user_store import UserStore, create_user_store

# ---------------------------------------------------------------------------
# Module-level singletons used by the callback
# ---------------------------------------------------------------------------

_settings = get_settings()
_auth_service = AuthorizationService(_settings)
_user_store: UserStore = create_user_store(_settings)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def layout() -> html.Div:
    """Return the login page layout.

    The layout is a vertically and horizontally centred card containing:
    - A page title
    - Username text input
    - Password input
    - Submit button
    - Error alert (initially hidden)
    - Hidden ``dcc.Location`` for programmatic redirect
    - Hidden ``dcc.Store`` for persisting user session data

    Returns
    -------
    html.Div
        Root component tree for the login page.
    """
    return html.Div(
        [
            # Location component — used to redirect after successful login
            dcc.Location(id="login-location", refresh=True),
            # Session store — persists authenticated user across page loads
            dcc.Store(id="user-session-store", storage_type="session"),
            # Centred login card
            dmc.Center(
                style={"minHeight": "100vh"},
                children=dmc.Card(
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    style={"width": 380},
                    children=dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Text(
                                "AIML Dash — Sign In",
                                size="xl",
                                fw=700,
                                ta="center",
                            ),
                            dmc.TextInput(
                                id="login-username",
                                label="Username",
                                placeholder="Enter your username",
                                required=True,
                            ),
                            dmc.PasswordInput(
                                id="login-password",
                                label="Password",
                                placeholder="Enter your password",
                                required=True,
                            ),
                            dmc.Button(
                                "Sign In",
                                id="login-submit-btn",
                                fullWidth=True,
                                color="blue",
                            ),
                            # Error alert — hidden until a login failure occurs
                            dmc.Alert(
                                id="login-error-msg",
                                color="red",
                                title="Authentication failed",
                                children="Invalid username or password. Please try again.",
                                style={"display": "none"},
                            ),
                        ],
                    ),
                ),
            ),
            # Hidden placeholder required by the redirect output
            html.Div(id="login-redirect", style={"display": "none"}),
        ]
    )


# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------


@callback(
    Output("login-location", "href"),
    Output("user-session-store", "data"),
    Output("login-error-msg", "style"),
    Input("login-submit-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def _handle_login(
    n_clicks: int | None,
    username: str | None,
    password: str | None,
) -> tuple[str | object, dict | object, dict]:
    """Process a login form submission.

    On success the user context is serialized into the session store and the
    browser is redirected to ``/home``.  On failure the error alert is made
    visible and no redirect or store update is performed.

    Parameters
    ----------
    n_clicks : int | None
        Click count on the submit button.
    username : str | None
        Value of the username input field.
    password : str | None
        Value of the password input field.

    Returns
    -------
    tuple[str | no_update, dict | no_update, dict]
        (href, store_data, error_style) triple.
    """
    if not n_clicks or not username or not password:
        return no_update, no_update, {"display": "none"}

    user_context = _auth_service.login(username, password, _user_store)

    if user_context is None:
        # Show the error alert; leave href and store unchanged
        return no_update, no_update, {"display": "block"}

    # Persist user context in session store
    session_data = {
        "user_id": user_context.user_id,
        "roles": list(user_context.roles),
    }
    return "/home", session_data, {"display": "none"}
