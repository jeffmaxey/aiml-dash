"""Tests for DataManager Parquet-based disk persistence and data quality."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from aiml_dash.utils.data_manager import DataManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def dm(tmp_path: Path) -> DataManager:
    """Return a DataManager with no sample data and a tmp data directory."""
    return DataManager(load_sample_data=False, data_dir=tmp_path)


@pytest.fixture()
def simple_df() -> pd.DataFrame:
    """Return a small, predictable DataFrame."""
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [10.0, 20.0, 30.0, 40.0, 50.0],
            "label": ["a", "b", "a", "b", "a"],
        }
    )


@pytest.fixture()
def dm_with_data(dm: DataManager, simple_df: pd.DataFrame) -> DataManager:
    """Return a DataManager pre-loaded with two datasets."""
    dm.add_dataset("alpha", simple_df, description="Alpha set", load_command="# alpha")
    dm.add_dataset("beta", simple_df.copy(), description="Beta set", load_command="# beta")
    dm.set_active_dataset("alpha")
    return dm


# ---------------------------------------------------------------------------
# persist_to_disk
# ---------------------------------------------------------------------------


class TestPersistToDisk:
    """Tests for persist_to_disk."""

    def test_returns_true_on_success(self, dm_with_data: DataManager, tmp_path: Path) -> None:
        """A successful save returns (True, message)."""
        ok, msg = dm_with_data.persist_to_disk("alpha", tmp_path)
        assert ok is True
        assert "alpha" in msg

    def test_parquet_file_created(self, dm_with_data: DataManager, tmp_path: Path) -> None:
        """The Parquet file must exist after persisting."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        assert (tmp_path / "alpha.parquet").exists()

    def test_sidecar_json_created(self, dm_with_data: DataManager, tmp_path: Path) -> None:
        """A JSON sidecar file must be written alongside the Parquet file."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        meta_file = tmp_path / "alpha.meta.json"
        assert meta_file.exists()

    def test_sidecar_json_content(self, dm_with_data: DataManager, tmp_path: Path) -> None:
        """Sidecar JSON must contain expected keys with correct values."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        sidecar = json.loads((tmp_path / "alpha.meta.json").read_text())

        assert sidecar["description"] == "Alpha set"
        assert sidecar["load_command"] == "# alpha"
        assert sidecar["rows"] == 5
        assert sidecar["columns"] == 3
        assert "added" in sidecar

    def test_uses_active_dataset_when_name_is_none(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Omitting *name* should persist the active dataset."""
        dm_with_data.set_active_dataset("alpha")
        ok, msg = dm_with_data.persist_to_disk(data_dir=tmp_path)
        assert ok is True
        assert (tmp_path / "alpha.parquet").exists()

    def test_uses_instance_data_dir_as_default(self, dm_with_data: DataManager) -> None:
        """When *data_dir* is not given, ``self.data_dir`` should be used."""
        ok, msg = dm_with_data.persist_to_disk("alpha")
        assert ok is True
        assert (dm_with_data.data_dir / "alpha.parquet").exists()

    def test_creates_directory_if_missing(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """The target directory is created automatically."""
        nested = tmp_path / "deep" / "nested"
        ok, _ = dm_with_data.persist_to_disk("alpha", nested)
        assert ok is True
        assert (nested / "alpha.parquet").exists()

    def test_returns_false_for_missing_dataset(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """Requesting a non-existent dataset name returns (False, ...)."""
        ok, msg = dm.persist_to_disk("ghost", tmp_path)
        assert ok is False
        assert "ghost" in msg

    def test_parquet_file_is_readable(
        self, dm_with_data: DataManager, tmp_path: Path, simple_df: pd.DataFrame
    ) -> None:
        """The written Parquet file must be readable and contain correct data."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        loaded = pd.read_parquet(tmp_path / "alpha.parquet")
        assert list(loaded.columns) == list(simple_df.columns)
        assert len(loaded) == len(simple_df)


# ---------------------------------------------------------------------------
# load_from_disk
# ---------------------------------------------------------------------------


class TestLoadFromDisk:
    """Tests for load_from_disk."""

    def _persist(self, dm: DataManager, name: str, tmp_path: Path) -> None:
        ok, _ = dm.persist_to_disk(name, tmp_path)
        assert ok, "Precondition: persist_to_disk must succeed"

    def test_returns_true_on_success(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """A successful load returns (True, message)."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        ok, msg = fresh.load_from_disk("alpha", tmp_path)
        assert ok is True

    def test_dataset_added_to_manager(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """After loading, the dataset must be present in the manager."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        fresh.load_from_disk("alpha", tmp_path)
        assert "alpha" in fresh.datasets

    def test_active_dataset_set_after_load(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """The loaded dataset becomes the active dataset."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        fresh.load_from_disk("alpha", tmp_path)
        assert fresh.active_dataset == "alpha"

    def test_description_restored_from_sidecar(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """The description from the JSON sidecar must be restored."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        fresh.load_from_disk("alpha", tmp_path)
        assert fresh.descriptions["alpha"] == "Alpha set"

    def test_load_command_restored_from_sidecar(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """The load_command from the JSON sidecar must be restored."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        fresh.load_from_disk("alpha", tmp_path)
        assert fresh.load_commands["alpha"] == "# alpha"

    def test_message_contains_rows_and_cols(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Success message should mention row and column counts."""
        self._persist(dm_with_data, "alpha", tmp_path)

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        _, msg = fresh.load_from_disk("alpha", tmp_path)
        assert "5" in msg  # rows
        assert "3" in msg  # cols

    def test_load_without_sidecar(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Loading without a sidecar should still succeed (empty description)."""
        self._persist(dm_with_data, "alpha", tmp_path)
        (tmp_path / "alpha.meta.json").unlink()

        fresh = DataManager(load_sample_data=False, data_dir=tmp_path)
        ok, _ = fresh.load_from_disk("alpha", tmp_path)
        assert ok is True
        assert fresh.descriptions.get("alpha", "") == ""

    def test_returns_false_for_missing_file(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """A missing Parquet file returns (False, ...)."""
        ok, msg = dm.load_from_disk("nonexistent", tmp_path)
        assert ok is False
        assert "nonexistent" in msg or "not found" in msg.lower()

    def test_uses_instance_data_dir_as_default(
        self, dm_with_data: DataManager
    ) -> None:
        """When *data_dir* is omitted, ``self.data_dir`` is used."""
        dm_with_data.persist_to_disk("alpha")
        fresh = DataManager(
            load_sample_data=False, data_dir=dm_with_data.data_dir
        )
        ok, _ = fresh.load_from_disk("alpha")
        assert ok is True


# ---------------------------------------------------------------------------
# list_disk_datasets
# ---------------------------------------------------------------------------


class TestListDiskDatasets:
    """Tests for list_disk_datasets."""

    def test_returns_empty_list_for_nonexistent_dir(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """An empty list is returned when the directory does not exist."""
        result = dm.list_disk_datasets(tmp_path / "does_not_exist")
        assert result == []

    def test_returns_empty_list_when_no_parquet_files(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """An empty list is returned when no Parquet files are present."""
        result = dm.list_disk_datasets(tmp_path)
        assert result == []

    def test_lists_persisted_datasets(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Each persisted dataset should appear in the listing."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        dm_with_data.persist_to_disk("beta", tmp_path)

        listing = dm_with_data.list_disk_datasets(tmp_path)
        names = [entry["name"] for entry in listing]
        assert "alpha" in names
        assert "beta" in names

    def test_entry_has_required_keys(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Every entry must expose the documented keys."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        listing = dm_with_data.list_disk_datasets(tmp_path)
        entry = listing[0]

        for key in ("name", "path", "size_kb", "description", "rows", "columns"):
            assert key in entry, f"Missing key: {key}"

    def test_entry_values_match_sidecar(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Row/column counts and description must come from the sidecar."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        listing = dm_with_data.list_disk_datasets(tmp_path)
        entry = next(e for e in listing if e["name"] == "alpha")

        assert entry["rows"] == 5
        assert entry["columns"] == 3
        assert entry["description"] == "Alpha set"

    def test_skips_files_starting_with_underscore(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """Files whose name starts with ``_`` must be excluded."""
        (tmp_path / "_private.parquet").write_bytes(b"")
        listing = dm.list_disk_datasets(tmp_path)
        assert all(e["name"] != "_private" for e in listing)

    def test_entry_without_sidecar_uses_defaults(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """When no sidecar exists, description is empty and rows/cols are 0."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        (tmp_path / "alpha.meta.json").unlink()

        listing = dm_with_data.list_disk_datasets(tmp_path)
        entry = next(e for e in listing if e["name"] == "alpha")
        assert entry["description"] == ""
        assert entry["rows"] == 0
        assert entry["columns"] == 0

    def test_size_kb_is_positive(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """size_kb must be a positive number for a real Parquet file."""
        dm_with_data.persist_to_disk("alpha", tmp_path)
        listing = dm_with_data.list_disk_datasets(tmp_path)
        entry = next(e for e in listing if e["name"] == "alpha")
        assert entry["size_kb"] > 0

    def test_uses_instance_data_dir_as_default(
        self, dm_with_data: DataManager
    ) -> None:
        """When *data_dir* is omitted, ``self.data_dir`` is scanned."""
        dm_with_data.persist_to_disk("alpha")
        listing = dm_with_data.list_disk_datasets()
        assert any(e["name"] == "alpha" for e in listing)


# ---------------------------------------------------------------------------
# persist_all_datasets
# ---------------------------------------------------------------------------


class TestPersistAllDatasets:
    """Tests for persist_all_datasets."""

    def test_returns_dict_with_all_names(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Result dict must contain an entry for every in-memory dataset."""
        results = dm_with_data.persist_all_datasets(tmp_path)
        assert set(results.keys()) == {"alpha", "beta"}

    def test_all_results_are_successful(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """Every result tuple must indicate success."""
        results = dm_with_data.persist_all_datasets(tmp_path)
        for name, (ok, msg) in results.items():
            assert ok is True, f"Dataset '{name}' failed: {msg}"

    def test_all_files_written(
        self, dm_with_data: DataManager, tmp_path: Path
    ) -> None:
        """A Parquet file must exist for every persisted dataset."""
        dm_with_data.persist_all_datasets(tmp_path)
        for name in ("alpha", "beta"):
            assert (tmp_path / f"{name}.parquet").exists()

    def test_empty_manager_returns_empty_dict(
        self, dm: DataManager, tmp_path: Path
    ) -> None:
        """No datasets -> empty result dict."""
        results = dm.persist_all_datasets(tmp_path)
        assert results == {}

    def test_uses_instance_data_dir_as_default(
        self, dm_with_data: DataManager
    ) -> None:
        """When *data_dir* is omitted, ``self.data_dir`` is used."""
        results = dm_with_data.persist_all_datasets()
        assert all(ok for ok, _ in results.values())


# ---------------------------------------------------------------------------
# get_data_quality
# ---------------------------------------------------------------------------


class TestGetDataQuality:
    """Tests for get_data_quality."""

    @pytest.fixture()
    def quality_df(self) -> pd.DataFrame:
        """DataFrame with known quality characteristics."""
        rng = np.random.default_rng(0)
        n = 100
        df = pd.DataFrame(
            {
                "has_nulls": [None, None] + list(rng.integers(1, 10, n - 2).astype(float)),
                "constant": [42] * n,
                "with_outlier": [1000.0] + list(rng.normal(0, 1, n - 1)),
                "high_card": [f"val_{i}" for i in range(n)],
                "dup_flag": [7, 7] + list(range(n - 2)),
            }
        )
        df["has_nulls"] = df["has_nulls"].astype(float)
        # make row 1 a full duplicate of row 0
        df.loc[1] = df.loc[0]
        return df

    @pytest.fixture()
    def dm_quality(self, dm: DataManager, quality_df: pd.DataFrame) -> DataManager:
        """DataManager pre-loaded with the quality DataFrame."""
        dm.add_dataset("q", quality_df)
        dm.set_active_dataset("q")
        return dm

    def test_returns_empty_for_missing_dataset(self, dm: DataManager) -> None:
        """Missing dataset must return {}."""
        assert dm.get_data_quality("ghost") == {}

    def test_returns_empty_when_no_active_dataset(self, dm: DataManager) -> None:
        """With no active dataset, returns {}."""
        assert dm.get_data_quality() == {}

    def test_required_keys_present(self, dm_quality: DataManager) -> None:
        """All documented keys must be present in the result."""
        quality = dm_quality.get_data_quality("q")
        required = {
            "row_count",
            "col_count",
            "null_counts",
            "null_pct",
            "duplicate_rows",
            "duplicate_pct",
            "high_cardinality_cols",
            "constant_cols",
            "outlier_counts",
            "dtypes",
        }
        assert required.issubset(quality.keys())

    def test_row_and_col_counts(self, dm_quality: DataManager, quality_df: pd.DataFrame) -> None:
        """row_count and col_count must match the DataFrame dimensions."""
        quality = dm_quality.get_data_quality("q")
        assert quality["row_count"] == len(quality_df)
        assert quality["col_count"] == len(quality_df.columns)

    def test_null_counts(self, dm_quality: DataManager) -> None:
        """has_nulls column should report at least 1 null."""
        quality = dm_quality.get_data_quality("q")
        assert quality["null_counts"]["has_nulls"] >= 1

    def test_null_pct_between_0_and_100(self, dm_quality: DataManager) -> None:
        """All null percentages must be in [0, 100]."""
        quality = dm_quality.get_data_quality("q")
        for col, pct in quality["null_pct"].items():
            assert 0.0 <= pct <= 100.0, f"pct for '{col}' out of range: {pct}"

    def test_null_pct_rounded_to_2dp(self, dm_quality: DataManager) -> None:
        """Null percentages must be rounded to 2 decimal places."""
        quality = dm_quality.get_data_quality("q")
        for pct in quality["null_pct"].values():
            assert pct == round(pct, 2)

    def test_duplicate_rows_detected(self, dm_quality: DataManager) -> None:
        """Duplicate row count must be at least 1 (row 1 duplicates row 0)."""
        quality = dm_quality.get_data_quality("q")
        assert quality["duplicate_rows"] >= 1

    def test_duplicate_pct_rounded_to_2dp(self, dm_quality: DataManager) -> None:
        """Duplicate percentage must be rounded to 2 decimal places."""
        quality = dm_quality.get_data_quality("q")
        pct = quality["duplicate_pct"]
        assert pct == round(pct, 2)

    def test_constant_cols_detected(self, dm_quality: DataManager) -> None:
        """The 'constant' column must appear in constant_cols."""
        quality = dm_quality.get_data_quality("q")
        assert "constant" in quality["constant_cols"]

    def test_high_cardinality_cols_detected(self, dm_quality: DataManager) -> None:
        """The high-cardinality column must appear in high_cardinality_cols."""
        quality = dm_quality.get_data_quality("q")
        assert "high_card" in quality["high_cardinality_cols"]

    def test_outlier_counts_non_negative(self, dm_quality: DataManager) -> None:
        """Outlier counts must be non-negative integers."""
        quality = dm_quality.get_data_quality("q")
        for col, count in quality["outlier_counts"].items():
            assert isinstance(count, int)
            assert count >= 0, f"Negative outlier count for '{col}'"

    def test_outlier_detected_in_with_outlier_column(
        self, dm_quality: DataManager
    ) -> None:
        """The large spike (1000) must be flagged as an outlier."""
        quality = dm_quality.get_data_quality("q")
        assert quality["outlier_counts"].get("with_outlier", 0) >= 1

    def test_constant_col_not_in_outliers_when_std_zero(
        self, dm: DataManager
    ) -> None:
        """A numeric column with std=0 should report 0 outliers."""
        df = pd.DataFrame({"flat": [5, 5, 5, 5, 5]})
        dm.add_dataset("flat_ds", df)
        quality = dm.get_data_quality("flat_ds")
        assert quality["outlier_counts"]["flat"] == 0

    def test_dtypes_are_strings(self, dm_quality: DataManager) -> None:
        """Every value in dtypes must be a string."""
        quality = dm_quality.get_data_quality("q")
        for col, dtype_str in quality["dtypes"].items():
            assert isinstance(dtype_str, str), f"dtype for '{col}' is not a str"

    def test_uses_active_dataset_when_name_is_none(
        self, dm_quality: DataManager
    ) -> None:
        """Omitting *name* should operate on the active dataset."""
        dm_quality.set_active_dataset("q")
        quality = dm_quality.get_data_quality()
        assert quality != {}
        assert quality["row_count"] > 0

    def test_no_high_cardinality_for_low_unique_col(self, dm: DataManager) -> None:
        """A column with few unique values must not appear in high_cardinality_cols."""
        df = pd.DataFrame({"cat": ["a", "b", "a", "b", "a"] * 20})
        dm.add_dataset("small_card", df)
        quality = dm.get_data_quality("small_card")
        assert "cat" not in quality["high_cardinality_cols"]
