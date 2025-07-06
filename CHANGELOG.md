# Release Notes - v1.0.0

## 🚀 Initial Release

Catapult API is a production-ready FastAPI application with built-in Prometheus metrics, health monitoring, and background event processing.

## ✨ Key Features

- **FastAPI Web Framework** - Modern, high-performance HTTP API
- **Prometheus Metrics** - Built-in metrics collection and `/metrics` endpoint
- **Health & Readiness Checks** - `/health` and `/ready` endpoints for monitoring
- **Background Event Loop** - Periodic state monitoring every 15 seconds
- **Interactive API Documentation** - Swagger UI at `/docs`
- **Graceful Shutdown** - Proper cleanup of background processes

## 🔧 System Requirements

- **Python**: 3.12 (required)
- **OS**: Linux (Debian 12+, Ubuntu 24.04+, Rocky Linux 8+) - Recommended
- **Memory**: 512MB RAM minimum (1GB+ recommended)

## 📋 API Endpoints

- `GET /health` - Health check
- `GET /ready` - Readiness check  
- `GET /metrics` - Prometheus metrics
- `GET /docs` - API documentation

## 🛠️ Development Features

- **Comprehensive Testing** - Full test suite with pytest
- **Code Quality** - Black formatting + Ruff linting
- **CI/CD Pipeline** - Automated testing and quality checks
- **Release Automation** - Release-please integration

## 🚨 Known Issues

- Python 3.13+ not supported due to dependency constraints

## 📦 Installation

```bash
git clone <repository-url>
cd catapult
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.catapult.main
```

## 📚 Documentation

See [README.md](README.md) for detailed setup and usage instructions.

---

**Contributors**: J. Gavin Ray
