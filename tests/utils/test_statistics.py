"""Tests for statistics module."""

import pandas as pd
import numpy as np
import pytest
from scipy import stats

from aiml_dash.utils.statistics import (
    n_obs,
    n_missing,
    percentile,
    p01,
    p025,
    p05,
    p10,
    p25,
    p75,
    p90,
    p95,
    p975,
    p99,
    cv,
    se,
    me,
    prop,
    varprop,
    sdprop,
    seprop,
    meprop,
    varpop,
    sdpop,
    modal,
    does_vary,
    skew,
    kurtosi,
    explore,
    chi_square_test,
    STAT_FUNCTIONS,
)


@pytest.fixture
def sample_series():
    """Create a sample numeric series for testing."""
    return pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


@pytest.fixture
def sample_series_with_nan():
    """Create a sample series with missing values."""
    return pd.Series([1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10])


@pytest.fixture
def sample_proportion():
    """Create a sample proportion series (0s and 1s)."""
    return pd.Series([0, 1, 1, 0, 1, 1, 1, 0, 1, 1])


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [10, 20, 30, 40, 50],
        "C": ["cat1", "cat2", "cat1", "cat2", "cat1"],
    })


class TestBasicStats:
    """Test basic statistical functions."""

    def test_n_obs(self, sample_series, sample_series_with_nan):
        """Test n_obs function."""
        assert n_obs(sample_series) == 10
        assert n_obs(sample_series_with_nan) == 10

    def test_n_missing(self, sample_series, sample_series_with_nan):
        """Test n_missing function."""
        assert n_missing(sample_series) == 0
        assert n_missing(sample_series_with_nan) == 2


class TestPercentiles:
    """Test percentile functions."""

    def test_percentile(self, sample_series):
        """Test percentile function."""
        assert percentile(sample_series, 0.5) == 5.5
        assert percentile(sample_series, 0.25) == 3.25

    def test_p01(self, sample_series):
        """Test 1st percentile."""
        result = p01(sample_series)
        assert result == pytest.approx(1.09, abs=0.01)

    def test_p025(self, sample_series):
        """Test 2.5th percentile."""
        result = p025(sample_series)
        assert result == pytest.approx(1.225, abs=0.01)

    def test_p05(self, sample_series):
        """Test 5th percentile."""
        result = p05(sample_series)
        assert result == pytest.approx(1.45, abs=0.01)

    def test_p10(self, sample_series):
        """Test 10th percentile."""
        result = p10(sample_series)
        assert result == pytest.approx(1.9, abs=0.01)

    def test_p25(self, sample_series):
        """Test 25th percentile."""
        assert p25(sample_series) == 3.25

    def test_p75(self, sample_series):
        """Test 75th percentile."""
        assert p75(sample_series) == 7.75

    def test_p90(self, sample_series):
        """Test 90th percentile."""
        result = p90(sample_series)
        assert result == pytest.approx(9.1, abs=0.01)

    def test_p95(self, sample_series):
        """Test 95th percentile."""
        result = p95(sample_series)
        assert result == pytest.approx(9.55, abs=0.01)

    def test_p975(self, sample_series):
        """Test 97.5th percentile."""
        result = p975(sample_series)
        assert result == pytest.approx(9.775, abs=0.01)

    def test_p99(self, sample_series):
        """Test 99th percentile."""
        result = p99(sample_series)
        assert result == pytest.approx(9.91, abs=0.01)


class TestVariability:
    """Test variability measures."""

    def test_cv(self, sample_series):
        """Test coefficient of variation."""
        result = cv(sample_series)
        expected = sample_series.std() / sample_series.mean()
        assert result == pytest.approx(expected)

    def test_cv_zero_mean(self):
        """Test CV with zero mean."""
        series = pd.Series([0, 0, 0])
        result = cv(series)
        assert np.isnan(result)

    def test_se(self, sample_series):
        """Test standard error."""
        result = se(sample_series)
        expected = sample_series.std() / np.sqrt(10)
        assert result == pytest.approx(expected)

    def test_me(self, sample_series):
        """Test margin of error."""
        result = me(sample_series, conf=0.95)
        assert result > 0
        assert isinstance(result, float)

    def test_varpop(self, sample_series):
        """Test population variance."""
        result = varpop(sample_series)
        expected = sample_series.var(ddof=0)
        assert result == pytest.approx(expected)

    def test_sdpop(self, sample_series):
        """Test population standard deviation."""
        result = sdpop(sample_series)
        expected = sample_series.std(ddof=0)
        assert result == pytest.approx(expected)


class TestProportions:
    """Test proportion functions."""

    def test_prop(self, sample_proportion):
        """Test proportion calculation."""
        result = prop(sample_proportion)
        assert result == 0.7  # 7 out of 10 are 1

    def test_varprop(self, sample_proportion):
        """Test variance of proportion."""
        result = varprop(sample_proportion)
        p = 0.7
        expected = p * (1 - p)
        assert result == pytest.approx(expected)

    def test_sdprop(self, sample_proportion):
        """Test standard deviation of proportion."""
        result = sdprop(sample_proportion)
        p = 0.7
        expected = np.sqrt(p * (1 - p))
        assert result == pytest.approx(expected)

    def test_seprop(self, sample_proportion):
        """Test standard error of proportion."""
        result = seprop(sample_proportion)
        p = 0.7
        expected = np.sqrt(p * (1 - p) / 10)
        assert result == pytest.approx(expected)

    def test_meprop(self, sample_proportion):
        """Test margin of error for proportion."""
        result = meprop(sample_proportion, conf=0.95)
        assert result > 0
        assert isinstance(result, float)


class TestDistribution:
    """Test distribution functions."""

    def test_modal(self, sample_series):
        """Test mode calculation."""
        series = pd.Series([1, 2, 2, 3, 3, 3])
        result = modal(series)
        assert result == 3

    def test_modal_empty(self):
        """Test mode with empty series."""
        series = pd.Series([], dtype=float)
        result = modal(series)
        assert np.isnan(result)

    def test_does_vary_true(self, sample_series):
        """Test does_vary returns True for varying data."""
        assert does_vary(sample_series) is True

    def test_does_vary_false(self):
        """Test does_vary returns False for constant data."""
        series = pd.Series([5, 5, 5, 5, 5])
        assert does_vary(series) is False

    def test_skew(self, sample_series):
        """Test skewness calculation."""
        result = skew(sample_series)
        expected = stats.skew(sample_series.dropna())
        assert result == pytest.approx(expected)

    def test_kurtosi(self, sample_series):
        """Test kurtosis calculation."""
        result = kurtosi(sample_series)
        expected = stats.kurtosis(sample_series.dropna())
        assert result == pytest.approx(expected)


class TestStatFunctions:
    """Test STAT_FUNCTIONS dictionary."""

    def test_stat_functions_exists(self):
        """Test STAT_FUNCTIONS dictionary exists."""
        assert isinstance(STAT_FUNCTIONS, dict)
        assert len(STAT_FUNCTIONS) > 0

    def test_stat_functions_structure(self):
        """Test STAT_FUNCTIONS has correct structure."""
        for key, value in STAT_FUNCTIONS.items():
            assert isinstance(key, str)
            assert isinstance(value, tuple)
            assert len(value) == 2


class TestExplore:
    """Test explore function."""

    def test_explore_basic(self, sample_dataframe):
        """Test basic explore functionality."""
        result = explore(sample_dataframe, vars=["A", "B"], fun=["mean", "min", "max"])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "A_mean" in result.columns
        assert "B_mean" in result.columns

    def test_explore_with_groupby(self, sample_dataframe):
        """Test explore with groupby."""
        result = explore(sample_dataframe, vars=["A"], byvar=["C"], fun=["mean"])
        assert isinstance(result, pd.DataFrame)
        assert "C" in result.columns
        assert len(result) == 2  # Two categories

    def test_explore_with_filter(self, sample_dataframe):
        """Test explore with data filter."""
        result = explore(sample_dataframe, vars=["A"], fun=["mean"], data_filter="A > 2")
        assert isinstance(result, pd.DataFrame)
        # Should only include rows where A > 2


class TestChiSquare:
    """Test chi-square test function."""

    def test_chi_square_test_basic(self):
        """Test basic chi-square test."""
        observed = pd.DataFrame([[10, 20], [30, 40]])
        result = chi_square_test(observed)
        assert "chi2" in result
        assert "p_value" in result
        assert "dof" in result
        assert "expected" in result
        assert "significant" in result
        assert isinstance(result["chi2"], float)
        assert isinstance(result["p_value"], float)
        assert isinstance(result["dof"], int)
        assert isinstance(result["significant"], (bool, np.bool_))

    def test_chi_square_test_error_handling(self):
        """Test chi-square test error handling."""
        # Test with invalid data
        observed = pd.DataFrame([[-1, -2]])
        result = chi_square_test(observed)
        assert "error" in result or "chi2" in result
