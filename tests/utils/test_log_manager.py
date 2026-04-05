"""Tests for aiml_dash.utils.log_manager module.

Covers LogEntry construction, LogManager CRUD operations, filtering, counts,
text formatting, and the singleton contract.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from aiml_dash.utils.log_manager import LogEntry, LogManager, log_manager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fresh_manager() -> LogManager:
    """Return a LogManager with its logs cleared."""
    mgr = LogManager()
    mgr.clear_logs()
    return mgr


# ---------------------------------------------------------------------------
# LogEntry
# ---------------------------------------------------------------------------


class TestLogEntry:
    """Tests for the LogEntry dataclass."""

    def test_level_stored_lowercase(self):
        """Level should always be stored in lower case."""
        entry = LogEntry("WARNING", "msg", "core")
        assert entry.level == "warning"

    def test_source_stored_lowercase(self):
        """Source should always be stored in lower case."""
        entry = LogEntry("info", "msg", "PLUGINS")
        assert entry.source == "plugins"

    def test_message_preserved(self):
        """Message text should be stored unchanged."""
        entry = LogEntry("info", "Hello world", "core")
        assert entry.message == "Hello world"

    def test_timestamp_defaults_to_now(self):
        """Timestamp should default to approximately now."""
        before = datetime.now()
        entry = LogEntry("debug", "msg", "core")
        after = datetime.now()
        assert before <= entry.timestamp <= after

    def test_custom_timestamp(self):
        """A custom timestamp should be stored as provided."""
        ts = datetime(2024, 1, 15, 10, 30, 0)
        entry = LogEntry("info", "msg", "data", timestamp=ts)
        assert entry.timestamp == ts

    def test_to_dict_keys(self):
        """to_dict() should return all required keys."""
        entry = LogEntry("error", "something went wrong", "callbacks")
        d = entry.to_dict()
        assert set(d.keys()) == {"level", "message", "source", "timestamp"}

    def test_to_dict_values(self):
        """to_dict() values should match the entry attributes."""
        ts = datetime(2025, 6, 1, 12, 0, 0)
        entry = LogEntry("info", "started", "core", timestamp=ts)
        d = entry.to_dict()
        assert d["level"] == "info"
        assert d["message"] == "started"
        assert d["source"] == "core"
        assert d["timestamp"] == "2025-06-01 12:00:00"

    def test_to_dict_timestamp_format(self):
        """to_dict() timestamp should use YYYY-MM-DD HH:MM:SS format."""
        ts = datetime(2024, 3, 5, 8, 7, 6)
        entry = LogEntry("debug", "x", "data", timestamp=ts)
        d = entry.to_dict()
        assert d["timestamp"] == "2024-03-05 08:07:06"


# ---------------------------------------------------------------------------
# LogManager — singleton
# ---------------------------------------------------------------------------


class TestLogManagerSingleton:
    """Tests for the LogManager singleton pattern."""

    def test_same_instance_returned(self):
        """LogManager() should always return the same object."""
        m1 = LogManager()
        m2 = LogManager()
        assert m1 is m2

    def test_module_level_instance(self):
        """log_manager should be a LogManager instance."""
        assert isinstance(log_manager, LogManager)


# ---------------------------------------------------------------------------
# LogManager — add_log / clear_logs
# ---------------------------------------------------------------------------


class TestLogManagerAddAndClear:
    """Tests for add_log() and clear_logs()."""

    def test_add_log_increases_count(self):
        """Adding a log should increase the total count by one."""
        mgr = fresh_manager()
        mgr.add_log("info", "test message", "core")
        counts = mgr.get_log_counts()
        assert counts["total"] == 1

    def test_add_multiple_logs(self):
        """Multiple add_log calls should accumulate entries."""
        mgr = fresh_manager()
        mgr.add_log("info", "msg1", "core")
        mgr.add_log("debug", "msg2", "data")
        mgr.add_log("error", "msg3", "plugins")
        counts = mgr.get_log_counts()
        assert counts["total"] == 3

    def test_clear_logs_empties_queue(self):
        """clear_logs() should remove all log entries."""
        mgr = fresh_manager()
        mgr.add_log("info", "to be cleared", "core")
        mgr.clear_logs()
        counts = mgr.get_log_counts()
        assert counts["total"] == 0

    def test_clear_logs_returns_none(self):
        """clear_logs() should return None."""
        mgr = fresh_manager()
        result = mgr.clear_logs()
        assert result is None


# ---------------------------------------------------------------------------
# LogManager — get_logs
# ---------------------------------------------------------------------------


class TestLogManagerGetLogs:
    """Tests for get_logs() with and without filters."""

    def test_get_logs_returns_list(self):
        """get_logs() should return a list."""
        mgr = fresh_manager()
        result = mgr.get_logs()
        assert isinstance(result, list)

    def test_get_logs_entries_are_dicts(self):
        """Each entry returned by get_logs() should be a dict."""
        mgr = fresh_manager()
        mgr.add_log("info", "hi", "core")
        result = mgr.get_logs()
        for entry in result:
            assert isinstance(entry, dict)

    def test_get_logs_all_returns_all(self):
        """get_logs() with level_filter='all' should return every entry."""
        mgr = fresh_manager()
        mgr.add_log("info", "a", "core")
        mgr.add_log("error", "b", "data")
        result = mgr.get_logs(level_filter="all")
        assert len(result) == 2

    def test_get_logs_level_filter(self):
        """get_logs() should return only entries matching level_filter."""
        mgr = fresh_manager()
        mgr.add_log("info", "info msg", "core")
        mgr.add_log("error", "error msg", "core")
        result = mgr.get_logs(level_filter="error")
        assert all(e["level"] == "error" for e in result)
        assert len(result) == 1

    def test_get_logs_source_filter(self):
        """get_logs() should return only entries matching source_filter."""
        mgr = fresh_manager()
        mgr.add_log("info", "core msg", "core")
        mgr.add_log("info", "data msg", "data")
        result = mgr.get_logs(source_filter="data")
        assert all(e["source"] == "data" for e in result)
        assert len(result) == 1

    def test_get_logs_combined_filter(self):
        """get_logs() should honour both level_filter and source_filter."""
        mgr = fresh_manager()
        mgr.add_log("warning", "w-core", "core")
        mgr.add_log("warning", "w-data", "data")
        mgr.add_log("info", "i-core", "core")
        result = mgr.get_logs(level_filter="warning", source_filter="core")
        assert len(result) == 1
        assert result[0]["message"] == "w-core"

    def test_get_logs_limit(self):
        """get_logs() should respect the limit parameter."""
        mgr = fresh_manager()
        for i in range(5):
            mgr.add_log("debug", f"msg{i}", "core")
        result = mgr.get_logs(limit=3)
        assert len(result) == 3

    def test_get_logs_returns_most_recent_when_limited(self):
        """get_logs(limit=N) should return the N most recent entries."""
        mgr = fresh_manager()
        for i in range(5):
            mgr.add_log("debug", f"msg{i}", "core")
        result = mgr.get_logs(limit=2)
        # Reversed order means most recent are first
        messages = [e["message"] for e in result]
        assert "msg4" in messages
        assert "msg3" in messages

    def test_get_logs_level_filter_case_insensitive(self):
        """level_filter should be case-insensitive."""
        mgr = fresh_manager()
        mgr.add_log("INFO", "msg", "core")
        result = mgr.get_logs(level_filter="INFO")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# LogManager — get_log_counts
# ---------------------------------------------------------------------------


class TestLogManagerGetLogCounts:
    """Tests for get_log_counts()."""

    def test_returns_dict_with_expected_keys(self):
        """get_log_counts() should return a dict with level keys and 'total'."""
        mgr = fresh_manager()
        counts = mgr.get_log_counts()
        assert "debug" in counts
        assert "info" in counts
        assert "warning" in counts
        assert "error" in counts
        assert "total" in counts

    def test_counts_are_accurate(self):
        """Count values should match the number of logged entries per level."""
        mgr = fresh_manager()
        mgr.add_log("info", "a", "core")
        mgr.add_log("info", "b", "core")
        mgr.add_log("error", "c", "core")
        counts = mgr.get_log_counts()
        assert counts["info"] == 2
        assert counts["error"] == 1
        assert counts["debug"] == 0
        assert counts["total"] == 3


# ---------------------------------------------------------------------------
# LogManager — get_logs_as_text
# ---------------------------------------------------------------------------


class TestLogManagerGetLogsAsText:
    """Tests for get_logs_as_text()."""

    def test_returns_string(self):
        """get_logs_as_text() should return a string."""
        mgr = fresh_manager()
        result = mgr.get_logs_as_text()
        assert isinstance(result, str)

    def test_empty_when_no_logs(self):
        """get_logs_as_text() should return an empty string when there are no logs."""
        mgr = fresh_manager()
        result = mgr.get_logs_as_text()
        assert result == ""

    def test_contains_message(self):
        """get_logs_as_text() output should contain logged messages."""
        mgr = fresh_manager()
        mgr.add_log("info", "unique-test-message", "core")
        result = mgr.get_logs_as_text()
        assert "unique-test-message" in result

    def test_contains_level(self):
        """get_logs_as_text() output should include the log level in uppercase."""
        mgr = fresh_manager()
        mgr.add_log("warning", "watch out", "core")
        result = mgr.get_logs_as_text()
        assert "WARNING" in result

    def test_contains_source(self):
        """get_logs_as_text() output should include the source in uppercase."""
        mgr = fresh_manager()
        mgr.add_log("debug", "debug info", "plugins")
        result = mgr.get_logs_as_text()
        assert "PLUGINS" in result

    def test_multiple_entries_each_on_own_line(self):
        """Each log entry should appear on its own line."""
        mgr = fresh_manager()
        mgr.add_log("info", "first", "core")
        mgr.add_log("info", "second", "core")
        lines = mgr.get_logs_as_text().splitlines()
        assert len(lines) == 2
