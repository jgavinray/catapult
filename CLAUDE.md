# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (Python 3.12 required)
python3.12 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -e ".[dev]"
```

### Configuration
```bash
# Create default configuration file
python -c "from src.catapult.config import create_default_config_file; create_default_config_file()"

# Edit config.yaml with your settings (Jira, ArgoCD, FireHydrant credentials)
```

### Running the Application
```bash
# Development mode with auto-reload (uses config.yaml)
python -m src.catapult.main

# Production mode (uses config.yaml)
uvicorn src.catapult.main:app --host 0.0.0.0 --port 8000

# Override configuration with environment variables
CATAPULT_SERVER_PORT=9000 JIRA_ENABLED=true python -m src.catapult.main
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_main.py
pytest tests/test_metrics.py  
pytest tests/test_event_loop.py
pytest tests/test_jira_client.py
pytest tests/test_config.py

# Run with coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking (no explicit mypy configuration found)
```

## Architecture

This is a FastAPI application with comprehensive YAML configuration and external service integration:

### 1. Configuration System (`src/catapult/config.py`)
- YAML-based configuration with Pydantic models for validation
- Environment variable override support
- Four main configuration sections: catapult, jira, argocd, firehydrant
- Automatic configuration discovery and validation
- Type-safe configuration with comprehensive error handling

### 2. FastAPI Application (`src/catapult/main.py`)
- Main HTTP server with health, readiness, and metrics endpoints
- Uses Prometheus middleware for request instrumentation
- Integrates with background event loop for state monitoring
- Dynamic readiness checks for enabled external services (Jira, ArgoCD, FireHydrant)
- Configuration-driven server settings and application metadata

### 3. External Service Clients
- **Jira Client** (`src/catapult/jira_client.py`): Full API integration for ticket management and analysis
- **ArgoCD Client** (`src/catapult/argocd_client.py`): Placeholder for GitOps application management
- **FireHydrant Client** (`src/catapult/firehydrant_client.py`): Placeholder for incident management

### 4. Prometheus Metrics (`src/catapult/metrics.py`)
- Centralized metrics definitions using prometheus-client
- HTTP request metrics (count, latency, active requests)
- Custom business metrics (counters and gauges)
- Provides `/metrics` endpoint for scraping

### 5. Event Loop (`src/catapult/event_loop.py`)
- Background thread with configurable check interval
- Configurable state check callback for custom monitoring
- Graceful shutdown handling
- Thread-safe status reporting

## Key Implementation Details

### Python Version Requirement
- **Must use Python 3.12** - Python 3.13+ not supported due to dependency incompatibilities
- Dependencies include pydantic 2.6.0 which requires Python 3.12

### YAML Configuration Structure
The application uses a comprehensive YAML configuration system:

```yaml
catapult:
  server:
    host: "0.0.0.0"
    port: 8000
    reload: false
    log_level: "info"
  event_loop:
    check_interval: 15
    enabled: true
  app_name: "Catapult API"
  app_description: "A base HTTP API with Prometheus metrics"
  app_version: "1.0.0"

jira:
  enabled: false
  base_url: "https://yourcompany.atlassian.net"
  username: "your-email@company.com"
  api_token: "your-jira-api-token"
  timeout: 30

argocd:
  enabled: false
  base_url: "https://argocd.yourcompany.com"
  username: "admin"
  password: "your-argocd-password"
  token: "your-argocd-token"
  timeout: 30
  verify_ssl: true

firehydrant:
  enabled: false
  base_url: "https://api.firehydrant.io"
  api_token: "your-firehydrant-token"
  timeout: 30
```

### Environment Variable Overrides
All configuration values can be overridden using environment variables:
- `CATAPULT_SERVER_HOST`, `CATAPULT_SERVER_PORT`, `CATAPULT_LOG_LEVEL`
- `JIRA_ENABLED`, `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- `ARGOCD_ENABLED`, `ARGOCD_BASE_URL`, `ARGOCD_USERNAME`, `ARGOCD_PASSWORD`, `ARGOCD_TOKEN`
- `FIREHYDRANT_ENABLED`, `FIREHYDRANT_BASE_URL`, `FIREHYDRANT_API_TOKEN`

### External Service Integration
The `/ready` endpoint dynamically checks connections to enabled services:
- **Jira**: Tests connection using `/rest/api/2/serverInfo` endpoint
- **ArgoCD**: Tests connection using `/api/version` endpoint  
- **FireHydrant**: Tests connection using `/v1/ping` or `/v1/users/me` endpoints

Services are only checked if enabled in configuration. Connection tests use actual API calls with configured credentials.

### Event Loop Customization
The event loop interval and enabled state are configurable via YAML:
- Modify `catapult.event_loop.check_interval` to change monitoring frequency
- Set `catapult.event_loop.enabled` to false to disable background monitoring
- Add custom state monitoring logic in the `state_check_callback` function

### Testing Strategy
- Uses pytest with FastAPI TestClient
- Tests cover all main endpoints (health, ready, metrics)
- Separate test files for each main component
- Uses httpx for async HTTP testing

## Project Structure
```
├── config.yaml                    # YAML configuration file
├── requirements.txt               # Python dependencies (includes PyYAML)
├── src/catapult/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app with endpoints and middleware
│   ├── config.py                 # YAML configuration system with Pydantic models
│   ├── metrics.py                # Prometheus metrics definitions
│   ├── event_loop.py             # Background monitoring thread
│   ├── jira_client.py            # Jira API client with full functionality
│   ├── argocd_client.py          # ArgoCD API client (placeholder)
│   └── firehydrant_client.py     # FireHydrant API client (placeholder)
└── tests/
    ├── __init__.py
    ├── test_main.py              # Tests for FastAPI endpoints
    ├── test_config.py            # Tests for configuration system
    ├── test_metrics.py           # Tests for metrics functionality
    ├── test_event_loop.py        # Tests for background event loop
    └── test_jira_client.py       # Tests for Jira client functionality
```

## Configuration
- Uses pyproject.toml for package configuration
- Black formatting with 88 character line length
- Ruff linting with extensive rule set
- Conventional commits enforced via commitlint