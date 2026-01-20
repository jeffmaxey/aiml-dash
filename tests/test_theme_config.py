"""
Tests for theme configuration.
"""

from aiml_dash.theme_config import THEME_CONFIG


def test_theme_config_exists():
    """Test that THEME_CONFIG is defined."""
    assert THEME_CONFIG is not None


def test_theme_config_structure():
    """Test that THEME_CONFIG has the expected structure."""
    assert isinstance(THEME_CONFIG, dict)
    assert "fontFamily" in THEME_CONFIG
    assert "primaryColor" in THEME_CONFIG
    assert "components" in THEME_CONFIG


def test_theme_config_font_family():
    """Test that font family is set correctly."""
    assert THEME_CONFIG["fontFamily"] == "'Inter', sans-serif"


def test_theme_config_primary_color():
    """Test that primary color is set correctly."""
    assert THEME_CONFIG["primaryColor"] == "blue"


def test_theme_config_components():
    """Test that component styles are configured."""
    components = THEME_CONFIG["components"]
    assert isinstance(components, dict)
    assert "Button" in components
    assert "Alert" in components
    assert "AvatarGroup" in components


def test_theme_config_button_styles():
    """Test Button component default props."""
    button_config = THEME_CONFIG["components"]["Button"]
    assert "defaultProps" in button_config
    assert button_config["defaultProps"]["fw"] == 400


def test_theme_config_alert_styles():
    """Test Alert component styles."""
    alert_config = THEME_CONFIG["components"]["Alert"]
    assert "styles" in alert_config
    assert "title" in alert_config["styles"]
    assert alert_config["styles"]["title"]["fontWeight"] == 500


def test_theme_config_avatar_group_styles():
    """Test AvatarGroup component styles."""
    avatar_group_config = THEME_CONFIG["components"]["AvatarGroup"]
    assert "styles" in avatar_group_config
    assert "truncated" in avatar_group_config["styles"]
    assert avatar_group_config["styles"]["truncated"]["fontWeight"] == 500
