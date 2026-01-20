"""
Configuration Management
========================

Centralized configuration for the AIML Dash application using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AIML_DASH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application metadata
    app_name: str = Field(default="AIML Dash", description="Application name")
    app_title: str = Field(default="AIML Dash", description="Application title")
    app_description: str = Field(
        default="A Dash application for Predictive Analytics and Machine Learning.",
        description="Application description",
    )
    github_url: str = Field(
        default="https://github.com/jeffmaxey/aiml-dash",
        description="GitHub repository URL",
    )

    # Server configuration
    debug: bool = Field(default=True, description="Enable debug mode")
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8090, description="Server port")

    # Data configuration
    max_file_size_mb: int = Field(default=100, description="Maximum upload file size in MB")
    data_cache_size: int = Field(default=100, description="Number of datasets to cache")

    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )

    # Security configuration
    enable_talisman: bool = Field(default=False, description="Enable Flask-Talisman security headers")
    enable_compression: bool = Field(default=True, description="Enable Flask-Compress")

    # Cache configuration
    cache_type: str = Field(default="SimpleCache", description="Cache type for Flask-Caching")
    cache_default_timeout: int = Field(default=300, description="Default cache timeout in seconds")

    # Session configuration
    session_lifetime_hours: int = Field(default=24, description="Session lifetime in hours")

    @property
    def base_dir(self) -> Path:
        """Get the base directory of the application."""
        return Path(__file__).parent

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


@lru_cache
def get_settings() -> AppSettings:
    """
    Get cached application settings.

    Returns
    -------
    AppSettings
        Application settings instance
    """
    return AppSettings()


# Convenience exports
settings = get_settings()
