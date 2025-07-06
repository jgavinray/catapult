"""
Configuration Management Module

This module provides comprehensive configuration management for the Catapult application
using YAML configuration files. It defines Pydantic models for all configuration sections
and provides utilities for loading and validating configuration.

Configuration Structure:
- catapult: Core application settings (server, logging, metrics)
- jira: Jira API connection settings
- argocd: ArgoCD API connection settings  
- firehydrant: FireHydrant API connection settings

Features:
- YAML configuration file support
- Environment variable override support
- Pydantic validation and type safety
- Default values and validation
- Comprehensive error handling

Usage:
    >>> from catapult.config import load_config
    >>> config = load_config("config.yaml")
    >>> print(config.catapult.server.host)
    >>> jira_client = JiraClient(config.jira)
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    """Server configuration settings"""

    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload in development")
    log_level: str = Field(default="info", description="Logging level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.lower()


class EventLoopConfig(BaseModel):
    """Event loop configuration settings"""

    check_interval: int = Field(default=15, description="Check interval in seconds")
    enabled: bool = Field(default=True, description="Enable event loop")


class CatapultConfig(BaseModel):
    """Core Catapult application configuration"""

    server: ServerConfig = Field(default_factory=ServerConfig)
    event_loop: EventLoopConfig = Field(default_factory=EventLoopConfig)
    app_name: str = Field(default="Catapult API", description="Application name")
    app_description: str = Field(
        default="A base HTTP API with Prometheus metrics",
        description="Application description",
    )
    app_version: str = Field(default="1.0.0", description="Application version")


class JiraConfig(BaseModel):
    """Jira API configuration settings"""

    enabled: bool = Field(default=False, description="Enable Jira integration")
    base_url: Optional[str] = Field(None, description="Base URL for Jira instance")
    username: Optional[str] = Field(None, description="Username for authentication")
    api_token: Optional[str] = Field(None, description="API token for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def model_post_init(self, __context):
        """Validate that required fields are provided when enabled"""
        if self.enabled:
            if not self.base_url:
                raise ValueError("base_url is required when Jira is enabled")
            if not self.username:
                raise ValueError("username is required when Jira is enabled")
            if not self.api_token:
                raise ValueError("api_token is required when Jira is enabled")


class ArgoCDConfig(BaseModel):
    """ArgoCD API configuration settings"""

    enabled: bool = Field(default=False, description="Enable ArgoCD integration")
    base_url: Optional[str] = Field(None, description="Base URL for ArgoCD instance")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    token: Optional[str] = Field(None, description="API token for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    def model_post_init(self, __context):
        """Validate that required fields are provided when enabled"""
        if self.enabled:
            if not self.base_url:
                raise ValueError("base_url is required when ArgoCD is enabled")


class FireHydrantConfig(BaseModel):
    """FireHydrant API configuration settings"""

    enabled: bool = Field(default=False, description="Enable FireHydrant integration")
    base_url: Optional[str] = Field(
        None, description="Base URL for FireHydrant instance"
    )
    api_token: Optional[str] = Field(None, description="API token for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def model_post_init(self, __context):
        """Validate that required fields are provided when enabled"""
        if self.enabled:
            if not self.base_url:
                raise ValueError("base_url is required when FireHydrant is enabled")
            if not self.api_token:
                raise ValueError("api_token is required when FireHydrant is enabled")


class AppConfig(BaseModel):
    """Complete application configuration"""

    catapult: CatapultConfig = Field(default_factory=CatapultConfig)
    jira: JiraConfig = Field(default_factory=JiraConfig)
    argocd: ArgoCDConfig = Field(default_factory=ArgoCDConfig)
    firehydrant: FireHydrantConfig = Field(default_factory=FireHydrantConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from YAML file with environment variable overrides.

    Args:
        config_path: Path to YAML configuration file. If None, looks for:
                    - ./config.yaml
                    - ./config/config.yaml
                    - /etc/catapult/config.yaml

    Returns:
        AppConfig: Validated configuration object

    Raises:
        FileNotFoundError: If configuration file is not found
        yaml.YAMLError: If YAML parsing fails
        ValueError: If configuration validation fails
    """

    # Determine configuration file path
    if config_path is None:
        possible_paths = [
            Path("config.yaml"),
            Path("config/config.yaml"),
            Path("/etc/catapult/config.yaml"),
        ]

        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break

        if config_path is None:
            # Create default config if none found
            default_config = AppConfig()
            return default_config

    # Load YAML configuration
    try:
        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file) or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML configuration: {e}")

    # Override with environment variables
    config_data = _apply_env_overrides(config_data)

    # Validate and return configuration
    try:
        return AppConfig(**config_data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def _apply_env_overrides(config_data: dict) -> dict:
    """Apply environment variable overrides to configuration data."""

    # Catapult server overrides
    if "CATAPULT_SERVER_HOST" in os.environ:
        config_data.setdefault("catapult", {}).setdefault("server", {})[
            "host"
        ] = os.environ["CATAPULT_SERVER_HOST"]

    if "CATAPULT_SERVER_PORT" in os.environ:
        config_data.setdefault("catapult", {}).setdefault("server", {})["port"] = int(
            os.environ["CATAPULT_SERVER_PORT"]
        )

    if "CATAPULT_LOG_LEVEL" in os.environ:
        config_data.setdefault("catapult", {}).setdefault("server", {})[
            "log_level"
        ] = os.environ["CATAPULT_LOG_LEVEL"]

    # Jira overrides
    if "JIRA_ENABLED" in os.environ:
        config_data.setdefault("jira", {})["enabled"] = (
            os.environ["JIRA_ENABLED"].lower() == "true"
        )

    if "JIRA_BASE_URL" in os.environ:
        config_data.setdefault("jira", {})["base_url"] = os.environ["JIRA_BASE_URL"]

    if "JIRA_USERNAME" in os.environ:
        config_data.setdefault("jira", {})["username"] = os.environ["JIRA_USERNAME"]

    if "JIRA_API_TOKEN" in os.environ:
        config_data.setdefault("jira", {})["api_token"] = os.environ["JIRA_API_TOKEN"]

    # ArgoCD overrides
    if "ARGOCD_ENABLED" in os.environ:
        config_data.setdefault("argocd", {})["enabled"] = (
            os.environ["ARGOCD_ENABLED"].lower() == "true"
        )

    if "ARGOCD_BASE_URL" in os.environ:
        config_data.setdefault("argocd", {})["base_url"] = os.environ["ARGOCD_BASE_URL"]

    if "ARGOCD_USERNAME" in os.environ:
        config_data.setdefault("argocd", {})["username"] = os.environ["ARGOCD_USERNAME"]

    if "ARGOCD_PASSWORD" in os.environ:
        config_data.setdefault("argocd", {})["password"] = os.environ["ARGOCD_PASSWORD"]

    if "ARGOCD_TOKEN" in os.environ:
        config_data.setdefault("argocd", {})["token"] = os.environ["ARGOCD_TOKEN"]

    # FireHydrant overrides
    if "FIREHYDRANT_ENABLED" in os.environ:
        config_data.setdefault("firehydrant", {})["enabled"] = (
            os.environ["FIREHYDRANT_ENABLED"].lower() == "true"
        )

    if "FIREHYDRANT_BASE_URL" in os.environ:
        config_data.setdefault("firehydrant", {})["base_url"] = os.environ[
            "FIREHYDRANT_BASE_URL"
        ]

    if "FIREHYDRANT_API_TOKEN" in os.environ:
        config_data.setdefault("firehydrant", {})["api_token"] = os.environ[
            "FIREHYDRANT_API_TOKEN"
        ]

    return config_data


def create_default_config_file(config_path: str = "config.yaml") -> None:
    """
    Create a default configuration file with example values.

    Args:
        config_path: Path where to create the configuration file
    """

    default_config = {
        "catapult": {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": False,
                "log_level": "info",
            },
            "event_loop": {"check_interval": 15, "enabled": True},
            "app_name": "Catapult API",
            "app_description": "A base HTTP API with Prometheus metrics",
            "app_version": "1.0.0",
        },
        "jira": {
            "enabled": False,
            "base_url": "https://yourcompany.atlassian.net",
            "username": "your-email@company.com",
            "api_token": "your-jira-api-token",
            "timeout": 30,
        },
        "argocd": {
            "enabled": False,
            "base_url": "https://argocd.yourcompany.com",
            "username": "admin",
            "password": "your-argocd-password",
            "token": "your-argocd-token",
            "timeout": 30,
            "verify_ssl": True,
        },
        "firehydrant": {
            "enabled": False,
            "base_url": "https://api.firehydrant.io",
            "api_token": "your-firehydrant-token",
            "timeout": 30,
        },
    }

    with open(config_path, "w") as file:
        yaml.safe_dump(default_config, file, default_flow_style=False, sort_keys=False)
