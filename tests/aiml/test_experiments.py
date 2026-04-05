"""Tests for aiml.experiments – Experiment and ExperimentRegistry."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from aiml.experiments import Experiment, ExperimentRegistry, ExperimentStatus
from aiml.supervised.linear import LinearRegression, LogisticRegression
from aiml.supervised.trees import RandomForestClassifier


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def regression_data():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((80, 3))
    y = 2 * X[:, 0] - X[:, 1] + rng.normal(0, 0.2, 80)
    return X, y


@pytest.fixture()
def classification_data():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((80, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


@pytest.fixture()
def blank_experiment():
    return Experiment(name="test_exp", description="unit test", tags={"env": "test"})


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ---------------------------------------------------------------------------
# ExperimentStatus
# ---------------------------------------------------------------------------

class TestExperimentStatus:
    def test_values(self):
        assert ExperimentStatus.CREATED.value == "created"
        assert ExperimentStatus.RUNNING.value == "running"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.FAILED.value == "failed"

    def test_is_string_enum(self):
        assert isinstance(ExperimentStatus.CREATED, str)


# ---------------------------------------------------------------------------
# Experiment construction
# ---------------------------------------------------------------------------

class TestExperimentConstruction:
    def test_defaults(self):
        exp = Experiment(name="x")
        assert exp.name == "x"
        assert exp.status == ExperimentStatus.CREATED
        assert exp.params == {}
        assert exp.metrics == {}
        assert exp.datasets == {}
        assert exp.artifacts == {}
        assert exp.error is None

    def test_custom_id(self):
        exp = Experiment(name="x", experiment_id="abc-123")
        assert exp.experiment_id == "abc-123"

    def test_auto_id_is_uuid_format(self):
        exp = Experiment(name="x")
        # UUID4 has 5 hyphen-separated groups
        parts = exp.experiment_id.split("-")
        assert len(parts) == 5

    def test_tags_stored(self):
        exp = Experiment(name="x", tags={"k": "v"})
        assert exp.tags == {"k": "v"}

    def test_repr(self):
        exp = Experiment(name="my_exp")
        assert "my_exp" in repr(exp)
        assert "created" in repr(exp)


# ---------------------------------------------------------------------------
# Logging – params
# ---------------------------------------------------------------------------

class TestLogParam:
    def test_single_param(self, blank_experiment):
        blank_experiment.log_param("alpha", 0.01)
        assert blank_experiment.params["alpha"] == 0.01

    def test_returns_self(self, blank_experiment):
        result = blank_experiment.log_param("x", 1)
        assert result is blank_experiment

    def test_multiple_params(self, blank_experiment):
        blank_experiment.log_params({"a": 1, "b": "hello", "c": True})
        assert blank_experiment.params["a"] == 1
        assert blank_experiment.params["b"] == "hello"
        assert blank_experiment.params["c"] is True

    def test_log_params_returns_self(self, blank_experiment):
        assert blank_experiment.log_params({"x": 1}) is blank_experiment

    def test_overwrite_param(self, blank_experiment):
        blank_experiment.log_param("lr", 0.1)
        blank_experiment.log_param("lr", 0.01)
        assert blank_experiment.params["lr"] == 0.01

    def test_numpy_scalar_serialized(self, blank_experiment):
        blank_experiment.log_param("val", np.float64(3.14))
        assert isinstance(blank_experiment.params["val"], float)


# ---------------------------------------------------------------------------
# Logging – metrics
# ---------------------------------------------------------------------------

class TestLogMetric:
    def test_single_metric(self, blank_experiment):
        blank_experiment.log_metric("r2", 0.95)
        assert "r2" in blank_experiment.metrics
        assert len(blank_experiment.metrics["r2"]) == 1
        assert blank_experiment.metrics["r2"][0]["value"] == 0.95

    def test_returns_self(self, blank_experiment):
        assert blank_experiment.log_metric("x", 1.0) is blank_experiment

    def test_metric_step(self, blank_experiment):
        blank_experiment.log_metric("loss", 0.5, step=1)
        blank_experiment.log_metric("loss", 0.3, step=2)
        entries = blank_experiment.metrics["loss"]
        assert len(entries) == 2
        assert entries[0]["step"] == 1
        assert entries[1]["step"] == 2

    def test_metric_no_step_is_none(self, blank_experiment):
        blank_experiment.log_metric("acc", 0.9)
        assert blank_experiment.metrics["acc"][0]["step"] is None

    def test_metric_has_timestamp(self, blank_experiment):
        blank_experiment.log_metric("acc", 0.9)
        assert "timestamp" in blank_experiment.metrics["acc"][0]

    def test_log_metrics_dict(self, blank_experiment):
        blank_experiment.log_metrics({"r2": 0.9, "mae": 0.1})
        assert "r2" in blank_experiment.metrics
        assert "mae" in blank_experiment.metrics

    def test_log_metrics_with_step(self, blank_experiment):
        blank_experiment.log_metrics({"loss": 0.2}, step=3)
        assert blank_experiment.metrics["loss"][0]["step"] == 3

    def test_multiple_values_accumulate(self, blank_experiment):
        blank_experiment.log_metric("loss", 1.0)
        blank_experiment.log_metric("loss", 0.5)
        blank_experiment.log_metric("loss", 0.2)
        assert len(blank_experiment.metrics["loss"]) == 3


# ---------------------------------------------------------------------------
# Logging – datasets
# ---------------------------------------------------------------------------

class TestLogDataset:
    def test_records_shape(self, blank_experiment, regression_data):
        X, y = regression_data
        blank_experiment.log_dataset("train", X, y)
        info = blank_experiment.datasets["train"]
        assert info["n_samples"] == 80
        assert info["n_features"] == 3

    def test_returns_self(self, blank_experiment, regression_data):
        X, y = regression_data
        assert blank_experiment.log_dataset("train", X, y) is blank_experiment

    def test_no_y(self, blank_experiment, regression_data):
        X, _ = regression_data
        blank_experiment.log_dataset("features", X)
        assert "features" in blank_experiment.datasets

    def test_description_stored(self, blank_experiment, regression_data):
        X, y = regression_data
        blank_experiment.log_dataset("train", X, y, description="my data")
        assert blank_experiment.datasets["train"]["description"] == "my data"


# ---------------------------------------------------------------------------
# Logging – artifacts
# ---------------------------------------------------------------------------

class TestLogArtifact:
    def test_stores_serializable(self, blank_experiment):
        blank_experiment.log_artifact("confusion_matrix", [[10, 2], [1, 15]])
        assert blank_experiment.artifacts["confusion_matrix"] == [[10, 2], [1, 15]]

    def test_returns_self(self, blank_experiment):
        assert blank_experiment.log_artifact("x", 1) is blank_experiment

    def test_stores_dict(self, blank_experiment):
        blank_experiment.log_artifact("stats", {"mean": 1.5, "std": 0.3})
        assert blank_experiment.artifacts["stats"]["mean"] == 1.5


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

class TestSetNotes:
    def test_stores_notes(self, blank_experiment):
        blank_experiment.set_notes("# Notes\nThis is a test run.")
        assert blank_experiment.notes == "# Notes\nThis is a test run."

    def test_returns_self(self, blank_experiment):
        assert blank_experiment.set_notes("hi") is blank_experiment


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

class TestRun:
    def test_run_sets_status_completed(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="run_test")
        model = LinearRegression()
        exp.run(model, X, y)
        assert exp.status == ExperimentStatus.COMPLETED

    def test_run_returns_metrics(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="run_test")
        metrics = exp.run(LinearRegression(), X, y)
        assert "r2" in metrics

    def test_run_logs_metrics(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="run_test")
        exp.run(LinearRegression(), X, y)
        assert len(exp.metrics) > 0

    def test_run_logs_model_params(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="run_test")
        exp.run(LinearRegression(), X, y)
        assert len(exp.params) > 0

    def test_run_records_model_info(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="run_test")
        exp.run(LinearRegression(), X, y)
        assert exp.model_info["class"] == "LinearRegression"

    def test_run_with_test_split(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="split_test")
        exp.run(LinearRegression(), X[:60], y[:60], X_test=X[60:], y_test=y[60:])
        assert exp.status == ExperimentStatus.COMPLETED
        assert "train_test" in exp.datasets

    def test_run_records_dataset_metadata(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="ds_test")
        exp.run(LinearRegression(), X, y)
        assert "train" in exp.datasets
        assert exp.datasets["train"]["n_samples"] == 80

    def test_run_sets_started_at(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="time_test")
        exp.run(LinearRegression(), X, y)
        assert exp.started_at is not None

    def test_run_sets_ended_at(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="time_test")
        exp.run(LinearRegression(), X, y)
        assert exp.ended_at is not None

    def test_run_failed_sets_status(self, regression_data):
        X, y = regression_data

        class BadModel:
            def get_params(self):
                return {}

            def fit(self, X, y):
                raise ValueError("intentional error")

        exp = Experiment(name="fail_test")
        with pytest.raises(RuntimeError, match="failed"):
            exp.run(BadModel(), X, y)  # type: ignore[arg-type]
        assert exp.status == ExperimentStatus.FAILED

    def test_run_failed_stores_traceback(self, regression_data):
        X, y = regression_data

        class BadModel:
            def get_params(self):
                return {}

            def fit(self, X, y):
                raise ValueError("intentional error")

        exp = Experiment(name="fail_test")
        with pytest.raises(RuntimeError):
            exp.run(BadModel(), X, y)  # type: ignore[arg-type]
        assert exp.error is not None
        assert "intentional error" in exp.error

    def test_run_classification(self, classification_data):
        X, y = classification_data
        exp = Experiment(name="cls_test")
        model = RandomForestClassifier(n_estimators=10, random_state=0)
        metrics = exp.run(model, X, y)
        assert "accuracy" in metrics
        assert exp.status == ExperimentStatus.COMPLETED


# ---------------------------------------------------------------------------
# report()
# ---------------------------------------------------------------------------

class TestReport:
    def test_report_keys(self, blank_experiment):
        report = blank_experiment.report()
        expected = {
            "experiment_id", "name", "description", "status", "tags",
            "params", "metrics", "model_info", "datasets", "notes",
            "created_at", "started_at", "ended_at", "updated_at", "error",
        }
        assert expected.issubset(report.keys())

    def test_report_metrics_are_latest(self, blank_experiment):
        blank_experiment.log_metric("loss", 1.0)
        blank_experiment.log_metric("loss", 0.5)
        report = blank_experiment.report()
        assert report["metrics"]["loss"] == 0.5

    def test_report_after_run(self, regression_data):
        X, y = regression_data
        exp = Experiment(name="r")
        exp.run(LinearRegression(), X, y)
        report = exp.report()
        assert report["status"] == "completed"
        assert report["model_info"]["class"] == "LinearRegression"


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_round_trip_json(self, tmp_dir, regression_data):
        X, y = regression_data
        exp = Experiment(name="save_test", tags={"v": "1"})
        exp.log_params({"alpha": 0.1, "n": 100})
        exp.log_metric("r2", 0.92)
        exp.set_notes("my notes")
        path = tmp_dir / "exp.json"
        exp.save(path)
        loaded = Experiment.load(path)
        assert loaded.name == "save_test"
        assert loaded.params == {"alpha": 0.1, "n": 100}
        assert loaded.tags == {"v": "1"}
        assert loaded.notes == "my notes"
        assert loaded.metrics["r2"][0]["value"] == 0.92

    def test_load_preserves_status(self, tmp_dir):
        exp = Experiment(name="s")
        exp.status = ExperimentStatus.COMPLETED
        path = tmp_dir / "e.json"
        exp.save(path)
        loaded = Experiment.load(path)
        assert loaded.status == ExperimentStatus.COMPLETED

    def test_load_preserves_id(self, tmp_dir):
        exp = Experiment(name="s", experiment_id="fixed-id")
        path = tmp_dir / "e.json"
        exp.save(path)
        loaded = Experiment.load(path)
        assert loaded.experiment_id == "fixed-id"

    def test_json_is_valid(self, tmp_dir):
        exp = Experiment(name="j")
        exp.log_param("x", 1)
        path = tmp_dir / "e.json"
        exp.save(path)
        data = json.loads(path.read_text())
        assert "experiment_id" in data

    def test_import_experiment_alias(self, tmp_dir):
        exp = Experiment(name="alias")
        path = tmp_dir / "e.json"
        exp.save(path)
        loaded = Experiment.import_experiment(path)
        assert loaded.name == "alias"


# ---------------------------------------------------------------------------
# export()
# ---------------------------------------------------------------------------

class TestExport:
    def test_export_json(self, tmp_dir):
        exp = Experiment(name="e")
        exp.log_param("x", 1)
        path = tmp_dir / "out.json"
        exp.export(path, fmt="json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["name"] == "e"

    def test_export_csv(self, tmp_dir):
        exp = Experiment(name="csv_test")
        exp.log_param("alpha", 0.1)
        exp.log_metric("r2", 0.9)
        path = tmp_dir / "out.csv"
        exp.export(path, fmt="csv")
        assert path.exists()
        content = path.read_text()
        assert "csv_test" in content
        assert "param_alpha" in content
        assert "metric_r2" in content

    def test_export_invalid_format(self, tmp_dir):
        exp = Experiment(name="e")
        with pytest.raises(ValueError, match="Unsupported"):
            exp.export(tmp_dir / "out.xyz", fmt="xyz")


# ---------------------------------------------------------------------------
# ExperimentRegistry – CRUD
# ---------------------------------------------------------------------------

class TestExperimentRegistryCRUD:
    def test_add_and_get(self):
        registry = ExperimentRegistry()
        exp = Experiment(name="a")
        registry.add(exp)
        assert registry.get("a") is exp

    def test_add_returns_self(self):
        registry = ExperimentRegistry()
        assert registry.add(Experiment(name="x")) is registry

    def test_len(self):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="a"))
        registry.add(Experiment(name="b"))
        assert len(registry) == 2

    def test_contains(self):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="a"))
        assert "a" in registry
        assert "z" not in registry

    def test_get_missing_raises_keyerror(self):
        registry = ExperimentRegistry()
        with pytest.raises(KeyError):
            registry.get("nonexistent")

    def test_delete(self):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="a"))
        registry.delete("a")
        assert "a" not in registry

    def test_delete_returns_self(self):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="a"))
        assert registry.delete("a") is registry

    def test_delete_missing_raises(self):
        registry = ExperimentRegistry()
        with pytest.raises(KeyError):
            registry.delete("ghost")

    def test_list_returns_summaries(self):
        registry = ExperimentRegistry()
        exp = Experiment(name="a", tags={"t": "1"})
        exp.log_param("x", 1)
        exp.log_metric("r2", 0.9)
        registry.add(exp)
        items = registry.list()
        assert len(items) == 1
        assert items[0]["name"] == "a"
        assert items[0]["n_params"] == 1
        assert items[0]["n_metrics"] == 1

    def test_names_sorted(self):
        registry = ExperimentRegistry()
        for n in ["c", "a", "b"]:
            registry.add(Experiment(name=n))
        assert registry.names() == ["a", "b", "c"]

    def test_repr(self):
        r = ExperimentRegistry(name="proj")
        assert "proj" in repr(r)
        assert "0" in repr(r)


# ---------------------------------------------------------------------------
# ExperimentRegistry – compare
# ---------------------------------------------------------------------------

class TestCompare:
    def test_compare_all(self):
        registry = ExperimentRegistry()
        for name, score in [("a", 0.7), ("b", 0.9), ("c", 0.8)]:
            exp = Experiment(name=name)
            exp.log_metric("accuracy", score)
            registry.add(exp)
        reports = registry.compare()
        assert len(reports) == 3
        # Best first
        assert reports[0]["metrics"]["accuracy"] >= reports[1]["metrics"]["accuracy"]

    def test_compare_subset(self):
        registry = ExperimentRegistry()
        for name, score in [("a", 0.7), ("b", 0.9), ("c", 0.8)]:
            exp = Experiment(name=name)
            exp.log_metric("accuracy", score)
            registry.add(exp)
        reports = registry.compare(["a", "b"])
        assert len(reports) == 2

    def test_compare_missing_raises(self):
        registry = ExperimentRegistry()
        with pytest.raises(KeyError):
            registry.compare(["ghost"])

    def test_compare_no_metrics(self):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="a"))
        registry.add(Experiment(name="b"))
        reports = registry.compare()
        assert len(reports) == 2


# ---------------------------------------------------------------------------
# ExperimentRegistry – save / load
# ---------------------------------------------------------------------------

class TestRegistrySaveLoad:
    def test_round_trip(self, tmp_dir):
        registry = ExperimentRegistry(name="proj")
        for name in ["exp1", "exp2"]:
            exp = Experiment(name=name)
            exp.log_param("lr", 0.01)
            exp.log_metric("r2", 0.95)
            registry.add(exp)
        path = tmp_dir / "registry.json"
        registry.save(path)
        loaded = ExperimentRegistry.load(path)
        assert loaded.name == "proj"
        assert len(loaded) == 2
        assert "exp1" in loaded
        assert loaded.get("exp1").params["lr"] == 0.01

    def test_json_is_valid(self, tmp_dir):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="x"))
        path = tmp_dir / "r.json"
        registry.save(path)
        data = json.loads(path.read_text())
        assert "experiments" in data

    def test_empty_registry_round_trip(self, tmp_dir):
        registry = ExperimentRegistry(name="empty")
        path = tmp_dir / "empty.json"
        registry.save(path)
        loaded = ExperimentRegistry.load(path)
        assert len(loaded) == 0


# ---------------------------------------------------------------------------
# ExperimentRegistry – export
# ---------------------------------------------------------------------------

class TestRegistryExport:
    def test_export_json(self, tmp_dir):
        registry = ExperimentRegistry()
        registry.add(Experiment(name="x"))
        path = tmp_dir / "out.json"
        registry.export(path, fmt="json")
        assert path.exists()

    def test_export_csv(self, tmp_dir):
        registry = ExperimentRegistry()
        exp = Experiment(name="x")
        exp.log_param("alpha", 0.1)
        exp.log_metric("r2", 0.92)
        registry.add(exp)
        path = tmp_dir / "out.csv"
        registry.export(path, fmt="csv")
        assert path.exists()
        content = path.read_text()
        assert "param_alpha" in content
        assert "metric_r2" in content

    def test_export_invalid_format(self, tmp_dir):
        registry = ExperimentRegistry()
        with pytest.raises(ValueError, match="Unsupported"):
            registry.export(tmp_dir / "out.xyz", fmt="xyz")

    def test_import_experiment(self, tmp_dir):
        exp = Experiment(name="imported")
        exp.log_metric("acc", 0.85)
        exp_path = tmp_dir / "exp.json"
        exp.save(exp_path)

        registry = ExperimentRegistry()
        registry.import_experiment(exp_path)
        assert "imported" in registry
        assert registry.get("imported").metrics["acc"][0]["value"] == 0.85


# ---------------------------------------------------------------------------
# Top-level aiml import
# ---------------------------------------------------------------------------

class TestTopLevelImport:
    def test_experiment_importable_from_aiml(self):
        import aiml
        assert hasattr(aiml, "Experiment")
        assert hasattr(aiml, "ExperimentRegistry")
        assert hasattr(aiml, "ExperimentStatus")
