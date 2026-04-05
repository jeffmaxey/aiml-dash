"""Authentication and authorization utilities for AIML Dash.

This module provides user context and authorization services used throughout
the application to control access to plugins and pages based on roles.

Classes:
    UserContext: Lightweight representation of the current user and their roles.
    AuthorizationService: Service for default user creation, role-based access
        checks, and Flask session-based session management.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiml_dash.utils.config import AppSettings
    from aiml_dash.utils.user_store import UserStore

# Key used to store/retrieve the serialised UserContext inside a Flask session
# dict.  Kept as a module-level constant so all methods share a single source
# of truth.
_SESSION_USER_KEY = "_auth_user"


@dataclass(frozen=True)
class UserContext:
    """Immutable representation of the current user.

    Attributes:
        user_id: Unique identifier for the user (e.g. "anonymous").
        roles: Tuple of role names granted to this user.
    """

    user_id: str = "anonymous"
    roles: tuple[str, ...] = field(default_factory=tuple)


class AuthorizationService:
    """Service for creating default users and checking role-based access.

    Parameters
    ----------
    settings : AppSettings
        Application settings used to obtain default role configuration.
    """

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> AppSettings:
        """Return the application settings."""
        return self._settings

    def default_user(self) -> UserContext:
        """Return an anonymous user with the configured default roles.

        Returns
        -------
        UserContext
            A new user context with ``user_id="anonymous"`` and the roles
            defined by ``settings.default_user_roles``.
        """
        return UserContext(
            user_id="anonymous",
            roles=tuple(self._settings.default_user_roles),
        )

    def has_role(self, user: UserContext, role: str) -> bool:
        """Check whether *user* has the given *role*.

        Parameters
        ----------
        user : UserContext
            The user to check.
        role : str
            The role name to look for.

        Returns
        -------
        bool
            ``True`` when the user's roles include *role*.
        """
        return role in user.roles

    def can_access(self, user: UserContext, allowed_roles: Sequence[str]) -> bool:
        """Check whether *user* is permitted to access a resource.

        Resources with an empty *allowed_roles* sequence are public and always
        accessible.  Otherwise the user must possess at least one of the listed
        roles.

        Parameters
        ----------
        user : UserContext
            The user requesting access.
        allowed_roles : Sequence[str]
            Roles that are permitted to access the resource.  An empty
            sequence means the resource is unrestricted.

        Returns
        -------
        bool
            ``True`` when access is permitted.
        """
        if not allowed_roles:
            return True
        return any(role in user.roles for role in allowed_roles)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def login(
        self,
        username: str,
        password: str,
        user_store: UserStore,
    ) -> UserContext | None:
        """Authenticate *username* / *password* against *user_store*.

        Returns a :class:`UserContext` on success or ``None`` on failure.

        Parameters
        ----------
        username : str
            Login name supplied by the user.
        password : str
            Plain-text password supplied by the user.
        user_store : UserStore
            The store to authenticate against.

        Returns
        -------
        UserContext | None
            An authenticated context on success, or ``None`` when credentials
            are invalid or the account is inactive.
        """
        user = user_store.authenticate(username, password)
        if user is None:
            return None
        return UserContext(user_id=user.user_id, roles=user.roles)

    def get_session_user(self, session: dict[str, Any]) -> UserContext:
        """Extract the current user from a Flask *session* dict.

        Falls back to :meth:`default_user` when no authenticated user is
        stored in the session.

        Parameters
        ----------
        session : dict[str, Any]
            Flask ``session`` proxy (or any plain dict with the same shape).

        Returns
        -------
        UserContext
            The stored user, or the anonymous default user if absent.
        """
        data = session.get(_SESSION_USER_KEY)
        if data is None:
            return self.default_user()
        try:
            return UserContext(
                user_id=data["user_id"],
                roles=tuple(data.get("roles", ())),
            )
        except (KeyError, TypeError):
            return self.default_user()

    def set_session_user(self, session: dict[str, Any], user: UserContext) -> None:
        """Persist *user* into the Flask *session* dict.

        Parameters
        ----------
        session : dict[str, Any]
            Flask ``session`` proxy to write into.
        user : UserContext
            The authenticated user to store.
        """
        session[_SESSION_USER_KEY] = {
            "user_id": user.user_id,
            "roles": list(user.roles),
        }

    def clear_session_user(self, session: dict[str, Any]) -> None:
        """Remove the authenticated user entry from the Flask *session* dict.

        Parameters
        ----------
        session : dict[str, Any]
            Flask ``session`` proxy to clear.
        """
        session.pop(_SESSION_USER_KEY, None)
