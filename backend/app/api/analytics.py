"""
Analytics API Endpoints

Provides endpoints for system metrics, agent analytics, and execution analytics
"""

from typing import List, Optional, Dict
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.metrics_collector import MetricsCollector
from app.infrastructure.database import get_db_session


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Response Models

class SystemHealthResponse(BaseModel):
    """System health metrics response"""
    timestamp: str
    total_agents: int
    agents_idle: int
    agents_busy: int
    agents_error: int
    agents_offline: int
    total_connections: int
    connections_active: int
    connections_pending: int
    active_executions: int
    avg_response_time_ms: float
    error_rate: float
    cpu_usage: float
    memory_usage: float


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response"""
    timeframe_start: str
    timeframe_end: str
    response_time_p50: float
    response_time_p95: float
    response_time_p99: float
    throughput_per_minute: float
    error_rate: float
    success_rate: float
    total_requests: int
    successful_requests: int
    failed_requests: int


class AgentMetricsResponse(BaseModel):
    """Agent metrics response"""
    agent_id: str
    agent_role: str
    total_tasks_completed: int
    total_tasks_failed: int
    avg_response_time_ms: float
    success_rate: float
    utilization: float
    total_cost_usd: float
    cost_per_task_usd: float
    uptime_percentage: float


class ExecutionAnalyticsResponse(BaseModel):
    """Execution analytics response"""
    timeframe_start: str
    timeframe_end: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_seconds: float
    execution_time_p50: float
    execution_time_p95: float
    execution_time_p99: float
    total_cost_usd: float
    avg_cost_per_execution_usd: float
    most_common_patterns: List[Dict]
    cost_by_model: Dict[str, float]


class DataPoint(BaseModel):
    """Time series data point"""
    timestamp: str
    value: float


class Anomaly(BaseModel):
    """Detected anomaly"""
    timestamp: str
    value: float
    reason: str


class TrendAnalysisResponse(BaseModel):
    """Trend analysis response"""
    metric_name: str
    timeframe_start: str
    timeframe_end: str
    granularity: str
    data_points: List[DataPoint]
    trend_direction: str
    growth_rate: float
    anomalies: List[Anomaly]


class UsageForecastResponse(BaseModel):
    """Usage forecast response"""
    forecast_start: str
    forecast_end: str
    predicted_execution_volume: int
    predicted_cost_usd: float
    predicted_resource_needs: Dict[str, int]
    confidence_lower: float
    confidence_upper: float
    forecast_method: str


# Dependency injection

async def get_metrics_collector(
    db: AsyncSession = Depends(get_db_session)
) -> MetricsCollector:
    """Get metrics collector instance"""
    return MetricsCollector(db)


# Helper functions

def parse_timeframe(timeframe_str: str) -> timedelta:
    """Parse timeframe string to timedelta"""
    mapping = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "12h": timedelta(hours=12),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
    }
    return mapping.get(timeframe_str, timedelta(hours=24))


# API Endpoints

@router.get("/system")
async def get_system_analytics(
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> SystemHealthResponse:
    """
    Get real-time system health metrics

    Returns current state of all system components:
    - Agent status distribution
    - Connection statistics
    - Active executions
    - Response time
    - Error rate
    - System resources (CPU, memory)

    Updated every second.
    """
    try:
        metrics = await collector.get_system_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")

    return SystemHealthResponse(
        timestamp=metrics.timestamp.isoformat(),
        total_agents=metrics.total_agents,
        agents_idle=metrics.agents_idle,
        agents_busy=metrics.agents_busy,
        agents_error=metrics.agents_error,
        agents_offline=metrics.agents_offline,
        total_connections=metrics.total_connections,
        connections_active=metrics.connections_active,
        connections_pending=metrics.connections_pending,
        active_executions=metrics.active_executions,
        avg_response_time_ms=metrics.avg_response_time_ms,
        error_rate=metrics.error_rate,
        cpu_usage=metrics.cpu_usage,
        memory_usage=metrics.memory_usage
    )


@router.get("/performance")
async def get_performance_analytics(
    timeframe: str = Query("24h", description="Timeframe (1h, 6h, 12h, 24h, 7d, 30d)"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> PerformanceMetricsResponse:
    """
    Get performance metrics over timeframe

    Returns:
    - Response time percentiles (p50, p95, p99)
    - Throughput (requests per minute)
    - Error rate and success rate
    - Total requests

    Useful for performance monitoring and SLA tracking.
    """
    try:
        timeframe_delta = parse_timeframe(timeframe)
        metrics = await collector.get_performance_metrics(timeframe=timeframe_delta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")

    return PerformanceMetricsResponse(
        timeframe_start=metrics.timeframe_start.isoformat(),
        timeframe_end=metrics.timeframe_end.isoformat(),
        response_time_p50=metrics.response_time_p50,
        response_time_p95=metrics.response_time_p95,
        response_time_p99=metrics.response_time_p99,
        throughput_per_minute=metrics.throughput_per_minute,
        error_rate=metrics.error_rate,
        success_rate=metrics.success_rate,
        total_requests=metrics.total_requests,
        successful_requests=metrics.successful_requests,
        failed_requests=metrics.failed_requests
    )


@router.get("/agents")
async def get_agent_analytics(
    agent_id: Optional[str] = Query(None, description="Specific agent ID (optional)"),
    timeframe: str = Query("7d", description="Timeframe (7d, 30d, 90d)"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> List[AgentMetricsResponse]:
    """
    Get agent performance analytics

    Returns metrics for specific agent or all agents:
    - Tasks completed/failed
    - Average response time
    - Success rate
    - Utilization (% time busy)
    - Total cost and cost per task
    - Uptime percentage

    Useful for identifying top/bottom performers.
    """
    try:
        timeframe_delta = parse_timeframe(timeframe)
        metrics_list = await collector.get_agent_metrics(
            agent_id=agent_id,
            timeframe=timeframe_delta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")

    return [
        AgentMetricsResponse(
            agent_id=m.agent_id,
            agent_role=m.agent_role,
            total_tasks_completed=m.total_tasks_completed,
            total_tasks_failed=m.total_tasks_failed,
            avg_response_time_ms=m.avg_response_time_ms,
            success_rate=m.success_rate,
            utilization=m.utilization,
            total_cost_usd=m.total_cost_usd,
            cost_per_task_usd=m.cost_per_task_usd,
            uptime_percentage=m.uptime_percentage
        )
        for m in metrics_list
    ]


@router.get("/agents/compare")
async def compare_agents(
    agent_ids: List[str] = Query(..., description="Agent IDs to compare"),
    metric: str = Query("success_rate", description="Metric to compare"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict[str, float]:
    """
    Compare multiple agents on a specific metric

    Args:
        agent_ids: List of agent IDs to compare
        metric: Metric to compare (success_rate, avg_response_time, total_cost, utilization)

    Returns:
        Dictionary mapping agent_id to metric value

    Useful for ranking agents and identifying best/worst performers.
    """
    try:
        comparison = await collector.get_agent_comparison(
            agent_ids=agent_ids,
            metric=metric
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare agents: {str(e)}")

    return comparison


@router.get("/executions")
async def get_execution_analytics(
    timeframe: str = Query("30d", description="Timeframe (7d, 30d, 90d)"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> ExecutionAnalyticsResponse:
    """
    Get execution analytics over timeframe

    Returns comprehensive execution statistics:
    - Total/successful/failed executions
    - Execution time distribution (avg, p50, p95, p99)
    - Total cost and cost per execution
    - Most common graph patterns
    - Cost breakdown by model

    Useful for understanding execution patterns and costs.
    """
    try:
        timeframe_delta = parse_timeframe(timeframe)
        analytics = await collector.get_execution_analytics(timeframe=timeframe_delta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect analytics: {str(e)}")

    return ExecutionAnalyticsResponse(
        timeframe_start=analytics.timeframe_start.isoformat(),
        timeframe_end=analytics.timeframe_end.isoformat(),
        total_executions=analytics.total_executions,
        successful_executions=analytics.successful_executions,
        failed_executions=analytics.failed_executions,
        avg_execution_time_seconds=analytics.avg_execution_time_seconds,
        execution_time_p50=analytics.execution_time_p50,
        execution_time_p95=analytics.execution_time_p95,
        execution_time_p99=analytics.execution_time_p99,
        total_cost_usd=analytics.total_cost_usd,
        avg_cost_per_execution_usd=analytics.avg_cost_per_execution_usd,
        most_common_patterns=analytics.most_common_patterns,
        cost_by_model=analytics.cost_by_model
    )


@router.get("/trends/{metric}")
async def get_trend(
    metric: str,
    timeframe: str = Query("30d", description="Timeframe (7d, 30d, 90d)"),
    granularity: str = Query("day", description="Granularity (hour, day, week)"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> TrendAnalysisResponse:
    """
    Get trend analysis for specific metric

    Args:
        metric: Metric to analyze (execution_count, success_rate, etc.)
        timeframe: Time period to analyze
        granularity: Data point granularity (hour, day, week)

    Returns:
        Trend analysis with:
        - Time series data points
        - Trend direction (up, down, stable)
        - Growth rate percentage
        - Detected anomalies

    Useful for identifying trends and anomalies over time.
    """
    try:
        timeframe_delta = parse_timeframe(timeframe)
        trend = await collector.get_trend_analysis(
            metric=metric,
            timeframe=timeframe_delta,
            granularity=granularity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze trend: {str(e)}")

    return TrendAnalysisResponse(
        metric_name=trend.metric_name,
        timeframe_start=trend.timeframe_start.isoformat(),
        timeframe_end=trend.timeframe_end.isoformat(),
        granularity=trend.granularity,
        data_points=[
            DataPoint(timestamp=ts.isoformat(), value=val)
            for ts, val in trend.data_points
        ],
        trend_direction=trend.trend_direction,
        growth_rate=trend.growth_rate,
        anomalies=[
            Anomaly(timestamp=ts.isoformat(), value=val, reason=reason)
            for ts, val, reason in trend.anomalies
        ]
    )


@router.get("/forecast")
async def get_forecast(
    horizon: str = Query("7d", description="Forecast horizon (7d, 14d, 30d)"),
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> UsageForecastResponse:
    """
    Get usage forecast for future period

    Args:
        horizon: Forecast horizon (7d, 14d, 30d)

    Returns:
        Usage forecast with:
        - Predicted execution volume
        - Predicted cost
        - Predicted resource needs (agents, connections)
        - Confidence intervals

    Uses linear extrapolation from recent trends.
    Useful for capacity planning and budgeting.
    """
    try:
        horizon_delta = parse_timeframe(horizon)
        forecast = await collector.forecast_usage(horizon=horizon_delta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")

    return UsageForecastResponse(
        forecast_start=forecast.forecast_start.isoformat(),
        forecast_end=forecast.forecast_end.isoformat(),
        predicted_execution_volume=forecast.predicted_execution_volume,
        predicted_cost_usd=forecast.predicted_cost_usd,
        predicted_resource_needs=forecast.predicted_resource_needs,
        confidence_lower=forecast.confidence_lower,
        confidence_upper=forecast.confidence_upper,
        forecast_method=forecast.forecast_method
    )


@router.get("/summary")
async def get_analytics_summary(
    collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict:
    """
    Get comprehensive analytics summary

    Returns combined summary of:
    - System health
    - Performance metrics (24h)
    - Top 5 agents by success rate
    - Execution analytics (30d)
    - Usage forecast (7d)

    Useful for executive dashboards and overview pages.
    """
    try:
        # Collect all metrics in parallel
        health = await collector.get_system_health()
        performance = await collector.get_performance_metrics(timeframe=timedelta(hours=24))
        agents = await collector.get_agent_metrics(timeframe=timedelta(days=7))
        executions = await collector.get_execution_analytics(timeframe=timedelta(days=30))
        forecast = await collector.forecast_usage(horizon=timedelta(days=7))

        # Sort agents by success rate
        top_agents = sorted(agents, key=lambda a: a.success_rate, reverse=True)[:5]

        return {
            "system_health": {
                "status": "healthy" if health.error_rate < 0.05 else "degraded",
                "total_agents": health.total_agents,
                "active_executions": health.active_executions,
                "error_rate": health.error_rate
            },
            "performance_24h": {
                "avg_response_time_ms": performance.response_time_p50,
                "throughput_per_minute": performance.throughput_per_minute,
                "success_rate": performance.success_rate
            },
            "top_agents": [
                {
                    "agent_id": a.agent_id,
                    "role": a.agent_role,
                    "success_rate": a.success_rate,
                    "tasks_completed": a.total_tasks_completed
                }
                for a in top_agents
            ],
            "executions_30d": {
                "total": executions.total_executions,
                "successful": executions.successful_executions,
                "avg_time_seconds": executions.avg_execution_time_seconds,
                "total_cost_usd": executions.total_cost_usd
            },
            "forecast_7d": {
                "predicted_executions": forecast.predicted_execution_volume,
                "predicted_cost_usd": forecast.predicted_cost_usd,
                "confidence": f"{forecast.confidence_lower:.0%} - {forecast.confidence_upper:.0%}"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
