"""Dataset state management for AIML Dash."""

from __future__ import annotations

import base64
import io
import pickle
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from aiml_dash.utils.logging import get_logger

logger = get_logger(__name__)


class DataManager:
    """Manage in-memory datasets for a single app instance."""

    def __init__(self, load_sample_data: bool = True):
        """Initialize the dataset manager."""
        self.datasets: dict[str, pd.DataFrame] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.load_commands: dict[str, str] = {}
        self.descriptions: dict[str, str] = {}
        self.active_dataset: str | None = None

        if load_sample_data:
            self._load_sample_data()

    def _load_sample_data(self) -> None:
        """Load bundled sample datasets for interactive exploration."""
        try:
            self._load_diamonds_dataset()
            self._load_titanic_dataset()
            self.active_dataset = self.active_dataset or "diamonds"
        except Exception:
            logger.exception("Could not load sample datasets")

    def _load_diamonds_dataset(self) -> None:
        np.random.seed(42)
        n = 200
        diamonds = pd.DataFrame(
            {
                "carat": np.random.gamma(2, 0.5, n),
                "cut": np.random.choice(
                    ["Fair", "Good", "Very Good", "Premium", "Ideal"], n
                ),
                "color": np.random.choice(["D", "E", "F", "G", "H", "I", "J"], n),
                "clarity": np.random.choice(
                    ["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"], n
                ),
                "depth": np.random.normal(61.5, 1.5, n),
                "table": np.random.normal(57, 2, n),
                "price": np.random.gamma(5, 800, n).astype(int),
                "x": np.random.normal(5.7, 1.1, n),
                "y": np.random.normal(5.7, 1.1, n),
                "z": np.random.normal(3.5, 0.7, n),
            }
        )

        diamonds["cut"] = pd.Categorical(
            diamonds["cut"],
            categories=["Fair", "Good", "Very Good", "Premium", "Ideal"],
            ordered=True,
        )
        diamonds["color"] = pd.Categorical(
            diamonds["color"],
            categories=["D", "E", "F", "G", "H", "I", "J"],
            ordered=True,
        )
        diamonds["clarity"] = pd.Categorical(
            diamonds["clarity"],
            categories=["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"],
            ordered=True,
        )

        self.add_dataset(
            "diamonds",
            diamonds,
            description="Diamond characteristics and prices",
            load_command='# Sample diamonds dataset\ndiamonds = pd.read_csv("diamonds.csv")',
        )

    def _load_titanic_dataset(self) -> None:
        np.random.seed(123)
        n = 150
        titanic = pd.DataFrame(
            {
                "pclass": np.random.choice([1, 2, 3], n, p=[0.2, 0.3, 0.5]),
                "survived": np.random.choice([0, 1], n, p=[0.6, 0.4]),
                "sex": np.random.choice(["male", "female"], n, p=[0.65, 0.35]),
                "age": np.random.gamma(4, 8, n),
                "sibsp": np.random.poisson(0.5, n),
                "parch": np.random.poisson(0.4, n),
                "fare": np.random.gamma(3, 10, n),
                "embarked": np.random.choice(["S", "C", "Q"], n, p=[0.7, 0.2, 0.1]),
            }
        )

        titanic["pclass"] = pd.Categorical(titanic["pclass"], ordered=True)
        titanic["sex"] = pd.Categorical(titanic["sex"])
        titanic["embarked"] = pd.Categorical(titanic["embarked"])

        self.add_dataset(
            "titanic",
            titanic,
            description="Titanic passenger survival data",
            load_command='# Sample titanic dataset\ntitanic = pd.read_csv("titanic.csv")',
        )

    def add_dataset(
        self,
        name: str,
        data: pd.DataFrame,
        description: str = "",
        load_command: str = "",
    ) -> None:
        """Add a dataset to the manager."""
        self.datasets[name] = data.copy()
        self.descriptions[name] = description
        self.load_commands[name] = load_command
        self.metadata[name] = {
            "rows": len(data),
            "columns": len(data.columns),
            "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "memory_usage": data.memory_usage(deep=True).sum() / 1024**2,
        }

    def get_dataset(self, name: str | None = None) -> pd.DataFrame | None:
        """Return a copy of the requested dataset."""
        dataset_name = name or self.active_dataset
        if dataset_name and dataset_name in self.datasets:
            return self.datasets[dataset_name].copy()
        return None

    def get_dataset_names(self) -> list[str]:
        """Return all dataset names."""
        return list(self.datasets.keys())

    def remove_dataset(self, name: str) -> None:
        """Remove a dataset from the manager."""
        if name not in self.datasets:
            return

        del self.datasets[name]
        self.metadata.pop(name, None)
        self.descriptions.pop(name, None)
        self.load_commands.pop(name, None)

        if self.active_dataset == name:
            self.active_dataset = next(iter(self.datasets), None)

    def set_active_dataset(self, name: str) -> None:
        """Set the active dataset when it exists."""
        if name in self.datasets:
            self.active_dataset = name

    def get_active_dataset_name(self) -> str | None:
        """Return the active dataset name."""
        return self.active_dataset

    def get_dataset_info(self, name: str | None = None) -> dict[str, Any]:
        """Return metadata for a dataset."""
        dataset_name = name or self.active_dataset
        if not dataset_name or dataset_name not in self.datasets:
            return {}

        data = self.datasets[dataset_name]
        return {
            "name": dataset_name,
            "rows": len(data),
            "columns": len(data.columns),
            "column_names": list(data.columns),
            "column_types": data.dtypes.astype(str).to_dict(),
            "description": self.descriptions.get(dataset_name, ""),
            "load_command": self.load_commands.get(dataset_name, ""),
            **self.metadata.get(dataset_name, {}),
        }

    def load_from_file(self, contents: str, filename: str) -> tuple[bool, str]:
        """Load a dataset from uploaded file contents."""
        try:
            _content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                load_cmd = (
                    f'# Load data from CSV\n{filename.split(".")[0]} = pd.read_csv("{filename}")'
                )
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
                load_cmd = (
                    f'# Load data from Excel\n{filename.split(".")[0]} = pd.read_excel("{filename}")'
                )
            elif filename.endswith(".json"):
                df = pd.read_json(io.BytesIO(decoded))
                load_cmd = (
                    f'# Load data from JSON\n{filename.split(".")[0]} = pd.read_json("{filename}")'
                )
            elif filename.endswith(".pkl"):
                df = pickle.loads(decoded)  # noqa: S301
                if not isinstance(df, pd.DataFrame):
                    return False, "Pickle file does not contain a DataFrame"
                load_cmd = (
                    f'# Load data from pickle\n{filename.split(".")[0]} = pd.read_pickle("{filename}")'
                )
            else:
                return False, f"Unsupported file type: {filename}"

            dataset_name = filename.rsplit(".", 1)[0]
            original_name = dataset_name
            counter = 1
            while dataset_name in self.datasets:
                dataset_name = f"{original_name}_{counter}"
                counter += 1

            self.add_dataset(
                dataset_name,
                df,
                description=f"Loaded from {filename}",
                load_command=load_cmd,
            )
            self.set_active_dataset(dataset_name)

            return (
                True,
                f"Successfully loaded {filename} as '{dataset_name}' ({len(df)} rows, {len(df.columns)} columns)",
            )
        except Exception as exc:
            logger.exception("Error loading dataset from file '%s'", filename)
            return False, f"Error loading file: {exc!s}"

    def export_dataset(
        self,
        name: str | None = None,
        export_format: str = "csv",
        format: str | None = None,
    ) -> str | None:
        """Export a dataset in the requested format."""
        resolved_format = format or export_format
        df = self.get_dataset(name)
        if df is None:
            return None

        try:
            if resolved_format == "csv":
                return df.to_csv(index=False)
            if resolved_format == "excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                return base64.b64encode(output.getvalue()).decode()
            if resolved_format == "json":
                return df.to_json(orient="records", indent=2)
        except Exception:
            logger.exception("Error exporting dataset '%s'", name or self.active_dataset)
        return None

    def apply_filter(
        self,
        name: str | None = None,
        filter_expr: str | None = None,
        sort_by: list[str] | None = None,
        ascending: list[bool] | None = None,
        rows: str | None = None,
    ) -> pd.DataFrame | None:
        """Apply filter, sorting, and row slicing to a dataset."""
        df = self.get_dataset(name)
        if df is None:
            return None

        try:
            if filter_expr and filter_expr.strip():
                df = df.query(filter_expr)

            if sort_by:
                resolved_ascending = ascending if ascending is not None else [True] * len(sort_by)
                df = df.sort_values(by=sort_by, ascending=resolved_ascending)

            if rows and rows.strip():
                if ":" in rows:
                    parts = rows.split(":")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if len(parts) > 1 and parts[1] else len(df)
                    df = df.iloc[start:end]
                elif "," in rows:
                    indices = [int(item.strip()) for item in rows.split(",")]
                    df = df.iloc[indices]
                else:
                    df = df.iloc[[int(rows)]]
        except Exception:
            logger.exception("Error applying filter to dataset '%s'", name or self.active_dataset)
        return df

    def export_all_state(self) -> dict[str, Any]:
        """Export the complete dataset state."""
        state: dict[str, Any] = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "active_dataset": self.active_dataset,
            "datasets": {},
            "metadata": self.metadata.copy(),
            "descriptions": self.descriptions.copy(),
            "load_commands": self.load_commands.copy(),
        }

        for name, df in self.datasets.items():
            try:
                state["datasets"][name] = {
                    "data": df.to_dict(orient="split"),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "index_name": df.index.name,
                }
            except Exception:
                logger.exception("Could not serialize dataset '%s'", name)

        return state

    def import_all_state(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Import the complete dataset state."""
        try:
            version = state.get("version", "1.0")
            if not version.startswith("2."):
                return False, f"Incompatible state version: {version}"

            self.datasets.clear()
            self.metadata = state.get("metadata", {}).copy()
            self.descriptions = state.get("descriptions", {}).copy()
            self.load_commands = state.get("load_commands", {}).copy()

            for name, dataset_info in state.get("datasets", {}).items():
                try:
                    df_dict = dataset_info["data"]
                    df = pd.DataFrame(
                        data=df_dict["data"],
                        columns=df_dict["columns"],
                        index=df_dict.get("index"),
                    )

                    for column, dtype_str in dataset_info.get("dtypes", {}).items():
                        if column not in df.columns:
                            continue
                        try:
                            lowered = dtype_str.lower()
                            if "category" in lowered:
                                df[column] = df[column].astype("category")
                            elif "int" in lowered:
                                df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
                            elif "float" in lowered:
                                df[column] = pd.to_numeric(df[column], errors="coerce")
                            elif "bool" in lowered:
                                df[column] = df[column].astype("bool")
                            elif "datetime" in lowered:
                                df[column] = pd.to_datetime(df[column], errors="coerce")
                        except Exception:
                            logger.exception("Could not restore dtype for %s.%s", name, column)

                    if dataset_info.get("index_name"):
                        df.index.name = dataset_info["index_name"]
                    self.datasets[name] = df
                except Exception:
                    logger.exception("Could not restore dataset '%s'", name)

            active_dataset = state.get("active_dataset")
            self.active_dataset = (
                active_dataset if active_dataset in self.datasets else next(iter(self.datasets), None)
            )
            return True, f"Successfully imported {len(self.datasets)} dataset(s)"
        except Exception as exc:
            logger.exception("Error importing dataset state")
            return False, f"Error importing state: {exc!s}"


def create_data_manager(load_sample_data: bool = True) -> DataManager:
    """Create a new data manager instance."""
    return DataManager(load_sample_data=load_sample_data)


data_manager = create_data_manager()

