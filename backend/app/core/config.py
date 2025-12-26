"""
AI Translation Benchmark - Configuration Management

Author: Zoltan Tamas Toth

Handles loading and validation of application configuration from
environment variables and YAML config files.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

from app.core.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_TEXT_LENGTH,
    DEFAULT_TIMEOUT,
    PATH_CONFIG_FILE,
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/translations.db",
        description="Database connection URL",
    )

    # Server Configuration
    backend_host: str = Field(default="0.0.0.0", description="Backend host")
    backend_port: int = Field(default=8000, description="Backend port")

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated CORS origins",
    )

    # Logging Configuration
    log_level: str = Field(default=DEFAULT_LOG_LEVEL, description="Logging level")
    log_dir: str = Field(default="logs", description="Log directory")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


class ConfigManager:
    """Manages application configuration from YAML file."""

    def __init__(self, config_path: str = PATH_CONFIG_FILE):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'metrics.heuristics')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_providers(self) -> list[dict[str, Any]]:
        """Get list of configured providers."""
        return self.get("providers", [])

    def get_enabled_providers(self) -> list[dict[str, Any]]:
        """Get list of enabled providers."""
        providers = self.get_providers()
        return [p for p in providers if p.get("enabled", False)]

    def get_metric_config(self, metric_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Metric configuration dictionary
        """
        return self.get(f"metrics.{metric_name}", {})

    def get_metric_weight(self, category: str, metric: str) -> float:
        """
        Get weight for a specific metric.

        Args:
            category: Metric category (e.g., 'heuristics', 'semantic')
            metric: Metric name

        Returns:
            Metric weight (default: 0.0)
        """
        return self.get(f"metrics.{category}.{metric}.weight", 0.0)

    def is_metric_enabled(self, category: str, metric: str) -> bool:
        """
        Check if a metric is enabled.

        Args:
            category: Metric category
            metric: Metric name

        Returns:
            True if metric is enabled
        """
        return self.get(f"metrics.{category}.{metric}.enabled", False)

    def get_supported_languages(self, lang_type: str = "target") -> list[dict[str, str]]:
        """
        Get list of supported languages.

        Args:
            lang_type: 'source' or 'target'

        Returns:
            List of language dictionaries with 'code' and 'name'
        """
        return self.get(f"languages.{lang_type}", [])

    def get_max_text_length(self) -> int:
        """Get maximum allowed text length."""
        return self.get("settings.max_text_length", DEFAULT_MAX_TEXT_LENGTH)

    def get_default_timeout(self) -> int:
        """Get default timeout for provider requests."""
        return self.get("settings.default_timeout", DEFAULT_TIMEOUT)


# Global instances
settings = Settings()
config_manager = ConfigManager()
