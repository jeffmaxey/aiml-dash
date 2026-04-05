"""
Model Selection
===============

Utilities for cross-validation, grid search, and model comparison.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score

if TYPE_CHECKING:
    from aiml.base import BaseModel


def cross_validate(
    model: "BaseModel",
    X: Any,
    y: Any,
    *,
    cv: int = 5,
    scoring: str | None = None,
) -> dict[str, Any]:
    """Cross-validate *model* and return a summary of scores.

    Parameters
    ----------
    model:
        An ``aiml`` model instance (must have been constructed but need not be
        fitted first).
    X:
        Feature matrix.
    y:
        Target vector.
    cv:
        Number of folds. Default ``5``.
    scoring:
        scikit-learn scoring string (e.g. ``"r2"``, ``"accuracy"``). When
        ``None`` the estimator's default scorer is used.

    Returns
    -------
    results : dict
        ``{"scores": [...], "mean": float, "std": float, "cv": int, "scoring": str}``
    """
    estimator = model._estimator
    scores = cross_val_score(estimator, X, y, cv=cv, scoring=scoring)
    return {
        "scores": scores.tolist(),
        "mean": float(scores.mean()),
        "std": float(scores.std()),
        "cv": cv,
        "scoring": scoring,
    }


def grid_search(
    model: "BaseModel",
    X: Any,
    y: Any,
    param_grid: dict[str, list[Any]],
    *,
    cv: int = 5,
    scoring: str | None = None,
    refit: bool = True,
) -> dict[str, Any]:
    """Exhaustive grid search over *param_grid*.

    Parameters
    ----------
    model:
        An ``aiml`` model instance.
    X:
        Feature matrix.
    y:
        Target vector.
    param_grid:
        Dictionary mapping parameter names to lists of candidate values.
    cv:
        Number of cross-validation folds.
    scoring:
        Scoring string. When ``None`` the estimator's default is used.
    refit:
        When ``True``, the best estimator is fitted on the full data and stored
        back on *model._estimator*.

    Returns
    -------
    results : dict
        ``{"best_params": dict, "best_score": float, "cv_results": dict}``
    """
    gs = GridSearchCV(
        model._estimator,
        param_grid,
        cv=cv,
        scoring=scoring,
        refit=refit,
    )
    gs.fit(X, y)
    if refit:
        model._estimator = gs.best_estimator_
    return {
        "best_params": gs.best_params_,
        "best_score": float(gs.best_score_),
        "cv_results": {
            k: v.tolist() if isinstance(v, np.ndarray) else v
            for k, v in gs.cv_results_.items()
        },
    }


def random_search(
    model: "BaseModel",
    X: Any,
    y: Any,
    param_distributions: dict[str, Any],
    *,
    n_iter: int = 10,
    cv: int = 5,
    scoring: str | None = None,
    refit: bool = True,
    random_state: int | None = None,
) -> dict[str, Any]:
    """Randomised hyperparameter search.

    Parameters
    ----------
    model:
        An ``aiml`` model instance.
    X:
        Feature matrix.
    y:
        Target vector.
    param_distributions:
        Dictionary mapping parameter names to distributions or lists.
    n_iter:
        Number of parameter settings sampled.
    cv:
        Number of cross-validation folds.
    scoring:
        Scoring string.
    refit:
        Refit on the full data with the best parameters when ``True``.
    random_state:
        Seed for reproducibility.

    Returns
    -------
    results : dict
        ``{"best_params": dict, "best_score": float}``
    """
    rs = RandomizedSearchCV(
        model._estimator,
        param_distributions,
        n_iter=n_iter,
        cv=cv,
        scoring=scoring,
        refit=refit,
        random_state=random_state,
    )
    rs.fit(X, y)
    if refit:
        model._estimator = rs.best_estimator_
    return {
        "best_params": rs.best_params_,
        "best_score": float(rs.best_score_),
    }


def compare_models(
    models: list["BaseModel"],
    X: Any,
    y: Any,
    *,
    cv: int = 5,
    scoring: str | None = None,
) -> list[dict[str, Any]]:
    """Compare multiple models via cross-validation.

    Parameters
    ----------
    models:
        List of ``aiml`` model instances.
    X:
        Feature matrix.
    y:
        Target vector.
    cv:
        Number of folds.
    scoring:
        Scoring string.

    Returns
    -------
    results : list[dict]
        One entry per model, sorted by descending mean score.
    """
    results = []
    for model in models:
        result = cross_validate(model, X, y, cv=cv, scoring=scoring)
        result["model"] = type(model).__name__
        results.append(result)
    return sorted(results, key=lambda r: r["mean"], reverse=True)
