"""
Experiment Tracking
====================

Core :class:`Experiment` class for managing end-to-end EDA and machine
learning experiments.

An experiment records:

* **Parameters** – hyperparameters or any configuration values.
* **Metrics** – numeric measurements (optionally associated with a step /
  epoch so that series can be tracked over time).
* **Datasets** – metadata about the data used.
* **Artifacts** – arbitrary in-memory objects (e.g. plots, data-frames).
* **Model info** – class name and hyperparameters of the fitted model.

Lifecycle
---------

``CREATED → RUNNING → COMPLETED``
                    ↘ ``FAILED``

Usage
-----
::

    from aiml.experiments import Experiment
    from aiml.supervised.trees import RandomForestClassifier

    exp = Experiment(name="rf_v1", tags={"dataset": "iris"})
    exp.log_params({"n_estimators": 200, "max_depth": 5})
    model = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=0)
    exp.run(model, X_train, y_train, X_test=X_test, y_test=y_test)

    print(exp.report())
    exp.save("rf_v1.json")

    exp2 = Experiment.load("rf_v1.json")
"""

from __future__ import annotations

import csv
import json
import traceback
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiml.base import BaseModel


# --------------------------------------------------------------------------- #
# Status enum                                                                  #
# --------------------------------------------------------------------------- #


class ExperimentStatus(str, Enum):
    """Lifecycle status of an :class:`Experiment`."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_serializable(obj: Any) -> Any:
    """Convert *obj* to a JSON-serializable type on a best-effort basis."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    # numpy scalar / array
    try:
        import numpy as np

        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    return str(obj)


# --------------------------------------------------------------------------- #
# Experiment                                                                   #
# --------------------------------------------------------------------------- #


class Experiment:
    """A single end-to-end ML / EDA experiment.

    Parameters
    ----------
    name:
        Human-readable experiment name. Should be unique within a registry.
    description:
        Optional free-text description.
    tags:
        Arbitrary string key-value tags for filtering/grouping.
    experiment_id:
        Explicit UUID string. Auto-generated when ``None``.

    Examples
    --------
    >>> from aiml.experiments import Experiment
    >>> exp = Experiment(name="demo")
    >>> exp.log_param("alpha", 0.01)
    >>> exp.log_metric("r2", 0.95)
    >>> exp.status
    <ExperimentStatus.CREATED: 'created'>
    """

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        tags: dict[str, str] | None = None,
        experiment_id: str | None = None,
    ) -> None:
        self.experiment_id: str = experiment_id or str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.tags: dict[str, str] = tags or {}

        self.status: ExperimentStatus = ExperimentStatus.CREATED
        self.created_at: str = _now_iso()
        self.updated_at: str = self.created_at
        self.started_at: str | None = None
        self.ended_at: str | None = None

        # Logged data
        self.params: dict[str, Any] = {}
        # metric_name → list of {"value", "step", "timestamp"}
        self.metrics: dict[str, list[dict[str, Any]]] = {}
        # name → serializable metadata
        self.datasets: dict[str, dict[str, Any]] = {}
        # name → serializable object (stored best-effort)
        self.artifacts: dict[str, Any] = {}

        self.model_info: dict[str, Any] = {}
        self.notes: str = ""
        self.error: str | None = None

    # ------------------------------------------------------------------ #
    # Logging                                                              #
    # ------------------------------------------------------------------ #

    def log_param(self, key: str, value: Any) -> "Experiment":
        """Log a single parameter.

        Parameters
        ----------
        key:
            Parameter name.
        value:
            Parameter value (must be JSON-serializable).

        Returns
        -------
        self
        """
        self.params[key] = _to_serializable(value)
        self.updated_at = _now_iso()
        return self

    def log_params(self, params: dict[str, Any]) -> "Experiment":
        """Log multiple parameters at once.

        Parameters
        ----------
        params:
            Dictionary of ``{key: value}`` pairs.

        Returns
        -------
        self
        """
        for k, v in params.items():
            self.log_param(k, v)
        return self

    def log_metric(
        self,
        key: str,
        value: float,
        *,
        step: int | None = None,
    ) -> "Experiment":
        """Log a scalar metric value.

        Parameters
        ----------
        key:
            Metric name (e.g. ``"accuracy"``, ``"loss"``).
        value:
            Numeric value.
        step:
            Optional training step or epoch index for series tracking.

        Returns
        -------
        self
        """
        entry: dict[str, Any] = {
            "value": _to_serializable(value),
            "step": step,
            "timestamp": _now_iso(),
        }
        self.metrics.setdefault(key, []).append(entry)
        self.updated_at = _now_iso()
        return self

    def log_metrics(
        self,
        metrics: dict[str, float],
        *,
        step: int | None = None,
    ) -> "Experiment":
        """Log multiple metrics at once.

        Parameters
        ----------
        metrics:
            Dictionary of ``{metric_name: value}`` pairs.
        step:
            Optional step index applied to every metric.

        Returns
        -------
        self
        """
        for k, v in metrics.items():
            self.log_metric(k, v, step=step)
        return self

    def log_dataset(
        self,
        name: str,
        X: Any,
        y: Any = None,
        *,
        description: str = "",
    ) -> "Experiment":
        """Record metadata about a dataset.

        Only lightweight descriptive metadata is stored (shape, column names).
        The raw data is **not** persisted.

        Parameters
        ----------
        name:
            Dataset label (e.g. ``"train"``, ``"test"``).
        X:
            Feature matrix.
        y:
            Target vector (optional).
        description:
            Free-text description.

        Returns
        -------
        self
        """
        info: dict[str, Any] = {"description": description}
        try:
            import numpy as np

            X_arr = np.asarray(X)
            info["n_samples"] = int(X_arr.shape[0])
            info["n_features"] = int(X_arr.shape[1]) if X_arr.ndim > 1 else 1
        except Exception:  # noqa: BLE001
            pass
        try:
            import pandas as pd

            if isinstance(X, pd.DataFrame):
                info["columns"] = list(X.columns)
        except ImportError:
            pass
        if y is not None:
            try:
                import numpy as np

                y_arr = np.asarray(y)
                info["n_targets"] = int(y_arr.shape[0])
            except Exception:  # noqa: BLE001
                pass
        self.datasets[name] = info
        self.updated_at = _now_iso()
        return self

    def log_artifact(self, name: str, obj: Any) -> "Experiment":
        """Store an in-memory artifact.

        The artifact is kept in memory and serialised to its string
        representation when the experiment is saved to JSON.

        Parameters
        ----------
        name:
            Artifact label.
        obj:
            Any Python object.

        Returns
        -------
        self
        """
        self.artifacts[name] = _to_serializable(obj)
        self.updated_at = _now_iso()
        return self

    def set_notes(self, notes: str) -> "Experiment":
        """Attach free-text notes.

        Parameters
        ----------
        notes:
            Markdown-formatted notes string.

        Returns
        -------
        self
        """
        self.notes = notes
        self.updated_at = _now_iso()
        return self

    # ------------------------------------------------------------------ #
    # Run                                                                  #
    # ------------------------------------------------------------------ #

    def run(
        self,
        model: "BaseModel",
        X: Any,
        y: Any,
        *,
        X_test: Any = None,
        y_test: Any = None,
        dataset_name: str = "train",
    ) -> dict[str, Any]:
        """Fit *model* and log all results.

        Performs a complete end-to-end run:

        1. Records model class name and hyperparameters.
        2. Logs dataset metadata.
        3. Fits the model on ``(X, y)``.
        4. Evaluates on ``(X_test, y_test)`` when provided, otherwise on
           the training data.
        5. Logs all evaluation metrics.
        6. Sets the experiment status to ``COMPLETED`` (or ``FAILED``).

        Parameters
        ----------
        model:
            An unfitted ``aiml`` model instance.
        X:
            Training feature matrix.
        y:
            Training target vector.
        X_test:
            Optional held-out feature matrix for evaluation.
        y_test:
            Optional held-out target vector for evaluation.
        dataset_name:
            Label used when recording the training dataset. Default
            ``"train"``.

        Returns
        -------
        metrics : dict
            Evaluation metrics produced by :meth:`~aiml.base.BaseModel.evaluate`.
        """
        self.status = ExperimentStatus.RUNNING
        self.started_at = _now_iso()
        self.updated_at = self.started_at

        try:
            # -- Model info ------------------------------------------------
            self.model_info = {
                "class": type(model).__name__,
                "module": type(model).__module__,
                "params": _to_serializable(model.get_params()),
            }
            # Log model params so they appear in self.params too
            self.log_params(model.get_params())

            # -- Dataset metadata -----------------------------------------
            self.log_dataset(dataset_name, X, y)
            if X_test is not None:
                self.log_dataset(f"{dataset_name}_test", X_test, y_test)

            # -- Fit -------------------------------------------------------
            model.fit(X, y)

            # -- Evaluate --------------------------------------------------
            eval_X = X_test if X_test is not None else X
            eval_y = y_test if y_test is not None else y
            metrics = model.evaluate(eval_X, eval_y)

            # Log every scalar metric
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    self.log_metric(key, float(value))

            self.status = ExperimentStatus.COMPLETED
            return metrics

        except Exception as exc:
            self.status = ExperimentStatus.FAILED
            self.error = traceback.format_exc()
            raise RuntimeError(f"Experiment '{self.name}' failed: {exc}") from exc

        finally:
            self.ended_at = _now_iso()
            self.updated_at = self.ended_at

    # ------------------------------------------------------------------ #
    # Report                                                               #
    # ------------------------------------------------------------------ #

    def report(self) -> dict[str, Any]:
        """Return a structured summary of the experiment.

        Returns
        -------
        summary : dict
            Contains ``experiment_id``, ``name``, ``status``, ``params``,
            ``metrics`` (latest value per metric), ``model_info``,
            ``datasets``, ``tags``, ``notes``, timing fields, and ``error``
            (when the run failed).
        """
        # Flatten metrics to latest value per key
        latest_metrics: dict[str, float] = {}
        for key, entries in self.metrics.items():
            if entries:
                latest_metrics[key] = entries[-1]["value"]

        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "tags": self.tags,
            "params": self.params,
            "metrics": latest_metrics,
            "model_info": self.model_info,
            "datasets": self.datasets,
            "notes": self.notes,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "updated_at": self.updated_at,
            "error": self.error,
        }

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict[str, Any]:
        """Serialise the experiment to a plain dictionary.

        Returns
        -------
        data : dict
        """
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "params": self.params,
            "metrics": self.metrics,
            "datasets": self.datasets,
            "artifacts": self.artifacts,
            "model_info": self.model_info,
            "notes": self.notes,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Experiment":
        """Reconstruct an :class:`Experiment` from a serialised dictionary.

        Parameters
        ----------
        data:
            Dictionary produced by :meth:`to_dict`.

        Returns
        -------
        experiment : Experiment
        """
        exp = cls(
            name=data["name"],
            description=data.get("description", ""),
            tags=data.get("tags", {}),
            experiment_id=data.get("experiment_id"),
        )
        exp.status = ExperimentStatus(data.get("status", "created"))
        exp.created_at = data.get("created_at", exp.created_at)
        exp.updated_at = data.get("updated_at", exp.updated_at)
        exp.started_at = data.get("started_at")
        exp.ended_at = data.get("ended_at")
        exp.params = data.get("params", {})
        exp.metrics = data.get("metrics", {})
        exp.datasets = data.get("datasets", {})
        exp.artifacts = data.get("artifacts", {})
        exp.model_info = data.get("model_info", {})
        exp.notes = data.get("notes", "")
        exp.error = data.get("error")
        return exp

    def save(self, path: str | Path) -> None:
        """Save the experiment to a JSON file.

        Parameters
        ----------
        path:
            Destination file path (``".json"`` extension recommended).
        """
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Experiment":
        """Load an experiment from a JSON file.

        Parameters
        ----------
        path:
            Path to a file previously written by :meth:`save`.

        Returns
        -------
        experiment : Experiment
        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    # ------------------------------------------------------------------ #
    # Export                                                               #
    # ------------------------------------------------------------------ #

    def export(self, path: str | Path, *, fmt: str = "json") -> None:
        """Export experiment results.

        Parameters
        ----------
        path:
            Output file path.
        fmt:
            ``"json"`` (default) or ``"csv"``.

        Raises
        ------
        ValueError
            When an unsupported format is requested.
        """
        fmt = fmt.lower()
        if fmt == "json":
            self.save(path)
        elif fmt == "csv":
            self._export_csv(path)
        else:
            msg = f"Unsupported export format '{fmt}'. Use 'json' or 'csv'."
            raise ValueError(msg)

    def _export_csv(self, path: str | Path) -> None:
        """Write a flat CSV summary of params + latest metrics."""
        row: dict[str, Any] = {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "status": self.status.value,
            "model": self.model_info.get("class", ""),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }
        # Flatten params
        for k, v in self.params.items():
            row[f"param_{k}"] = v
        # Flatten latest metrics
        for key, entries in self.metrics.items():
            if entries:
                row[f"metric_{key}"] = entries[-1]["value"]

        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)

    # ------------------------------------------------------------------ #
    # Import                                                               #
    # ------------------------------------------------------------------ #

    @classmethod
    def import_experiment(cls, path: str | Path) -> "Experiment":
        """Alias for :meth:`load` – import an experiment from a JSON file.

        Parameters
        ----------
        path:
            Path to a saved experiment JSON file.

        Returns
        -------
        experiment : Experiment
        """
        return cls.load(path)

    # ------------------------------------------------------------------ #
    # Dunder                                                               #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (
            f"Experiment(name={self.name!r}, "
            f"status={self.status.value!r}, "
            f"id={self.experiment_id!r})"
        )
