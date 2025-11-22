"""Tests for paginate_df module."""

import pandas as pd
import pytest

from aiml_dash.utils.paginate_df import paginate_df


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        "A": list(range(1, 101)),
        "B": list(range(101, 201)),
        "C": ["cat"] * 50 + ["dog"] * 50,
    })


class TestPaginateDf:
    """Test paginate_df function."""

    def test_paginate_df_first_page(self, sample_dataframe):
        """Test paginate_df returns first page correctly."""
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=10)

        assert len(data) == 10
        assert len(columns) == 3
        assert data[0]["A"] == 1
        assert data[9]["A"] == 10

    def test_paginate_df_second_page(self, sample_dataframe):
        """Test paginate_df returns second page correctly."""
        data, columns = paginate_df(sample_dataframe, page_current=1, page_size=10)

        assert len(data) == 10
        assert data[0]["A"] == 11
        assert data[9]["A"] == 20

    def test_paginate_df_last_page(self, sample_dataframe):
        """Test paginate_df returns last page correctly."""
        data, columns = paginate_df(sample_dataframe, page_current=9, page_size=10)

        assert len(data) == 10
        assert data[0]["A"] == 91
        assert data[9]["A"] == 100

    def test_paginate_df_partial_page(self, sample_dataframe):
        """Test paginate_df handles partial last page."""
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=30)

        assert len(data) == 30

    def test_paginate_df_empty_dataframe(self):
        """Test paginate_df handles empty dataframe."""
        df = pd.DataFrame()
        data, columns = paginate_df(df, page_current=0, page_size=10)

        assert data == []
        assert columns == []

    def test_paginate_df_none_dataframe(self):
        """Test paginate_df handles None dataframe."""
        data, columns = paginate_df(None, page_current=0, page_size=10)

        assert data == []
        assert columns == []

    def test_paginate_df_columns_structure(self, sample_dataframe):
        """Test paginate_df returns correct column structure."""
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=10)

        assert isinstance(columns, list)
        assert len(columns) == 3
        assert all("name" in col for col in columns)
        assert all("id" in col for col in columns)
        assert columns[0]["name"] == "A"
        assert columns[0]["id"] == "A"

    def test_paginate_df_with_sorting_asc(self, sample_dataframe):
        """Test paginate_df with ascending sort."""
        sort_by = [{"column_id": "B", "direction": "asc"}]
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5, sort_by=sort_by)

        assert len(data) == 5
        assert data[0]["B"] == 101
        assert data[4]["B"] == 105

    def test_paginate_df_with_sorting_desc(self, sample_dataframe):
        """Test paginate_df with descending sort."""
        sort_by = [{"column_id": "A", "direction": "desc"}]
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5, sort_by=sort_by)

        assert len(data) == 5
        assert data[0]["A"] == 100
        assert data[4]["A"] == 96

    def test_paginate_df_with_multi_column_sort(self, sample_dataframe):
        """Test paginate_df with multiple column sort."""
        sort_by = [{"column_id": "C", "direction": "asc"}, {"column_id": "A", "direction": "desc"}]
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5, sort_by=sort_by)

        assert len(data) == 5
        # First should be 'cat' with highest A value among cats
        assert data[0]["C"] == "cat"

    def test_paginate_df_with_invalid_sort(self, sample_dataframe):
        """Test paginate_df handles invalid sort gracefully."""
        sort_by = [{"column_id": "nonexistent", "direction": "asc"}]
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5, sort_by=sort_by)

        # Should return data without sorting
        assert len(data) == 5

    def test_paginate_df_page_beyond_data(self, sample_dataframe):
        """Test paginate_df handles page beyond available data."""
        data, columns = paginate_df(sample_dataframe, page_current=20, page_size=10)

        # Should return empty page
        assert len(data) == 0
        assert len(columns) == 3

    def test_paginate_df_large_page_size(self, sample_dataframe):
        """Test paginate_df with page size larger than dataframe."""
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=200)

        # Should return all 100 rows
        assert len(data) == 100

    def test_paginate_df_data_is_dict(self, sample_dataframe):
        """Test paginate_df returns data as list of dicts."""
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5)

        assert isinstance(data, list)
        assert all(isinstance(row, dict) for row in data)
        assert all("A" in row and "B" in row and "C" in row for row in data)

    def test_paginate_df_sort_direction_default(self, sample_dataframe):
        """Test paginate_df uses default sort direction when not specified."""
        sort_by = [{"column_id": "A"}]
        data, columns = paginate_df(sample_dataframe, page_current=0, page_size=5, sort_by=sort_by)

        # Default should be ascending
        assert data[0]["A"] == 1
        assert data[4]["A"] == 5
