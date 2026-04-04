"""Authentication and authorization utilities for AIML Dash.

This module provides user context and authorization services used throughout
the application to control access to plugins and pages based on roles.

Classes:
    UserContext: Lightweight representation of the current user and their roles.
    AuthorizationService: Service for default user creation and role-based access checks.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiml_dash.utils.config import AppSettings


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
