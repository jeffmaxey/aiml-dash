"""Application configuration management for AIML Dash."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]


class AppSettings(BaseSettings):
    """Validated application settings with environment-aware defaults."""

    model_config = SettingsConfigDict(
        env_prefix="AIML_DASH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="AIML Dash", description="Application name")
    app_title: str = Field(default="AIML Dash", description="Display title")
    app_description: str = Field(
        default="A Dash application for Predictive Analytics and Machine Learning.",
        description="Application description",
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Environment = Field(
        default="development", description="Runtime environment"
    )
    github_url: str = Field(
        default="https://github.com/jeffmaxey/aiml-dash",
        description="Source repository URL",
    )

    debug: bool = Field(default=True, description="Enable debug mode")
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8050, description="Server port")

    max_file_size_mb: int = Field(
        default=100, description="Maximum upload file size in MB"
    )
    data_cache_size: int = Field(
        default=100, description="Number of datasets to retain in memory"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s %(levelname)s %(name)s %(message)s",
        description="Log format string",
    )
    log_json: bool = Field(
        default=False, description="Emit logs in JSON format when enabled"
    )

    enable_talisman: bool = Field(
        default=False, description="Enable Flask-Talisman security headers"
    )
    enable_compression: bool = Field(
        default=True, description="Enable Flask-Compress"
    )
    cache_type: str = Field(
        default="SimpleCache", description="Cache type for Flask-Caching"
    )
    cache_default_timeout: int = Field(
        default=300, description="Default cache timeout in seconds"
    )
    session_lifetime_hours: int = Field(
        default=24, description="Session lifetime in hours"
    )

    enable_dynamic_plugins: bool = Field(
        default=False, description="Enable dynamic plugin discovery at runtime"
    )
    plugin_api_version: str = Field(
        default="1.0", description="Supported plugin API version"
    )

    default_user_roles: tuple[str, ...] = Field(
        default=("viewer",), description="Roles granted to anonymous/default users"
    )
    admin_roles: tuple[str, ...] = Field(
        default=("admin",), description="Roles considered privileged"
    )

    @property
    def package_dir(self) -> Path:
        """Return the package directory."""
        return Path(__file__).resolve().parent.parent

    @property
    def project_dir(self) -> Path:
        """Return the project root."""
        return self.package_dir.parent

    @property
    def runtime_dir(self) -> Path:
        """Return the runtime state directory."""
        return self.project_dir / ".aiml_dash"

    @property
    def data_dir(self) -> Path:
        """Return the runtime data directory."""
        return self.runtime_dir / "data"

    @property
    def config_dir(self) -> Path:
        """Return the runtime config directory."""
        return self.runtime_dir / "config"

    @property
    def plugin_config_dir(self) -> Path:
        """Return the plugin config directory."""
        return self.config_dir / "plugins"

    @property
    def log_dir(self) -> Path:
        """Return the log directory."""
        return self.runtime_dir / "logs"

    def model_post_init(self, __context: object) -> None:
        """Apply environment-specific defaults after validation."""
        if self.environment != "development":
            object.__setattr__(self, "debug", False)
        if self.environment == "production":
            object.__setattr__(self, "enable_talisman", True)
            object.__setattr__(self, "log_json", True)

    def ensure_runtime_directories(self) -> None:
        """Create expected runtime directories explicitly."""
        for directory in (
            self.runtime_dir,
            self.data_dir,
            self.config_dir,
            self.plugin_config_dir,
            self.log_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> AppSettings:
    """Return cached settings."""
    return AppSettings()


settings = get_settings()

