# Catapult API

A base HTTP API built with FastAPI that exposes Prometheus metrics and includes a background event loop for state monitoring.

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Configuration](#configuration)
  - [YAML Configuration](#yaml-configuration)
  - [Environment Variables](#environment-variables)
  - [External Services](#external-services)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Running Locally](#running-locally)
  - [Step 1: Clone and Setup](#step-1-clone-and-setup)
  - [Step 2: Configuration Setup](#step-2-configuration-setup)
  - [Step 3: Run the Application](#step-3-run-the-application)
  - [Step 4: Verify the Application](#step-4-verify-the-application)
  - [Step 5: Stop the Application](#step-5-stop-the-application)
- [Testing](#testing)
- [Commit Types](#commit-types)
- [API Endpoints](#api-endpoints)
  - [Core Endpoints](#core-endpoints)
  - [Health Check](#health-check)
  - [Readiness Check](#readiness-check)
  - [Metrics](#metrics)
- [Prometheus Metrics](#prometheus-metrics)
  - [HTTP Metrics](#http-metrics)
  - [Custom Metrics](#custom-metrics)
- [Event Loop](#event-loop)
  - [Configuration](#event-loop-configuration)
  - [Customization](#customization)
- [External Service Clients](#external-service-clients)
  - [Jira Integration](#jira-integration)
  - [ArgoCD Integration](#argocd-integration)
  - [FireHydrant Integration](#firehydrant-integration)
- [Development](#development)
  - [Running in Development Mode](#running-in-development-mode)
  - [Production Deployment](#production-deployment)
- [Monitoring](#monitoring)
  - [Prometheus Configuration](#prometheus-configuration)
  - [Health Check Monitoring](#health-check-monitoring)
- [Dependencies](#dependencies)
- [License](#license)

## Architecture

The application consists of five main components:

- **Configuration System** (`src/catapult/config.py`) - YAML-based configuration with Pydantic validation
- **FastAPI Application** (`src/catapult/main.py`) - HTTP server with health, readiness, and metrics endpoints
- **External Service Clients** - Jira, ArgoCD, and FireHydrant API integration
- **Prometheus Metrics** (`src/catapult/metrics.py`) - Centralized metrics definitions and collection
- **Event Loop** (`src/catapult/event_loop.py`) - Background thread that performs periodic state checks

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **YAML Configuration System**: Comprehensive configuration management with Pydantic validation
- **External Service Integration**: Support for Jira, ArgoCD, and FireHydrant APIs
- **Prometheus Integration**: Built-in metrics collection and exposure via `/metrics` endpoint
- **Health & Readiness Checks**: Separate endpoints for health (`/health`) and readiness (`/ready`) monitoring
- **Environment Variable Overrides**: Configuration values can be overridden via environment variables
- **Background Event Loop**: Configurable threaded event loop for state monitoring
- **Graceful Shutdown**: Proper cleanup of background processes on application exit
- **UTC Timestamp Support**: Timestamp in UTC format
- **Comprehensive Testing Setup**: 54 tests covering all components with high code coverage
- **Code Formatting with Black**: Code formatting tool for consistent code style
- **Linting with Ruff**: Code linting tool for code quality
- **Conventional Commit Enforcement**: Commit messages follow conventional commit format

## Configuration

The application uses a comprehensive YAML-based configuration system with support for environment variable overrides.

### YAML Configuration

Create a configuration file using the built-in helper:

```bash
python -c "from src.catapult.config import create_default_config_file; create_default_config_file()"
```

This creates a `config.yaml` file with the following structure:

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

### Environment Variables

All configuration values can be overridden using environment variables:

**Catapult Server Settings:**
- `CATAPULT_SERVER_HOST` - Server host address
- `CATAPULT_SERVER_PORT` - Server port number
- `CATAPULT_LOG_LEVEL` - Logging level (debug, info, warning, error, critical)

**Jira Configuration:**
- `JIRA_ENABLED` - Enable/disable Jira integration (true/false)
- `JIRA_BASE_URL` - Jira instance URL
- `JIRA_USERNAME` - Jira username/email
- `JIRA_API_TOKEN` - Jira API token

**ArgoCD Configuration:**
- `ARGOCD_ENABLED` - Enable/disable ArgoCD integration (true/false)
- `ARGOCD_BASE_URL` - ArgoCD instance URL
- `ARGOCD_USERNAME` - ArgoCD username
- `ARGOCD_PASSWORD` - ArgoCD password
- `ARGOCD_TOKEN` - ArgoCD API token

**FireHydrant Configuration:**
- `FIREHYDRANT_ENABLED` - Enable/disable FireHydrant integration (true/false)
- `FIREHYDRANT_BASE_URL` - FireHydrant API URL
- `FIREHYDRANT_API_TOKEN` - FireHydrant API token

### External Services

The application supports integration with three external services:

- **Jira**: Issue tracking and project management
- **ArgoCD**: GitOps continuous delivery
- **FireHydrant**: Incident management

When enabled, these services are checked during readiness probes and can be used by your application logic.

## Project Structure

```
catapult/
├── src/
│   └── catapult/
│       ├── __init__.py
│       ├── main.py              # FastAPI application with endpoints
│       ├── metrics.py           # Prometheus metrics definitions
│       └── event_loop.py        # Background event loop implementation
├── tests/
│   ├── __init__.py
│   ├── test_main.py             # Tests for main application
│   ├── test_metrics.py          # Tests for metrics module
│   └── test_event_loop.py       # Tests for event loop
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Prerequisites

- **Python 3.12** (required; Python 3.13+ is not supported due to library incompatibility)
- pip

> **Note:** This project requires Python 3.12 because some dependencies (such as pydantic and its core libraries) are not yet compatible with Python 3.13 or above. Attempting to use Python 3.13+ will result in installation errors.

## Running Locally

### Step 1: Clone and Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd catapult
```

2. Create a virtual environment:
```bash
python3.12 -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option A: Using Python module (Recommended for development)**
```bash
python -m src.catapult.main
```

**Option B: Using uvicorn directly**
```bash
uvicorn src.catapult.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Verify the Application

The API will be available at `http://localhost:8000`

Test the endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Metrics
curl http://localhost:8000/metrics

# API documentation
open http://localhost:8000/docs
```

### Step 4: Stop the Application

Press `Ctrl+C` to stop the application. The event loop will be properly cleaned up.

## Testing

**Make sure your virtual environment is activated before running tests.**

Run the test suite:

```bash
pytest tests/
```

Run specific test files:

```bash
pytest tests/test_main.py
pytest tests/test_metrics.py
pytest tests/test_event_loop.py
```

## Commit Types

This project uses conventional commits. When making commits, use one of the following types:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## API Endpoints

### Core Endpoints

- `GET /health` - Basic health check endpoint
- `GET /ready` - Readiness check endpoint (checks external service connections)
- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456+00:00"
}
```

### Readiness Check

```bash
curl http://localhost:8000/ready
```

The readiness endpoint checks connections to:
- Jira
- ArgoCD  
- FireHydrant

Response:
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:45.123456+00:00"
}
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

Returns Prometheus-formatted metrics including:
- HTTP request counts and latency
- Active request gauges
- Custom business metrics

## Prometheus Metrics

The application exposes the following metrics:

### HTTP Metrics
- `http_requests_total` - Total number of HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request latency histogram by method and endpoint
- `http_requests_in_progress` - Number of active requests by method and endpoint

### Custom Metrics
- `custom_operations_total` - Custom operation counters by operation type
- `custom_value` - Custom gauge values by metric name

## Event Loop

The background event loop runs every 15 seconds and can be customized for your specific state checking needs.

### Configuration

The event loop is configured in `src/catapult/main.py`:

```python
event_loop = EventLoop(check_interval=15)

def state_check_callback():
    """Add your state checking logic here"""
    pass

event_loop.set_state_check_callback(state_check_callback)
```

### Customization

To add custom state checking logic, modify the `state_check_callback()` function in `src/catapult/main.py`:

```python
def state_check_callback():
    """Example state checking logic"""
    # Check database connections
    # Verify external service health
    # Update custom metrics
    # Log state information
    pass
```

## Development

### Running in Development Mode

**Make sure your virtual environment is activated.**

The application includes auto-reload for development:

```bash
python -m src.catapult.main
```

### Production Deployment

For production, use uvicorn directly:

```bash
uvicorn src.catapult.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: info)

## Monitoring

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'catapult-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Health Check Monitoring

Monitor the health and readiness endpoints:

```bash
# Health check
curl -f http://localhost:8000/health

# Readiness check  
curl -f http://localhost:8000/ready
```

## Dependencies

### System Requirements

- **Python**: 3.12 (required; Python 3.13+ is not supported due to library incompatibility)
- **Git**: Latest stable version for version control
- **Operating Systems**: 
  - Linux (Debian 12+, Ubuntu 24.04+, Rocky Linux 8+) - **Recommended**
  - macOS (tested on macOS 15.5.0)
  - Windows (Windows 10/11 with WSL2 recommended)
- **Memory**: Minimum 512MB RAM (1GB+ recommended)
- **Disk Space**: At least 100MB free space
- **Network**: Internet access for package installation and external service connections

### Python Dependencies

For a complete list of Python library dependencies, see [requirements.txt](requirements.txt).
