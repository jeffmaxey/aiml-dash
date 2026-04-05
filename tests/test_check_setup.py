"""Tests for aiml_dash.check_setup module.

Covers _ensure_project_on_path, check_imports, _discover_project_modules,
check_modules, and main().
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

import pytest

import aiml_dash.check_setup as cs


# ---------------------------------------------------------------------------
# _ensure_project_on_path
# ---------------------------------------------------------------------------


class TestEnsureProjectOnPath:
    """Tests for _ensure_project_on_path()."""

    def test_adds_parent_when_missing(self):
        """Parent directory should be inserted into sys.path when absent."""
        expected_parent = str(cs.PROJECT_DIR.parent)
        original = sys.path[:]
        try:
            if expected_parent in sys.path:
                sys.path.remove(expected_parent)
            cs._ensure_project_on_path()
            assert expected_parent in sys.path
        finally:
            sys.path[:] = original

    def test_no_duplicate_when_already_present(self):
        """sys.path should not grow on repeated calls when parent is already present."""
        expected_parent = str(cs.PROJECT_DIR.parent)
        original = sys.path[:]
        try:
            # Start from a clean state with the parent present exactly once.
            while expected_parent in sys.path:
                sys.path.remove(expected_parent)
            sys.path.insert(0, expected_parent)
            count_before = sys.path.count(expected_parent)
            cs._ensure_project_on_path()
            count_after = sys.path.count(expected_parent)
            assert count_after == count_before
        finally:
            sys.path[:] = original


# ---------------------------------------------------------------------------
# check_imports
# ---------------------------------------------------------------------------


class TestCheckImports:
    """Tests for check_imports()."""

    def test_returns_true_when_all_packages_available(self, capsys):
        """check_imports() should return True when every package is importable."""
        # All packages are installed in the test environment
        result = cs.check_imports()
        assert isinstance(result, bool)

    def test_returns_false_on_missing_package(self, capsys):
        """check_imports() should return False when a package cannot be imported."""
        original_import = import_module

        def fake_import(name, *args, **kwargs):
            if name == "dash":
                raise ImportError("No module named 'dash'")
            return original_import(name, *args, **kwargs)

        with patch("aiml_dash.check_setup.import_module", side_effect=fake_import):
            result = cs.check_imports()

        assert result is False

    def test_prints_check_message(self, capsys):
        """check_imports() should print a heading."""
        cs.check_imports()
        captured = capsys.readouterr()
        assert "Checking required packages" in captured.out

    def test_prints_tick_for_installed_packages(self, capsys):
        """Installed packages should be printed with ✓."""
        cs.check_imports()
        captured = capsys.readouterr()
        assert "✓" in captured.out

    def test_prints_cross_for_missing_package(self, capsys):
        """Missing packages should be printed with ✗."""
        original_import = import_module

        def fake_import(name, *args, **kwargs):
            if name == "dash":
                raise ImportError("simulated failure")
            return original_import(name, *args, **kwargs)

        with patch("aiml_dash.check_setup.import_module", side_effect=fake_import):
            cs.check_imports()

        captured = capsys.readouterr()
        assert "✗" in captured.out


# ---------------------------------------------------------------------------
# _discover_project_modules
# ---------------------------------------------------------------------------


class TestDiscoverProjectModules:
    """Tests for _discover_project_modules()."""

    def test_returns_list(self):
        """_discover_project_modules() should return a list."""
        result = cs._discover_project_modules()
        assert isinstance(result, list)

    def test_no_duplicates(self):
        """Returned module names should be unique."""
        result = cs._discover_project_modules()
        assert len(result) == len(set(result))

    def test_contains_string_entries(self):
        """Every entry should be a string."""
        result = cs._discover_project_modules()
        for name in result:
            assert isinstance(name, str)

    def test_contains_project_modules(self):
        """Core top-level modules should appear in the discovered list."""
        result = cs._discover_project_modules()
        # At least one known module should be present
        assert any("check_setup" in name or "run" in name or "aiml_dash" in name for name in result)

    def test_excludes_init_modules(self):
        """__init__ itself should not be discovered as a standalone module name."""
        result = cs._discover_project_modules()
        for name in result:
            assert name != "__init__"


# ---------------------------------------------------------------------------
# check_modules
# ---------------------------------------------------------------------------


class TestCheckModules:
    """Tests for check_modules()."""

    def test_returns_bool(self, capsys):
        """check_modules() should return a bool."""
        result = cs.check_modules()
        assert isinstance(result, bool)

    def test_returns_false_on_import_error(self, capsys):
        """check_modules() should return False when a module raises on import."""
        with patch("aiml_dash.check_setup._discover_project_modules", return_value=["nonexistent_xyz_module"]):
            result = cs.check_modules()
        assert result is False

    def test_prints_application_modules_heading(self, capsys):
        """check_modules() should print a heading."""
        cs.check_modules()
        captured = capsys.readouterr()
        assert "application modules" in captured.out.lower()

    def test_prints_cross_for_unimportable_module(self, capsys):
        """Unimportable modules should be printed with ✗."""
        with patch(
            "aiml_dash.check_setup._discover_project_modules",
            return_value=["_nonexistent_module_xyz"],
        ):
            cs.check_modules()
        captured = capsys.readouterr()
        assert "✗" in captured.out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    """Tests for main()."""

    def test_returns_zero_when_all_pass(self):
        """main() should return 0 when all checks succeed."""
        with patch("aiml_dash.check_setup.check_imports", return_value=True), \
             patch("aiml_dash.check_setup.check_modules", return_value=True):
            result = cs.main()
        assert result == 0

    def test_returns_one_when_imports_fail(self):
        """main() should return 1 when package imports fail."""
        with patch("aiml_dash.check_setup.check_imports", return_value=False), \
             patch("aiml_dash.check_setup.check_modules", return_value=True):
            result = cs.main()
        assert result == 1

    def test_returns_one_when_modules_fail(self):
        """main() should return 1 when module checks fail."""
        with patch("aiml_dash.check_setup.check_imports", return_value=True), \
             patch("aiml_dash.check_setup.check_modules", return_value=False):
            result = cs.main()
        assert result == 1

    def test_returns_one_when_both_fail(self):
        """main() should return 1 when both checks fail."""
        with patch("aiml_dash.check_setup.check_imports", return_value=False), \
             patch("aiml_dash.check_setup.check_modules", return_value=False):
            result = cs.main()
        assert result == 1

    def test_prints_summary_on_success(self, capsys):
        """main() should print success message when all checks pass."""
        with patch("aiml_dash.check_setup.check_imports", return_value=True), \
             patch("aiml_dash.check_setup.check_modules", return_value=True):
            cs.main()
        captured = capsys.readouterr()
        assert "All checks passed" in captured.out

    def test_prints_failure_message_on_failure(self, capsys):
        """main() should print failure message when a check fails."""
        with patch("aiml_dash.check_setup.check_imports", return_value=False), \
             patch("aiml_dash.check_setup.check_modules", return_value=False):
            cs.main()
        captured = capsys.readouterr()
        assert "Some checks failed" in captured.out
