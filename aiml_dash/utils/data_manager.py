"""
Data Manager Utility
====================

Handles data storage, retrieval, and session management for the AIML Dash application.
Uses a singleton pattern to maintain datasets across callbacks.
"""

import base64
import io
import pickle
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


class DataManager:
    """
    Singleton class to manage datasets and application state.

    Stores datasets in memory and provides methods for loading,
    saving, and manipulating data across the application.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Dictionary to store datasets
        self.datasets: dict[str, pd.DataFrame] = {}

        # Dictionary to store dataset metadata
        self.metadata: dict[str, dict[str, Any]] = {}

        # Dictionary to store dataset load commands (for code generation)
        self.load_commands: dict[str, str] = {}

        # Dictionary to store dataset descriptions
        self.descriptions: dict[str, str] = {}

        # Current active dataset name
        self.active_dataset: str | None = None

        # Initialize with sample datasets
        self._load_sample_data()

        self._initialized = True

    def _load_sample_data(self):
        """Load sample datasets (diamonds, titanic) for demonstration."""
        try:
            # Try to load from aiml_data_py package if available
            import sys
            from pathlib import Path

            # Add aiml_data_py to path
            aiml_py_path = Path(__file__).parent.parent.parent / "aiml_data_py"
            if aiml_py_path.exists() and str(aiml_py_path) not in sys.path:
                sys.path.insert(0, str(aiml_py_path))

            # Create sample diamonds dataset
            np.random.seed(42)
            n = 200
            diamonds = pd.DataFrame({
                "carat": np.random.gamma(2, 0.5, n),
                "cut": np.random.choice(["Fair", "Good", "Very Good", "Premium", "Ideal"], n),
                "color": np.random.choice(["D", "E", "F", "G", "H", "I", "J"], n),
                "clarity": np.random.choice(["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"], n),
                "depth": np.random.normal(61.5, 1.5, n),
                "table": np.random.normal(57, 2, n),
                "price": np.random.gamma(5, 800, n).astype(int),
                "x": np.random.normal(5.7, 1.1, n),
                "y": np.random.normal(5.7, 1.1, n),
                "z": np.random.normal(3.5, 0.7, n),
            })

            # Convert to categorical
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

            # Create sample titanic dataset
            np.random.seed(123)
            n = 150
            titanic = pd.DataFrame({
                "pclass": np.random.choice([1, 2, 3], n, p=[0.2, 0.3, 0.5]),
                "survived": np.random.choice([0, 1], n, p=[0.6, 0.4]),
                "sex": np.random.choice(["male", "female"], n, p=[0.65, 0.35]),
                "age": np.random.gamma(4, 8, n),
                "sibsp": np.random.poisson(0.5, n),
                "parch": np.random.poisson(0.4, n),
                "fare": np.random.gamma(3, 10, n),
                "embarked": np.random.choice(["S", "C", "Q"], n, p=[0.7, 0.2, 0.1]),
            })

            titanic["pclass"] = pd.Categorical(titanic["pclass"], ordered=True)
            titanic["sex"] = pd.Categorical(titanic["sex"])
            titanic["embarked"] = pd.Categorical(titanic["embarked"])

            self.add_dataset(
                "titanic",
                titanic,
                description="Titanic passenger survival data",
                load_command='# Sample titanic dataset\ntitanic = pd.read_csv("titanic.csv")',
            )

            # Set diamonds as active dataset
            self.active_dataset = "diamonds"

        except Exception as e:
            print(f"Warning: Could not load sample data: {e!s}")

    def add_dataset(
        self,
        name: str,
        data: pd.DataFrame,
        description: str = "",
        load_command: str = "",
    ):
        """
        Add a dataset to the manager.

        Parameters
        ----------
        name : str
            Name of the dataset
        data : pd.DataFrame
            The dataset to add
        description : str, optional
            Description of the dataset
        load_command : str, optional
            Command used to load this dataset (for code generation)
        """
        self.datasets[name] = data.copy()
        self.descriptions[name] = description
        self.load_commands[name] = load_command
        self.metadata[name] = {
            "rows": len(data),
            "columns": len(data.columns),
            "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "memory_usage": data.memory_usage(deep=True).sum() / 1024**2,  # MB
        }

    def get_dataset(self, name: str | None = None) -> pd.DataFrame | None:
        """
        Get a dataset by name, or the active dataset if name is None.

        Parameters
        ----------
        name : str, optional
            Name of the dataset to retrieve

        Returns
        -------
        pd.DataFrame or None
            The requested dataset, or None if not found
        """
        if name is None:
            name = self.active_dataset

        if name and name in self.datasets:
            return self.datasets[name].copy()
        return None

    def get_dataset_names(self) -> list[str]:
        """Get list of all dataset names."""
        return list(self.datasets.keys())

    def remove_dataset(self, name: str):
        """Remove a dataset from the manager."""
        if name in self.datasets:
            del self.datasets[name]
            del self.metadata[name]
            if name in self.descriptions:
                del self.descriptions[name]
            if name in self.load_commands:
                del self.load_commands[name]

            # Update active dataset if needed
            if self.active_dataset == name:
                remaining = self.get_dataset_names()
                self.active_dataset = remaining[0] if remaining else None

    def set_active_dataset(self, name: str):
        """Set the active dataset."""
        if name in self.datasets:
            self.active_dataset = name

    def get_active_dataset_name(self) -> str | None:
        """Get the name of the active dataset."""
        return self.active_dataset

    def get_dataset_info(self, name: str | None = None) -> dict[str, Any]:
        """
        Get metadata and information about a dataset.

        Parameters
        ----------
        name : str, optional
            Name of the dataset

        Returns
        -------
        dict
            Dictionary containing dataset information
        """
        if name is None:
            name = self.active_dataset

        if name and name in self.datasets:
            data = self.datasets[name]
            return {
                "name": name,
                "rows": len(data),
                "columns": len(data.columns),
                "column_names": list(data.columns),
                "column_types": data.dtypes.astype(str).to_dict(),
                "description": self.descriptions.get(name, ""),
                "load_command": self.load_commands.get(name, ""),
                **self.metadata.get(name, {}),
            }
        return {}

    def load_from_file(self, contents: str, filename: str) -> tuple[bool, str]:
        """
        Load a dataset from uploaded file.

        Parameters
        ----------
        contents : str
            Base64 encoded file contents
        filename : str
            Name of the uploaded file

        Returns
        -------
        tuple
            (success: bool, message: str)
        """
        try:
            # Decode the file contents
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            # Determine file type and load accordingly
            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                load_cmd = f'# Load data from CSV\n{filename.split(".")[0]} = pd.read_csv("{filename}")'

            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
                load_cmd = f'# Load data from Excel\n{filename.split(".")[0]} = pd.read_excel("{filename}")'

            elif filename.endswith(".json"):
                df = pd.read_json(io.BytesIO(decoded))
                load_cmd = f'# Load data from JSON\n{filename.split(".")[0]} = pd.read_json("{filename}")'

            elif filename.endswith(".pkl"):
                df = pickle.loads(decoded)
                if not isinstance(df, pd.DataFrame):
                    return False, "Pickle file does not contain a DataFrame"
                load_cmd = f'# Load data from pickle\n{filename.split(".")[0]} = pd.read_pickle("{filename}")'

            else:
                return False, f"Unsupported file type: {filename}"

            # Generate dataset name from filename
            dataset_name = filename.rsplit(".", 1)[0]

            # Make name unique if it already exists
            original_name = dataset_name
            counter = 1
            while dataset_name in self.datasets:
                dataset_name = f"{original_name}_{counter}"
                counter += 1

            # Add to datasets
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

        except Exception as e:
            return False, f"Error loading file: {e!s}"

    def export_dataset(self, name: str | None = None, format: str = "csv") -> str | None:
        """
        Export a dataset to a file format.

        Parameters
        ----------
        name : str, optional
            Name of the dataset to export
        format : str
            Export format ('csv', 'excel', 'json')

        Returns
        -------
        str or None
            Exported data as string, or None if failed
        """
        df = self.get_dataset(name)
        if df is None:
            return None

        try:
            if format == "csv":
                return df.to_csv(index=False)
            elif format == "excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                return base64.b64encode(output.getvalue()).decode()
            elif format == "json":
                return df.to_json(orient="records", indent=2)
        except Exception as e:
            print(f"Error exporting dataset: {e!s}")
            return None

    def apply_filter(
        self,
        name: str | None = None,
        filter_expr: str | None = None,
        sort_by: list[str] | None = None,
        ascending: list[bool] | None = None,
        rows: str | None = None,
    ) -> pd.DataFrame | None:
        """
        Apply filter, sort, and row selection to a dataset.

        Parameters
        ----------
        name : str, optional
            Name of the dataset
        filter_expr : str, optional
            pandas query expression for filtering
        sort_by : list of str, optional
            Columns to sort by
        ascending : list of bool, optional
            Sort order for each column
        rows : str, optional
            Row selection expression (e.g., '1:50', '0,5,10')

        Returns
        -------
        pd.DataFrame or None
            Filtered/sorted dataset
        """
        df = self.get_dataset(name)
        if df is None:
            return None

        try:
            # Apply filter
            if filter_expr and filter_expr.strip():
                df = df.query(filter_expr)

            # Apply sort
            if sort_by and len(sort_by) > 0:
                if ascending is None:
                    ascending = [True] * len(sort_by)
                df = df.sort_values(by=sort_by, ascending=ascending)

            # Apply row selection
            if rows and rows.strip():
                # Parse row selection (e.g., '1:50', '0,5,10', '1,5,10:20')
                if ":" in rows:
                    # Range selection
                    parts = rows.split(":")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if len(parts) > 1 and parts[1] else len(df)
                    df = df.iloc[start:end]
                elif "," in rows:
                    # Individual rows
                    indices = [int(i.strip()) for i in rows.split(",")]
                    df = df.iloc[indices]
                else:
                    # Single row
                    idx = int(rows)
                    df = df.iloc[[idx]]

            return df

        except Exception as e:
            print(f"Error applying filter: {e!s}")
            return df

    def export_all_state(self) -> dict:
        """
        Export complete application state including all datasets.

        Returns
        -------
        dict
            Complete state with all datasets serialized
        """
        state = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "active_dataset": self.active_dataset,
            "datasets": {},
            "metadata": self.metadata.copy(),
            "descriptions": self.descriptions.copy(),
            "load_commands": self.load_commands.copy(),
        }

        # Serialize each dataset
        for name, df in self.datasets.items():
            try:
                # Convert to JSON-serializable format
                state["datasets"][name] = {
                    "data": df.to_dict(orient="split"),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "index_name": df.index.name,
                }
            except Exception as e:
                print(f"Warning: Could not serialize dataset '{name}': {e!s}")

        return state

    def import_all_state(self, state: dict) -> tuple[bool, str]:
        """
        Import complete application state including all datasets.

        Parameters
        ----------
        state : dict
            Complete state dictionary from export_all_state

        Returns
        -------
        tuple
            (success: bool, message: str)
        """
        try:
            # Validate version
            version = state.get("version", "1.0")
            if not version.startswith("2."):
                return False, f"Incompatible state version: {version}"

            # Clear current state
            self.datasets.clear()
            self.metadata.clear()
            self.descriptions.clear()
            self.load_commands.clear()

            # Restore metadata
            self.metadata = state.get("metadata", {}).copy()
            self.descriptions = state.get("descriptions", {}).copy()
            self.load_commands = state.get("load_commands", {}).copy()

            # Restore datasets
            datasets_data = state.get("datasets", {})
            for name, dataset_info in datasets_data.items():
                try:
                    # Reconstruct DataFrame
                    df_dict = dataset_info["data"]
                    df = pd.DataFrame(
                        data=df_dict["data"],
                        columns=df_dict["columns"],
                        index=df_dict.get("index"),
                    )

                    # Restore data types
                    dtypes = dataset_info.get("dtypes", {})
                    for col, dtype_str in dtypes.items():
                        if col in df.columns:
                            try:
                                if "category" in dtype_str.lower():
                                    df[col] = df[col].astype("category")
                                elif "int" in dtype_str.lower():
                                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                                elif "float" in dtype_str.lower():
                                    df[col] = pd.to_numeric(df[col], errors="coerce")
                                elif "bool" in dtype_str.lower():
                                    df[col] = df[col].astype("bool")
                                elif "datetime" in dtype_str.lower():
                                    df[col] = pd.to_datetime(df[col], errors="coerce")
                            except Exception as e:
                                print(f"Warning: Could not restore dtype for {name}.{col}: {e!s}")

                    # Restore index name
                    if dataset_info.get("index_name"):
                        df.index.name = dataset_info["index_name"]

                    self.datasets[name] = df

                except Exception as e:
                    print(f"Warning: Could not restore dataset '{name}': {e!s}")

            # Restore active dataset
            active = state.get("active_dataset")
            if active and active in self.datasets:
                self.active_dataset = active
            elif self.datasets:
                self.active_dataset = list(self.datasets.keys())[0]

            dataset_count = len(self.datasets)
            return True, f"Successfully imported {dataset_count} dataset(s)"

        except Exception as e:
            return False, f"Error importing state: {e!s}"


# Global instance
data_manager = DataManager()
