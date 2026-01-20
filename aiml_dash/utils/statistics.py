"""
Statistical Functions
====================

Statistical and exploration functions mirroring aiml.data R package.
"""

import contextlib
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


def n_obs(x: pd.Series) -> int:
    """Count total observations including NaN."""
    return len(x)


def n_missing(x: pd.Series) -> int:
    """Count missing (NaN) values."""
    return x.isna().sum()


def percentile(x: pd.Series, q: float) -> float:
    """Calculate percentile."""
    return float(np.percentile(x.dropna(), q * 100))


# Percentile functions
def p01(x: pd.Series) -> float:
    """1st percentile."""
    return percentile(x, 0.01)


def p025(x: pd.Series) -> float:
    """2.5th percentile."""
    return percentile(x, 0.025)


def p05(x: pd.Series) -> float:
    """5th percentile."""
    return percentile(x, 0.05)


def p10(x: pd.Series) -> float:
    """10th percentile."""
    return percentile(x, 0.10)


def p25(x: pd.Series) -> float:
    """25th percentile."""
    return percentile(x, 0.25)


def p75(x: pd.Series) -> float:
    """75th percentile."""
    return percentile(x, 0.75)


def p90(x: pd.Series) -> float:
    """90th percentile."""
    return percentile(x, 0.90)


def p95(x: pd.Series) -> float:
    """95th percentile."""
    return percentile(x, 0.95)


def p975(x: pd.Series) -> float:
    """97.5th percentile."""
    return percentile(x, 0.975)


def p99(x: pd.Series) -> float:
    """99th percentile."""
    return percentile(x, 0.99)


def cv(x: pd.Series) -> float:
    """Coefficient of variation."""
    return x.std() / x.mean() if x.mean() != 0 else np.nan


def se(x: pd.Series) -> float:
    """Standard error."""
    return x.std() / np.sqrt(len(x.dropna()))


def me(x: pd.Series, conf: float = 0.95) -> float:
    """Margin of error."""
    return float(se(x) * stats.t.ppf((1 + conf) / 2, len(x.dropna()) - 1))


def prop(x: pd.Series) -> float:
    """Proportion of successes (1s or True)."""
    return x.mean()


def varprop(x: pd.Series) -> float:
    """Variance of proportion."""
    p = prop(x)
    return p * (1 - p)


def sdprop(x: pd.Series) -> float:
    """Standard deviation of proportion."""
    return np.sqrt(varprop(x))


def seprop(x: pd.Series) -> float:
    """Standard error of proportion."""
    return np.sqrt(varprop(x) / len(x.dropna()))


def meprop(x: pd.Series, conf: float = 0.95) -> float:
    """Margin of error for proportion."""
    return float(seprop(x) * stats.norm.ppf((1 + conf) / 2))


def varpop(x: pd.Series) -> float:
    """Population variance."""
    return float(x.var(ddof=0))


def sdpop(x: pd.Series) -> float:
    """Population standard deviation."""
    return x.std(ddof=0)


def modal(x: pd.Series) -> Any:
    """Mode - most frequent value."""
    mode_values = x.mode()
    return mode_values.iloc[0] if len(mode_values) > 0 else np.nan


def does_vary(x: pd.Series) -> bool:
    """Check if variable varies."""
    return x.nunique() > 1


def skew(x: pd.Series) -> float:
    """Skewness."""
    return stats.skew(x.dropna())


def kurtosi(x: pd.Series) -> float:
    """Kurtosis."""
    return stats.kurtosis(x.dropna())


# Function name mapping for UI
STAT_FUNCTIONS = {
    "n_obs": ("n_obs", "Number of observations"),
    "n_missing": ("n_missing", "Number of missing values"),
    "n_distinct": ("nunique", "Number of distinct values"),
    "mean": ("mean", "Mean"),
    "median": ("median", "Median"),
    "modal": (modal, "Mode"),
    "min": ("min", "Minimum"),
    "max": ("max", "Maximum"),
    "sum": ("sum", "Sum"),
    "var": ("var", "Variance"),
    "sd": ("std", "Standard deviation"),
    "se": (se, "Standard error"),
    "me": (me, "Margin of error"),
    "cv": (cv, "Coefficient of variation"),
    "prop": (prop, "Proportion"),
    "varprop": (varprop, "Variance of proportion"),
    "sdprop": (sdprop, "Standard deviation of proportion"),
    "seprop": (seprop, "Standard error of proportion"),
    "meprop": (meprop, "Margin of error of proportion"),
    "varpop": (varpop, "Population variance"),
    "sdpop": (sdpop, "Population standard deviation"),
    "p01": (p01, "1st percentile"),
    "p025": (p025, "2.5th percentile"),
    "p05": (p05, "5th percentile"),
    "p10": (p10, "10th percentile"),
    "p25": (p25, "25th percentile"),
    "p75": (p75, "75th percentile"),
    "p90": (p90, "90th percentile"),
    "p95": (p95, "95th percentile"),
    "p975": (p975, "97.5th percentile"),
    "p99": (p99, "99th percentile"),
    "skew": (skew, "Skewness"),
    "kurtosi": (kurtosi, "Kurtosis"),
}


def explore(
    df: pd.DataFrame,
    variables: list[str],
    byvar: list[str] | None = None,
    fun: list[str] | None = None,
    data_filter: str | None = None,
) -> pd.DataFrame:
    """
    Explore data with summary statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    variables: list of str
        Variables to summarize
    byvar : list of str, optional
        Variables to group by
    fun : list of str
        Functions to apply
    data_filter : str, optional
        Query string to filter data

    Returns
    -------
    pd.DataFrame
        Summary statistics table
    """
    # Apply filter if specified
    if fun is None:
        fun = ["mean", "sd", "min", "max"]
    if data_filter:
        with contextlib.suppress(Exception):
            df = df.query(data_filter)

    # Build aggregation dictionary
    agg_dict = {}
    for var in variables:
        agg_list = []
        for f in fun:
            if f in STAT_FUNCTIONS:
                func, _ = STAT_FUNCTIONS[f]
                agg_list.append(func)
            elif hasattr(df[var], f):
                agg_list.append(f)
        agg_dict[var] = agg_list

    # Apply grouping if specified
    if byvar and len(byvar) > 0:
        result = df.groupby(byvar)[vars].agg(agg_dict)
        # Flatten multi-level columns
        result.columns = ["_".join(col).strip() for col in result.columns.values]
        result = result.reset_index()
    else:
        # No grouping - apply to entire dataset
        result_dict = {}
        for var in variables:
            for f in fun:
                if f in STAT_FUNCTIONS:
                    func, _ = STAT_FUNCTIONS[f]
                    if callable(func):
                        result_dict[f"{var}_{f}"] = func(df[var])
                    else:
                        result_dict[f"{var}_{f}"] = getattr(df[var], func)()
                elif hasattr(df[var], f):
                    result_dict[f"{var}_{f}"] = getattr(df[var], f)()
        result = pd.DataFrame([result_dict])

    return result


def chi_square_test(observed: pd.DataFrame) -> dict[str, Any]:
    """
    Perform chi-square test on a contingency table.

    Parameters
    ----------
    observed : pd.DataFrame
        Contingency table

    Returns
    -------
    dict
        Chi-square test results
    """
    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        return {
            "chi2": chi2,
            "p_value": p_value,
            "dof": dof,
            "expected": expected,
            "significant": p_value < 0.05,
        }
    except Exception as e:
        return {"error": str(e)}
