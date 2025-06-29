"""
Tests for main application endpoints.
"""

from fastapi.testclient import TestClient

from src.catapult.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health endpoint returns correct format."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_ready_endpoint():
    """Test ready endpoint returns correct format."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] in ["ready", "not ready"]


def test_metrics_endpoint():
    """Test metrics endpoint returns Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    content = response.text
    assert "# HELP" in content
    assert "# TYPE" in content
