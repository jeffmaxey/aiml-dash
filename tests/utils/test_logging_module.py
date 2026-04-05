"""Tests for aiml_dash.utils.logging module.

Covers RequestContextFilter, JsonFormatter, generate_request_id,
set_request_id, clear_request_id, get_logger, and setup_logging.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiml_dash.utils.logging import (
    JsonFormatter,
    RequestContextFilter,
    _build_formatter,
    clear_request_id,
    generate_request_id,
    get_logger,
    set_request_id,
    setup_logging,
)


# ---------------------------------------------------------------------------
# generate_request_id
# ---------------------------------------------------------------------------


class TestGenerateRequestId:
    """Tests for generate_request_id()."""

    def test_returns_string(self):
        """generate_request_id() should return a string."""
        assert isinstance(generate_request_id(), str)

    def test_non_empty(self):
        """generate_request_id() should return a non-empty string."""
        assert len(generate_request_id()) > 0

    def test_unique_each_call(self):
        """Each call should return a different id."""
        ids = {generate_request_id() for _ in range(10)}
        assert len(ids) == 10

    def test_hex_characters_only(self):
        """Request id should consist only of hex characters."""
        rid = generate_request_id()
        assert all(c in "0123456789abcdef" for c in rid)


# ---------------------------------------------------------------------------
# set_request_id / clear_request_id
# ---------------------------------------------------------------------------


class TestRequestIdContext:
    """Tests for set_request_id() and clear_request_id()."""

    def test_set_returns_the_id(self):
        """set_request_id() should return the id that was set."""
        rid = set_request_id("my-id")
        assert rid == "my-id"

    def test_set_with_none_generates_id(self):
        """set_request_id(None) should auto-generate and return an id."""
        rid = set_request_id(None)
        assert isinstance(rid, str)
        assert len(rid) > 0

    def test_clear_resets_to_dash(self):
        """clear_request_id() should reset the context var to '-'."""
        from aiml_dash.utils.logging import _request_id

        set_request_id("some-id")
        clear_request_id()
        assert _request_id.get() == "-"


# ---------------------------------------------------------------------------
# RequestContextFilter
# ---------------------------------------------------------------------------


class TestRequestContextFilter:
    """Tests for RequestContextFilter."""

    def _make_record(self, msg: str = "test") -> logging.LogRecord:
        return logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None,
        )

    def test_filter_returns_true(self):
        """filter() should always return True (allow the record)."""
        flt = RequestContextFilter()
        record = self._make_record()
        assert flt.filter(record) is True

    def test_filter_attaches_request_id(self):
        """filter() should add request_id attribute to the record."""
        flt = RequestContextFilter()
        set_request_id("abc123")
        record = self._make_record()
        flt.filter(record)
        assert record.request_id == "abc123"

    def test_filter_uses_dash_when_not_set(self):
        """filter() should attach '-' when no request id is active."""
        flt = RequestContextFilter()
        clear_request_id()
        record = self._make_record()
        flt.filter(record)
        assert record.request_id == "-"


# ---------------------------------------------------------------------------
# JsonFormatter
# ---------------------------------------------------------------------------


class TestJsonFormatter:
    """Tests for JsonFormatter."""

    def _make_record(
        self, msg: str = "hello", level: int = logging.INFO
    ) -> logging.LogRecord:
        record = logging.LogRecord(
            name="mylogger", level=level, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None,
        )
        record.request_id = "req-1"
        return record

    def test_format_returns_valid_json(self):
        """format() should return a valid JSON string."""
        fmt = JsonFormatter()
        record = self._make_record("test message")
        output = fmt.format(record)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_format_contains_level(self):
        """Formatted JSON should include the log level."""
        fmt = JsonFormatter()
        record = self._make_record("msg", logging.WARNING)
        data = json.loads(fmt.format(record))
        assert data["level"] == "WARNING"

    def test_format_contains_message(self):
        """Formatted JSON should include the log message."""
        fmt = JsonFormatter()
        record = self._make_record("unique-message-xyz")
        data = json.loads(fmt.format(record))
        assert data["message"] == "unique-message-xyz"

    def test_format_contains_logger_name(self):
        """Formatted JSON should include the logger name."""
        fmt = JsonFormatter()
        record = self._make_record()
        data = json.loads(fmt.format(record))
        assert data["logger"] == "mylogger"

    def test_format_contains_timestamp(self):
        """Formatted JSON should include a timestamp field."""
        fmt = JsonFormatter()
        record = self._make_record()
        data = json.loads(fmt.format(record))
        assert "timestamp" in data

    def test_format_contains_request_id(self):
        """Formatted JSON should include the request_id field."""
        fmt = JsonFormatter()
        record = self._make_record()
        data = json.loads(fmt.format(record))
        assert data["request_id"] == "req-1"

    def test_format_includes_exception_info(self):
        """Formatted JSON should include exception info when present."""
        fmt = JsonFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="t", level=logging.ERROR, pathname="", lineno=0,
            msg="error", args=(), exc_info=exc_info,
        )
        record.request_id = "-"
        data = json.loads(fmt.format(record))
        assert "exception" in data
        assert "ValueError" in data["exception"]


# ---------------------------------------------------------------------------
# _build_formatter
# ---------------------------------------------------------------------------


class TestBuildFormatter:
    """Tests for _build_formatter()."""

    def _settings(self, log_json: bool = False, log_format: str = "%(message)s"):
        settings = MagicMock()
        settings.log_json = log_json
        settings.log_format = log_format
        return settings

    def test_returns_json_formatter_when_log_json_true(self):
        """_build_formatter() should return a JsonFormatter when log_json=True."""
        settings = self._settings(log_json=True)
        fmt = _build_formatter(settings, None)
        assert isinstance(fmt, JsonFormatter)

    def test_returns_standard_formatter_when_log_json_false(self):
        """_build_formatter() should return a standard Formatter when log_json=False."""
        settings = self._settings(log_json=False)
        fmt = _build_formatter(settings, None)
        assert isinstance(fmt, logging.Formatter)

    def test_uses_provided_format_string(self):
        """_build_formatter() should use the supplied format_string."""
        settings = self._settings(log_json=False, log_format="default")
        fmt = _build_formatter(settings, "%(levelname)s %(message)s")
        # The formatter's _fmt should reflect the custom string
        assert "%(levelname)s" in fmt._fmt

    def test_falls_back_to_settings_format(self):
        """_build_formatter() should fall back to settings.log_format when no string given."""
        settings = self._settings(log_json=False, log_format="%(name)s %(message)s")
        fmt = _build_formatter(settings, None)
        assert "%(name)s" in fmt._fmt


# ---------------------------------------------------------------------------
# get_logger
# ---------------------------------------------------------------------------


class TestGetLogger:
    """Tests for get_logger()."""

    def test_returns_logger_instance(self):
        """get_logger() should return a logging.Logger."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_logger_name_matches(self):
        """Logger name should match the requested name."""
        logger = get_logger("my.custom.logger")
        assert logger.name == "my.custom.logger"

    def test_same_logger_returned_for_same_name(self):
        """get_logger() with the same name should return the same instance."""
        l1 = get_logger("shared.logger")
        l2 = get_logger("shared.logger")
        assert l1 is l2


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


class TestSetupLogging:
    """Tests for setup_logging()."""

    def test_sets_root_logger_level(self):
        """setup_logging() should configure the root logger level."""
        root = logging.getLogger()
        setup_logging(level="DEBUG")
        assert root.level == logging.DEBUG
        # Restore to avoid polluting other tests
        setup_logging(level="WARNING")

    def test_adds_stream_handler(self):
        """setup_logging() should add at least one StreamHandler to the root logger."""
        setup_logging(level="INFO")
        root = logging.getLogger()
        stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1

    def test_clears_existing_handlers(self):
        """setup_logging() should clear pre-existing handlers before adding new ones."""
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        initial_count = len(root.handlers)
        setup_logging(level="INFO")
        # After setup, handler count should be exactly 1 (just console)
        assert len(root.handlers) == 1

    def test_adds_file_handler_when_log_file_given(self, tmp_path):
        """setup_logging() with a log_file argument should add a FileHandler."""
        log_file = tmp_path / "app.log"
        setup_logging(level="INFO", log_file=log_file)
        root = logging.getLogger()
        file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1
        # Clean up
        for h in file_handlers:
            h.close()
            root.removeHandler(h)

    def test_creates_log_directory_if_missing(self, tmp_path):
        """setup_logging() should create parent directories for the log file."""
        log_file = tmp_path / "nested" / "dir" / "app.log"
        setup_logging(level="INFO", log_file=log_file)
        assert log_file.parent.exists()
        # Clean up
        root = logging.getLogger()
        for h in list(root.handlers):
            if isinstance(h, logging.FileHandler):
                h.close()
                root.removeHandler(h)
