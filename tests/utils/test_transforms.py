"""Tests for transforms module."""

import pandas as pd
import numpy as np
import pytest

from aiml_dash.utils.transforms import (
    center,
    standardize,
    square,
    inverse,
    normalize,
    ln,
    log10,
    exp,
    sqrt,
    xtile,
    as_integer,
    as_numeric,
    as_factor,
    as_character,
    make_train,
    refactor,
    mutate_ext,
    type_convert,
    create_variable,
    TRANSFORM_FUNCTIONS,
)


@pytest.fixture
def sample_series():
    """Create a sample numeric series for testing."""
    return pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


@pytest.fixture
def sample_array():
    """Create a sample numpy array for testing."""
    return np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 30, 40, 50],
        'cat': ['A', 'B', 'A', 'B', 'A'],
    })


class TestBasicTransforms:
    """Test basic transformation functions."""

    def test_center(self, sample_series):
        """Test centering transformation."""
        result = center(sample_series)
        assert result.mean() == pytest.approx(0, abs=1e-10)
        assert len(result) == len(sample_series)

    def test_standardize(self, sample_series):
        """Test standardization transformation."""
        result = standardize(sample_series)
        assert result.mean() == pytest.approx(0, abs=1e-10)
        assert result.std() == pytest.approx(1, abs=1e-10)

    def test_square(self, sample_series):
        """Test square transformation."""
        result = square(sample_series)
        expected = sample_series ** 2
        pd.testing.assert_series_equal(result, expected)

    def test_inverse(self):
        """Test inverse transformation."""
        series = pd.Series([1, 2, 4, 5, 10])
        result = inverse(series)
        expected = 1 / series
        pd.testing.assert_series_equal(result, expected)

    def test_normalize(self):
        """Test normalize transformation."""
        x = pd.Series([10, 20, 30, 40, 50])
        y = pd.Series([2, 4, 5, 8, 10])
        result = normalize(x, y)
        expected = x / y
        pd.testing.assert_series_equal(result, expected)


class TestMathTransforms:
    """Test mathematical transformation functions."""

    def test_ln(self):
        """Test natural logarithm."""
        series = pd.Series([1, 2, 3, 4, 5])
        result = ln(series)
        expected = np.log(series)
        pd.testing.assert_series_equal(result, expected)

    def test_log10(self):
        """Test base-10 logarithm."""
        series = pd.Series([1, 10, 100, 1000])
        result = log10(series)
        expected = np.log10(series)
        pd.testing.assert_series_equal(result, expected)

    def test_exp(self):
        """Test exponential function."""
        series = pd.Series([0, 1, 2, 3])
        result = exp(series)
        expected = np.exp(series)
        pd.testing.assert_series_equal(result, expected)

    def test_sqrt(self):
        """Test square root."""
        series = pd.Series([1, 4, 9, 16, 25])
        result = sqrt(series)
        expected = np.sqrt(series)
        pd.testing.assert_series_equal(result, expected)


class TestXtile:
    """Test xtile function for quantile binning."""

    def test_xtile_basic(self):
        """Test basic xtile functionality."""
        series = pd.Series(range(1, 101))
        result = xtile(series, n=4)
        assert result.min() == 1
        assert result.max() == 4

    def test_xtile_reversed(self):
        """Test xtile with reverse order."""
        series = pd.Series(range(1, 101))
        result = xtile(series, n=4, rev=True)
        assert result.min() == 1
        assert result.max() == 4

    def test_xtile_custom_bins(self):
        """Test xtile with custom number of bins."""
        series = pd.Series(range(1, 51))
        result = xtile(series, n=10)
        assert result.min() == 1
        assert result.max() == 10


class TestTypeConversions:
    """Test type conversion functions."""

    def test_as_integer(self):
        """Test conversion to integer."""
        series = pd.Series([1, 2, 3, 4])
        result = as_integer(series)
        assert result.dtype == 'Int64'

    def test_as_integer_with_strings(self):
        """Test integer conversion with strings."""
        series = pd.Series(['1', '2', '3', '4'])
        result = as_integer(series)
        assert result.dtype == 'Int64'

    def test_as_numeric(self):
        """Test conversion to numeric."""
        series = pd.Series(['1.5', '2.7', '3.2', 'invalid'])
        result = as_numeric(series)
        assert pd.api.types.is_numeric_dtype(result)
        assert result.isna().sum() == 1  # 'invalid' becomes NaN

    def test_as_factor(self):
        """Test conversion to categorical."""
        series = pd.Series(['A', 'B', 'A', 'C', 'B'])
        result = as_factor(series)
        assert isinstance(result, pd.Categorical)
        assert not result.ordered

    def test_as_factor_ordered(self):
        """Test conversion to ordered categorical."""
        series = pd.Series(['low', 'medium', 'high', 'low'])
        result = as_factor(series, ordered=True)
        assert isinstance(result, pd.Categorical)
        assert result.ordered

    def test_as_character(self):
        """Test conversion to string."""
        series = pd.Series([1, 2, 3, 4])
        result = as_character(series)
        assert result.dtype == object
        assert all(isinstance(x, str) for x in result)


class TestMakeTrain:
    """Test make_train function."""

    def test_make_train_basic(self):
        """Test basic train/test split."""
        result = make_train(p=0.7, n=100, seed=42)
        assert len(result) == 100
        assert result.dtype == bool
        # With seed, proportion should be close to 0.7
        assert 0.6 <= result.sum() / 100 <= 0.8

    def test_make_train_reproducible(self):
        """Test make_train is reproducible with seed."""
        result1 = make_train(p=0.7, n=50, seed=123)
        result2 = make_train(p=0.7, n=50, seed=123)
        assert np.array_equal(result1, result2)

    def test_make_train_different_proportions(self):
        """Test make_train with different proportions."""
        result1 = make_train(p=0.5, n=1000, seed=42)
        result2 = make_train(p=0.9, n=1000, seed=42)
        assert result1.sum() < result2.sum()


class TestRefactor:
    """Test refactor function."""

    def test_refactor_basic(self):
        """Test basic refactor functionality."""
        series = pd.Series(['B', 'A', 'C', 'A', 'B'])
        result = refactor(series)
        assert isinstance(result, pd.Categorical)

    def test_refactor_custom_levels(self):
        """Test refactor with custom levels."""
        series = pd.Series(['B', 'A', 'C', 'A', 'B'])
        result = refactor(series, levs=['A', 'B', 'C'])
        assert isinstance(result, pd.Categorical)
        assert list(result.categories) == ['A', 'B', 'C']


class TestMutateExt:
    """Test mutate_ext function."""

    def test_mutate_ext_center(self, sample_dataframe):
        """Test mutate_ext with center function."""
        result = mutate_ext(sample_dataframe, 'x', 'center')
        assert 'x_center' in result.columns
        assert len(result.columns) == len(sample_dataframe.columns) + 1

    def test_mutate_ext_standardize(self, sample_dataframe):
        """Test mutate_ext with standardize function."""
        result = mutate_ext(sample_dataframe, 'x', 'standardize')
        assert 'x_standardize' in result.columns

    def test_mutate_ext_square(self, sample_dataframe):
        """Test mutate_ext with square function."""
        result = mutate_ext(sample_dataframe, 'x', 'square')
        assert 'x_square' in result.columns
        expected = sample_dataframe['x'] ** 2
        pd.testing.assert_series_equal(result['x_square'], expected, check_names=False)

    def test_mutate_ext_ln(self, sample_dataframe):
        """Test mutate_ext with ln function."""
        result = mutate_ext(sample_dataframe, 'x', 'ln')
        assert 'x_ln' in result.columns


class TestTransformFunctions:
    """Test TRANSFORM_FUNCTIONS dictionary."""

    def test_transform_functions_exists(self):
        """Test TRANSFORM_FUNCTIONS dictionary exists."""
        assert isinstance(TRANSFORM_FUNCTIONS, dict)
        assert len(TRANSFORM_FUNCTIONS) > 0

    def test_transform_functions_structure(self):
        """Test TRANSFORM_FUNCTIONS has correct structure."""
        for key, value in TRANSFORM_FUNCTIONS.items():
            assert isinstance(key, str)
            assert isinstance(value, tuple)
            assert len(value) == 2


class TestTypeConvert:
    """Test type_convert function."""

    def test_type_convert_to_integer(self, sample_dataframe):
        """Test type conversion to integer."""
        result = type_convert(sample_dataframe, 'x', 'integer')
        assert result['x'].dtype == 'Int64'

    def test_type_convert_to_numeric(self, sample_dataframe):
        """Test type conversion to numeric."""
        result = type_convert(sample_dataframe, 'x', 'numeric')
        assert pd.api.types.is_numeric_dtype(result['x'])

    def test_type_convert_to_factor(self, sample_dataframe):
        """Test type conversion to factor."""
        result = type_convert(sample_dataframe, 'cat', 'factor')
        assert isinstance(result['cat'].dtype, pd.CategoricalDtype)

    def test_type_convert_to_character(self, sample_dataframe):
        """Test type conversion to character."""
        result = type_convert(sample_dataframe, 'x', 'character')
        assert result['x'].dtype == object


class TestCreateVariable:
    """Test create_variable function."""

    def test_create_variable_simple(self, sample_dataframe):
        """Test create_variable with simple expression."""
        result = create_variable(sample_dataframe, 'z', 'x + y')
        assert 'z' in result.columns
        expected = sample_dataframe['x'] + sample_dataframe['y']
        pd.testing.assert_series_equal(result['z'], expected, check_names=False)

    def test_create_variable_complex(self, sample_dataframe):
        """Test create_variable with complex expression."""
        result = create_variable(sample_dataframe, 'ratio', 'y / x')
        assert 'ratio' in result.columns
        expected = sample_dataframe['y'] / sample_dataframe['x']
        pd.testing.assert_series_equal(result['ratio'], expected, check_names=False)

    def test_create_variable_invalid(self, sample_dataframe):
        """Test create_variable with invalid expression."""
        # Should handle error gracefully
        result = create_variable(sample_dataframe, 'invalid', 'nonexistent_col * 2')
        # Original dataframe should be unchanged or error handled
        assert len(result.columns) >= len(sample_dataframe.columns)
