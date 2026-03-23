"""Structured logging helpers for AIML Dash."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from aiml_dash.utils.config import AppSettings, get_settings

_request_id: ContextVar[str] = ContextVar("request_id", default="-")


class RequestContextFilter(logging.Filter):
    """Attach request-scoped metadata to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request metadata to the log record."""
        record.request_id = _request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a record to JSON."""
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def generate_request_id() -> str:
    """Generate a request correlation id."""
    return uuid4().hex


def set_request_id(request_id: str | None = None) -> str:
    """Set and return the active request id."""
    value = request_id or generate_request_id()
    _request_id.set(value)
    return value


def clear_request_id() -> None:
    """Clear the active request id."""
    _request_id.set("-")


def _build_formatter(settings: AppSettings, format_string: str | None) -> logging.Formatter:
    """Build the configured formatter."""
    if settings.log_json:
        return JsonFormatter()
    return logging.Formatter(format_string or settings.log_format)


def setup_logging(
    level: str | None = None,
    log_file: Path | None = None,
    format_string: str | None = None,
    settings: AppSettings | None = None,
) -> None:
    """Configure application logging."""
    resolved_settings = settings or get_settings()
    resolved_level = level or resolved_settings.log_level
    formatter = _build_formatter(resolved_settings, format_string)
    context_filter = RequestContextFilter()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, resolved_level))
    root_logger.handlers.clear()
    root_logger.filters.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, resolved_level))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, resolved_level))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""
    return logging.getLogger(name)

