"""
Tests for metrics module.
"""

from src.catapult.metrics import (
    ACTIVE_REQUESTS,
    CUSTOM_COUNTER,
    CUSTOM_GAUGE,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    get_metrics_response,
)


def test_metrics_defined():
    """Test that all metrics are properly defined."""
    assert REQUEST_COUNT is not None
    assert REQUEST_LATENCY is not None
    assert ACTIVE_REQUESTS is not None
    assert CUSTOM_COUNTER is not None
    assert CUSTOM_GAUGE is not None


def test_get_metrics_response():
    """Test metrics response function."""
    response = get_metrics_response()
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
