"""Tests for aiml_dash.plugins.hot_reload module.

Covers PluginReloadHandler, PluginHotReloader, reload_plugin_module,
and create_hot_reloader — without starting actual filesystem watchers.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, call, patch

import pytest

import aiml_dash.plugins.hot_reload as hr_mod
from aiml_dash.plugins.hot_reload import (
    WATCHDOG_AVAILABLE,
    PluginHotReloader,
    PluginReloadHandler,
    create_hot_reloader,
    reload_plugin_module,
)


# ---------------------------------------------------------------------------
# reload_plugin_module
# ---------------------------------------------------------------------------


class TestReloadPluginModule:
    """Tests for reload_plugin_module()."""

    def test_returns_true_on_success(self):
        """Should return True when the reload succeeds."""
        # aiml_dash.plugins.example_plugin is already imported
        result = reload_plugin_module("example_plugin")
        assert result is True

    def test_returns_false_on_import_error(self):
        """Should return False when importlib.reload raises ImportError."""
        import importlib

        def bad_reload(mod):
            raise ImportError("reload failed")

        with patch.object(importlib, "reload", side_effect=bad_reload):
            result = reload_plugin_module("example_plugin")
        assert result is False

    def test_returns_false_on_attribute_error(self):
        """Should return False when importlib.reload raises AttributeError."""
        import importlib

        with patch.object(importlib, "reload", side_effect=AttributeError("oops")):
            result = reload_plugin_module("example_plugin")
        assert result is False

    def test_handles_unknown_plugin_gracefully(self):
        """Should return True (no modules to reload) for an unknown plugin id."""
        result = reload_plugin_module("totally_nonexistent_plugin_xyz")
        assert result is True

    def test_custom_package_prefix_accepted(self):
        """reload_plugin_module() should accept a custom plugins_package."""
        result = reload_plugin_module(
            "example_plugin",
            plugins_package="aiml_dash.plugins",
        )
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# PluginReloadHandler
# ---------------------------------------------------------------------------


class TestPluginReloadHandler:
    """Tests for PluginReloadHandler."""

    def _handler(self, tmp_path: Path, callback=None):
        cb = callback or MagicMock()
        return PluginReloadHandler(plugins_path=tmp_path, reload_callback=cb), cb

    def _event(self, src_path: str, is_directory: bool = False):
        evt = MagicMock()
        evt.src_path = src_path
        evt.is_directory = is_directory
        return evt

    def test_ignores_directory_events(self, tmp_path):
        """on_modified() should not call the callback for directory events."""
        handler, cb = self._handler(tmp_path)
        evt = self._event(str(tmp_path / "some_plugin"), is_directory=True)
        handler.on_modified(evt)
        cb.assert_not_called()

    def test_ignores_non_python_files(self, tmp_path):
        """on_modified() should not call the callback for non-.py files."""
        handler, cb = self._handler(tmp_path)
        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()
        evt = self._event(str(plugin_dir / "data.csv"))
        handler.on_modified(evt)
        cb.assert_not_called()

    def test_calls_callback_for_python_file(self, tmp_path):
        """on_modified() should invoke the callback for .py files inside plugins_path."""
        handler, cb = self._handler(tmp_path)
        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()
        evt = self._event(str(plugin_dir / "layout.py"))
        handler.on_modified(evt)
        cb.assert_called_once_with("my_plugin")

    def test_debounce_suppresses_rapid_changes(self, tmp_path):
        """Rapid successive changes within debounce_seconds should fire callback once."""
        handler, cb = self._handler(tmp_path)
        plugin_dir = tmp_path / "debounce_plugin"
        plugin_dir.mkdir()
        evt = self._event(str(plugin_dir / "layout.py"))
        handler.on_modified(evt)
        handler.on_modified(evt)
        handler.on_modified(evt)
        cb.assert_called_once()

    def test_callback_fires_again_after_debounce_window(self, tmp_path):
        """Callback should fire again once the debounce window has elapsed."""
        handler, cb = self._handler(tmp_path)
        handler.debounce_seconds = 0.05
        plugin_dir = tmp_path / "slow_plugin"
        plugin_dir.mkdir()
        evt = self._event(str(plugin_dir / "layout.py"))
        handler.on_modified(evt)
        time.sleep(0.1)
        handler.on_modified(evt)
        assert cb.call_count == 2

    def test_callback_exception_does_not_propagate(self, tmp_path):
        """Exceptions from the callback should be swallowed, not propagated."""
        def boom(plugin_id):
            raise RuntimeError("crash")

        handler, _ = self._handler(tmp_path, callback=boom)
        plugin_dir = tmp_path / "crash_plugin"
        plugin_dir.mkdir()
        evt = self._event(str(plugin_dir / "callbacks.py"))
        handler.on_modified(evt)  # should not raise

    def test_file_outside_plugins_path_ignored(self, tmp_path):
        """Files outside plugins_path should not trigger the callback."""
        handler, cb = self._handler(tmp_path)
        outside = Path("/tmp/unrelated_file.py")
        evt = self._event(str(outside))
        handler.on_modified(evt)
        cb.assert_not_called()


# ---------------------------------------------------------------------------
# PluginHotReloader
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestPluginHotReloader:
    """Tests for PluginHotReloader."""

    def _make_reloader(self, tmp_path: Path, callback=None):
        cb = callback or MagicMock()
        with patch("aiml_dash.plugins.hot_reload.Observer") as MockObserver:
            observer_instance = MagicMock()
            MockObserver.return_value = observer_instance
            reloader = PluginHotReloader(plugins_path=tmp_path, reload_callback=cb)
        return reloader, observer_instance, cb

    def test_raises_without_watchdog(self, tmp_path):
        """PluginHotReloader should raise RuntimeError when watchdog is unavailable."""
        with patch.object(hr_mod, "WATCHDOG_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="watchdog"):
                PluginHotReloader(tmp_path, MagicMock())

    def test_start_calls_observer_start(self, tmp_path):
        """start() should call observer.start()."""
        reloader, obs, _ = self._make_reloader(tmp_path)
        reloader.start()
        obs.start.assert_called_once()

    def test_stop_calls_observer_stop_and_join(self, tmp_path):
        """stop() should call observer.stop() then observer.join()."""
        reloader, obs, _ = self._make_reloader(tmp_path)
        reloader.stop()
        obs.stop.assert_called_once()
        obs.join.assert_called_once()

    def test_context_manager_starts_and_stops(self, tmp_path):
        """Context manager should call start() on entry and stop() on exit."""
        reloader, obs, _ = self._make_reloader(tmp_path)
        with patch.object(reloader, "start") as mock_start, \
             patch.object(reloader, "stop") as mock_stop:
            with reloader:
                mock_start.assert_called_once()
            mock_stop.assert_called_once()

    def test_context_manager_stops_on_exception(self, tmp_path):
        """Context manager should still call stop() even if an exception occurs."""
        reloader, obs, _ = self._make_reloader(tmp_path)
        with patch.object(reloader, "start"), \
             patch.object(reloader, "stop") as mock_stop:
            with pytest.raises(ValueError):
                with reloader:
                    raise ValueError("test error")
        mock_stop.assert_called_once()


# ---------------------------------------------------------------------------
# create_hot_reloader
# ---------------------------------------------------------------------------


class TestCreateHotReloader:
    """Tests for create_hot_reloader()."""

    def test_returns_none_when_watchdog_unavailable(self, tmp_path):
        """create_hot_reloader() should return None when watchdog is not available."""
        with patch.object(hr_mod, "WATCHDOG_AVAILABLE", False):
            result = create_hot_reloader(tmp_path)
        assert result is None

    @pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
    def test_returns_hot_reloader_instance(self, tmp_path):
        """create_hot_reloader() should return a PluginHotReloader when available."""
        with patch("aiml_dash.plugins.hot_reload.Observer"):
            result = create_hot_reloader(tmp_path)
        assert isinstance(result, PluginHotReloader)

    @pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
    def test_on_reload_callback_called_on_success(self, tmp_path):
        """The on_reload callback should be invoked after a successful module reload."""
        on_reload = MagicMock()

        with patch("aiml_dash.plugins.hot_reload.Observer"):
            reloader = create_hot_reloader(tmp_path, on_reload=on_reload)

        assert reloader is not None

        # Simulate a successful reload via the internal reload_callback
        with patch("aiml_dash.plugins.hot_reload.reload_plugin_module", return_value=True):
            reloader.reload_callback("my_plugin")

        on_reload.assert_called_once_with("my_plugin")

    @pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
    def test_on_reload_not_called_on_failure(self, tmp_path):
        """The on_reload callback should NOT be invoked when reload fails."""
        on_reload = MagicMock()

        with patch("aiml_dash.plugins.hot_reload.Observer"):
            reloader = create_hot_reloader(tmp_path, on_reload=on_reload)

        assert reloader is not None

        with patch("aiml_dash.plugins.hot_reload.reload_plugin_module", return_value=False):
            reloader.reload_callback("bad_plugin")

        on_reload.assert_not_called()
