"""
Settings and Configuration Management
======================================

Centralized configuration for the AIML Dash application using Pydantic Settings.
Consolidated from settings.py and config.py for unified configuration management.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class AppSettings(BaseSettings):
    """
    Unified settings for the AIML Dash application.

    This class consolidates general application settings, server configuration,
    database settings, security, and logging configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="AIML_DASH_",
    )

    # Application metadata
    APP_NAME: str = Field(default="aiml_dash", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_TITLE: str = Field(default="AIML Dash", description="Application title")
    APP_DESCRIPTION: str = Field(
        default="A Dash application for Predictive Analytics and Machine Learning.",
        description="Application description",
    )
    APP_OVERVIEW : str = Field(
        default="""`aiml_dash` is a Dash application designed to provide interactive insights into predictive analytics and machine learning. This application serves as a platform for users to explore and visualize datasets, perform machine learning experiments and develop insights through an intuitive web interface.""", description="Application overview")
    GITHUB_URL: str = Field(
        default="https://github.com/jeffmaxey/aiml-dash",
        description="GitHub repository URL",
    )

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )

    # Server settings
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8050, description="Server port")

    # Database settings
    DATABASE_URL: str | None = Field(default=None, description="Database connection URL")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # Security settings
    SECRET_KEY: str | None = Field(default=None, description="Secret key for sessions")
    ALLOWED_HOSTS: list[str] = Field(default=["*"], description="Allowed hosts")
    ENABLE_TALISMAN: bool = Field(default=False, description="Enable Flask-Talisman security headers")

    # UI settings
    THEME: str = Field(default="light", description="UI theme")
    PAGE_SIZE: int = Field(default=50, description="Default page size for tables")
    MAX_UPLOAD_SIZE_MB: int = Field(default=100, description="Maximum upload file size in MB")

    # Data management
    MAX_DATASETS: int = Field(default=100, description="Maximum number of datasets to store")
    DATA_CACHE_SIZE: int = Field(default=100, description="Number of datasets to cache")
    AUTO_SAVE: bool = Field(default=True, description="Enable auto-save")

    # Cache configuration
    CACHE_ENABLED: bool = Field(default=True, description="Enable caching")
    CACHE_TYPE: str = Field(default="SimpleCache", description="Cache type for Flask-Caching")
    CACHE_TIMEOUT: int = Field(default=3600, description="Default cache timeout in seconds")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300, description="Default cache timeout for Flask-Caching")

    # Analysis settings
    DEFAULT_CONFIDENCE_LEVEL: float = Field(default=0.95, description="Default confidence level for statistics")
    DEFAULT_RANDOM_SEED: int = Field(default=1234, description="Default random seed")
    MAX_ITERATIONS: int = Field(default=10000, description="Maximum iterations for algorithms")

    # Plot settings
    DEFAULT_PLOT_HEIGHT: int = Field(default=600, description="Default plot height in pixels")
    DEFAULT_PLOT_WIDTH: int | None = Field(default=None, description="Default plot width in pixels")
    PLOT_TEMPLATE: str = Field(default="plotly_white", description="Default Plotly template")

    # Performance
    ENABLE_COMPRESSION: bool = Field(default=True, description="Enable Flask-Compress")
    ENABLE_CACHING: bool = Field(default=True, description="Enable result caching")
    CALLBACK_TIMEOUT: int = Field(default=300, description="Callback timeout in seconds")

    # Session configuration
    SESSION_LIFETIME_HOURS: int = Field(default=24, description="Session lifetime in hours")

    @property
    def base_dir(self) -> Path:
        """Get the base directory of the application."""
        BASE_DIR = Path(__file__).resolve().parent.parent
        return BASE_DIR

    @property
    def assets_dir(self) -> Path:
        """Get the assets directory."""
        return self.base_dir / "assets"

    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        data_path = self.base_dir.parent / "data"
        data_path.mkdir(exist_ok=True)
        return data_path

    def export(self, filepath: str | Path, indent: int = 2) -> None:
        """
        Export settings to a file. Format is determined by file extension.

        Args:
            filepath: Path to the output file (.json or .yaml/.yml)
            indent: Number of spaces for JSON indentation (only used for JSON format)

        Raises:
            ValueError: If file extension is not supported
            ImportError: If PyYAML is not installed (for YAML export)
            IOError: If file cannot be written
        """
        filepath = Path(filepath)
        extension = filepath.suffix.lower()

        if extension == ".json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, indent=indent, ensure_ascii=False)
        elif extension in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                msg = "PyYAML is not installed. Install it with: pip install pyyaml"
                raise ImportError(msg)
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(self.model_dump(), f, default_flow_style=False, allow_unicode=True)
        else:
            msg = f"Unsupported file extension: {extension}. Use .json, .yaml, or .yml"
            raise ValueError(msg)

    @classmethod
    def load(cls, filepath: str | Path) -> "AppSettings":
        """
        Load settings from a file. Format is determined by file extension.

        Args:
            filepath: Path to the input file (.json or .yaml/.yml)

        Returns:
            New AppSettings instance

        Raises:
            ValueError: If file extension is not supported
            ImportError: If PyYAML is not installed (for YAML files)
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If JSON file is not valid
            yaml.YAMLError: If YAML file is not valid
            TypeError: If file structure is invalid
        """
        filepath = Path(filepath)
        extension = filepath.suffix.lower()

        if extension == ".json":
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                msg = "JSON file must contain an object"
                raise TypeError(msg)
        elif extension in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                msg = "PyYAML is not installed. Install it with: pip install pyyaml"
                raise ImportError(msg)
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                msg = "YAML file must contain a mapping"
                raise TypeError(msg)
        else:
            msg = f"Unsupported file extension: {extension}. Use .json, .yaml, or .yml"
            raise ValueError(msg)

        return cls(**data)


@lru_cache
def get_app_settings() -> "AppSettings":
    """
    Get cached application settings instance.

    Returns:
        Settings: Cached settings instance
    """
    return AppSettings()


# Global application settings instance
app_settings = get_app_settings()
