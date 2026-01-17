"""
Tests for DataManager and ProjectManager integration.

Tests the interaction between DataManager and ProjectManager,
including dataset synchronization and project creation.
"""

import pandas as pd
import pytest
from aiml_dash.managers.data_manager import DataManager, PROJECT_MANAGER_AVAILABLE
from aiml_dash.managers.project_manager import ProjectManager, Project, Dataset


@pytest.fixture
def data_manager():
    """Create a fresh DataManager instance for testing."""
    dm = DataManager()
    # Clear existing datasets except sample data
    for name in list(dm.datasets.keys()):
        if name not in ["diamonds", "titanic"]:
            dm.remove_dataset(name)
    return dm


@pytest.fixture
def project_manager():
    """Create a fresh ProjectManager instance for testing."""
    pm = ProjectManager()
    # Clear existing projects
    pm.projects.clear()
    pm.active_project_id = None
    return pm


@pytest.mark.skipif(not PROJECT_MANAGER_AVAILABLE, reason="ProjectManager not available")
class TestDataProjectIntegration:
    """Test integration between DataManager and ProjectManager."""

    def test_data_manager_has_project_manager(self, data_manager):
        """Test that DataManager has access to ProjectManager."""
        assert data_manager.project_manager is not None
        assert isinstance(data_manager.project_manager, ProjectManager)

    def test_add_dataset_to_project(self, data_manager, project_manager):
        """Test adding a dataset from DataManager to a project."""
        # Create test dataset
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        data_manager.add_dataset("test_data", df, description="Test dataset")

        # Create project
        project = project_manager.create_project("Test Project")
        project_manager.set_active_project(project.id)

        # Add dataset to project
        success, msg = data_manager.add_dataset_to_project("test_data")

        assert success
        assert "test_data" in msg
        assert len(project.list_datasets()) == 1
        assert project.list_datasets()[0].name == "test_data"

    def test_load_dataset_from_project(self, data_manager, project_manager):
        """Test loading a dataset from a project into DataManager."""
        # Create project with dataset
        project = project_manager.create_project("Test Project")
        project_manager.set_active_project(project.id)

        df = pd.DataFrame({"x": [10, 20, 30], "y": [40, 50, 60]})
        dataset = Dataset(name="project_data", source="manual")
        dataset.set_data(df)
        project.add_dataset(dataset)

        # Load into DataManager
        success, msg = data_manager.load_dataset_from_project(dataset.id, dataset_name="loaded_data")

        assert success
        assert "loaded_data" in msg
        assert "loaded_data" in data_manager.datasets
        loaded_df = data_manager.get_dataset("loaded_data")
        assert loaded_df is not None
        assert len(loaded_df) == 3
        assert list(loaded_df.columns) == ["x", "y"]

    def test_sync_with_active_project(self, data_manager, project_manager):
        """Test synchronizing datasets from active project."""
        # Create project with multiple datasets
        project = project_manager.create_project("Multi Dataset Project")
        project_manager.set_active_project(project.id)

        # Add datasets to project
        df1 = pd.DataFrame({"a": [1, 2]})
        dataset1 = Dataset(name="data1", source="manual")
        dataset1.set_data(df1)
        project.add_dataset(dataset1)

        df2 = pd.DataFrame({"b": [3, 4]})
        dataset2 = Dataset(name="data2", source="manual")
        dataset2.set_data(df2)
        project.add_dataset(dataset2)

        # Clear DataManager datasets
        for name in list(data_manager.datasets.keys()):
            data_manager.remove_dataset(name)

        # Sync
        success, msg = data_manager.sync_with_active_project()

        assert success
        assert "2 dataset(s)" in msg
        assert "data1" in data_manager.datasets
        assert "data2" in data_manager.datasets

    def test_create_project_from_datasets(self, data_manager):
        """Test creating a project from DataManager datasets."""
        # Add test datasets
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})
        data_manager.add_dataset("dataset1", df1, description="First dataset")
        data_manager.add_dataset("dataset2", df2, description="Second dataset")

        # Create project from these datasets
        success, msg = data_manager.create_project_from_datasets(
            project_name="New Project",
            dataset_names=["dataset1", "dataset2"],
            description="Test project",
        )

        assert success
        assert "New Project" in msg
        assert "2 dataset(s)" in msg

        # Verify project was created
        project = data_manager.project_manager.get_active_project()
        assert project is not None
        assert project.name == "New Project"
        assert len(project.list_datasets()) == 2

    def test_create_project_from_all_datasets(self, data_manager):
        """Test creating a project from all DataManager datasets."""
        # Clear and add specific datasets
        for name in list(data_manager.datasets.keys()):
            data_manager.remove_dataset(name)

        df1 = pd.DataFrame({"a": [1]})
        df2 = pd.DataFrame({"b": [2]})
        data_manager.add_dataset("data_a", df1)
        data_manager.add_dataset("data_b", df2)

        # Create project without specifying dataset names
        success, msg = data_manager.create_project_from_datasets(project_name="All Datasets Project")

        assert success
        project = data_manager.project_manager.get_active_project()
        assert len(project.list_datasets()) == 2

    def test_get_project_datasets(self, data_manager, project_manager):
        """Test retrieving dataset list from a project."""
        # Create project with datasets
        project = project_manager.create_project("Dataset List Project")
        project_manager.set_active_project(project.id)

        df = pd.DataFrame({"val": [100, 200]})
        dataset = Dataset(name="test_dataset", source="manual", description="A test")
        dataset.set_data(df)
        project.add_dataset(dataset)

        # Get datasets
        datasets_info = data_manager.get_project_datasets()

        assert len(datasets_info) == 1
        assert datasets_info[0]["name"] == "test_dataset"
        assert datasets_info[0]["description"] == "A test"
        assert datasets_info[0]["rows"] == 2
        assert datasets_info[0]["columns"] == 1

    def test_has_active_project(self, data_manager, project_manager):
        """Test checking for active project."""
        # No active project initially
        assert not data_manager.has_active_project()

        # Create and activate project
        project = project_manager.create_project("Active Test")
        project_manager.set_active_project(project.id)

        assert data_manager.has_active_project()

    def test_get_active_project_info(self, data_manager, project_manager):
        """Test getting active project information."""
        # No active project
        assert data_manager.get_active_project_info() is None

        # Create and activate project
        project = project_manager.create_project("Info Test", description="Testing info retrieval")
        project_manager.set_active_project(project.id)

        info = data_manager.get_active_project_info()

        assert info is not None
        assert info["name"] == "Info Test"
        assert info["description"] == "Testing info retrieval"
        assert info["num_experiments"] == 0
        assert info["num_datasets"] == 0
        assert not info["is_locked"]

    def test_add_dataset_to_project_no_active(self, data_manager, project_manager):
        """Test adding dataset to project when no project is active."""
        df = pd.DataFrame({"x": [1, 2]})
        data_manager.add_dataset("test", df)

        # No active project
        project_manager.active_project_id = None

        success, msg = data_manager.add_dataset_to_project("test")

        assert not success
        assert "No active project" in msg

    def test_add_nonexistent_dataset_to_project(self, data_manager, project_manager):
        """Test adding a non-existent dataset to project."""
        project = project_manager.create_project("Test")
        project_manager.set_active_project(project.id)

        success, msg = data_manager.add_dataset_to_project("nonexistent")

        assert not success
        assert "not found" in msg

    def test_load_dataset_from_project_no_data(self, data_manager, project_manager):
        """Test loading dataset from project when dataset has no data."""
        project = project_manager.create_project("Test")
        project_manager.set_active_project(project.id)

        # Create dataset without data
        dataset = Dataset(name="empty", source="manual")
        project.add_dataset(dataset)

        success, msg = data_manager.load_dataset_from_project(dataset.id)

        assert not success
        assert "no data" in msg.lower()

    def test_sync_with_no_active_project(self, data_manager, project_manager):
        """Test syncing when no project is active."""
        project_manager.active_project_id = None

        success, msg = data_manager.sync_with_active_project()

        assert not success
        assert "No active project" in msg

    def test_dataset_roundtrip(self, data_manager, project_manager):
        """Test adding dataset to project and loading it back."""
        # Create dataset in DataManager
        df_original = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
        })
        data_manager.add_dataset("roundtrip", df_original, description="Roundtrip test")

        # Create project and add dataset
        project = project_manager.create_project("Roundtrip Project")
        project_manager.set_active_project(project.id)
        data_manager.add_dataset_to_project("roundtrip")

        # Remove from DataManager
        data_manager.remove_dataset("roundtrip")
        assert "roundtrip" not in data_manager.datasets

        # Load back from project
        dataset_id = project.list_datasets()[0].id
        success, msg = data_manager.load_dataset_from_project(dataset_id, dataset_name="roundtrip_loaded")

        assert success
        df_loaded = data_manager.get_dataset("roundtrip_loaded")
        assert df_loaded is not None
        assert len(df_loaded) == 3
        assert list(df_loaded.columns) == ["int_col", "float_col", "str_col"]
        assert df_loaded["int_col"].tolist() == [1, 2, 3]
