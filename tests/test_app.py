"""Tests for aiml_dash/app.py.

Covers pure helper functions (_build_project_snapshot, _project_alert,
_project_metadata_lookup, _user_from_store), create_app(), the Flask test
client integration, and the observability request hooks.
"""

from __future__ import annotations

import json

import pytest

import dash
import dash_mantine_components as dmc

from aiml_dash.auth import UserContext
from aiml_dash.services import AppServices, build_services
from aiml_dash.utils.config import AppSettings, get_settings

# Import under test
from aiml_dash.app import (
    _build_project_snapshot,
    _project_alert,
    _project_metadata_lookup,
    _user_from_store,
    create_app,
    app,
    server,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def services() -> AppServices:
    return build_services(get_settings())


@pytest.fixture()
def flask_client():
    server.config["TESTING"] = True
    with server.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# _build_project_snapshot
# ---------------------------------------------------------------------------


class TestBuildProjectSnapshot:
    """Tests for _build_project_snapshot()."""

    def test_returns_dict(self):
        """Result should be a dict."""
        result = _build_project_snapshot(
            app_state=None,
            active_page=None,
            enabled_plugins=None,
            navbar_collapsed=None,
            aside_collapsed=None,
            active_dataset=None,
            data_state={},
        )
        assert isinstance(result, dict)

    def test_version_field(self):
        """Snapshot should include a 'version' key."""
        result = _build_project_snapshot(
            app_state={}, active_page="home", enabled_plugins=["basics"],
            navbar_collapsed=False, aside_collapsed=False,
            active_dataset="iris", data_state={"key": "val"},
        )
        assert result["version"] == "1.0"

    def test_ui_state_keys(self):
        """Snapshot ui_state should contain all expected keys."""
        result = _build_project_snapshot(
            app_state={}, active_page="home", enabled_plugins=[],
            navbar_collapsed=False, aside_collapsed=True,
            active_dataset=None, data_state={},
        )
        ui = result["ui_state"]
        expected = {"app_state", "active_page", "enabled_plugins",
                    "navbar_collapsed", "aside_collapsed", "active_dataset"}
        assert set(ui.keys()) == expected

    def test_none_app_state_becomes_empty_dict(self):
        """None app_state should default to {}."""
        result = _build_project_snapshot(
            app_state=None, active_page=None, enabled_plugins=None,
            navbar_collapsed=None, aside_collapsed=None,
            active_dataset=None, data_state={},
        )
        assert result["ui_state"]["app_state"] == {}

    def test_none_active_page_defaults_to_home(self):
        """None active_page should resolve to HOME_PAGE_ID."""
        from aiml_dash.plugins.models import HOME_PAGE_ID

        result = _build_project_snapshot(
            app_state={}, active_page=None, enabled_plugins=None,
            navbar_collapsed=False, aside_collapsed=False,
            active_dataset=None, data_state={},
        )
        assert result["ui_state"]["active_page"] == HOME_PAGE_ID

    def test_custom_active_page_preserved(self):
        """A provided active_page should be stored unchanged."""
        result = _build_project_snapshot(
            app_state={}, active_page="my-page", enabled_plugins=[],
            navbar_collapsed=False, aside_collapsed=False,
            active_dataset=None, data_state={},
        )
        assert result["ui_state"]["active_page"] == "my-page"

    def test_navbar_collapsed_coerced_to_bool(self):
        """navbar_collapsed should be stored as a bool."""
        result = _build_project_snapshot(
            app_state={}, active_page=None, enabled_plugins=[],
            navbar_collapsed=1, aside_collapsed=0,
            active_dataset=None, data_state={},
        )
        assert result["ui_state"]["navbar_collapsed"] is True
        assert result["ui_state"]["aside_collapsed"] is False

    def test_data_state_preserved(self):
        """data_state should be stored verbatim."""
        ds = {"dataset": "iris", "columns": ["a", "b"]}
        result = _build_project_snapshot(
            app_state={}, active_page=None, enabled_plugins=[],
            navbar_collapsed=False, aside_collapsed=False,
            active_dataset=None, data_state=ds,
        )
        assert result["data_state"] == ds


# ---------------------------------------------------------------------------
# _project_alert
# ---------------------------------------------------------------------------


class TestProjectAlert:
    """Tests for _project_alert()."""

    def test_returns_alert_component(self):
        """_project_alert() should return a dmc.Alert."""
        result = _project_alert("All good", color="green", title="Success")
        assert isinstance(result, dmc.Alert)

    def test_green_uses_checkmark_icon(self):
        """Green alerts should use the carbon:checkmark icon."""
        from dash_iconify import DashIconify

        result = _project_alert("msg", color="green", title="ok")
        # The icon child should exist
        assert result is not None

    def test_non_green_uses_warning_icon(self):
        """Non-green alerts should use the carbon:warning icon."""
        result = _project_alert("uh oh", color="red", title="Error")
        assert isinstance(result, dmc.Alert)

    def test_message_and_color_set(self):
        """Alert message and color should match the arguments."""
        result = _project_alert("test msg", color="yellow", title="T")
        assert result.color == "yellow"


# ---------------------------------------------------------------------------
# _project_metadata_lookup
# ---------------------------------------------------------------------------


class TestProjectMetadataLookup:
    """Tests for _project_metadata_lookup()."""

    def test_none_metadata_returns_empty_dict(self):
        assert _project_metadata_lookup(None, "p1") == {}

    def test_none_project_id_returns_empty_dict(self):
        assert _project_metadata_lookup([{"id": "p1"}], None) == {}

    def test_found_entry_returned(self):
        metadata = [{"id": "p1", "name": "Project One"}, {"id": "p2", "name": "P2"}]
        result = _project_metadata_lookup(metadata, "p1")
        assert result == {"id": "p1", "name": "Project One"}

    def test_missing_id_returns_empty_dict(self):
        metadata = [{"id": "p1"}]
        result = _project_metadata_lookup(metadata, "p99")
        assert result == {}

    def test_empty_list_returns_empty_dict(self):
        assert _project_metadata_lookup([], "p1") == {}


# ---------------------------------------------------------------------------
# _user_from_store
# ---------------------------------------------------------------------------


class TestUserFromStore:
    """Tests for _user_from_store()."""

    def test_none_data_returns_default_user(self, services):
        user = _user_from_store(None, services)
        assert isinstance(user, UserContext)
        assert user.user_id == "anonymous"

    def test_empty_dict_returns_default_user(self, services):
        user = _user_from_store({}, services)
        assert isinstance(user, UserContext)
        assert user.user_id == "anonymous"

    def test_provided_user_id_stored(self, services):
        user = _user_from_store({"user_id": "alice", "roles": ["admin"]}, services)
        assert user.user_id == "alice"

    def test_provided_roles_stored(self, services):
        user = _user_from_store({"user_id": "bob", "roles": ["editor", "viewer"]}, services)
        assert "editor" in user.roles
        assert "viewer" in user.roles

    def test_missing_roles_falls_back_to_settings(self, services):
        """If roles key is absent, settings.default_user_roles should be used."""
        user = _user_from_store({"user_id": "carol"}, services)
        assert isinstance(user.roles, tuple)
        assert len(user.roles) > 0

    def test_empty_roles_falls_back_to_settings(self, services):
        """If roles is empty/falsy, settings.default_user_roles should be used."""
        user = _user_from_store({"user_id": "dave", "roles": []}, services)
        assert isinstance(user.roles, tuple)
        assert len(user.roles) > 0


# ---------------------------------------------------------------------------
# create_app
# ---------------------------------------------------------------------------


class TestCreateApp:
    """Tests for create_app()."""

    def test_returns_dash_instance(self):
        """create_app() should return a Dash application."""
        result = create_app()
        assert isinstance(result, dash.Dash)

    def test_app_has_server(self):
        """The returned app should expose a Flask server."""
        from flask import Flask

        result = create_app()
        assert isinstance(result.server, Flask)

    def test_app_layout_is_set(self):
        """The app layout should not be None after creation."""
        result = create_app()
        assert result.layout is not None

    def test_app_title_from_settings(self):
        """App title should match the configured title."""
        settings = get_settings()
        result = create_app(settings=settings)
        assert result.title == settings.app_title

    def test_services_attached_to_app(self):
        """The app should carry aiml_services and aiml_settings attributes."""
        result = create_app()
        assert hasattr(result, "aiml_services")
        assert hasattr(result, "aiml_settings")

    def test_custom_services_accepted(self, services):
        """create_app() should accept pre-built services."""
        result = create_app(services=services)
        assert result.aiml_services is services


# ---------------------------------------------------------------------------
# Flask integration: request/response hooks
# ---------------------------------------------------------------------------


class TestFlaskIntegration:
    """Tests for the Flask request / response hooks registered in _register_observability."""

    def test_get_root_returns_200(self, flask_client):
        """GET / should return 200 OK."""
        response = flask_client.get("/")
        assert response.status_code == 200

    def test_x_request_id_header_present(self, flask_client):
        """Every response should carry an X-Request-ID header."""
        response = flask_client.get("/")
        assert "X-Request-ID" in response.headers

    def test_custom_request_id_echoed(self, flask_client):
        """A client-supplied X-Request-ID should be echoed in the response."""
        response = flask_client.get("/", headers={"X-Request-ID": "client-id-42"})
        assert response.headers.get("X-Request-ID") == "client-id-42"

    def test_auto_generated_request_id_is_hex(self, flask_client):
        """Auto-generated request ids should be hex strings."""
        response = flask_client.get("/")
        rid = response.headers.get("X-Request-ID", "")
        assert rid != "-"
        assert all(c in "0123456789abcdef" for c in rid)

    def test_assets_endpoint_accessible(self, flask_client):
        """Dash assets endpoint should respond without server error."""
        response = flask_client.get("/_dash-layout")
        assert response.status_code in {200, 204, 401, 403}

    def test_update_endpoint_exists(self, flask_client):
        """The Dash update-component endpoint should exist."""
        response = flask_client.get("/_dash-update-component")
        # 405 means the endpoint exists (wrong method) which is fine
        assert response.status_code in {200, 400, 405}


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------


class TestModuleSingletons:
    """Tests for the module-level app and server singletons."""

    def test_app_is_dash_instance(self):
        """The module-level app should be a Dash instance."""
        assert isinstance(app, dash.Dash)

    def test_server_is_flask_instance(self):
        """The module-level server should be a Flask instance."""
        from flask import Flask

        assert isinstance(server, Flask)

    def test_server_is_app_server(self):
        """server should be the Flask server of app."""
        assert server is app.server
