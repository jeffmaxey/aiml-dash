"""Tests for aiml_dash.services module.

Verifies that build_services() returns a fully populated AppServices container
and that ProjectsService behaves correctly for CRUD and UI operations.
"""

from __future__ import annotations

import pytest

from aiml_dash.auth import AuthorizationService, UserContext
from aiml_dash.services import AppServices, ProjectRecord, ProjectsService, build_services
from aiml_dash.utils.config import get_settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def services() -> AppServices:
    """Return a fully built AppServices for testing."""
    return build_services(get_settings())


@pytest.fixture()
def projects() -> ProjectsService:
    """Return a fresh ProjectsService."""
    return ProjectsService()


# ---------------------------------------------------------------------------
# build_services
# ---------------------------------------------------------------------------


class TestBuildServices:
    """Tests for the build_services() factory."""

    def test_returns_app_services(self, services):
        """build_services() should return an AppServices instance."""
        assert isinstance(services, AppServices)

    def test_settings_attribute(self, services):
        """AppServices.settings should be an AppSettings instance."""
        from aiml_dash.utils.config import AppSettings

        assert isinstance(services.settings, AppSettings)

    def test_auth_attribute(self, services):
        """AppServices.auth should be an AuthorizationService instance."""
        assert isinstance(services.auth, AuthorizationService)

    def test_plugins_attribute(self, services):
        """AppServices.plugins should expose plugin management methods."""
        plugins = services.plugins
        assert hasattr(plugins, "get_plugin_metadata")
        assert hasattr(plugins, "get_default_enabled_plugins")
        assert hasattr(plugins, "normalize_enabled_plugins")
        assert hasattr(plugins, "get_pages")
        assert hasattr(plugins, "get_page_registry")
        assert hasattr(plugins, "register_plugin_callbacks")

    def test_data_manager_attribute(self, services):
        """AppServices.data_manager should be a DataManager instance."""
        from aiml_dash.utils.data_manager import DataManager

        assert isinstance(services.data_manager, DataManager)

    def test_projects_attribute(self, services):
        """AppServices.projects should be a ProjectsService instance."""
        assert isinstance(services.projects, ProjectsService)

    def test_auth_default_user(self, services):
        """AuthorizationService.default_user() should return a valid UserContext."""
        user = services.auth.default_user()
        assert isinstance(user, UserContext)
        assert user.user_id == "anonymous"

    def test_plugins_returns_pages(self, services):
        """PluginService.get_pages() should return at least the home page."""
        defaults = services.plugins.get_default_enabled_plugins()
        pages = services.plugins.get_pages(defaults)
        page_ids = {p.id for p in pages}
        assert "home" in page_ids


# ---------------------------------------------------------------------------
# ProjectsService CRUD
# ---------------------------------------------------------------------------


class TestProjectsServiceCrud:
    """Tests for basic CRUD operations on ProjectsService."""

    def test_initial_state_is_empty(self, projects):
        """A new ProjectsService should have no projects."""
        assert projects.metadata() == []
        assert projects.active_project_id is None

    def test_create_project(self, projects):
        """create_project() should return a ProjectRecord with the given name."""
        project = projects.create_project(name="My Project", description="desc")
        assert isinstance(project, ProjectRecord)
        assert project.name == "My Project"
        assert project.description == "desc"
        assert project.id  # non-empty id

    def test_create_sets_active(self, projects):
        """Creating a project should set it as the active project."""
        project = projects.create_project(name="P")
        assert projects.active_project_id == project.id

    def test_create_project_empty_name_raises(self, projects):
        """create_project() should raise ValueError for an empty name."""
        with pytest.raises(ValueError, match="empty"):
            projects.create_project(name="")

    def test_get_project(self, projects):
        """get_project() should return the project by id."""
        project = projects.create_project(name="Test")
        result = projects.get_project(project.id)
        assert result is not None
        assert result.id == project.id

    def test_get_project_missing(self, projects):
        """get_project() should return None for unknown ids."""
        assert projects.get_project("nonexistent") is None

    def test_update_project_name(self, projects):
        """update_project() should update the project name."""
        project = projects.create_project(name="Original")
        updated = projects.update_project(project.id, name="Updated")
        assert updated.name == "Updated"

    def test_update_protected_project_raises(self, projects):
        """Updating a protected project should raise ValueError."""
        project = projects.create_project(name="Protected")
        projects.set_protected(project.id, protected=True)
        with pytest.raises(ValueError, match="protected"):
            projects.update_project(project.id, name="New name")

    def test_copy_project(self, projects):
        """copy_project() should create a separate copy with a new id."""
        original = projects.create_project(name="Original", description="desc")
        copy = projects.copy_project(original.id, name="Copy")
        assert copy.id != original.id
        assert copy.name == "Copy"

    def test_delete_project(self, projects):
        """delete_project() should remove the project from the store."""
        project = projects.create_project(name="ToDelete")
        projects.delete_project(project.id)
        assert projects.get_project(project.id) is None

    def test_delete_protected_project_raises(self, projects):
        """Deleting a protected project should raise ValueError."""
        project = projects.create_project(name="Safe")
        projects.set_protected(project.id, protected=True)
        with pytest.raises(ValueError, match="protected"):
            projects.delete_project(project.id)

    def test_delete_clears_active_project(self, projects):
        """Deleting the active project should clear active_project_id."""
        project = projects.create_project(name="Only")
        assert projects.active_project_id == project.id
        projects.delete_project(project.id)
        assert projects.active_project_id is None


# ---------------------------------------------------------------------------
# ProjectsService – protection and state
# ---------------------------------------------------------------------------


class TestProjectsServiceProtection:
    """Tests for project protection and state snapshot operations."""

    def test_set_protected_true(self, projects):
        """set_protected() should mark the project as protected."""
        project = projects.create_project(name="P")
        updated = projects.set_protected(project.id, protected=True)
        assert updated.protected is True

    def test_set_protected_false(self, projects):
        """set_protected() should remove protection."""
        project = projects.create_project(name="P")
        projects.set_protected(project.id, protected=True)
        updated = projects.set_protected(project.id, protected=False)
        assert updated.protected is False

    def test_save_project_state(self, projects):
        """save_project_state() should persist the snapshot."""
        project = projects.create_project(name="P")
        snapshot = {"ui_state": {"active_page": "home"}, "data_state": {}}
        updated = projects.save_project_state(project.id, snapshot)
        assert updated.state_snapshot == snapshot

    def test_save_protected_project_raises(self, projects):
        """Saving state to a protected project should raise ValueError."""
        project = projects.create_project(name="P")
        projects.set_protected(project.id, protected=True)
        with pytest.raises(ValueError, match="protected"):
            projects.save_project_state(project.id, {})


# ---------------------------------------------------------------------------
# ProjectsService – active project
# ---------------------------------------------------------------------------


class TestProjectsServiceActive:
    """Tests for get_active_project and set_active_project."""

    def test_set_and_get_active_project(self, projects):
        """set_active_project() should update the active project."""
        projects.create_project(name="A")
        p2 = projects.create_project(name="B")
        projects.set_active_project(p2.id)
        active = projects.get_active_project()
        assert active is not None
        assert active.id == p2.id

    def test_clear_active_project(self, projects):
        """set_active_project(None) should clear the active project."""
        projects.create_project(name="P")
        projects.set_active_project(None)
        assert projects.get_active_project() is None

    def test_set_active_missing_project_raises(self, projects):
        """set_active_project() should raise KeyError for unknown ids."""
        with pytest.raises(KeyError):
            projects.set_active_project("nonexistent")


# ---------------------------------------------------------------------------
# ProjectsService – UI helpers
# ---------------------------------------------------------------------------


class TestProjectsServiceUi:
    """Tests for metadata() and project_options()."""

    def test_metadata_returns_list(self, projects):
        """metadata() should return a list of dicts."""
        projects.create_project(name="P1")
        meta = projects.metadata()
        assert isinstance(meta, list)
        assert len(meta) == 1
        assert meta[0]["name"] == "P1"

    def test_metadata_keys(self, projects):
        """Each metadata dict should contain the expected keys."""
        projects.create_project(name="P")
        meta = projects.metadata()[0]
        for key in ("id", "name", "description", "protected", "created_at", "updated_at"):
            assert key in meta

    def test_project_options(self, projects):
        """project_options() should return label/value dicts."""
        project = projects.create_project(name="Option")
        options = projects.project_options()
        assert len(options) == 1
        assert options[0]["label"] == "Option"
        assert options[0]["value"] == project.id
