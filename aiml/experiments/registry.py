"""
Experiment Registry
====================

:class:`ExperimentRegistry` manages a named collection of
:class:`~aiml.experiments.experiment.Experiment` objects and provides
facilities to compare, save, load, and export them as a group.

Usage
-----
::

    from aiml.experiments import Experiment, ExperimentRegistry

    registry = ExperimentRegistry()
    exp = Experiment(name="run_1")
    exp.log_params({"alpha": 0.1})
    exp.log_metric("r2", 0.91)
    registry.add(exp)

    # Compare all experiments side-by-side
    df = registry.compare()

    # Persist the entire registry
    registry.save("experiments.json")
    registry2 = ExperimentRegistry.load("experiments.json")
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from aiml.experiments.experiment import Experiment


class ExperimentRegistry:
    """A collection of :class:`~aiml.experiments.experiment.Experiment` objects.

    Experiments are stored by name. If two experiments share a name,
    the later one replaces the earlier.

    Parameters
    ----------
    name:
        Optional registry label.

    Examples
    --------
    >>> from aiml.experiments import Experiment, ExperimentRegistry
    >>> registry = ExperimentRegistry(name="my_project")
    >>> exp = Experiment(name="baseline")
    >>> exp.log_metric("accuracy", 0.88)
    Experiment(...)
    >>> registry.add(exp)
    >>> len(registry) == 1
    True
    """

    def __init__(self, *, name: str = "default") -> None:
        self.name = name
        self._experiments: dict[str, Experiment] = {}

    # ------------------------------------------------------------------ #
    # CRUD                                                                 #
    # ------------------------------------------------------------------ #

    def add(self, experiment: Experiment) -> "ExperimentRegistry":
        """Add or overwrite an experiment.

        Parameters
        ----------
        experiment:
            The :class:`~aiml.experiments.experiment.Experiment` to store.

        Returns
        -------
        self
        """
        self._experiments[experiment.name] = experiment
        return self

    def get(self, name: str) -> Experiment:
        """Retrieve an experiment by name.

        Parameters
        ----------
        name:
            Experiment name.

        Returns
        -------
        experiment : Experiment

        Raises
        ------
        KeyError
            When no experiment with the given name exists.
        """
        if name not in self._experiments:
            msg = f"No experiment named '{name}' in registry '{self.name}'."
            raise KeyError(msg)
        return self._experiments[name]

    def delete(self, name: str) -> "ExperimentRegistry":
        """Remove an experiment by name.

        Parameters
        ----------
        name:
            Experiment name.

        Returns
        -------
        self

        Raises
        ------
        KeyError
            When no experiment with the given name exists.
        """
        if name not in self._experiments:
            msg = f"No experiment named '{name}' in registry '{self.name}'."
            raise KeyError(msg)
        del self._experiments[name]
        return self

    def list(self) -> list[dict[str, Any]]:
        """Return a lightweight summary of all experiments.

        Returns
        -------
        summaries : list[dict]
            One dict per experiment containing ``name``, ``status``,
            ``created_at``, ``model``, ``n_params``, and ``n_metrics``.
        """
        return [
            {
                "name": exp.name,
                "experiment_id": exp.experiment_id,
                "status": exp.status.value,
                "model": exp.model_info.get("class", ""),
                "n_params": len(exp.params),
                "n_metrics": len(exp.metrics),
                "tags": exp.tags,
                "created_at": exp.created_at,
            }
            for exp in self._experiments.values()
        ]

    def names(self) -> list[str]:
        """Return sorted list of experiment names.

        Returns
        -------
        names : list[str]
        """
        return sorted(self._experiments.keys())

    def __len__(self) -> int:
        return len(self._experiments)

    def __contains__(self, name: str) -> bool:
        return name in self._experiments

    def __repr__(self) -> str:
        return f"ExperimentRegistry(name={self.name!r}, n_experiments={len(self)})"

    # ------------------------------------------------------------------ #
    # Comparison                                                           #
    # ------------------------------------------------------------------ #

    def compare(
        self,
        names: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Compare experiments side-by-side.

        Returns one report dict per experiment (via
        :meth:`~aiml.experiments.experiment.Experiment.report`), sorted by
        the first numeric metric found (descending) so that the best
        experiment appears first.

        Parameters
        ----------
        names:
            Subset of experiment names to compare.  When ``None`` all
            experiments are compared.

        Returns
        -------
        reports : list[dict]
            Sorted experiment reports.

        Raises
        ------
        KeyError
            When any name in *names* is not present in the registry.
        """
        if names is None:
            experiments = list(self._experiments.values())
        else:
            experiments = [self.get(n) for n in names]

        reports = [exp.report() for exp in experiments]

        # Sort by first numeric metric value (best first), fall back to name
        def _sort_key(r: dict[str, Any]) -> tuple[float, str]:
            metrics = r.get("metrics", {})
            if metrics:
                first_val = next(
                    (v for v in metrics.values() if isinstance(v, (int, float))),
                    0.0,
                )
                return (-float(first_val), r["name"])
            return (0.0, r["name"])

        return sorted(reports, key=_sort_key)

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict[str, Any]:
        """Serialise the entire registry to a plain dictionary.

        Returns
        -------
        data : dict
        """
        return {
            "registry_name": self.name,
            "experiments": {
                name: exp.to_dict()
                for name, exp in self._experiments.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentRegistry":
        """Reconstruct a registry from a serialised dictionary.

        Parameters
        ----------
        data:
            Dictionary produced by :meth:`to_dict`.

        Returns
        -------
        registry : ExperimentRegistry
        """
        registry = cls(name=data.get("registry_name", "default"))
        for exp_data in data.get("experiments", {}).values():
            registry.add(Experiment.from_dict(exp_data))
        return registry

    def save(self, path: str | Path) -> None:
        """Save the registry to a JSON file.

        Parameters
        ----------
        path:
            Destination file path.
        """
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ExperimentRegistry":
        """Load a registry from a JSON file.

        Parameters
        ----------
        path:
            Path to a file previously written by :meth:`save`.

        Returns
        -------
        registry : ExperimentRegistry
        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    # ------------------------------------------------------------------ #
    # Export / Import                                                      #
    # ------------------------------------------------------------------ #

    def export(self, path: str | Path, *, fmt: str = "json") -> None:
        """Export all experiments in the registry.

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
        """Write a flat CSV summary of all experiments."""
        rows = []
        fieldnames: list[str] = []
        for exp in self._experiments.values():
            row: dict[str, Any] = {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "status": exp.status.value,
                "model": exp.model_info.get("class", ""),
                "created_at": exp.created_at,
                "started_at": exp.started_at,
                "ended_at": exp.ended_at,
            }
            for k, v in exp.params.items():
                row[f"param_{k}"] = v
            for key, entries in exp.metrics.items():
                if entries:
                    row[f"metric_{key}"] = entries[-1]["value"]
            rows.append(row)
            for k in row:
                if k not in fieldnames:
                    fieldnames.append(k)

        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def import_experiment(self, path: str | Path) -> "ExperimentRegistry":
        """Import a single experiment JSON file into this registry.

        Parameters
        ----------
        path:
            Path to an experiment JSON file produced by
            :meth:`~aiml.experiments.experiment.Experiment.save`.

        Returns
        -------
        self
        """
        exp = Experiment.load(path)
        self.add(exp)
        return self
