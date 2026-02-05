"""
Prometheus Metrics Middleware

Exports custom business metrics and HTTP metrics for monitoring.
Integrates with Prometheus for scraping via /metrics endpoint.
"""

from typing import Callable
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
import time


# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)


# ============================================================================
# Business Metrics - Agents
# ============================================================================

agent_operations_total = Counter(
    'agent_operations_total',
    'Total agent operations',
    ['operation', 'status']
)

active_agents_gauge = Gauge(
    'active_agents',
    'Number of active agents by status',
    ['status']
)

agent_task_duration_seconds = Histogram(
    'agent_task_duration_seconds',
    'Agent task execution time',
    ['agent_role', 'task_type'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)


# ============================================================================
# Business Metrics - Tasks
# ============================================================================

task_operations_total = Counter(
    'task_operations_total',
    'Total task operations',
    ['operation', 'priority', 'status']
)

pending_tasks_gauge = Gauge(
    'pending_tasks',
    'Number of pending tasks by priority',
    ['priority']
)

task_execution_duration_seconds = Histogram(
    'task_execution_duration_seconds',
    'Task execution time by priority',
    ['priority', 'status'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)

task_queue_size = Gauge(
    'task_queue_size',
    'Number of tasks in queue',
    ['priority']
)


# ============================================================================
# Business Metrics - Optimization
# ============================================================================

graph_optimization_total = Counter(
    'graph_optimization_total',
    'Total graph optimizations',
    ['strategy', 'status']
)

graph_optimization_duration_seconds = Histogram(
    'graph_optimization_duration_seconds',
    'Graph optimization execution time',
    ['strategy'],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300)
)

graph_optimization_time_saved_seconds = Histogram(
    'graph_optimization_time_saved_seconds',
    'Time saved by optimization',
    ['strategy'],
    buckets=(10, 30, 60, 120, 300, 600, 1800, 3600)
)

graph_analysis_total = Counter(
    'graph_analysis_total',
    'Total graph analyses',
    ['analysis_type']
)


# ============================================================================
# Business Metrics - Alerts
# ============================================================================

alert_triggers_total = Counter(
    'alert_triggers_total',
    'Alert triggers',
    ['severity', 'rule_name']
)

active_alerts_gauge = Gauge(
    'active_alerts',
    'Active alerts by severity',
    ['severity', 'status']
)

alert_acknowledgment_duration_seconds = Histogram(
    'alert_acknowledgment_duration_seconds',
    'Time to acknowledge alerts',
    ['severity'],
    buckets=(10, 30, 60, 300, 600, 1800, 3600)
)

alert_resolution_duration_seconds = Histogram(
    'alert_resolution_duration_seconds',
    'Time to resolve alerts',
    ['severity'],
    buckets=(60, 300, 600, 1800, 3600, 7200, 14400, 28800)
)


# ============================================================================
# System Metrics
# ============================================================================

database_connections_gauge = Gauge(
    'database_connections',
    'Database connection pool status',
    ['pool_name', 'state']
)

cache_operations_total = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio by cache type',
    ['cache_type']
)

background_jobs_total = Counter(
    'background_jobs_total',
    'Background jobs processed',
    ['job_type', 'status']
)

background_jobs_duration_seconds = Histogram(
    'background_jobs_duration_seconds',
    'Background job execution time',
    ['job_type'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)


# ============================================================================
# WebSocket Metrics
# ============================================================================

websocket_connections_gauge = Gauge(
    'websocket_connections',
    'Active WebSocket connections',
    ['channel']
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'WebSocket messages sent/received',
    ['direction', 'message_type']
)


# ============================================================================
# Middleware
# ============================================================================

class PrometheusMiddleware:
    """
    FastAPI middleware to track HTTP metrics.

    Tracks request count, duration, and in-progress requests.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request info
        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        # Normalize path (remove IDs)
        endpoint = self._normalize_path(path)

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Track request duration
        start_time = time.time()

        try:
            # Process request
            await self.app(scope, receive, send)

            # Note: We can't easily get status code here without modifying response
            # For now, we'll use a separate function to record status codes

        finally:
            # Record metrics
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by replacing UUIDs and IDs with placeholders.

        Examples:
        - /api/agents/123e4567-e89b-12d3-a456-426614174000 -> /api/agents/{id}
        - /api/tasks/456 -> /api/tasks/{id}
        """
        import re

        # Replace UUIDs
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{id}',
            path,
            flags=re.IGNORECASE
        )

        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)

        return path


def record_http_request(method: str, endpoint: str, status_code: int):
    """
    Record HTTP request metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()


# ============================================================================
# Helper Functions for Business Metrics
# ============================================================================

def record_agent_operation(operation: str, status: str):
    """Record agent operation (create, update, delete, etc.)."""
    agent_operations_total.labels(operation=operation, status=status).inc()


def update_active_agents(status: str, count: int):
    """Update gauge for active agents by status."""
    active_agents_gauge.labels(status=status).set(count)


def record_agent_task_duration(agent_role: str, task_type: str, duration: float):
    """Record agent task execution duration."""
    agent_task_duration_seconds.labels(
        agent_role=agent_role,
        task_type=task_type
    ).observe(duration)


def record_task_operation(operation: str, priority: str, status: str):
    """Record task operation."""
    task_operations_total.labels(
        operation=operation,
        priority=priority,
        status=status
    ).inc()


def update_pending_tasks(priority: str, count: int):
    """Update gauge for pending tasks by priority."""
    pending_tasks_gauge.labels(priority=priority).set(count)


def record_task_execution(priority: str, status: str, duration: float):
    """Record task execution duration."""
    task_execution_duration_seconds.labels(
        priority=priority,
        status=status
    ).observe(duration)


def update_task_queue_size(priority: str, size: int):
    """Update task queue size gauge."""
    task_queue_size.labels(priority=priority).set(size)


def record_optimization(strategy: str, status: str, duration: float, time_saved: float = 0):
    """Record graph optimization metrics."""
    graph_optimization_total.labels(strategy=strategy, status=status).inc()
    graph_optimization_duration_seconds.labels(strategy=strategy).observe(duration)

    if time_saved > 0:
        graph_optimization_time_saved_seconds.labels(strategy=strategy).observe(time_saved)


def record_graph_analysis(analysis_type: str):
    """Record graph analysis operation."""
    graph_analysis_total.labels(analysis_type=analysis_type).inc()


def record_alert_trigger(severity: str, rule_name: str):
    """Record alert trigger."""
    alert_triggers_total.labels(severity=severity, rule_name=rule_name).inc()


def update_active_alerts(severity: str, status: str, count: int):
    """Update active alerts gauge."""
    active_alerts_gauge.labels(severity=severity, status=status).set(count)


def record_alert_acknowledgment(severity: str, duration: float):
    """Record time to acknowledge alert."""
    alert_acknowledgment_duration_seconds.labels(severity=severity).observe(duration)


def record_alert_resolution(severity: str, duration: float):
    """Record time to resolve alert."""
    alert_resolution_duration_seconds.labels(severity=severity).observe(duration)


def update_database_connections(pool_name: str, state: str, count: int):
    """Update database connection pool metrics."""
    database_connections_gauge.labels(pool_name=pool_name, state=state).set(count)


def record_cache_operation(operation: str, result: str):
    """Record cache operation (hit, miss, set, delete)."""
    cache_operations_total.labels(operation=operation, result=result).inc()


def update_cache_hit_ratio(cache_type: str, ratio: float):
    """Update cache hit ratio gauge."""
    cache_hit_ratio.labels(cache_type=cache_type).set(ratio)


def record_background_job(job_type: str, status: str, duration: float):
    """Record background job execution."""
    background_jobs_total.labels(job_type=job_type, status=status).inc()
    background_jobs_duration_seconds.labels(job_type=job_type).observe(duration)


def update_websocket_connections(channel: str, count: int):
    """Update WebSocket connections gauge."""
    websocket_connections_gauge.labels(channel=channel).set(count)


def record_websocket_message(direction: str, message_type: str):
    """Record WebSocket message."""
    websocket_messages_total.labels(
        direction=direction,
        message_type=message_type
    ).inc()


# ============================================================================
# Metrics Endpoint
# ============================================================================

async def metrics_endpoint(request: Request) -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus exposition format.
    """
    metrics_data = generate_latest()

    return FastAPIResponse(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
