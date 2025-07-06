import atexit
import time
from datetime import UTC, datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .argocd_client import ArgoCDClient
from .config import load_config, AppConfig
from .event_loop import EventLoop
from .firehydrant_client import FireHydrantClient
from .jira_client import JiraClient
from .metrics import (
    ACTIVE_REQUESTS,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    get_metrics_response,
)

# Load configuration
config = load_config()

# Create FastAPI app with configuration
app = FastAPI(
    title=config.catapult.app_name,
    description=config.catapult.app_description,
    version=config.catapult.app_version,
)

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Create and start event loop
event_loop = EventLoop(check_interval=config.catapult.event_loop.check_interval)

# Initialize service clients
jira_client: Optional[JiraClient] = None
if config.jira.enabled:
    jira_client = JiraClient(config.jira)

# Initialize ArgoCD client
argocd_client: Optional[ArgoCDClient] = None
if config.argocd.enabled:
    argocd_client = ArgoCDClient(config.argocd)

# Initialize FireHydrant client
firehydrant_client: Optional[FireHydrantClient] = None
if config.firehydrant.enabled:
    firehydrant_client = FireHydrantClient(config.firehydrant)


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
    """Readiness check endpoint - verifies external service connections"""
    services_status = {}
    overall_ready = True
    
    # Check Jira connection
    if config.jira.enabled and jira_client:
        jira_ready = jira_client.test_connection()
        services_status["jira"] = "ready" if jira_ready else "not ready"
        if not jira_ready:
            overall_ready = False
    elif config.jira.enabled:
        services_status["jira"] = "not configured"
        overall_ready = False
    
    # Check ArgoCD connection
    if config.argocd.enabled and argocd_client:
        argocd_ready = argocd_client.test_connection()
        services_status["argocd"] = "ready" if argocd_ready else "not ready"
        if not argocd_ready:
            overall_ready = False
    elif config.argocd.enabled:
        services_status["argocd"] = "not configured"
        overall_ready = False
    
    # Check FireHydrant connection
    if config.firehydrant.enabled and firehydrant_client:
        firehydrant_ready = firehydrant_client.test_connection()
        services_status["firehydrant"] = "ready" if firehydrant_ready else "not ready"
        if not firehydrant_ready:
            overall_ready = False
    elif config.firehydrant.enabled:
        services_status["firehydrant"] = "not configured"
        overall_ready = False
    
    status = "ready" if overall_ready else "not ready"
    
    return {
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "services": services_status
    }


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
    # Start the event loop if enabled
    if config.catapult.event_loop.enabled:
        event_loop.start()

    try:
        uvicorn.run(
            "src.catapult.main:app",
            host=config.catapult.server.host,
            port=config.catapult.server.port,
            reload=config.catapult.server.reload,
            log_level=config.catapult.server.log_level,
        )
    finally:
        # Ensure event loop is stopped
        if config.catapult.event_loop.enabled:
            event_loop.stop()
