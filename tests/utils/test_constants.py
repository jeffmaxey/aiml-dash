"""Tests for constants module."""

from aiml_dash.utils.constants import (
    APP_NAME,
    APP_TITLE,
    APP_DESCRIPTION,
    APP_OVERVIEW,
    GITHUB_URL,
)


def test_app_name():
    """Test APP_NAME constant."""
    assert APP_NAME == "AIML Dash"
    assert isinstance(APP_NAME, str)


def test_app_title():
    """Test APP_TITLE constant."""
    assert APP_TITLE == "AIML Dash"
    assert isinstance(APP_TITLE, str)


def test_app_description():
    """Test APP_DESCRIPTION constant."""
    assert "Dash application" in APP_DESCRIPTION
    assert isinstance(APP_DESCRIPTION, str)


def test_app_overview():
    """Test APP_OVERVIEW constant."""
    assert "aiml_dash" in APP_OVERVIEW
    assert "predictive analytics" in APP_OVERVIEW.lower()
    assert isinstance(APP_OVERVIEW, str)


def test_github_url():
    """Test GITHUB_URL constant."""
    assert GITHUB_URL == "https://github.com/jeffmaxey/aiml-dash"
    assert GITHUB_URL.startswith("https://")
    assert isinstance(GITHUB_URL, str)
