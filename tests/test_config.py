import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.catapult.config import (
    AppConfig,
    ArgoCDConfig,
    CatapultConfig,
    FireHydrantConfig,
    JiraConfig,
    ServerConfig,
    create_default_config_file,
    load_config,
)


class TestServerConfig:
    """Test ServerConfig model"""

    def test_server_config_defaults(self):
        """Test ServerConfig with default values"""
        config = ServerConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.reload is False
        assert config.log_level == "info"

    def test_server_config_custom_values(self):
        """Test ServerConfig with custom values"""
        config = ServerConfig(
            host="127.0.0.1", port=9000, reload=True, log_level="debug"
        )
        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.reload is True
        assert config.log_level == "debug"

    def test_server_config_invalid_log_level(self):
        """Test ServerConfig with invalid log level"""
        with pytest.raises(ValueError, match="log_level must be one of"):
            ServerConfig(log_level="invalid")


class TestJiraConfig:
    """Test JiraConfig model"""

    def test_jira_config_disabled(self):
        """Test JiraConfig when disabled"""
        config = JiraConfig(enabled=False)
        assert config.enabled is False
        assert config.base_url is None
        assert config.username is None
        assert config.api_token is None
        assert config.timeout == 30

    def test_jira_config_enabled_valid(self):
        """Test JiraConfig when enabled with valid values"""
        config = JiraConfig(
            enabled=True,
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )
        assert config.enabled is True
        assert config.base_url == "https://test.atlassian.net"
        assert config.username == "test@example.com"
        assert config.api_token == "test-token"

    def test_jira_config_enabled_missing_base_url(self):
        """Test JiraConfig validation when enabled but missing base_url"""
        with pytest.raises(ValueError, match="base_url is required"):
            JiraConfig(enabled=True, username="test", api_token="token")

    def test_jira_config_enabled_missing_username(self):
        """Test JiraConfig validation when enabled but missing username"""
        with pytest.raises(ValueError, match="username is required"):
            JiraConfig(enabled=True, base_url="https://test.com", api_token="token")

    def test_jira_config_enabled_missing_api_token(self):
        """Test JiraConfig validation when enabled but missing api_token"""
        with pytest.raises(ValueError, match="api_token is required"):
            JiraConfig(
                enabled=True, base_url="https://test.com", username="test@example.com"
            )


class TestArgoCDConfig:
    """Test ArgoCDConfig model"""

    def test_argocd_config_disabled(self):
        """Test ArgoCDConfig when disabled"""
        config = ArgoCDConfig(enabled=False)
        assert config.enabled is False
        assert config.base_url is None
        assert config.timeout == 30
        assert config.verify_ssl is True

    def test_argocd_config_enabled_valid(self):
        """Test ArgoCDConfig when enabled with valid values"""
        config = ArgoCDConfig(
            enabled=True,
            base_url="https://argocd.example.com",
            username="admin",
            password="password",
        )
        assert config.enabled is True
        assert config.base_url == "https://argocd.example.com"
        assert config.username == "admin"
        assert config.password == "password"

    def test_argocd_config_enabled_missing_base_url(self):
        """Test ArgoCDConfig validation when enabled but missing base_url"""
        with pytest.raises(ValueError, match="base_url is required"):
            ArgoCDConfig(enabled=True, username="admin", password="password")


class TestFireHydrantConfig:
    """Test FireHydrantConfig model"""

    def test_firehydrant_config_disabled(self):
        """Test FireHydrantConfig when disabled"""
        config = FireHydrantConfig(enabled=False)
        assert config.enabled is False
        assert config.base_url is None
        assert config.api_token is None
        assert config.timeout == 30

    def test_firehydrant_config_enabled_valid(self):
        """Test FireHydrantConfig when enabled with valid values"""
        config = FireHydrantConfig(
            enabled=True,
            base_url="https://api.firehydrant.io",
            api_token="test-token",
        )
        assert config.enabled is True
        assert config.base_url == "https://api.firehydrant.io"
        assert config.api_token == "test-token"

    def test_firehydrant_config_enabled_missing_base_url(self):
        """Test FireHydrantConfig validation when enabled but missing base_url"""
        with pytest.raises(ValueError, match="base_url is required"):
            FireHydrantConfig(enabled=True, api_token="token")

    def test_firehydrant_config_enabled_missing_api_token(self):
        """Test FireHydrantConfig validation when enabled but missing api_token"""
        with pytest.raises(ValueError, match="api_token is required"):
            FireHydrantConfig(enabled=True, base_url="https://api.firehydrant.io")


class TestAppConfig:
    """Test AppConfig model"""

    def test_app_config_defaults(self):
        """Test AppConfig with default values"""
        config = AppConfig()
        assert isinstance(config.catapult, CatapultConfig)
        assert isinstance(config.jira, JiraConfig)
        assert isinstance(config.argocd, ArgoCDConfig)
        assert isinstance(config.firehydrant, FireHydrantConfig)
        assert config.jira.enabled is False
        assert config.argocd.enabled is False
        assert config.firehydrant.enabled is False


class TestConfigLoader:
    """Test configuration loading functionality"""

    def test_load_config_no_file(self):
        """Test loading config when no file exists"""
        with patch("pathlib.Path.exists", return_value=False):
            config = load_config()
            assert isinstance(config, AppConfig)
            assert config.jira.enabled is False

    def test_load_config_from_file(self):
        """Test loading config from YAML file"""
        config_data = {
            "catapult": {"app_name": "Test App", "server": {"port": 9000}},
            "jira": {
                "enabled": True,
                "base_url": "https://test.atlassian.net",
                "username": "test@example.com",
                "api_token": "test-token",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_path = f.name

        try:
            config = load_config(temp_path)
            assert config.catapult.app_name == "Test App"
            assert config.catapult.server.port == 9000
            assert config.jira.enabled is True
            assert config.jira.base_url == "https://test.atlassian.net"
        finally:
            os.unlink(temp_path)

    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_config_invalid_schema(self):
        """Test loading config with invalid schema"""
        config_data = {"jira": {"enabled": True}}  # Missing required fields

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Configuration validation failed"):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_config_file_not_found(self):
        """Test loading config when specified file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    @patch.dict(
        os.environ,
        {
            "CATAPULT_SERVER_HOST": "127.0.0.1",
            "CATAPULT_SERVER_PORT": "9000",
            "CATAPULT_LOG_LEVEL": "debug",
            "JIRA_ENABLED": "true",
            "JIRA_BASE_URL": "https://env.atlassian.net",
            "JIRA_USERNAME": "env@example.com",
            "JIRA_API_TOKEN": "env-token",
        },
    )
    def test_load_config_env_overrides(self):
        """Test environment variable overrides"""
        config_data = {
            "catapult": {"server": {"host": "0.0.0.0", "port": 8000}},
            "jira": {"enabled": False},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_path = f.name

        try:
            config = load_config(temp_path)
            # Environment variables should override file values
            assert config.catapult.server.host == "127.0.0.1"
            assert config.catapult.server.port == 9000
            assert config.catapult.server.log_level == "debug"
            assert config.jira.enabled is True
            assert config.jira.base_url == "https://env.atlassian.net"
            assert config.jira.username == "env@example.com"
            assert config.jira.api_token == "env-token"
        finally:
            os.unlink(temp_path)


class TestCreateDefaultConfig:
    """Test default configuration file creation"""

    def test_create_default_config_file(self):
        """Test creating default configuration file"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            # Remove the temporary file so we can create it
            os.unlink(temp_path)
            create_default_config_file(temp_path)

            # Verify file was created and is valid
            assert Path(temp_path).exists()

            with open(temp_path, "r") as f:
                config_data = yaml.safe_load(f)

            assert "catapult" in config_data
            assert "jira" in config_data
            assert "argocd" in config_data
            assert "firehydrant" in config_data
            assert config_data["jira"]["enabled"] is False
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)
