"""
Transform Functions
==================

Data transformation functions mirroring aiml.data R package.
"""


import numpy as np
import pandas as pd


def center(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Center variable by subtracting the mean."""
    return x - x.mean()


def standardize(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Standardize variable to mean=0, sd=1."""
    return (x - x.mean()) / x.std()


def square(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Square the variable."""
    return x**2


def inverse(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Calculate 1/x."""
    return 1 / x


def normalize(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Normalize x by y (x/y)."""
    return x / y


def ln(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Natural logarithm."""
    return np.log(x)


def log10(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Base-10 logarithm."""
    return np.log10(x)


def exp(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Exponential function."""
    return np.exp(x)


def sqrt(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """Square root."""
    return np.sqrt(x)


def xtile(x: pd.Series, n: int = 5, rev: bool = False) -> pd.Series:
    """
    Create quantile bins.

    Parameters
    ----------
    x : pd.Series
        Input variable
    n : int
        Number of quantiles
    rev : bool
        Reverse order

    Returns
    -------
    pd.Series
        Quantile bin labels
    """
    bins = pd.qcut(x, q=n, labels=False, duplicates="drop") + 1
    if rev:
        bins = bins.max() - bins + 1
    return bins


def as_integer(x: pd.Series) -> pd.Series:
    """Convert to integer type."""
    try:
        return pd.to_numeric(x, errors="coerce").astype("Int64")
    except (ValueError, TypeError):
        return x.astype("Int64")


def as_numeric(x: pd.Series) -> pd.Series:
    """Convert to numeric type."""
    return pd.to_numeric(x, errors="coerce")


def as_factor(x: pd.Series, ordered: bool = False) -> pd.Categorical:
    """Convert to categorical/factor."""
    return pd.Categorical(x, ordered=ordered)


def as_character(x: pd.Series) -> pd.Series:
    """Convert to string type."""
    return x.astype(str)


def make_train(p: float = 0.7, n: int = 100, seed: int | None = None) -> np.ndarray:
    """
    Create train/test split indicator.

    Parameters
    ----------
    p : float
        Proportion for training set
    n : int
        Total number of observations
    seed : int, optional
        Random seed

    Returns
    -------
    np.ndarray
        Boolean array indicating training samples
    """
    if seed is not None:
        np.random.seed(seed)

    return np.random.rand(n) < p


def refactor(x: pd.Series, levs: list[str] | None = None) -> pd.Categorical:
    """
    Refactor categorical variable.

    Parameters
    ----------
    x : pd.Series
        Categorical variable
    levs : list of str, optional
        New category order

    Returns
    -------
    pd.Categorical
        Refactored categorical
    """
    if levs is None:
        levs = sorted(x.unique())

    return pd.Categorical(x, categories=levs, ordered=False)


def mutate_ext(df: pd.DataFrame, var: str, function: str, args: dict | None = None) -> pd.DataFrame:
    """
    Extended mutate - apply transformation and add as new column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    var : str
        Variable name to transform
    function : str
        Function name to apply
    args : dict, optional
        Additional arguments

    Returns
    -------
    pd.DataFrame
        DataFrame with new column
    """
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
    """
    Convert variable type.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    var : str
        Variable to convert
    to_type : str
        Target type ('integer', 'numeric', 'factor', 'character')

    Returns
    -------
    pd.DataFrame
        DataFrame with converted variable
    """
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
    """
    Create new variable from expression.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    var_name : str
        Name for new variable
    expression : str
        Python expression using column names

    Returns
    -------
    pd.DataFrame
        DataFrame with new variable
    """
    result = df.copy()

    try:
        # Evaluate expression in context of dataframe
        result[var_name] = result.eval(expression)
    except Exception as e:
        print(f"Error creating variable: {e!s}")

    return result
