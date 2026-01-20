"""
Utilities for server-side DataTable pagination and sorting.

Provides a small, well-typed paginate_df() function used by view callbacks and
unit tests to verify correct paging behavior.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def paginate_df(
    df: pd.DataFrame, page_current: int, page_size: int, sort_by: list[dict[str, Any]] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Return a page slice of `df` and column definitions suitable for dash DataTable.

    Parameters
    ----------
    df : pandas.DataFrame
        Source dataframe.
    page_current : int
        Zero-based page index.
    page_size : int
        Number of rows per page.
    sort_by : list of dict, optional
        Dash-style sort_by metadata: [{"column_id": "col", "direction": "asc"}]

    Returns
    -------
    data : list of dict
        Page rows as list of record dicts.
    columns : list of dict
        Column definitions for dash DataTable: [{"name": col, "id": col}, ...]
    """
    if df is None or df.empty:
        return [], []
    dff = df
    # Apply server-side sorting if requested
    if sort_by:
        sort_cols = [s["column_id"] for s in sort_by]
        asc = [s.get("direction", "asc") == "asc" for s in sort_by]
        try:
            dff = dff.sort_values(by=sort_cols, ascending=asc)
        except Exception:
            dff = dff
    # Calculate slice
    start = int(page_current) * int(page_size)
    end = start + int(page_size)
    page_df = dff.iloc[start:end]
    data = page_df.to_dict("records")
    columns = [{"name": c, "id": c} for c in page_df.columns]
    return data, columns
