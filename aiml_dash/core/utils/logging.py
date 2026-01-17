"""
Logging Configuration
=====================

Centralized logging setup for the AIML Dash application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from aiml_dash.utils.settings import app_settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> None:
    """
    Configure application logging.

    Parameters
    ----------
    level : str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        Defaults to app_settings.LOG_LEVEL
    log_file : Path, optional
        Path to log file. If None, logs only to console
    format_string : str, optional
        Custom log format string. Defaults to app_settings.LOG_FORMAT
    """
    log_level = level or app_settings.LOG_LEVEL
    log_format = format_string or app_settings.LOG_FORMAT

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configure third-party loggers to reduce noise
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Parameters
    ----------
    name : str
        Logger name (typically __name__)

    Returns
    -------
    logging.Logger
        Logger instance
    """
    return logging.getLogger(name)
