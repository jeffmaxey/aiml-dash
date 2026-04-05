"""Tests for aiml_dash.components.ace_editor module.

Covers get_code_editor() with both the dash_ace-available and fallback paths.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from dash import dcc

import aiml_dash.components.ace_editor as ace_mod
from aiml_dash.components.ace_editor import get_code_editor


class TestGetCodeEditorFallback:
    """Tests for get_code_editor() when dash_ace is NOT available."""

    def test_returns_textarea_when_no_ace(self):
        """get_code_editor() should return a dcc.Textarea when dash_ace is absent."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("my-editor")
        assert isinstance(component, dcc.Textarea)

    def test_textarea_id_matches(self):
        """Textarea id should match the requested editor_id."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("test-id")
        assert component.id == "test-id"

    def test_textarea_value_default_empty(self):
        """Textarea value should default to an empty string."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("e1")
        assert component.value == ""

    def test_textarea_custom_value(self):
        """Textarea value should reflect the provided value argument."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("e2", value="print('hello')")
        assert component.value == "print('hello')"

    def test_textarea_height_in_style(self):
        """Textarea style should include the requested height."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("e3", height="500px")
        assert component.style["height"] == "500px"

    def test_textarea_width_is_full(self):
        """Textarea style should set width to 100%."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("e4")
        assert component.style["width"] == "100%"

    def test_textarea_spell_check_disabled(self):
        """Textarea should have spellCheck disabled."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            component = get_code_editor("e5")
        assert component.spellCheck is False


class TestGetCodeEditorWithAce:
    """Tests for get_code_editor() when dash_ace IS available."""

    def _make_ace_stub(self):
        """Return a simple namespace that mimics dash_ace.Ace."""
        import types

        class FakeAce:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        module = types.ModuleType("dash_ace")
        module.Ace = FakeAce
        return module

    def test_uses_ace_when_available(self):
        """get_code_editor() should use dash_ace.Ace when _HAS_ACE is True."""
        ace_module = self._make_ace_stub()
        with patch.object(ace_mod, "_HAS_ACE", True), \
             patch.dict("sys.modules", {"dash_ace": ace_module}), \
             patch("aiml_dash.components.ace_editor.dash_ace", ace_module, create=True):
            component = get_code_editor("ace-id", value="x = 1")
        assert hasattr(component, "id")
        assert component.id == "ace-id"

    def test_ace_value_passed_through(self):
        """Ace component value should match the provided value."""
        ace_module = self._make_ace_stub()
        with patch.object(ace_mod, "_HAS_ACE", True), \
             patch.dict("sys.modules", {"dash_ace": ace_module}), \
             patch("aiml_dash.components.ace_editor.dash_ace", ace_module, create=True):
            component = get_code_editor("ace-id2", value="y = 2")
        assert component.value == "y = 2"

    def test_ace_mode_passed_through(self):
        """Ace component mode should reflect the mode argument."""
        ace_module = self._make_ace_stub()
        with patch.object(ace_mod, "_HAS_ACE", True), \
             patch.dict("sys.modules", {"dash_ace": ace_module}), \
             patch("aiml_dash.components.ace_editor.dash_ace", ace_module, create=True):
            component = get_code_editor("ace-id3", mode="python")
        assert component.mode == "python"

    def test_ace_theme_passed_through(self):
        """Ace component theme should reflect the theme argument."""
        ace_module = self._make_ace_stub()
        with patch.object(ace_mod, "_HAS_ACE", True), \
             patch.dict("sys.modules", {"dash_ace": ace_module}), \
             patch("aiml_dash.components.ace_editor.dash_ace", ace_module, create=True):
            component = get_code_editor("ace-id4", theme="monokai")
        assert component.theme == "monokai"


class TestGetCodeEditorDefaults:
    """Tests for default argument values."""

    def test_default_mode_is_r(self):
        """Default mode should be 'r'."""
        with patch.object(ace_mod, "_HAS_ACE", False):
            # inspect signature rather than rely on the component attribute
            import inspect
            sig = inspect.signature(get_code_editor)
            assert sig.parameters["mode"].default == "r"

    def test_default_theme_is_github(self):
        """Default theme should be 'github'."""
        import inspect
        sig = inspect.signature(get_code_editor)
        assert sig.parameters["theme"].default == "github"

    def test_default_height_is_300px(self):
        """Default height should be '300px'."""
        import inspect
        sig = inspect.signature(get_code_editor)
        assert sig.parameters["height"].default == "300px"
