"""Tests for aiml_dash.utils.user_store module.

Covers User construction, UserStore CRUD operations, authentication
(success and failure paths), list_users, and the create_user_store factory.
"""

from __future__ import annotations

import os

import pytest

from aiml_dash.utils.user_store import User, UserStore, create_user_store


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store() -> UserStore:
    """Return a fresh empty UserStore."""
    return UserStore()


@pytest.fixture()
def populated_store(store: UserStore) -> UserStore:
    """Return a UserStore with one admin and one viewer user pre-added."""
    store.add_user(
        user_id="u-admin",
        username="admin",
        password="secret_admin",
        roles=("admin",),
    )
    store.add_user(
        user_id="u-viewer",
        username="viewer",
        password="secret_viewer",
        roles=("viewer",),
    )
    return store


# ---------------------------------------------------------------------------
# User dataclass
# ---------------------------------------------------------------------------


class TestUserDataclass:
    """Tests for the User dataclass."""

    def test_fields_stored_correctly(self):
        """User stores all provided field values."""
        user = User(
            user_id="u1",
            username="alice",
            password_hash="abc:def",
            roles=("admin", "viewer"),
            is_active=True,
        )
        assert user.user_id == "u1"
        assert user.username == "alice"
        assert user.password_hash == "abc:def"
        assert user.roles == ("admin", "viewer")
        assert user.is_active is True

    def test_default_is_active_true(self):
        """User.is_active defaults to True."""
        user = User(user_id="u2", username="bob", password_hash="x:y")
        assert user.is_active is True

    def test_default_roles_empty_tuple(self):
        """User.roles defaults to an empty tuple."""
        user = User(user_id="u3", username="carol", password_hash="p:q")
        assert user.roles == ()


# ---------------------------------------------------------------------------
# UserStore.add_user
# ---------------------------------------------------------------------------


class TestAddUser:
    """Tests for UserStore.add_user()."""

    def test_add_user_returns_user(self, store: UserStore):
        """add_user() returns the created User."""
        user = store.add_user(
            user_id="u1", username="alice", password="pw", roles=("viewer",)
        )
        assert isinstance(user, User)
        assert user.username == "alice"

    def test_password_is_hashed(self, store: UserStore):
        """add_user() does not store the plain-text password."""
        user = store.add_user(user_id="u1", username="alice", password="plain")
        assert user.password_hash != "plain"
        assert ":" in user.password_hash  # salt:digest format

    def test_roles_stored(self, store: UserStore):
        """add_user() persists the specified roles."""
        user = store.add_user(
            user_id="u1", username="alice", password="pw", roles=("admin", "viewer")
        )
        assert set(user.roles) == {"admin", "viewer"}

    def test_duplicate_username_raises(self, store: UserStore):
        """add_user() raises ValueError for a duplicate username."""
        store.add_user(user_id="u1", username="alice", password="pw")
        with pytest.raises(ValueError, match="already exists"):
            store.add_user(user_id="u2", username="alice", password="pw2")

    def test_is_active_defaults_true(self, store: UserStore):
        """Users are active by default."""
        user = store.add_user(user_id="u1", username="alice", password="pw")
        assert user.is_active is True

    def test_inactive_user_stored(self, store: UserStore):
        """add_user() respects is_active=False."""
        user = store.add_user(
            user_id="u1", username="alice", password="pw", is_active=False
        )
        assert user.is_active is False


# ---------------------------------------------------------------------------
# UserStore.get_user
# ---------------------------------------------------------------------------


class TestGetUser:
    """Tests for UserStore.get_user()."""

    def test_get_existing_user(self, populated_store: UserStore):
        """get_user() returns the User for a known username."""
        user = populated_store.get_user("admin")
        assert user is not None
        assert user.username == "admin"

    def test_get_unknown_user_returns_none(self, populated_store: UserStore):
        """get_user() returns None for an unknown username."""
        assert populated_store.get_user("no_such_user") is None

    def test_get_user_case_sensitive(self, populated_store: UserStore):
        """get_user() treats usernames as case-sensitive."""
        assert populated_store.get_user("Admin") is None
        assert populated_store.get_user("ADMIN") is None


# ---------------------------------------------------------------------------
# UserStore.list_users
# ---------------------------------------------------------------------------


class TestListUsers:
    """Tests for UserStore.list_users()."""

    def test_empty_store_returns_empty_list(self, store: UserStore):
        """list_users() returns an empty list for a fresh store."""
        assert store.list_users() == []

    def test_returns_all_users(self, populated_store: UserStore):
        """list_users() returns every stored user."""
        users = populated_store.list_users()
        assert len(users) == 2
        usernames = {u.username for u in users}
        assert usernames == {"admin", "viewer"}

    def test_returns_list_type(self, populated_store: UserStore):
        """list_users() always returns a list."""
        assert isinstance(populated_store.list_users(), list)

    def test_returns_snapshot(self, store: UserStore):
        """Modifying the returned list does not affect the internal state."""
        store.add_user(user_id="u1", username="alice", password="pw")
        users = store.list_users()
        users.clear()
        assert len(store.list_users()) == 1


# ---------------------------------------------------------------------------
# UserStore.authenticate
# ---------------------------------------------------------------------------


class TestAuthenticate:
    """Tests for UserStore.authenticate()."""

    def test_correct_credentials_return_user(self, populated_store: UserStore):
        """authenticate() returns the User for correct credentials."""
        user = populated_store.authenticate("admin", "secret_admin")
        assert user is not None
        assert user.username == "admin"

    def test_wrong_password_returns_none(self, populated_store: UserStore):
        """authenticate() returns None for a wrong password."""
        assert populated_store.authenticate("admin", "wrong_password") is None

    def test_unknown_username_returns_none(self, populated_store: UserStore):
        """authenticate() returns None for an unknown username."""
        assert populated_store.authenticate("no_such_user", "any_password") is None

    def test_empty_password_fails(self, store: UserStore):
        """authenticate() returns None when password is empty and does not match."""
        store.add_user(user_id="u1", username="alice", password="realpass")
        assert store.authenticate("alice", "") is None

    def test_inactive_user_rejected(self, store: UserStore):
        """authenticate() returns None for an inactive account."""
        store.add_user(
            user_id="u1", username="inactive", password="pw", is_active=False
        )
        assert store.authenticate("inactive", "pw") is None

    def test_authenticated_user_has_correct_roles(self, populated_store: UserStore):
        """authenticate() returns a User with the expected roles."""
        user = populated_store.authenticate("viewer", "secret_viewer")
        assert user is not None
        assert "viewer" in user.roles

    def test_multiple_successful_authentications(self, populated_store: UserStore):
        """authenticate() succeeds on repeated calls with the same credentials."""
        for _ in range(3):
            user = populated_store.authenticate("admin", "secret_admin")
            assert user is not None


# ---------------------------------------------------------------------------
# create_user_store factory
# ---------------------------------------------------------------------------


class TestCreateUserStore:
    """Tests for the create_user_store() factory function."""

    def test_returns_user_store(self):
        """create_user_store() returns a UserStore instance."""
        store = create_user_store()
        assert isinstance(store, UserStore)

    def test_default_admin_user_exists(self):
        """Default store contains an 'admin' user."""
        env = {
            "AIML_DASH_ADMIN_USERNAME": "admin",
            "AIML_DASH_ADMIN_PASSWORD": "admin",
            "AIML_DASH_VIEWER_USERNAME": "viewer",
            "AIML_DASH_VIEWER_PASSWORD": "viewer",
        }
        original = {k: os.environ.pop(k, None) for k in env}
        try:
            for k, v in env.items():
                os.environ[k] = v
            store = create_user_store()
            assert store.get_user("admin") is not None
        finally:
            for k, v in original.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_default_viewer_user_exists(self):
        """Default store contains a 'viewer' user."""
        store = create_user_store()
        assert store.get_user("viewer") is not None

    def test_admin_has_admin_role(self):
        """Default admin user has the 'admin' role."""
        store = create_user_store()
        admin = store.get_user("admin")
        assert admin is not None
        assert "admin" in admin.roles

    def test_viewer_has_viewer_role(self):
        """Default viewer user has the 'viewer' role."""
        store = create_user_store()
        viewer = store.get_user("viewer")
        assert viewer is not None
        assert "viewer" in viewer.roles

    def test_reads_admin_username_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """create_user_store() uses AIML_DASH_ADMIN_USERNAME env var."""
        monkeypatch.setenv("AIML_DASH_ADMIN_USERNAME", "superadmin")
        monkeypatch.setenv("AIML_DASH_ADMIN_PASSWORD", "superpass")
        store = create_user_store()
        assert store.get_user("superadmin") is not None
        assert store.get_user("admin") is None

    def test_reads_admin_password_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """create_user_store() uses AIML_DASH_ADMIN_PASSWORD for hashing."""
        monkeypatch.setenv("AIML_DASH_ADMIN_USERNAME", "admin")
        monkeypatch.setenv("AIML_DASH_ADMIN_PASSWORD", "env_admin_pass")
        store = create_user_store()
        assert store.authenticate("admin", "env_admin_pass") is not None
        assert store.authenticate("admin", "wrong_pass") is None

    def test_reads_viewer_username_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """create_user_store() uses AIML_DASH_VIEWER_USERNAME env var."""
        monkeypatch.setenv("AIML_DASH_VIEWER_USERNAME", "readonly")
        monkeypatch.setenv("AIML_DASH_VIEWER_PASSWORD", "readpass")
        store = create_user_store()
        assert store.get_user("readonly") is not None
        assert store.get_user("viewer") is None

    def test_reads_viewer_password_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """create_user_store() uses AIML_DASH_VIEWER_PASSWORD for hashing."""
        monkeypatch.setenv("AIML_DASH_VIEWER_USERNAME", "viewer")
        monkeypatch.setenv("AIML_DASH_VIEWER_PASSWORD", "env_viewer_pass")
        store = create_user_store()
        assert store.authenticate("viewer", "env_viewer_pass") is not None
        assert store.authenticate("viewer", "wrong_pass") is None

    def test_accepts_settings_parameter(self):
        """create_user_store() accepts an optional settings parameter."""
        # Should not raise regardless of what is passed
        store = create_user_store(settings=None)
        assert isinstance(store, UserStore)

    def test_two_users_in_store(self):
        """Default store contains exactly two users."""
        store = create_user_store()
        assert len(store.list_users()) == 2
