"""
Project Manager Utility
========================

Manages projects, experiments, and datasets for the AIML Dash application.
Provides serialization, locking, and comprehensive project management capabilities.

Author: AIML Dash Team
Date: 2026-01-13
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import pandas as pd

from aiml_dash.utils.settings import app_settings


class Experiment:
    """
    Represents an experiment within a project.

    Attributes
    ----------
    id : str
        Unique identifier for the experiment
    name : str
        Name of the experiment
    type : str
        Type of experiment (e.g., "Linear Regression", "Neural Network")
    description : str
        Description of the experiment
    created : str
        Creation timestamp
    modified : str
        Last modification timestamp
    status : str
        Current status (Pending, Running, Completed, Failed)
    parameters : dict
        Experiment parameters and configuration
    results : dict
        Experiment results and metrics
    metadata : dict
        Additional metadata
    """

    def __init__(
        self,
        name: str,
        exp_type: str = "General",
        description: str = "",
        exp_id: Optional[str] = None,
    ):
        """Initialize an experiment."""
        self.id = exp_id or f"exp-{uuid4().hex[:8]}"
        self.name = name
        self.type = exp_type
        self.description = description
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified = self.created
        self.status = "Pending"
        self.parameters: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def update_status(self, status: str):
        """Update experiment status."""
        valid_statuses = ["Pending", "Running", "Completed", "Failed", "Cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
        self.status = status
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_parameters(self, parameters: Dict[str, Any]):
        """Set experiment parameters."""
        self.parameters.update(parameters)
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_results(self, results: Dict[str, Any]):
        """Set experiment results."""
        self.results.update(results)
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Convert experiment to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "created": self.created,
            "modified": self.modified,
            "status": self.status,
            "parameters": self.parameters,
            "results": self.results,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experiment":
        """Create experiment from dictionary."""
        exp = cls(
            name=data["name"],
            exp_type=data.get("type", "General"),
            description=data.get("description", ""),
            exp_id=data.get("id"),
        )
        exp.created = data.get("created", exp.created)
        exp.modified = data.get("modified", exp.modified)
        exp.status = data.get("status", "Pending")
        exp.parameters = data.get("parameters", {})
        exp.results = data.get("results", {})
        exp.metadata = data.get("metadata", {})
        return exp


class Dataset:
    """
    Represents a dataset within a project.

    Attributes
    ----------
    id : str
        Unique identifier for the dataset
    name : str
        Name of the dataset
    source : str
        Source of the dataset (file, database, etc.)
    source_info : dict
        Detailed source information
    description : str
        Description of the dataset
    created : str
        Creation timestamp
    modified : str
        Last modification timestamp
    rows : int
        Number of rows
    columns : int
        Number of columns
    size : str
        Size in human-readable format
    metadata : dict
        Additional metadata
    data : pd.DataFrame, optional
        The actual data (not serialized by default)
    """

    def __init__(
        self,
        name: str,
        source: str = "file",
        description: str = "",
        dataset_id: Optional[str] = None,
    ):
        """Initialize a dataset."""
        self.id = dataset_id or f"ds-{uuid4().hex[:8]}"
        self.name = name
        self.source = source  # 'file', 'database', 'api', 'existing'
        self.source_info: Dict[str, Any] = {}
        self.description = description
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified = self.created
        self.rows = 0
        self.columns = 0
        self.size = "0 KB"
        self.metadata: Dict[str, Any] = {}
        self._data: Optional[pd.DataFrame] = None

    def set_source_info(self, info: Dict[str, Any]):
        """Set source information (connection details, file path, etc.)."""
        self.source_info.update(info)
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_data(self, data: pd.DataFrame):
        """Set the dataset data and update statistics."""
        self._data = data.copy()
        self.rows = len(data)
        self.columns = len(data.columns)

        # Calculate size
        size_bytes = data.memory_usage(deep=True).sum()
        if size_bytes < 1024:
            self.size = f"{size_bytes} B"
        elif size_bytes < 1024**2:
            self.size = f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024**3:
            self.size = f"{size_bytes / 1024**2:.2f} MB"
        else:
            self.size = f"{size_bytes / 1024**3:.2f} GB"

        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the dataset data."""
        if self._data is not None:
            return self._data.copy()
        return None

    def to_dict(self, include_data: bool = False) -> Dict[str, Any]:
        """
        Convert dataset to dictionary.

        Parameters
        ----------
        include_data : bool
            Whether to include the actual data (serialized as JSON)
        """
        result = {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "source_info": self.source_info,
            "description": self.description,
            "created": self.created,
            "modified": self.modified,
            "rows": self.rows,
            "columns": self.columns,
            "size": self.size,
            "metadata": self.metadata,
        }

        if include_data and self._data is not None:
            # Convert DataFrame to JSON-serializable format
            result["data"] = self._data.to_dict(orient="split")

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dataset":
        """Create dataset from dictionary."""
        ds = cls(
            name=data["name"],
            source=data.get("source", "file"),
            description=data.get("description", ""),
            dataset_id=data.get("id"),
        )
        ds.source_info = data.get("source_info", {})
        ds.created = data.get("created", ds.created)
        ds.modified = data.get("modified", ds.modified)
        ds.rows = data.get("rows", 0)
        ds.columns = data.get("columns", 0)
        ds.size = data.get("size", "0 KB")
        ds.metadata = data.get("metadata", {})

        # Restore data if available
        if data.get("data"):
            try:
                ds._data = pd.DataFrame(**data["data"])
            except (KeyError, ValueError, TypeError):
                # Skip if data can't be restored
                pass

        return ds


class Project:
    """
    Represents a project containing experiments and datasets.

    Attributes
    ----------
    id : str
        Unique identifier for the project
    name : str
        Name of the project
    description : str
        Description of the project
    project_type : str
        Type of project
    created : str
        Creation timestamp
    modified : str
        Last modification timestamp
    status : str
        Current status (Active, Archived, Locked)
    locked : bool
        Whether the project is locked for editing
    locked_by : str, optional
        User who locked the project
    locked_at : str, optional
        When the project was locked
    experiments : dict
        Dictionary of experiments (id -> Experiment)
    datasets : dict
        Dictionary of datasets (id -> Dataset)
    metadata : dict
        Additional metadata
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        project_type: str = "General",
        project_id: Optional[str] = None,
    ):
        """Initialize a project."""
        self.id = project_id or f"proj-{uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.project_type = project_type
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified = self.created
        self.status = "Active"
        self.locked = False
        self.locked_by: Optional[str] = None
        self.locked_at: Optional[str] = None

        self.experiments: Dict[str, Experiment] = {}
        self.datasets: Dict[str, Dataset] = {}
        self.metadata: Dict[str, Any] = {}

    def lock(self, user: str = "system"):
        """Lock the project for editing."""
        if self.locked:
            raise ValueError(f"Project is already locked by {self.locked_by}")
        self.locked = True
        self.locked_by = user
        self.locked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified = self.locked_at

    def unlock(self, user: str = "system", force: bool = False):
        """Unlock the project."""
        if not self.locked:
            return

        if not force and self.locked_by != user:
            raise ValueError(f"Project is locked by {self.locked_by}. Use force=True to override.")

        self.locked = False
        self.locked_by = None
        self.locked_at = None
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _check_locked(self):
        """Check if project is locked and raise error if so."""
        if self.locked:
            raise ValueError(f"Project is locked by {self.locked_by}. Unlock before making changes.")

    def add_experiment(self, experiment: Experiment):
        """Add an experiment to the project."""
        self._check_locked()
        self.experiments[experiment.id] = experiment
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def remove_experiment(self, experiment_id: str):
        """Remove an experiment from the project."""
        self._check_locked()
        if experiment_id in self.experiments:
            del self.experiments[experiment_id]
            self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        return self.experiments.get(experiment_id)

    def list_experiments(self) -> List[Experiment]:
        """Get list of all experiments."""
        return list(self.experiments.values())

    def add_dataset(self, dataset: Dataset):
        """Add a dataset to the project."""
        self._check_locked()
        self.datasets[dataset.id] = dataset
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def remove_dataset(self, dataset_id: str):
        """Remove a dataset from the project."""
        self._check_locked()
        if dataset_id in self.datasets:
            del self.datasets[dataset_id]
            self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a dataset by ID."""
        return self.datasets.get(dataset_id)

    def list_datasets(self) -> List[Dataset]:
        """Get list of all datasets."""
        return list(self.datasets.values())

    def archive(self):
        """Archive the project."""
        self._check_locked()
        self.status = "Archived"
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def activate(self):
        """Activate an archived project."""
        self._check_locked()
        self.status = "Active"
        self.modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self, include_data: bool = False) -> Dict[str, Any]:
        """
        Convert project to dictionary for serialization.

        Parameters
        ----------
        include_data : bool
            Whether to include actual dataset data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "created": self.created,
            "modified": self.modified,
            "status": self.status,
            "locked": self.locked,
            "locked_by": self.locked_by,
            "locked_at": self.locked_at,
            "experiments": {exp_id: exp.to_dict() for exp_id, exp in self.experiments.items()},
            "datasets": {ds_id: ds.to_dict(include_data=include_data) for ds_id, ds in self.datasets.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create project from dictionary."""
        proj = cls(
            name=data["name"],
            description=data.get("description", ""),
            project_type=data.get("project_type", "General"),
            project_id=data.get("id"),
        )
        proj.created = data.get("created", proj.created)
        proj.modified = data.get("modified", proj.modified)
        proj.status = data.get("status", "Active")
        proj.locked = data.get("locked", False)
        proj.locked_by = data.get("locked_by")
        proj.locked_at = data.get("locked_at")
        proj.metadata = data.get("metadata", {})

        # Restore experiments
        for exp_data in data.get("experiments", {}).values():
            exp = Experiment.from_dict(exp_data)
            proj.experiments[exp.id] = exp

        # Restore datasets
        for ds_data in data.get("datasets", {}).values():
            ds = Dataset.from_dict(ds_data)
            proj.datasets[ds.id] = ds

        return proj

    def export_json(self, filepath: Union[str, Path], include_data: bool = True):
        """
        Export project to JSON file.

        Parameters
        ----------
        filepath : str or Path
            Path to the output file
        include_data : bool
            Whether to include actual dataset data
        """
        filepath = Path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(include_data=include_data), f, indent=2)

    @classmethod
    def import_json(cls, filepath: Union[str, Path]) -> "Project":
        """
        Import project from JSON file.

        Parameters
        ----------
        filepath : str or Path
            Path to the input file
        """
        filepath = Path(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def export_pickle(self, filepath: Union[str, Path]):
        """
        Export project to pickle file (includes all data).

        Parameters
        ----------
        filepath : str or Path
            Path to the output file
        """
        filepath = Path(filepath)
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def import_pickle(cls, filepath: Union[str, Path]) -> "Project":
        """
        Import project from pickle file.

        Parameters
        ----------
        filepath : str or Path
            Path to the input file
        """
        filepath = Path(filepath)
        with open(filepath, "rb") as f:
            return pickle.load(f)


class ProjectManager:
    """
    Singleton class to manage all projects in the application.

    Provides methods for creating, loading, saving, and managing projects.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Dictionary to store projects
        self.projects: Dict[str, Project] = {}

        # Current active project ID
        self.active_project_id: Optional[str] = None

        # Storage directory
        self.storage_dir = Path.home() / ".aiml_dash" / "projects"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._initialized = True

    def create_project(
        self,
        name: str,
        description: str = "",
        project_type: str = "General",
    ) -> Project:
        """
        Create a new project.

        Parameters
        ----------
        name : str
            Project name
        description : str
            Project description
        project_type : str
            Type of project

        Returns
        -------
        Project
            The created project
        """
        project = Project(name=name, description=description, project_type=project_type)
        self.projects[project.id] = project
        return project

    def add_project(self, project: Project):
        """Add an existing project to the manager."""
        self.projects[project.id] = project

    def remove_project(self, project_id: str):
        """Remove a project from the manager."""
        if project_id in self.projects:
            # Clear active project if it's being removed
            if self.active_project_id == project_id:
                self.active_project_id = None
            del self.projects[project_id]

    def get_project(self, project_id: Optional[str] = None) -> Optional[Project]:
        """
        Get a project by ID, or the active project if ID is None.

        Parameters
        ----------
        project_id : str, optional
            Project ID to retrieve

        Returns
        -------
        Project or None
            The requested project, or None if not found
        """
        if project_id is None:
            project_id = self.active_project_id

        return self.projects.get(project_id) if project_id else None

    def list_projects(self) -> List[Project]:
        """Get list of all projects."""
        return list(self.projects.values())

    def set_active_project(self, project_id: str):
        """Set the active project."""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        self.active_project_id = project_id

    def get_active_project(self) -> Optional[Project]:
        """Get the currently active project."""
        return self.get_project()

    def export_project(
        self,
        project_id: str,
        filepath: Union[str, Path],
        file_format: str = "json",
        include_data: bool = True,
    ):
        """
        Export a project to file.

        Parameters
        ----------
        project_id : str
            Project ID to export
        filepath : str or Path
            Path to the output file
        format : str
            Export format ('json' or 'pickle')
        include_data : bool
            Whether to include actual dataset data (JSON only)
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if file_format == "json":
            project.export_json(filepath, include_data=include_data)
        elif file_format == "pickle":
            project.export_pickle(filepath)
        else:
            raise ValueError(f"Invalid format: {file_format}. Use 'json' or 'pickle'")

    def import_project(
        self,
        filepath: Union[str, Path],
        file_format: str = "json",
        set_active: bool = False,
    ) -> Project:
        """
        Import a project from file.

        Parameters
        ----------
        filepath : str or Path
            Path to the input file
        format : str
            Import format ('json' or 'pickle')
        set_active : bool
            Whether to set the imported project as active

        Returns
        -------
        Project
            The imported project
        """
        if file_format == "json":
            project = Project.import_json(filepath)
        elif file_format == "pickle":
            project = Project.import_pickle(filepath)
        else:
            raise ValueError(f"Invalid format: {file_format}. Use 'json' or 'pickle'")

        self.add_project(project)

        if set_active:
            self.set_active_project(project.id)

        return project

    def save_all_projects(self, directory: Optional[Union[str, Path]] = None):
        """
        Save all projects to disk.

        Parameters
        ----------
        directory : str or Path, optional
            Directory to save projects (defaults to storage_dir)
        """
        if directory is None:
            directory = self.storage_dir
        else:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)

        for project in self.projects.values():
            filename = f"{project.id}_{project.name.replace(' ', '_')}.json"
            filepath = directory / filename
            project.export_json(filepath, include_data=True)

    def load_all_projects(self, directory: Optional[Union[str, Path]] = None):
        """
        Load all projects from disk.

        Parameters
        ----------
        directory : str or Path, optional
            Directory to load projects from (defaults to storage_dir)
        """
        if directory is None:
            directory = self.storage_dir
        else:
            directory = Path(directory)

        if not directory.exists():
            return

        for filepath in directory.glob("*.json"):
            try:
                project = Project.import_json(filepath)
                self.add_project(project)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip files that can't be loaded
                continue

    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """
        Get a summary of a project.

        Parameters
        ----------
        project_id : str
            Project ID

        Returns
        -------
        dict
            Project summary with counts and metadata
        """
        project = self.get_project(project_id)
        if not project:
            return {}

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "type": project.project_type,
            "status": project.status,
            "created": project.created,
            "modified": project.modified,
            "locked": project.locked,
            "locked_by": project.locked_by,
            "num_experiments": len(project.experiments),
            "num_datasets": len(project.datasets),
            "experiments": [
                {
                    "id": exp.id,
                    "name": exp.name,
                    "type": exp.type,
                    "status": exp.status,
                }
                for exp in project.list_experiments()
            ],
            "datasets": [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "source": ds.source,
                    "rows": ds.rows,
                    "columns": ds.columns,
                }
                for ds in project.list_datasets()
            ],
        }


# Create a singleton instance
project_manager = ProjectManager()
