"""Tests for the session management methods of AuthorizationService.

Covers login(), get_session_user(), set_session_user(), and
clear_session_user().  All tests are self-contained — no external fixtures
or running Dash app are required.
"""

from __future__ import annotations

import pytest

from aiml_dash.auth import AuthorizationService, UserContext
from aiml_dash.utils.user_store import UserStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeSettings:
    """Minimal settings stub sufficient for AuthorizationService."""

    default_user_roles: tuple[str, ...] = ("viewer",)
    admin_roles: tuple[str, ...] = ("admin",)


@pytest.fixture()
def settings() -> _FakeSettings:
    """Return a minimal settings stub."""
    return _FakeSettings()


@pytest.fixture()
def auth(settings: _FakeSettings) -> AuthorizationService:
    """Return an AuthorizationService backed by _FakeSettings."""
    return AuthorizationService(settings)


@pytest.fixture()
def store() -> UserStore:
    """Return a UserStore pre-populated with admin and viewer accounts."""
    s = UserStore()
    s.add_user(
        user_id="user-admin",
        username="admin",
        password="admin_pass",
        roles=("admin",),
    )
    s.add_user(
        user_id="user-viewer",
        username="viewer",
        password="viewer_pass",
        roles=("viewer",),
    )
    return s


@pytest.fixture()
def session() -> dict:
    """Return a plain dict that mimics a Flask session."""
    return {}


# ---------------------------------------------------------------------------
# AuthorizationService.login
# ---------------------------------------------------------------------------


class TestLogin:
    """Tests for AuthorizationService.login()."""

    def test_valid_credentials_return_user_context(
        self, auth: AuthorizationService, store: UserStore
    ):
        """login() returns a UserContext for correct credentials."""
        ctx = auth.login("admin", "admin_pass", store)
        assert ctx is not None
        assert isinstance(ctx, UserContext)

    def test_user_context_has_correct_user_id(
        self, auth: AuthorizationService, store: UserStore
    ):
        """The returned UserContext carries the correct user_id."""
        ctx = auth.login("admin", "admin_pass", store)
        assert ctx is not None
        assert ctx.user_id == "user-admin"

    def test_user_context_has_correct_roles(
        self, auth: AuthorizationService, store: UserStore
    ):
        """The returned UserContext carries the roles from the user store."""
        ctx = auth.login("admin", "admin_pass", store)
        assert ctx is not None
        assert "admin" in ctx.roles

    def test_viewer_login_returns_viewer_roles(
        self, auth: AuthorizationService, store: UserStore
    ):
        """login() returns a viewer-role context for viewer credentials."""
        ctx = auth.login("viewer", "viewer_pass", store)
        assert ctx is not None
        assert "viewer" in ctx.roles

    def test_wrong_password_returns_none(
        self, auth: AuthorizationService, store: UserStore
    ):
        """login() returns None for a wrong password."""
        ctx = auth.login("admin", "wrong_password", store)
        assert ctx is None

    def test_unknown_user_returns_none(
        self, auth: AuthorizationService, store: UserStore
    ):
        """login() returns None for an unknown username."""
        ctx = auth.login("no_such_user", "any_password", store)
        assert ctx is None

    def test_empty_password_returns_none(
        self, auth: AuthorizationService, store: UserStore
    ):
        """login() returns None when password is an empty string."""
        ctx = auth.login("admin", "", store)
        assert ctx is None

    def test_returned_context_is_immutable(
        self, auth: AuthorizationService, store: UserStore
    ):
        """The returned UserContext is frozen (immutable)."""
        ctx = auth.login("admin", "admin_pass", store)
        assert ctx is not None
        with pytest.raises((AttributeError, TypeError)):
            ctx.user_id = "tampered"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# AuthorizationService.get_session_user
# ---------------------------------------------------------------------------


class TestGetSessionUser:
    """Tests for AuthorizationService.get_session_user()."""

    def test_empty_session_returns_default_user(
        self, auth: AuthorizationService, session: dict
    ):
        """get_session_user() falls back to default_user() for an empty session."""
        user = auth.get_session_user(session)
        assert user == auth.default_user()

    def test_empty_session_default_user_is_anonymous(
        self, auth: AuthorizationService, session: dict
    ):
        """Default fallback user has user_id='anonymous'."""
        user = auth.get_session_user(session)
        assert user.user_id == "anonymous"

    def test_returns_stored_user_context(
        self, auth: AuthorizationService, session: dict
    ):
        """get_session_user() reconstructs the UserContext stored via set_session_user."""
        original = UserContext(user_id="user-admin", roles=("admin",))
        auth.set_session_user(session, original)
        retrieved = auth.get_session_user(session)
        assert retrieved == original

    def test_retrieved_user_id_matches(
        self, auth: AuthorizationService, session: dict
    ):
        """get_session_user() returns correct user_id after set_session_user."""
        auth.set_session_user(session, UserContext(user_id="u99", roles=("viewer",)))
        user = auth.get_session_user(session)
        assert user.user_id == "u99"

    def test_retrieved_roles_match(
        self, auth: AuthorizationService, session: dict
    ):
        """get_session_user() returns correct roles after set_session_user."""
        auth.set_session_user(
            session, UserContext(user_id="u1", roles=("admin", "viewer"))
        )
        user = auth.get_session_user(session)
        assert set(user.roles) == {"admin", "viewer"}

    def test_malformed_session_data_returns_default_user(
        self, auth: AuthorizationService
    ):
        """get_session_user() gracefully handles corrupted session data."""
        bad_session: dict = {"_auth_user": "not_a_dict"}
        user = auth.get_session_user(bad_session)
        assert user == auth.default_user()

    def test_missing_user_id_returns_default_user(
        self, auth: AuthorizationService
    ):
        """get_session_user() falls back to default when user_id key is absent."""
        partial_session: dict = {"_auth_user": {"roles": ["admin"]}}
        user = auth.get_session_user(partial_session)
        assert user == auth.default_user()


# ---------------------------------------------------------------------------
# AuthorizationService.set_session_user
# ---------------------------------------------------------------------------


class TestSetSessionUser:
    """Tests for AuthorizationService.set_session_user()."""

    def test_stores_user_id(self, auth: AuthorizationService, session: dict):
        """set_session_user() persists user_id into the session dict."""
        auth.set_session_user(session, UserContext(user_id="u42", roles=("viewer",)))
        assert auth.get_session_user(session).user_id == "u42"

    def test_stores_roles(self, auth: AuthorizationService, session: dict):
        """set_session_user() persists roles into the session dict."""
        auth.set_session_user(
            session, UserContext(user_id="u1", roles=("admin", "editor"))
        )
        assert "admin" in auth.get_session_user(session).roles

    def test_overwrites_previous_user(
        self, auth: AuthorizationService, session: dict
    ):
        """set_session_user() replaces any previously stored user."""
        auth.set_session_user(session, UserContext(user_id="first", roles=("viewer",)))
        auth.set_session_user(session, UserContext(user_id="second", roles=("admin",)))
        assert auth.get_session_user(session).user_id == "second"

    def test_session_key_is_present_after_set(
        self, auth: AuthorizationService, session: dict
    ):
        """set_session_user() populates the session dict with at least one key."""
        auth.set_session_user(session, UserContext(user_id="u1", roles=()))
        assert len(session) > 0

    def test_returns_none(self, auth: AuthorizationService, session: dict):
        """set_session_user() returns None (no meaningful return value)."""
        result = auth.set_session_user(session, UserContext())
        assert result is None


# ---------------------------------------------------------------------------
# AuthorizationService.clear_session_user
# ---------------------------------------------------------------------------


class TestClearSessionUser:
    """Tests for AuthorizationService.clear_session_user()."""

    def test_clear_removes_user_from_session(
        self, auth: AuthorizationService, session: dict
    ):
        """clear_session_user() removes the stored user from the session."""
        auth.set_session_user(session, UserContext(user_id="u1", roles=("admin",)))
        auth.clear_session_user(session)
        user = auth.get_session_user(session)
        assert user == auth.default_user()

    def test_clear_on_empty_session_is_safe(
        self, auth: AuthorizationService, session: dict
    ):
        """clear_session_user() does not raise on an already-empty session."""
        auth.clear_session_user(session)  # should not raise

    def test_session_returns_anonymous_after_clear(
        self, auth: AuthorizationService, session: dict
    ):
        """After clearing, get_session_user() returns anonymous user."""
        auth.set_session_user(session, UserContext(user_id="u1", roles=("admin",)))
        auth.clear_session_user(session)
        assert auth.get_session_user(session).user_id == "anonymous"

    def test_returns_none(self, auth: AuthorizationService, session: dict):
        """clear_session_user() returns None."""
        result = auth.clear_session_user(session)
        assert result is None

    def test_idempotent(self, auth: AuthorizationService, session: dict):
        """Calling clear_session_user() twice does not raise."""
        auth.set_session_user(session, UserContext(user_id="u1", roles=()))
        auth.clear_session_user(session)
        auth.clear_session_user(session)  # second call must also be safe
