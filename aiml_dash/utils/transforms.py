"""
Transform Functions
==================

Data transformation functions mirroring aiml.data R package.
"""

import numpy as np
import pandas as pd


def center(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Center variable by subtracting the mean.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return x - x.mean()


def standardize(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Standardize variable to mean=0, sd=1.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return (x - x.mean()) / x.std()


def square(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Square the variable.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return x**2


def inverse(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Calculate 1/x.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return 1 / x


def normalize(
    x: pd.Series | np.ndarray, y: pd.Series | np.ndarray
) -> pd.Series | np.ndarray:
    """Normalize x by y (x/y).

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.
    y : pd.Series | np.ndarray
        Input value for ``y``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return x / y


def ln(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Natural logarithm.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return np.log(x)


def log10(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Base-10 logarithm.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return np.log10(x)


def exp(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Exponential function.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return np.exp(x)


def sqrt(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Square root.

    Parameters
    ----------
    x : pd.Series | np.ndarray
        Input value for ``x``.

    Returns
    -------
    value : pd.Series | np.ndarray
        Result produced by this function."""
    return np.sqrt(x)


def xtile(x: pd.Series, n: int = 5, rev: bool = False) -> pd.Series:
    """Create quantile bins.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.
    n : int
        Input value for ``n``.
    rev : bool
        Input value for ``rev``.

    Returns
    -------
    value : pd.Series
        Result produced by this function."""
    bins = pd.qcut(x, q=n, labels=False, duplicates="drop") + 1
    if rev:
        bins = bins.max() - bins + 1
    return bins


def as_integer(x: pd.Series) -> pd.Series:
    """Convert to integer type.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.

    Returns
    -------
    value : pd.Series
        Result produced by this function."""
    try:
        return pd.to_numeric(x, errors="coerce").astype("Int64")
    except (ValueError, TypeError):
        return x.astype("Int64")


def as_numeric(x: pd.Series) -> pd.Series:
    """Convert to numeric type.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.

    Returns
    -------
    value : pd.Series
        Result produced by this function."""
    return pd.to_numeric(x, errors="coerce")


def as_factor(x: pd.Series, ordered: bool = False) -> pd.Categorical:
    """Convert to categorical/factor.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.
    ordered : bool
        Input value for ``ordered``.

    Returns
    -------
    value : pd.Categorical
        Result produced by this function."""
    return pd.Categorical(x, ordered=ordered)


def as_character(x: pd.Series) -> pd.Series:
    """Convert to string type.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.

    Returns
    -------
    value : pd.Series
        Result produced by this function."""
    return x.astype(str)


def make_train(p: float = 0.7, n: int = 100, seed: int | None = None) -> np.ndarray:
    """Create train/test split indicator.

    Parameters
    ----------
    p : float
        Input value for ``p``.
    n : int
        Input value for ``n``.
    seed : int | None
        Input value for ``seed``.

    Returns
    -------
    value : np.ndarray
        Result produced by this function."""
    if seed is not None:
        np.random.seed(seed)

    return np.random.rand(n) < p


def refactor(x: pd.Series, levs: list[str] | None = None) -> pd.Categorical:
    """Refactor categorical variable.

    Parameters
    ----------
    x : pd.Series
        Input value for ``x``.
    levs : list[str] | None
        Input value for ``levs``.

    Returns
    -------
    value : pd.Categorical
        Result produced by this function."""
    if levs is None:
        levs = sorted(x.unique())

    return pd.Categorical(x, categories=levs, ordered=False)


def mutate_ext(
    df: pd.DataFrame, var: str, function: str, args: dict | None = None
) -> pd.DataFrame:
    """Extended mutate - apply transformation and add as new column.

    Parameters
    ----------
    df : pd.DataFrame
        Input value for ``df``.
    var : str
        Input value for ``var``.
    function : str
        Input value for ``function``.
    args : dict | None
        Input value for ``args``.

    Returns
    -------
    value : pd.DataFrame
        Result produced by this function."""
    result = df.copy()

    # Get the transform function
    func_map = {
        "center": center,
        "standardize": standardize,
        "square": square,
        "inverse": inverse,
        "ln": ln,
        "log10": log10,
        "exp": exp,
        "sqrt": sqrt,
    }

    if function in func_map:
        new_col_name = f"{var}_{function}"
        result[new_col_name] = func_map[function](df[var])

    return result


# Transform name mapping for UI
TRANSFORM_FUNCTIONS = {
    "center": ("Center", "Center by subtracting mean"),
    "standardize": ("Standardize", "Standardize to mean=0, sd=1"),
    "square": ("Square", "Square the variable (x²)"),
    "inverse": ("Inverse", "Calculate inverse (1/x)"),
    "ln": ("Natural log", "Natural logarithm"),
    "log10": ("Log 10", "Base-10 logarithm"),
    "exp": ("Exponential", "Exponential (eˣ)"),
    "sqrt": ("Square root", "Square root (√x)"),
    "xtile": ("Create bins", "Create quantile bins"),
    "as_integer": ("As integer", "Convert to integer"),
    "as_numeric": ("As numeric", "Convert to numeric"),
    "as_factor": ("As factor", "Convert to categorical"),
    "as_character": ("As character", "Convert to string"),
}


def type_convert(df: pd.DataFrame, var: str, to_type: str) -> pd.DataFrame:
    """Convert variable type.

    Parameters
    ----------
    df : pd.DataFrame
        Input value for ``df``.
    var : str
        Input value for ``var``.
    to_type : str
        Input value for ``to_type``.

    Returns
    -------
    value : pd.DataFrame
        Result produced by this function."""
    result = df.copy()

    if to_type == "integer":
        result[var] = as_integer(df[var])
    elif to_type == "numeric":
        result[var] = as_numeric(df[var])
    elif to_type == "factor":
        result[var] = as_factor(df[var])
    elif to_type == "character":
        result[var] = as_character(df[var])

    return result


def create_variable(df: pd.DataFrame, var_name: str, expression: str) -> pd.DataFrame:
    """Create new variable from expression.

    Parameters
    ----------
    df : pd.DataFrame
        Input value for ``df``.
    var_name : str
        Input value for ``var_name``.
    expression : str
        Input value for ``expression``.

    Returns
    -------
    value : pd.DataFrame
        Result produced by this function."""
    result = df.copy()

    try:
        # Evaluate expression in context of dataframe
        result[var_name] = result.eval(expression)
    except Exception as e:
        print(f"Error creating variable: {e!s}")

    return result
