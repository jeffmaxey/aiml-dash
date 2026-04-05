"""Tests for aiml_dash.auth module.

Covers UserContext construction, AuthorizationService.default_user(),
has_role(), and can_access() with various role combinations.
"""

from __future__ import annotations

import pytest

from aiml_dash.auth import AuthorizationService, UserContext


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeSettings:
    """Minimal settings stub sufficient for AuthorizationService."""

    default_user_roles: tuple[str, ...] = ("viewer",)
    admin_roles: tuple[str, ...] = ("admin",)


@pytest.fixture()
def settings() -> _FakeSettings:
    return _FakeSettings()


@pytest.fixture()
def auth(settings) -> AuthorizationService:
    return AuthorizationService(settings)


@pytest.fixture()
def viewer_user() -> UserContext:
    return UserContext(user_id="alice", roles=("viewer",))


@pytest.fixture()
def admin_user() -> UserContext:
    return UserContext(user_id="bob", roles=("admin", "viewer"))


@pytest.fixture()
def no_role_user() -> UserContext:
    return UserContext(user_id="guest", roles=())


# ---------------------------------------------------------------------------
# UserContext
# ---------------------------------------------------------------------------


class TestUserContext:
    """Tests for the UserContext dataclass."""

    def test_default_user_id(self):
        """UserContext should have 'anonymous' as the default user_id."""
        user = UserContext()
        assert user.user_id == "anonymous"

    def test_default_roles_is_empty_tuple(self):
        """Default roles should be an empty tuple."""
        user = UserContext()
        assert user.roles == ()

    def test_custom_user_id_and_roles(self):
        """UserContext stores provided user_id and roles."""
        user = UserContext(user_id="alice", roles=("admin", "viewer"))
        assert user.user_id == "alice"
        assert "admin" in user.roles
        assert "viewer" in user.roles

    def test_frozen_dataclass(self):
        """UserContext should be immutable (frozen dataclass)."""
        user = UserContext(user_id="x", roles=("r",))
        with pytest.raises((AttributeError, TypeError)):
            user.user_id = "y"  # type: ignore[misc]

    def test_equality(self):
        """Two UserContexts with the same data should be equal."""
        u1 = UserContext(user_id="x", roles=("a",))
        u2 = UserContext(user_id="x", roles=("a",))
        assert u1 == u2

    def test_inequality_different_id(self):
        """UserContexts with different user_ids should not be equal."""
        u1 = UserContext(user_id="x", roles=("a",))
        u2 = UserContext(user_id="y", roles=("a",))
        assert u1 != u2


# ---------------------------------------------------------------------------
# AuthorizationService.default_user
# ---------------------------------------------------------------------------


class TestDefaultUser:
    """Tests for AuthorizationService.default_user()."""

    def test_returns_user_context(self, auth):
        """default_user() should return a UserContext."""
        user = auth.default_user()
        assert isinstance(user, UserContext)

    def test_default_user_id_is_anonymous(self, auth):
        """Default user id should be 'anonymous'."""
        user = auth.default_user()
        assert user.user_id == "anonymous"

    def test_default_roles_from_settings(self, auth):
        """Default user should receive roles from settings.default_user_roles."""
        user = auth.default_user()
        assert "viewer" in user.roles

    def test_settings_accessible(self, auth, settings):
        """auth.settings property should return the provided settings."""
        assert auth.settings is settings


# ---------------------------------------------------------------------------
# AuthorizationService.has_role
# ---------------------------------------------------------------------------


class TestHasRole:
    """Tests for AuthorizationService.has_role()."""

    def test_has_role_true(self, auth, viewer_user):
        """has_role() returns True when the user has the role."""
        assert auth.has_role(viewer_user, "viewer") is True

    def test_has_role_false(self, auth, viewer_user):
        """has_role() returns False when the user lacks the role."""
        assert auth.has_role(viewer_user, "admin") is False

    def test_has_role_multiple_roles(self, auth, admin_user):
        """has_role() works correctly for users with multiple roles."""
        assert auth.has_role(admin_user, "admin") is True
        assert auth.has_role(admin_user, "viewer") is True
        assert auth.has_role(admin_user, "superuser") is False

    def test_has_role_no_roles(self, auth, no_role_user):
        """has_role() returns False for a user with no roles."""
        assert auth.has_role(no_role_user, "viewer") is False


# ---------------------------------------------------------------------------
# AuthorizationService.can_access
# ---------------------------------------------------------------------------


class TestCanAccess:
    """Tests for AuthorizationService.can_access()."""

    def test_empty_allowed_roles_is_public(self, auth, no_role_user):
        """Empty allowed_roles means the resource is public (always accessible)."""
        assert auth.can_access(no_role_user, []) is True

    def test_user_with_matching_role(self, auth, viewer_user):
        """can_access() returns True when the user has at least one allowed role."""
        assert auth.can_access(viewer_user, ["viewer"]) is True

    def test_user_without_matching_role(self, auth, viewer_user):
        """can_access() returns False when the user has no allowed role."""
        assert auth.can_access(viewer_user, ["admin"]) is False

    def test_admin_can_access_viewer_resource(self, auth, admin_user):
        """An admin user with 'viewer' role can access a viewer-only resource."""
        assert auth.can_access(admin_user, ["viewer"]) is True

    def test_partial_match_is_sufficient(self, auth, admin_user):
        """A single matching role is enough — the user need not have all roles."""
        assert auth.can_access(admin_user, ["admin", "superuser"]) is True

    def test_no_match_returns_false(self, auth, no_role_user):
        """can_access() returns False when the user has no roles at all."""
        assert auth.can_access(no_role_user, ["admin", "viewer"]) is False

    def test_tuple_allowed_roles(self, auth, viewer_user):
        """can_access() accepts tuples as well as lists for allowed_roles."""
        assert auth.can_access(viewer_user, ("viewer",)) is True
