"""In-memory user store for AIML Dash authentication.

This module provides a lightweight, self-contained user store backed by an
in-memory dictionary.  Password hashing uses :func:`hashlib.pbkdf2_hmac` from
the Python standard library — no third-party dependencies are required.

Classes:
    User: Dataclass representing a stored user record.
    UserStore: In-memory user store with CRUD and authentication helpers.

Functions:
    create_user_store: Factory that seeds a ``UserStore`` from environment variables.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HASH_ALGORITHM = "sha256"
_ITERATIONS = 260_000  # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256
_SALT_BYTES = 32
_SEPARATOR = ":"


# ---------------------------------------------------------------------------
# User dataclass
# ---------------------------------------------------------------------------


@dataclass
class User:
    """Stored representation of an application user.

    Attributes:
        user_id: Unique identifier for the user.
        username: Human-readable login name (must be unique within the store).
        password_hash: Encoded PBKDF2 digest in the form ``salt_hex:hash_hex``.
        roles: Tuple of role names granted to this user.
        is_active: Whether the user account is enabled.
    """

    user_id: str
    username: str
    password_hash: str
    roles: tuple[str, ...] = field(default_factory=tuple)
    is_active: bool = True


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------


def _hash_password(password: str, salt_hex: str | None = None) -> str:
    """Return a ``salt_hex:hash_hex`` PBKDF2 digest for *password*.

    Parameters
    ----------
    password : str
        Plain-text password to hash.
    salt_hex : str | None
        Hex-encoded salt to use.  When ``None`` a fresh random salt is
        generated.

    Returns
    -------
    str
        Encoded digest in the form ``<salt_hex>:<hash_hex>``.
    """
    salt_bytes = (
        bytes.fromhex(salt_hex) if salt_hex is not None else secrets.token_bytes(_SALT_BYTES)
    )
    digest = hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM,
        password.encode(),
        salt_bytes,
        _ITERATIONS,
    )
    return f"{salt_bytes.hex()}{_SEPARATOR}{digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Return ``True`` when *password* matches *stored_hash*.

    The comparison is performed in constant time to mitigate timing attacks.

    Parameters
    ----------
    password : str
        Plain-text password candidate.
    stored_hash : str
        Previously generated ``salt_hex:hash_hex`` digest.

    Returns
    -------
    bool
        ``True`` if the password matches.
    """
    try:
        salt_hex, _ = stored_hash.split(_SEPARATOR, 1)
    except ValueError:
        return False
    candidate = _hash_password(password, salt_hex=salt_hex)
    return secrets.compare_digest(candidate, stored_hash)


# ---------------------------------------------------------------------------
# UserStore
# ---------------------------------------------------------------------------


class UserStore:
    """In-memory user store.

    Users are keyed by *username* for fast lookup.  All mutation methods are
    thread-safe for CPython (GIL-protected dict operations), but callers that
    require strict consistency across threads should add external locking.
    """

    def __init__(self) -> None:
        # username -> User
        self._users: dict[str, User] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_user(
        self,
        *,
        user_id: str,
        username: str,
        password: str,
        roles: tuple[str, ...] = (),
        is_active: bool = True,
    ) -> User:
        """Create and store a new user, hashing the plain-text *password*.

        Parameters
        ----------
        user_id : str
            Unique identifier for the user.
        username : str
            Login name (case-sensitive).  Must be unique within the store.
        password : str
            Plain-text password; stored as a PBKDF2 hash.
        roles : tuple[str, ...]
            Role names to grant.  Defaults to an empty tuple.
        is_active : bool
            Whether the account is enabled.  Defaults to ``True``.

        Returns
        -------
        User
            The newly created :class:`User` record.

        Raises
        ------
        ValueError
            If a user with the same *username* already exists.
        """
        if username in self._users:
            msg = f"User '{username}' already exists"
            raise ValueError(msg)
        user = User(
            user_id=user_id,
            username=username,
            password_hash=_hash_password(password),
            roles=roles,
            is_active=is_active,
        )
        self._users[username] = user
        return user

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_user(self, username: str) -> User | None:
        """Return the :class:`User` for *username*, or ``None`` if not found.

        Parameters
        ----------
        username : str
            Login name to look up.

        Returns
        -------
        User | None
            Matching user record or ``None``.
        """
        return self._users.get(username)

    def list_users(self) -> list[User]:
        """Return all stored users as a list.

        Returns
        -------
        list[User]
            Snapshot of all user records in insertion order.
        """
        return list(self._users.values())

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, username: str, password: str) -> User | None:
        """Verify *username* / *password* credentials.

        Returns the matching :class:`User` only when the account is active and
        the password is correct.  Returns ``None`` for any failure (unknown
        user, wrong password, or inactive account) without revealing which
        condition failed.

        Parameters
        ----------
        username : str
            Login name.
        password : str
            Plain-text password candidate.

        Returns
        -------
        User | None
            Authenticated user or ``None`` on failure.
        """
        user = self._users.get(username)
        if user is None or not user.is_active:
            # Perform a dummy hash to avoid timing oracle on unknown usernames.
            _hash_password(password)
            return None
        if not _verify_password(password, user.password_hash):
            return None
        return user


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_user_store(settings: object | None = None) -> UserStore:  # noqa: ARG001
    """Build a :class:`UserStore` seeded from environment variables.

    The *settings* parameter is accepted for API symmetry with other factory
    functions in this package but is not currently used — configuration is
    read exclusively from environment variables.

    Environment variables
    ---------------------
    AIML_DASH_ADMIN_USERNAME
        Admin login name.  Defaults to ``"admin"``.
    AIML_DASH_ADMIN_PASSWORD
        Admin plain-text password.  Defaults to ``"admin"``.
    AIML_DASH_VIEWER_USERNAME
        Viewer login name.  Defaults to ``"viewer"``.
    AIML_DASH_VIEWER_PASSWORD
        Viewer plain-text password.  Defaults to ``"viewer"``.

    Parameters
    ----------
    settings : object | None
        Ignored; present for API consistency.

    Returns
    -------
    UserStore
        A freshly created store containing admin and viewer accounts.
    """
    store = UserStore()

    admin_username = os.environ.get("AIML_DASH_ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("AIML_DASH_ADMIN_PASSWORD", "admin")
    store.add_user(
        user_id="user-admin",
        username=admin_username,
        password=admin_password,
        roles=("admin",),
    )

    viewer_username = os.environ.get("AIML_DASH_VIEWER_USERNAME", "viewer")
    viewer_password = os.environ.get("AIML_DASH_VIEWER_PASSWORD", "viewer")
    store.add_user(
        user_id="user-viewer",
        username=viewer_username,
        password=viewer_password,
        roles=("viewer",),
    )

    return store
