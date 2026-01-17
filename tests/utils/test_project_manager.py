"""
Tests for Project Manager
==========================

Unit tests for the project_manager module.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from aiml_dash.managers.project_manager import (
    Dataset,
    Experiment,
    Project,
    ProjectManager,
)


class TestExperiment:
    """Tests for the Experiment class."""

    def test_experiment_creation(self):
        """Test creating an experiment."""
        exp = Experiment(name="Test Experiment", exp_type="Linear Regression")
        assert exp.name == "Test Experiment"
        assert exp.type == "Linear Regression"
        assert exp.status == "Pending"
        assert exp.id.startswith("exp-")

    def test_experiment_update_status(self):
        """Test updating experiment status."""
        exp = Experiment(name="Test Experiment")
        exp.update_status("Running")
        assert exp.status == "Running"

        with pytest.raises(ValueError):
            exp.update_status("InvalidStatus")

    def test_experiment_parameters(self):
        """Test setting experiment parameters."""
        exp = Experiment(name="Test Experiment")
        exp.set_parameters({"learning_rate": 0.01, "epochs": 100})
        assert exp.parameters["learning_rate"] == 0.01
        assert exp.parameters["epochs"] == 100

    def test_experiment_serialization(self):
        """Test experiment to_dict and from_dict."""
        exp = Experiment(name="Test Experiment", exp_type="Neural Network")
        exp.set_parameters({"layers": 3})
        exp.set_results({"accuracy": 0.95})

        exp_dict = exp.to_dict()
        restored = Experiment.from_dict(exp_dict)

        assert restored.name == exp.name
        assert restored.type == exp.type
        assert restored.parameters["layers"] == 3
        assert restored.results["accuracy"] == 0.95


class TestDataset:
    """Tests for the Dataset class."""

    def test_dataset_creation(self):
        """Test creating a dataset."""
        ds = Dataset(name="test_data.csv", source="file")
        assert ds.name == "test_data.csv"
        assert ds.source == "file"
        assert ds.id.startswith("ds-")

    def test_dataset_with_data(self):
        """Test dataset with actual data."""
        ds = Dataset(name="test_data.csv")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        ds.set_data(df)

        assert ds.rows == 3
        assert ds.columns == 2
        assert ds.size  # Should have a size string

        retrieved = ds.get_data()
        assert retrieved is not None
        assert len(retrieved) == 3

    def test_dataset_source_info(self):
        """Test setting dataset source information."""
        ds = Dataset(name="db_table", source="database")
        ds.set_source_info({"db_type": "PostgreSQL", "host": "localhost", "table": "users"})
        assert ds.source_info["db_type"] == "PostgreSQL"
        assert ds.source_info["table"] == "users"

    def test_dataset_serialization(self):
        """Test dataset serialization."""
        ds = Dataset(name="test_data.csv", source="file")
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        ds.set_data(df)

        # Without data
        ds_dict = ds.to_dict(include_data=False)
        restored = Dataset.from_dict(ds_dict)
        assert restored.name == ds.name
        assert restored.rows == ds.rows
        assert restored.get_data() is None

        # With data
        ds_dict = ds.to_dict(include_data=True)
        restored = Dataset.from_dict(ds_dict)
        assert restored.name == ds.name
        restored_data = restored.get_data()
        assert restored_data is not None
        assert len(restored_data) == 3


class TestProject:
    """Tests for the Project class."""

    def test_project_creation(self):
        """Test creating a project."""
        proj = Project(name="Test Project", description="A test project")
        assert proj.name == "Test Project"
        assert proj.description == "A test project"
        assert proj.status == "Active"
        assert not proj.locked
        assert proj.id.startswith("proj-")

    def test_project_locking(self):
        """Test project locking mechanism."""
        proj = Project(name="Test Project")

        # Lock the project
        proj.lock(user="alice")
        assert proj.locked
        assert proj.locked_by == "alice"

        # Try to lock again (should fail)
        with pytest.raises(ValueError):
            proj.lock(user="bob")

        # Try to unlock with wrong user (should fail)
        with pytest.raises(ValueError):
            proj.unlock(user="bob")

        # Unlock with correct user
        proj.unlock(user="alice")
        assert not proj.locked

        # Force unlock
        proj.lock(user="alice")
        proj.unlock(user="bob", force=True)
        assert not proj.locked

    def test_project_experiments(self):
        """Test adding and managing experiments."""
        proj = Project(name="Test Project")

        exp1 = Experiment(name="Exp 1")
        exp2 = Experiment(name="Exp 2")

        proj.add_experiment(exp1)
        proj.add_experiment(exp2)

        assert len(proj.experiments) == 2
        assert proj.get_experiment(exp1.id) == exp1

        exps = proj.list_experiments()
        assert len(exps) == 2

        proj.remove_experiment(exp1.id)
        assert len(proj.experiments) == 1

    def test_project_datasets(self):
        """Test adding and managing datasets."""
        proj = Project(name="Test Project")

        ds1 = Dataset(name="data1.csv")
        ds2 = Dataset(name="data2.csv")

        proj.add_dataset(ds1)
        proj.add_dataset(ds2)

        assert len(proj.datasets) == 2
        assert proj.get_dataset(ds1.id) == ds1

        datasets = proj.list_datasets()
        assert len(datasets) == 2

        proj.remove_dataset(ds1.id)
        assert len(proj.datasets) == 1

    def test_project_locked_modifications(self):
        """Test that locked projects can't be modified."""
        proj = Project(name="Test Project")
        proj.lock()

        exp = Experiment(name="Test Exp")
        ds = Dataset(name="test.csv")

        with pytest.raises(ValueError):
            proj.add_experiment(exp)

        with pytest.raises(ValueError):
            proj.add_dataset(ds)

        with pytest.raises(ValueError):
            proj.archive()

    def test_project_archive(self):
        """Test archiving and activating projects."""
        proj = Project(name="Test Project")

        proj.archive()
        assert proj.status == "Archived"

        proj.activate()
        assert proj.status == "Active"

    def test_project_serialization(self):
        """Test project serialization."""
        proj = Project(name="Test Project", description="Test")

        exp = Experiment(name="Exp 1")
        ds = Dataset(name="data.csv")

        proj.add_experiment(exp)
        proj.add_dataset(ds)

        proj_dict = proj.to_dict()
        restored = Project.from_dict(proj_dict)

        assert restored.name == proj.name
        assert len(restored.experiments) == 1
        assert len(restored.datasets) == 1

    def test_project_export_import_json(self):
        """Test exporting and importing projects as JSON."""
        proj = Project(name="Test Project")
        exp = Experiment(name="Exp 1")
        ds = Dataset(name="data.csv")
        df = pd.DataFrame({"a": [1, 2, 3]})
        ds.set_data(df)

        proj.add_experiment(exp)
        proj.add_dataset(ds)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "project.json"

            # Export with data
            proj.export_json(filepath, include_data=True)
            assert filepath.exists()

            # Import
            restored = Project.import_json(filepath)
            assert restored.name == proj.name
            assert len(restored.experiments) == 1
            assert len(restored.datasets) == 1

            # Check data was preserved
            restored_ds = list(restored.datasets.values())[0]
            restored_data = restored_ds.get_data()
            assert restored_data is not None
            assert len(restored_data) == 3

    def test_project_export_import_pickle(self):
        """Test exporting and importing projects as pickle."""
        proj = Project(name="Test Project")
        exp = Experiment(name="Exp 1")
        proj.add_experiment(exp)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "project.pkl"

            # Export
            proj.export_pickle(filepath)
            assert filepath.exists()

            # Import
            restored = Project.import_pickle(filepath)
            assert restored.name == proj.name
            assert len(restored.experiments) == 1


class TestProjectManager:
    """Tests for the ProjectManager class."""

    def test_singleton(self):
        """Test that ProjectManager is a singleton."""
        pm1 = ProjectManager()
        pm2 = ProjectManager()
        assert pm1 is pm2

    def test_create_project(self):
        """Test creating a project through the manager."""
        pm = ProjectManager()
        pm.projects.clear()  # Clear for testing

        proj = pm.create_project(name="Test Project", description="Test")
        assert proj.name == "Test Project"
        assert proj.id in pm.projects

    def test_add_remove_project(self):
        """Test adding and removing projects."""
        pm = ProjectManager()
        pm.projects.clear()

        proj = Project(name="Test Project")
        pm.add_project(proj)
        assert proj.id in pm.projects

        pm.remove_project(proj.id)
        assert proj.id not in pm.projects

    def test_active_project(self):
        """Test setting and getting active project."""
        pm = ProjectManager()
        pm.projects.clear()

        proj1 = pm.create_project(name="Project 1")
        proj2 = pm.create_project(name="Project 2")

        pm.set_active_project(proj1.id)
        assert pm.get_active_project() == proj1

        pm.set_active_project(proj2.id)
        assert pm.get_active_project() == proj2

    def test_list_projects(self):
        """Test listing all projects."""
        pm = ProjectManager()
        pm.projects.clear()

        pm.create_project(name="Project 1")
        pm.create_project(name="Project 2")
        pm.create_project(name="Project 3")

        projects = pm.list_projects()
        assert len(projects) == 3

    def test_export_import_project(self):
        """Test exporting and importing through manager."""
        pm = ProjectManager()
        pm.projects.clear()

        proj = pm.create_project(name="Test Project")
        exp = Experiment(name="Exp 1")
        proj.add_experiment(exp)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "project.json"

            # Export
            pm.export_project(proj.id, filepath, file_format="json")

            # Clear and import
            pm.projects.clear()
            imported = pm.import_project(filepath, file_format="json", set_active=True)

            assert imported.name == "Test Project"
            assert pm.get_active_project() == imported

    def test_save_load_all_projects(self):
        """Test saving and loading all projects."""
        pm = ProjectManager()
        pm.projects.clear()

        pm.create_project(name="Project 1")
        pm.create_project(name="Project 2")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save all
            pm.save_all_projects(tmpdir)

            # Clear and load
            pm.projects.clear()
            pm.load_all_projects(tmpdir)

            assert len(pm.list_projects()) == 2

    def test_project_summary(self):
        """Test getting project summary."""
        pm = ProjectManager()
        pm.projects.clear()

        proj = pm.create_project(name="Test Project")
        exp = Experiment(name="Exp 1")
        ds = Dataset(name="data.csv")

        proj.add_experiment(exp)
        proj.add_dataset(ds)

        summary = pm.get_project_summary(proj.id)
        assert summary["name"] == "Test Project"
        assert summary["num_experiments"] == 1
        assert summary["num_datasets"] == 1
        assert len(summary["experiments"]) == 1
        assert len(summary["datasets"]) == 1
