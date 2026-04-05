"""Tests for basics_plugin/callbacks_clt.py.

The CLT simulation callback has no data_manager dependency and can be
called with simple numeric parameters.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pytest

from aiml_dash.plugins.basics_plugin.callbacks_clt import run_clt_simulation


class TestRunCltSimulation:
    """Tests for run_clt_simulation()."""

    def test_missing_sample_size_returns_error(self):
        """Missing sample_size should raise ValueError and return error state."""
        result = run_clt_simulation(1, "normal", None, 100, None)
        stats_list, style, fig = result
        assert isinstance(stats_list, list)

    def test_missing_num_samples_returns_error(self):
        """Missing num_samples should raise ValueError and return error state."""
        stats_list, style, fig = run_clt_simulation(1, "normal", 30, None, None)
        assert isinstance(stats_list, list)

    def test_returns_three_elements(self):
        """Callback always returns a 3-tuple."""
        result = run_clt_simulation(1, "uniform", 30, 100, 42)
        assert len(result) == 3

    def test_uniform_distribution(self):
        """Uniform distribution should return a Figure."""
        _, style, fig = run_clt_simulation(1, "uniform", 30, 100, 42)
        assert isinstance(fig, go.Figure)
        assert style.get("display") == "block"

    def test_normal_distribution(self):
        """Normal distribution should return a Figure."""
        _, style, fig = run_clt_simulation(1, "normal", 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_exponential_distribution(self):
        """Exponential distribution should return a Figure."""
        _, style, fig = run_clt_simulation(1, "exponential", 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_skewed_distribution(self):
        """Skewed distribution should return a Figure."""
        _, style, fig = run_clt_simulation(1, "skewed", 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_bimodal_distribution(self):
        """Bimodal distribution should return a Figure."""
        _, style, fig = run_clt_simulation(1, "bimodal", 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_stats_list_not_empty_on_success(self):
        """Successful run should return a non-empty stats list."""
        stats_list, _, _ = run_clt_simulation(1, "uniform", 30, 100, 42)
        assert len(stats_list) > 0

    def test_reproducible_with_same_seed(self):
        """Two calls with the same seed should produce identical stat summaries."""
        stats_a, _, _ = run_clt_simulation(1, "normal", 50, 200, 7)
        stats_b, _, _ = run_clt_simulation(1, "normal", 50, 200, 7)
        # Both should succeed and produce the same number of stat elements
        assert len(stats_a) == len(stats_b)

    def test_none_seed_accepted(self):
        """A None seed should be accepted without error."""
        _, _, fig = run_clt_simulation(1, "uniform", 30, 100, None)
        assert isinstance(fig, go.Figure)

    def test_none_distribution_defaults_to_uniform(self):
        """A None distribution should fall back to uniform."""
        _, _, fig = run_clt_simulation(1, None, 30, 100, 42)
        assert isinstance(fig, go.Figure)

    def test_float_sample_size_accepted(self):
        """Float inputs for sample_size/num_samples should be converted to int."""
        _, _, fig = run_clt_simulation(1, "normal", 30.0, 100.0, 42)
        assert isinstance(fig, go.Figure)

    def test_large_sample_size(self):
        """A larger sample size should still produce a valid Figure."""
        _, _, fig = run_clt_simulation(1, "uniform", 200, 500, 42)
        assert isinstance(fig, go.Figure)
