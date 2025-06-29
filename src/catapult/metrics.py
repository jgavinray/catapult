from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# HTTP Request Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently in progress",
    ["method", "endpoint"],
)

# Custom Business Metrics
CUSTOM_COUNTER = Counter(
    "custom_operations_total", "Total number of custom operations", ["operation_type"]
)

CUSTOM_GAUGE = Gauge("custom_value", "A custom gauge value", ["metric_name"])


def get_metrics_response():
    """Generate Prometheus metrics response"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
