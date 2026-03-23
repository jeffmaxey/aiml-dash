#!/usr/bin/env python3
"""Profile representative AIML Dash workloads and print hotspot reports.

Usage:
    python scripts/profile_hotspots.py

This script profiles:
- utilities (`explore`, transforms, pagination)
- model callback execution paths (decision tree, random forest, logistic)

It prints wall-clock timing and top cumulative cProfile entries per workload.
"""

from __future__ import annotations

import cProfile
import importlib
import io
import pstats
import sys
import time

REQUIRED_MODULES = ("dash", "numpy", "pandas", "sklearn")


def _check_dependencies() -> None:
    """Exit with a clear message if required runtime dependencies are missing."""
    missing: list[str] = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(module_name)

    if missing:
        joined = ", ".join(missing)
        print(f"Missing dependencies for profiling: {joined}")
        print("Install project dependencies first (example: `uv sync --all-groups`).")
        sys.exit(1)


def _profile_case(name: str, fn, top_n: int = 20) -> None:
    """Run cProfile for a single workload and print top cumulative entries.

    Parameters
    ----------
    name : str
        Input value for ``name``.
    fn : Any
        Input value for ``fn``.
    top_n : int
        Value provided for this parameter."""
    pr = cProfile.Profile()
    start = time.perf_counter()
    pr.enable()
    fn()
    pr.disable()
    elapsed = time.perf_counter() - start

    stream = io.StringIO()
    pstats.Stats(pr, stream=stream).sort_stats("cumulative").print_stats(top_n)

    print(f"\n=== {name} ===")
    print(f"wall_time_sec={elapsed:.4f}")
    print(stream.getvalue())


def main() -> int:
    """Run all profiling workloads and print their hotspot summaries.

    Returns
    -------
    value : int
        Result produced by this function."""
    _check_dependencies()

    import numpy as np
    import pandas as pd

    from aiml_dash.plugins.model_plugin.pages.decision_tree import build_tree
    from aiml_dash.plugins.model_plugin.pages.logistic import estimate_model
    from aiml_dash.plugins.model_plugin.pages.random_forest import train_forest
    from aiml_dash.utils.data_manager import data_manager
    from aiml_dash.utils.paginate_df import paginate_df
    from aiml_dash.utils.statistics import explore
    from aiml_dash.utils.transforms import (create_variable, mutate_ext,
                                            type_convert, xtile)

    np.random.seed(42)
    n = 120_000
    base_df = pd.DataFrame(
        {
            "y_bin": np.random.choice([0, 1], n),
            "y_num": np.random.normal(0, 1, n),
            "x1": np.random.normal(10, 3, n),
            "x2": np.random.gamma(2, 1.5, n),
            "x3": np.random.uniform(-3, 3, n),
            "grp": np.random.choice(["A", "B", "C", "D"], n),
            "cat1": np.random.choice(["low", "mid", "high"], n),
        }
    )

    data_manager.add_dataset("profile_df", base_df, description="profiling dataset")

    def case_explore() -> None:
        _ = explore(
            base_df,
            variables=["x1", "x2", "x3", "y_num"],
            byvar=["grp"],
            fun=["mean", "sd", "min", "max", "p25", "p75"],
        )

    def case_transforms() -> None:
        df = base_df.copy()
        for _ in range(10):
            df = mutate_ext(df, "x1", "standardize")
            df = type_convert(df, "y_bin", "factor")
            df = create_variable(df, "x_sum", "x1 + x2 + x3")
            _ = xtile(df["x2"], n=10)

    def case_paginate() -> None:
        for page in range(0, 120):
            _ = paginate_df(
                base_df,
                page_current=page,
                page_size=200,
                sort_by=[{"column_id": "x2", "direction": "desc"}],
            )

    def case_decision_tree() -> None:
        _ = build_tree(
            n=1,
            dataset="profile_df",
            response="y_bin",
            explanatory=["x1", "x2", "x3"],
            tree_type="classification",
            max_depth=7,
            min_samples=5,
        )

    def case_random_forest() -> None:
        _ = train_forest(
            n=1,
            dataset="profile_df",
            response="y_bin",
            explanatory=["x1", "x2", "x3"],
            rf_type="classification",
            n_trees=120,
            max_depth=12,
            seed=123,
        )

    def case_logistic_regression() -> None:
        _ = estimate_model(
            n_clicks=1,
            dataset_name="profile_df",
            response="y_bin",
            predictors=["x1", "x2", "x3", "cat1"],
        )

    _profile_case("statistics.explore grouped summary", case_explore)
    _profile_case("transforms mutate/type/eval loop", case_transforms)
    _profile_case("paginate_df repeated pages with sort", case_paginate)
    _profile_case("decision_tree callback path", case_decision_tree)
    _profile_case("random_forest callback path", case_random_forest)
    _profile_case("logistic callback path", case_logistic_regression)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
