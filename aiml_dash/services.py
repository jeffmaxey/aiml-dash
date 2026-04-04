"""Application service layer for AIML Dash.

This module wires together the various subsystems (auth, plugins, data, projects)
into a single ``AppServices`` container that is created once per application
instance and threaded through the request lifecycle.

Classes:
    ProjectRecord: Lightweight in-memory project record.
    ProjectsService: In-memory project persistence service.
    PluginService: Thin facade exposing ``PluginRuntime`` methods.
    AppServices: Container for all application-level service singletons.

Functions:
    build_services: Factory that constructs a fully initialised ``AppServices``.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from aiml_dash.auth import AuthorizationService, UserContext
from aiml_dash.plugins.registry import (
    _default_runtime,
)
from aiml_dash.plugins.runtime import PluginRuntime
from aiml_dash.utils.config import AppSettings
from aiml_dash.utils.data_manager import DataManager, create_data_manager

# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@dataclass
class ProjectRecord:
    """In-memory project record.

    Attributes:
        id: Unique project identifier (UUID string).
        name: Human-readable project name.
        description: Optional project description.
        protected: Whether the project is protected from editing/deletion.
        state_snapshot: Serialisable snapshot of UI and data state.
        created_at: ISO-8601 timestamp of creation.
        updated_at: ISO-8601 timestamp of last modification.
    """

    id: str
    name: str
    description: str = ""
    protected: bool = False
    state_snapshot: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ProjectsService:
    """In-memory project management service.

    Stores project records in memory.  All data is lost when the process
    restarts; a persistent backend can be substituted by replacing this class
    in :func:`build_services`.
    """

    def __init__(self) -> None:
        self._projects: dict[str, ProjectRecord] = {}
        self._active_project_id: str | None = None

    @property
    def active_project_id(self) -> str | None:
        """Return the id of the currently active project, or ``None``."""
        return self._active_project_id

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def create_project(
        self,
        *,
        name: str,
        description: str = "",
        state_snapshot: dict[str, Any] | None = None,
    ) -> ProjectRecord:
        """Create a new project.

        Parameters
        ----------
        name : str
            Project name (must be non-empty).
        description : str
            Optional description.
        state_snapshot : dict[str, Any] | None
            Initial state snapshot.

        Returns
        -------
        ProjectRecord
            The newly created project record.
        """
        if not name:
            msg = "Project name must not be empty"
            raise ValueError(msg)
        project = ProjectRecord(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            state_snapshot=state_snapshot or {},
        )
        self._projects[project.id] = project
        self._active_project_id = project.id
        return project

    def get_project(self, project_id: str) -> ProjectRecord | None:
        """Return the project with the given id, or ``None``.

        Parameters
        ----------
        project_id : str
            Project identifier.

        Returns
        -------
        ProjectRecord | None
            Matching project or ``None`` if not found.
        """
        return self._projects.get(project_id)

    def update_project(
        self,
        project_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> ProjectRecord:
        """Update a project's name and/or description.

        Parameters
        ----------
        project_id : str
            Project identifier.
        name : str | None
            New project name (unchanged if ``None``).
        description : str | None
            New project description (unchanged if ``None``).

        Returns
        -------
        ProjectRecord
            The updated project record.
        """
        project = self._require_project(project_id)
        if project.protected:
            msg = f"Project '{project.name}' is protected and cannot be edited"
            raise ValueError(msg)
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        project.updated_at = datetime.now().isoformat()
        return project

    def copy_project(
        self,
        project_id: str,
        *,
        name: str,
        description: str = "",
    ) -> ProjectRecord:
        """Create a copy of an existing project.

        Parameters
        ----------
        project_id : str
            Source project identifier.
        name : str
            Name for the copy.
        description : str
            Optional description for the copy.

        Returns
        -------
        ProjectRecord
            The newly created copy.
        """
        source = self._require_project(project_id)
        return self.create_project(
            name=name,
            description=description or source.description,
            state_snapshot=dict(source.state_snapshot),
        )

    def delete_project(self, project_id: str) -> None:
        """Delete a project.

        Parameters
        ----------
        project_id : str
            Project identifier.
        """
        project = self._require_project(project_id)
        if project.protected:
            msg = f"Project '{project.name}' is protected and cannot be deleted"
            raise ValueError(msg)
        del self._projects[project_id]
        if self._active_project_id == project_id:
            self._active_project_id = next(iter(self._projects), None)

    def set_protected(self, project_id: str, *, protected: bool) -> ProjectRecord:
        """Set the protection flag on a project.

        Parameters
        ----------
        project_id : str
            Project identifier.
        protected : bool
            New protection state.

        Returns
        -------
        ProjectRecord
            The updated project record.
        """
        project = self._require_project(project_id)
        project.protected = protected
        project.updated_at = datetime.now().isoformat()
        return project

    def save_project_state(
        self, project_id: str, state_snapshot: dict[str, Any]
    ) -> ProjectRecord:
        """Persist a state snapshot into a project.

        Parameters
        ----------
        project_id : str
            Project identifier.
        state_snapshot : dict[str, Any]
            New state snapshot to persist.

        Returns
        -------
        ProjectRecord
            The updated project record.
        """
        project = self._require_project(project_id)
        if project.protected:
            msg = f"Project '{project.name}' is protected and cannot be overwritten"
            raise ValueError(msg)
        project.state_snapshot = state_snapshot
        project.updated_at = datetime.now().isoformat()
        return project

    def set_active_project(self, project_id: str | None) -> ProjectRecord | None:
        """Change the active project.

        Parameters
        ----------
        project_id : str | None
            Project to activate, or ``None`` to clear the active project.

        Returns
        -------
        ProjectRecord | None
            The activated project, or ``None`` when *project_id* is ``None``.
        """
        if project_id is None:
            self._active_project_id = None
            return None
        project = self._require_project(project_id)
        self._active_project_id = project_id
        return project

    def get_active_project(self) -> ProjectRecord | None:
        """Return the currently active project, or ``None``.

        Returns
        -------
        ProjectRecord | None
            Active project record or ``None``.
        """
        if self._active_project_id is None:
            return None
        return self._projects.get(self._active_project_id)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def metadata(self) -> list[dict[str, Any]]:
        """Return serialisable metadata for all projects.

        Returns
        -------
        list[dict[str, Any]]
            One metadata dict per project, suitable for ``dcc.Store``.
        """
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "protected": p.protected,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p in self._projects.values()
        ]

    def project_options(self) -> list[dict[str, str]]:
        """Return ``[{"label": name, "value": id}]`` options for dropdowns.

        Returns
        -------
        list[dict[str, str]]
            Options suitable for DMC Select / dcc.Dropdown components.
        """
        return [{"label": p.name, "value": p.id} for p in self._projects.values()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_project(self, project_id: str) -> ProjectRecord:
        project = self._projects.get(project_id)
        if project is None:
            msg = f"Project '{project_id}' not found"
            raise KeyError(msg)
        return project


# ---------------------------------------------------------------------------
# Plugin service facade
# ---------------------------------------------------------------------------

class PluginService:
    """Thin facade that delegates to a ``PluginRuntime`` instance.

    This class exists so that ``AppServices.plugins`` has a stable interface
    even if the underlying runtime implementation changes.
    """

    def __init__(self, runtime: PluginRuntime) -> None:
        self._runtime = runtime

    @property
    def runtime(self) -> PluginRuntime:
        """Return the underlying ``PluginRuntime``."""
        return self._runtime

    def get_plugin_metadata(
        self,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[dict[str, Any]]:
        """Delegate to :meth:`PluginRuntime.get_plugin_metadata`."""
        return self._runtime.get_plugin_metadata(
            enable_dynamic_loading=enable_dynamic_loading,
            user=user,
        )

    def get_default_enabled_plugins(
        self,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[str]:
        """Delegate to :meth:`PluginRuntime.get_default_enabled_plugins`."""
        return self._runtime.get_default_enabled_plugins(
            enable_dynamic_loading=enable_dynamic_loading,
            user=user,
        )

    def normalize_enabled_plugins(
        self,
        enabled_plugins: Any,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[str]:
        """Delegate to :meth:`PluginRuntime.normalize_enabled_plugins`."""
        return self._runtime.normalize_enabled_plugins(
            enabled_plugins,
            enable_dynamic_loading=enable_dynamic_loading,
            user=user,
        )

    def get_pages(
        self,
        enabled_plugins: Any = None,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[Any]:
        """Delegate to :meth:`PluginRuntime.get_pages`."""
        return self._runtime.get_pages(
            enabled_plugins,
            enable_dynamic_loading=enable_dynamic_loading,
            user=user,
        )

    def get_page_registry(
        self,
        enabled_plugins: Any = None,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> dict[str, Any]:
        """Delegate to :meth:`PluginRuntime.get_page_registry`."""
        return self._runtime.get_page_registry(
            enabled_plugins,
            enable_dynamic_loading=enable_dynamic_loading,
            user=user,
        )

    def register_plugin_callbacks(self, app: object) -> None:
        """Delegate to :meth:`PluginRuntime.register_plugin_callbacks`."""
        self._runtime.register_plugin_callbacks(app)


# ---------------------------------------------------------------------------
# AppServices container
# ---------------------------------------------------------------------------

@dataclass
class AppServices:
    """Container for all application-level service singletons.

    Attributes:
        settings: Application configuration.
        auth: Authorization service for user/role management.
        plugins: Plugin management facade.
        data_manager: In-memory dataset manager.
        projects: Project persistence service.
    """

    settings: AppSettings
    auth: AuthorizationService
    plugins: PluginService
    data_manager: DataManager
    projects: ProjectsService


def build_services(settings: AppSettings) -> AppServices:
    """Construct a fully initialised ``AppServices`` container.

    Parameters
    ----------
    settings : AppSettings
        Application configuration to use for all services.

    Returns
    -------
    AppServices
        Wired-up service container ready for injection into the application.
    """
    auth = AuthorizationService(settings)
    runtime = _default_runtime()
    plugin_service = PluginService(runtime)
    data_manager = create_data_manager()
    projects = ProjectsService()

    return AppServices(
        settings=settings,
        auth=auth,
        plugins=plugin_service,
        data_manager=data_manager,
        projects=projects,
    )
