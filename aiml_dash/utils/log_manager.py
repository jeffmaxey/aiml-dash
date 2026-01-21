"""Simple in-memory log manager for AIML Dash.

This module provides a lightweight logging system that stores log entries
in memory for display in the Logs page.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Literal


class LogEntry:
    """Represents a single log entry."""

    def __init__(
        self,
        level: str,
        message: str,
        source: str,
        timestamp: datetime | None = None,
    ):
        """Initialize a log entry.
        
        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            source: Source of the log (core, plugins, data, callbacks)
            timestamp: Timestamp of the log entry
        """
        self.level = level.lower()
        self.message = message
        self.source = source.lower()
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, str]:
        """Convert log entry to dictionary."""
        return {
            "level": self.level,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class LogManager:
    """Manages application logs in memory."""

    _instance = None
    _logs: deque[LogEntry]
    _max_logs: int

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logs = deque(maxlen=1000)  # Keep last 1000 logs
            cls._instance._max_logs = 1000
        return cls._instance

    def add_log(
        self,
        level: Literal["debug", "info", "warning", "error"],
        message: str,
        source: Literal["core", "plugins", "data", "callbacks"] = "core",
    ) -> None:
        """Add a log entry.
        
        Args:
            level: Log level
            message: Log message
            source: Source of the log
        """
        entry = LogEntry(level, message, source)
        self._logs.append(entry)

    def get_logs(
        self,
        level_filter: str = "all",
        source_filter: str = "all",
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Get log entries with optional filtering.
        
        Args:
            level_filter: Filter by log level (all, debug, info, warning, error)
            source_filter: Filter by source (all, core, plugins, data, callbacks)
            limit: Maximum number of logs to return
            
        Returns:
            List of log entry dictionaries
        """
        logs = list(self._logs)
        
        # Apply filters
        if level_filter != "all":
            logs = [log for log in logs if log.level == level_filter.lower()]
        
        if source_filter != "all":
            logs = [log for log in logs if log.source == source_filter.lower()]
        
        # Apply limit
        if limit:
            logs = logs[-limit:]
        
        return [log.to_dict() for log in reversed(logs)]

    def get_log_counts(self) -> dict[str, int]:
        """Get counts of logs by level.
        
        Returns:
            Dictionary with counts for each log level
        """
        counts = {"debug": 0, "info": 0, "warning": 0, "error": 0, "total": len(self._logs)}
        
        for log in self._logs:
            if log.level in counts:
                counts[log.level] += 1
        
        return counts

    def clear_logs(self) -> None:
        """Clear all log entries."""
        self._logs.clear()

    def get_logs_as_text(self) -> str:
        """Get all logs as formatted text.
        
        Returns:
            Formatted string with all log entries
        """
        lines = []
        for log in self._logs:
            lines.append(
                f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{log.level.upper():8s} [{log.source.upper():10s}] "
                f"{log.message}"
            )
        return "\n".join(lines)


# Global instance
log_manager = LogManager()


# Add some initial sample logs
log_manager.add_log("info", "AIML Dash application started", "core")
log_manager.add_log("info", "Loading plugins from plugins directory", "plugins")
log_manager.add_log("debug", "Initializing data manager", "data")
log_manager.add_log("info", "Core plugin registered successfully", "plugins")
log_manager.add_log("info", "Data plugin registered successfully", "plugins")
log_manager.add_log("info", "Basics plugin registered successfully", "plugins")
log_manager.add_log("info", "All plugins loaded successfully", "plugins")
log_manager.add_log("info", "Application ready at http://127.0.0.1:8050", "core")
