"""Shared fixtures for basics_plugin callback tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aiml_dash.utils.data_manager import DataManager, data_manager


@pytest.fixture(autouse=True)
def _seed_datasets():
    """Ensure a known set of datasets exists in the global data_manager before each test."""
    rng = np.random.default_rng(42)

    numeric_df = pd.DataFrame(
        {
            "x": rng.normal(5.0, 1.5, 60),
            "y": rng.normal(3.0, 1.0, 60),
            "z": rng.normal(7.0, 2.0, 60),
        }
    )
    data_manager.add_dataset("cb_numeric", numeric_df, description="numeric test data")

    two_group_df = pd.DataFrame(
        {
            "value": np.concatenate(
                [rng.normal(5.0, 1.0, 30), rng.normal(7.0, 1.0, 30)]
            ),
            "group": ["A"] * 30 + ["B"] * 30,
            "outcome": (["yes", "no"] * 30),
        }
    )
    data_manager.add_dataset("cb_two_groups", two_group_df, description="two-group test data")

    cat_df = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B", "C"] * 10,
            "color": ["red", "blue"] * 25,
        }
    )
    data_manager.add_dataset("cb_categorical", cat_df, description="categorical test data")

    yield
