"""Tests for data_manager module."""

import pandas as pd
import numpy as np
import pytest
import base64
import io

from aiml_dash.managers.data_manager import DataManager, data_manager


@pytest.fixture
def dm():
    """Create a fresh DataManager instance for testing."""
    # Reset the singleton
    DataManager._instance = None
    return DataManager()


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [10, 20, 30, 40, 50],
        "C": ["cat", "dog", "cat", "dog", "cat"],
    })


class TestDataManagerSingleton:
    """Test DataManager singleton pattern."""

    def test_singleton_pattern(self):
        """Test DataManager follows singleton pattern."""
        dm1 = DataManager()
        dm2 = DataManager()
        assert dm1 is dm2

    def test_singleton_initialization(self):
        """Test singleton is initialized only once."""
        DataManager._instance = None
        dm1 = DataManager()
        initial_datasets = len(dm1.datasets)

        dm2 = DataManager()
        assert len(dm2.datasets) == initial_datasets


class TestAddDataset:
    """Test add_dataset method."""

    def test_add_dataset_basic(self, dm, sample_dataframe):
        """Test adding a dataset."""
        dm.add_dataset("test_data", sample_dataframe, description="Test dataset")

        assert "test_data" in dm.datasets
        assert dm.descriptions["test_data"] == "Test dataset"

    def test_add_dataset_with_metadata(self, dm, sample_dataframe):
        """Test dataset metadata is created."""
        dm.add_dataset("test_data", sample_dataframe)

        assert "test_data" in dm.metadata
        assert dm.metadata["test_data"]["rows"] == 5
        assert dm.metadata["test_data"]["columns"] == 3

    def test_add_dataset_with_load_command(self, dm, sample_dataframe):
        """Test adding dataset with load command."""
        load_cmd = 'df = pd.read_csv("data.csv")'
        dm.add_dataset("test_data", sample_dataframe, load_command=load_cmd)

        assert dm.load_commands["test_data"] == load_cmd


class TestGetDataset:
    """Test get_dataset method."""

    def test_get_dataset_by_name(self, dm, sample_dataframe):
        """Test getting dataset by name."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.get_dataset("test_data")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_get_dataset_returns_copy(self, dm, sample_dataframe):
        """Test get_dataset returns a copy, not reference."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.get_dataset("test_data")
        result["A"] = 999

        # Original should be unchanged
        original = dm.get_dataset("test_data")
        assert original["A"].iloc[0] != 999

    def test_get_dataset_none(self, dm):
        """Test getting nonexistent dataset returns None."""
        result = dm.get_dataset("nonexistent")
        assert result is None

    def test_get_dataset_active(self, dm, sample_dataframe):
        """Test getting active dataset when name is None."""
        dm.add_dataset("test_data", sample_dataframe)
        dm.set_active_dataset("test_data")
        result = dm.get_dataset(None)

        assert isinstance(result, pd.DataFrame)


class TestGetDatasetNames:
    """Test get_dataset_names method."""

    def test_get_dataset_names(self, dm, sample_dataframe):
        """Test getting list of dataset names."""
        dm.add_dataset("data1", sample_dataframe)
        dm.add_dataset("data2", sample_dataframe)

        names = dm.get_dataset_names()
        assert isinstance(names, list)
        assert "data1" in names
        assert "data2" in names


class TestRemoveDataset:
    """Test remove_dataset method."""

    def test_remove_dataset(self, dm, sample_dataframe):
        """Test removing a dataset."""
        dm.add_dataset("test_data", sample_dataframe)
        dm.remove_dataset("test_data")

        assert "test_data" not in dm.datasets
        assert "test_data" not in dm.metadata

    def test_remove_active_dataset(self, dm, sample_dataframe):
        """Test removing active dataset updates active_dataset."""
        dm.add_dataset("data1", sample_dataframe)
        dm.add_dataset("data2", sample_dataframe)
        dm.set_active_dataset("data1")

        dm.remove_dataset("data1")
        assert dm.active_dataset != "data1"


class TestSetActiveDataset:
    """Test set_active_dataset method."""

    def test_set_active_dataset(self, dm, sample_dataframe):
        """Test setting active dataset."""
        dm.add_dataset("test_data", sample_dataframe)
        dm.set_active_dataset("test_data")

        assert dm.active_dataset == "test_data"

    def test_set_active_dataset_nonexistent(self, dm):
        """Test setting nonexistent dataset as active does nothing."""
        original_active = dm.active_dataset
        dm.set_active_dataset("nonexistent")
        # Should not change if dataset doesn't exist
        assert dm.active_dataset == original_active or dm.active_dataset != "nonexistent"


class TestGetDatasetInfo:
    """Test get_dataset_info method."""

    def test_get_dataset_info(self, dm, sample_dataframe):
        """Test getting dataset info."""
        dm.add_dataset("test_data", sample_dataframe, description="Test")
        info = dm.get_dataset_info("test_data")

        assert info["name"] == "test_data"
        assert info["rows"] == 5
        assert info["columns"] == 3
        assert "column_names" in info
        assert "column_types" in info

    def test_get_dataset_info_none(self, dm):
        """Test getting info for nonexistent dataset."""
        info = dm.get_dataset_info("nonexistent")
        assert info == {}


class TestLoadFromFile:
    """Test load_from_file method."""

    def test_load_from_csv(self, dm):
        """Test loading CSV file."""
        csv_data = "A,B,C\n1,10,cat\n2,20,dog\n3,30,cat"
        encoded = base64.b64encode(csv_data.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"

        success, message = dm.load_from_file(contents, "test.csv")

        assert success is True
        assert "test" in dm.datasets

    def test_load_from_file_duplicate_name(self, dm, sample_dataframe):
        """Test loading file with duplicate name creates unique name."""
        dm.add_dataset("test", sample_dataframe)

        csv_data = "A,B\n1,10\n2,20"
        encoded = base64.b64encode(csv_data.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"

        success, message = dm.load_from_file(contents, "test.csv")

        assert success is True
        assert "test_1" in dm.datasets or len(dm.datasets) > 1

    def test_load_from_file_unsupported(self, dm):
        """Test loading unsupported file type."""
        contents = "data:text/plain;base64,dGVzdA=="
        success, message = dm.load_from_file(contents, "test.txt")

        assert success is False
        assert "Unsupported file type" in message


class TestExportDataset:
    """Test export_dataset method."""

    def test_export_dataset_csv(self, dm, sample_dataframe):
        """Test exporting dataset to CSV."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.export_dataset("test_data", file_format="csv")

        assert result is not None
        assert "A,B,C" in result

    def test_export_dataset_json(self, dm, sample_dataframe):
        """Test exporting dataset to JSON."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.export_dataset("test_data", file_format="json")

        assert result is not None
        assert isinstance(result, str)

    def test_export_nonexistent_dataset(self, dm):
        """Test exporting nonexistent dataset returns None."""
        result = dm.export_dataset("nonexistent", file_format="csv")
        assert result is None


class TestApplyFilter:
    """Test apply_filter method."""

    def test_apply_filter_basic(self, dm, sample_dataframe):
        """Test applying basic filter."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.apply_filter("test_data", filter_expr="A > 2")

        assert len(result) == 3
        assert result["A"].min() > 2

    def test_apply_sort(self, dm, sample_dataframe):
        """Test applying sort."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.apply_filter("test_data", sort_by=["A"], ascending=[False])

        assert result["A"].iloc[0] == 5
        assert result["A"].iloc[-1] == 1

    def test_apply_row_selection_range(self, dm, sample_dataframe):
        """Test applying row selection with range."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.apply_filter("test_data", rows="1:3")

        assert len(result) == 2

    def test_apply_row_selection_individual(self, dm, sample_dataframe):
        """Test applying row selection with individual rows."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.apply_filter("test_data", rows="0,2,4")

        assert len(result) == 3

    def test_apply_filter_invalid_expr(self, dm, sample_dataframe):
        """Test applying invalid filter expression."""
        dm.add_dataset("test_data", sample_dataframe)
        result = dm.apply_filter("test_data", filter_expr="invalid_expr")

        # Should handle error gracefully and return data
        assert result is not None


class TestExportImportState:
    """Test export_all_state and import_all_state methods."""

    def test_export_state(self, dm, sample_dataframe):
        """Test exporting application state."""
        dm.add_dataset("test_data", sample_dataframe)
        state = dm.export_all_state()

        assert isinstance(state, dict)
        assert "version" in state
        assert "datasets" in state
        assert "test_data" in state["datasets"]

    def test_import_state(self, dm, sample_dataframe):
        """Test importing application state."""
        dm.add_dataset("test_data", sample_dataframe)
        state = dm.export_all_state()

        # Clear and reimport
        dm.datasets.clear()
        success, message = dm.import_all_state(state)

        assert success is True
        assert "test_data" in dm.datasets

    def test_import_state_invalid_version(self, dm):
        """Test importing state with invalid version."""
        state = {"version": "0.1"}
        success, message = dm.import_all_state(state)

        assert success is False
        assert "version" in message.lower()


class TestGlobalInstance:
    """Test global data_manager instance."""

    def test_global_instance_exists(self):
        """Test global data_manager instance exists."""
        assert data_manager is not None
        assert isinstance(data_manager, DataManager)

    def test_global_instance_has_sample_data(self):
        """Test global instance has sample data loaded."""
        # Should have some datasets loaded by default
        assert len(data_manager.get_dataset_names()) > 0
