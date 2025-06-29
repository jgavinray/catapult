import atexit
import time
from datetime import UTC, datetime

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .event_loop import EventLoop
from .metrics import (
    ACTIVE_REQUESTS,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    get_metrics_response,
)

# Create FastAPI app
app = FastAPI(
    title="Catapult API",
    description="A base HTTP API with Prometheus metrics",
    version="1.0.0",
)

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Create and start event loop
event_loop = EventLoop(check_interval=15)


def state_check_callback():
    """Callback function for state checks"""
    # Add your state checking logic here
    pass


# Set up event loop
event_loop.set_state_check_callback(state_check_callback)


@app.middleware("http")
async def prometheus_middleware(request, call_next):
    start_time = time.time()

    # Increment active requests
    ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()

    try:
        response = await call_next(request)

        # Record request count and latency
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method, endpoint=request.url.path
        ).observe(time.time() - start_time)

        return response
    finally:
        # Decrement active requests
        ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).dec()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/ready")
async def ready_check():
    """Health check endpoint"""
    # Check Jira connection
    if None is not None:
        return {
            "status": "not ready",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    # Check ArgoCD connection
    if None is not None:
        return {
            "status": "not ready",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # Check FireHydrant connection
    if None is not None:
        return {
            "status": "not ready",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    return {"status": "ready", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/metrics")
async def metrics():
    """Raw Prometheus metrics endpoint"""
    return get_metrics_response()


def cleanup():
    """Cleanup function to stop event loop on shutdown"""
    event_loop.stop()


# Register cleanup function
atexit.register(cleanup)

if __name__ == "__main__":
    # Start the event loop
    event_loop.start()

    try:
        uvicorn.run(
            "src.catapult.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    finally:
        # Ensure event loop is stopped
        event_loop.stop()
