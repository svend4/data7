"""
Metrics Collection Service

Collects and aggregates system metrics for monitoring and analytics
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

from sqlalchemy import select, func, and_, or_, case, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import (
    AgentModel,
    TaskModel,
    ConnectionModel,
    GraphExecutionModel,
    MessageModel
)


@dataclass
class SystemHealthMetrics:
    """Real-time system health metrics"""
    timestamp: datetime
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
    error_rate: float  # 0.0-1.0
    cpu_usage: float  # 0.0-1.0 (not implemented, placeholder)
    memory_usage: float  # 0.0-1.0 (not implemented, placeholder)


@dataclass
class PerformanceMetrics:
    """Performance metrics over a timeframe"""
    timeframe_start: datetime
    timeframe_end: datetime
    response_time_p50: float  # milliseconds
    response_time_p95: float  # milliseconds
    response_time_p99: float  # milliseconds
    throughput_per_minute: float  # requests per minute
    error_rate: float  # 0.0-1.0
    success_rate: float  # 0.0-1.0
    total_requests: int
    successful_requests: int
    failed_requests: int


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    agent_id: str
    agent_role: str
    total_tasks_completed: int
    total_tasks_failed: int
    avg_response_time_ms: float
    success_rate: float  # 0.0-1.0
    utilization: float  # 0.0-1.0 (% time busy)
    total_cost_usd: float
    cost_per_task_usd: float
    uptime_percentage: float  # 0.0-1.0


@dataclass
class ExecutionAnalytics:
    """Execution analytics over a timeframe"""
    timeframe_start: datetime
    timeframe_end: datetime
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_seconds: float
    execution_time_p50: float
    execution_time_p95: float
    execution_time_p99: float
    total_cost_usd: float
    avg_cost_per_execution_usd: float
    most_common_patterns: List[Dict[str, any]]
    cost_by_model: Dict[str, float]


@dataclass
class TrendAnalysis:
    """Trend analysis for a specific metric"""
    metric_name: str
    timeframe_start: datetime
    timeframe_end: datetime
    granularity: str  # hour, day, week
    data_points: List[Tuple[datetime, float]]  # (timestamp, value)
    trend_direction: str  # up, down, stable
    growth_rate: float  # percentage
    anomalies: List[Tuple[datetime, float, str]]  # (timestamp, value, reason)


@dataclass
class UsageForecast:
    """Usage forecast for future period"""
    forecast_start: datetime
    forecast_end: datetime
    predicted_execution_volume: int
    predicted_cost_usd: float
    predicted_resource_needs: Dict[str, int]
    confidence_lower: float  # lower bound confidence (0.0-1.0)
    confidence_upper: float  # upper bound confidence (0.0-1.0)
    forecast_method: str  # linear, exponential, etc.


class MetricsCollector:
    """Collects and aggregates system metrics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # System Metrics

    async def get_system_health(self) -> SystemHealthMetrics:
        """
        Get real-time system health metrics

        Returns current state of all system components
        """
        now = datetime.utcnow()

        # Agent statistics
        agent_stats = await self.db.execute(
            select(
                func.count(AgentModel.id).label('total'),
                func.sum(case((AgentModel.status == 'idle', 1), else_=0)).label('idle'),
                func.sum(case((AgentModel.status == 'busy', 1), else_=0)).label('busy'),
                func.sum(case((AgentModel.status == 'error', 1), else_=0)).label('error'),
                func.sum(case((AgentModel.status == 'offline', 1), else_=0)).label('offline'),
            )
        )
        agent_row = agent_stats.first()

        # Connection statistics
        conn_stats = await self.db.execute(
            select(
                func.count(ConnectionModel.id).label('total'),
                func.sum(case((ConnectionModel.status == 'connected', 1), else_=0)).label('active'),
                func.sum(case((ConnectionModel.status == 'pending', 1), else_=0)).label('pending'),
            )
        )
        conn_row = conn_stats.first()

        # Active executions
        exec_count = await self.db.execute(
            select(func.count(GraphExecutionModel.id))
            .where(GraphExecutionModel.status.in_(['queued', 'running']))
        )
        active_execs = exec_count.scalar() or 0

        # Average response time (last hour)
        hour_ago = now - timedelta(hours=1)
        task_stats = await self.db.execute(
            select(func.avg(TaskModel.processing_time_ms))
            .where(
                and_(
                    TaskModel.status == 'completed',
                    TaskModel.updated_at >= hour_ago
                )
            )
        )
        avg_response = task_stats.scalar() or 0.0

        # Error rate (last hour)
        error_stats = await self.db.execute(
            select(
                func.count(TaskModel.id).label('total'),
                func.sum(case((TaskModel.status == 'failed', 1), else_=0)).label('failed'),
            )
            .where(TaskModel.created_at >= hour_ago)
        )
        error_row = error_stats.first()
        total_tasks = error_row.total or 0
        failed_tasks = error_row.failed or 0
        error_rate = failed_tasks / total_tasks if total_tasks > 0 else 0.0

        return SystemHealthMetrics(
            timestamp=now,
            total_agents=agent_row.total or 0,
            agents_idle=agent_row.idle or 0,
            agents_busy=agent_row.busy or 0,
            agents_error=agent_row.error or 0,
            agents_offline=agent_row.offline or 0,
            total_connections=conn_row.total or 0,
            connections_active=conn_row.active or 0,
            connections_pending=conn_row.pending or 0,
            active_executions=active_execs,
            avg_response_time_ms=float(avg_response),
            error_rate=error_rate,
            cpu_usage=0.0,  # Placeholder
            memory_usage=0.0  # Placeholder
        )

    async def get_performance_metrics(
        self,
        timeframe: timedelta = timedelta(hours=24)
    ) -> PerformanceMetrics:
        """
        Get performance metrics over timeframe

        Calculates response time percentiles, throughput, error rates
        """
        now = datetime.utcnow()
        start = now - timeframe

        # Fetch all completed tasks in timeframe
        tasks = await self.db.execute(
            select(TaskModel.processing_time_ms, TaskModel.status)
            .where(
                and_(
                    TaskModel.updated_at >= start,
                    TaskModel.status.in_(['completed', 'failed'])
                )
            )
        )
        task_rows = tasks.all()

        # Calculate statistics
        response_times = [r.processing_time_ms for r in task_rows if r.processing_time_ms]
        total_requests = len(task_rows)
        successful = sum(1 for r in task_rows if r.status == 'completed')
        failed = sum(1 for r in task_rows if r.status == 'failed')

        if response_times:
            sorted_times = sorted(response_times)
            p50_idx = int(len(sorted_times) * 0.50)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)

            response_time_p50 = sorted_times[p50_idx] if p50_idx < len(sorted_times) else 0
            response_time_p95 = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
            response_time_p99 = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
        else:
            response_time_p50 = response_time_p95 = response_time_p99 = 0

        # Throughput
        minutes = timeframe.total_seconds() / 60
        throughput = total_requests / minutes if minutes > 0 else 0

        # Rates
        success_rate = successful / total_requests if total_requests > 0 else 0
        error_rate = failed / total_requests if total_requests > 0 else 0

        return PerformanceMetrics(
            timeframe_start=start,
            timeframe_end=now,
            response_time_p50=float(response_time_p50),
            response_time_p95=float(response_time_p95),
            response_time_p99=float(response_time_p99),
            throughput_per_minute=throughput,
            error_rate=error_rate,
            success_rate=success_rate,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed
        )

    # Agent Metrics

    async def get_agent_metrics(
        self,
        agent_id: Optional[str] = None,
        timeframe: timedelta = timedelta(days=7)
    ) -> List[AgentMetrics]:
        """
        Get agent performance metrics

        Returns metrics for specific agent or all agents
        """
        now = datetime.utcnow()
        start = now - timeframe

        # Build query
        query = select(
            AgentModel.id,
            AgentModel.role,
            AgentModel.total_tasks_completed,
            AgentModel.status
        )

        if agent_id:
            query = query.where(AgentModel.id == agent_id)

        agents = await self.db.execute(query)
        agent_rows = agents.all()

        metrics = []
        for agent in agent_rows:
            # Get task statistics for this agent
            task_stats = await self.db.execute(
                select(
                    func.count(TaskModel.id).label('total'),
                    func.sum(case((TaskModel.status == 'completed', 1), else_=0)).label('completed'),
                    func.sum(case((TaskModel.status == 'failed', 1), else_=0)).label('failed'),
                    func.avg(TaskModel.processing_time_ms).label('avg_time'),
                )
                .where(
                    and_(
                        TaskModel.agent_id == agent.id,
                        TaskModel.created_at >= start
                    )
                )
            )
            stats = task_stats.first()

            total = stats.total or 0
            completed = stats.completed or 0
            failed = stats.failed or 0
            avg_time = stats.avg_time or 0

            success_rate = completed / total if total > 0 else 0

            # Estimate cost (placeholder - would need actual LLM usage tracking)
            cost_per_task = 0.01  # $0.01 per task (placeholder)
            total_cost = completed * cost_per_task

            # Utilization (placeholder - would need detailed time tracking)
            utilization = 0.5 if agent.status == 'busy' else 0.2

            # Uptime (placeholder)
            uptime = 0.99  # 99% uptime

            metrics.append(AgentMetrics(
                agent_id=agent.id,
                agent_role=agent.role,
                total_tasks_completed=completed,
                total_tasks_failed=failed,
                avg_response_time_ms=float(avg_time),
                success_rate=success_rate,
                utilization=utilization,
                total_cost_usd=total_cost,
                cost_per_task_usd=cost_per_task,
                uptime_percentage=uptime
            ))

        return metrics

    async def get_agent_comparison(
        self,
        agent_ids: List[str],
        metric: str = "success_rate"
    ) -> Dict[str, float]:
        """
        Compare multiple agents on a specific metric

        Args:
            agent_ids: List of agent IDs to compare
            metric: Metric to compare (success_rate, avg_time, cost, etc.)

        Returns:
            Dictionary mapping agent_id to metric value
        """
        metrics = await self.get_agent_metrics()

        result = {}
        for m in metrics:
            if m.agent_id in agent_ids:
                if metric == "success_rate":
                    result[m.agent_id] = m.success_rate
                elif metric == "avg_response_time":
                    result[m.agent_id] = m.avg_response_time_ms
                elif metric == "total_cost":
                    result[m.agent_id] = m.total_cost_usd
                elif metric == "utilization":
                    result[m.agent_id] = m.utilization

        return result

    # Execution Metrics

    async def get_execution_analytics(
        self,
        timeframe: timedelta = timedelta(days=30)
    ) -> ExecutionAnalytics:
        """
        Get execution analytics over timeframe

        Returns comprehensive execution statistics
        """
        now = datetime.utcnow()
        start = now - timeframe

        # Execution statistics
        exec_stats = await self.db.execute(
            select(
                func.count(GraphExecutionModel.id).label('total'),
                func.sum(case((GraphExecutionModel.status == 'completed', 1), else_=0)).label('completed'),
                func.sum(case((GraphExecutionModel.status == 'failed', 1), else_=0)).label('failed'),
            )
            .where(GraphExecutionModel.created_at >= start)
        )
        stats = exec_stats.first()

        # Execution times
        exec_times = await self.db.execute(
            select(GraphExecutionModel.execution_time_seconds)
            .where(
                and_(
                    GraphExecutionModel.created_at >= start,
                    GraphExecutionModel.status == 'completed',
                    GraphExecutionModel.execution_time_seconds.isnot(None)
                )
            )
        )
        times = [r[0] for r in exec_times.all() if r[0]]

        if times:
            avg_time = statistics.mean(times)
            sorted_times = sorted(times)
            p50 = sorted_times[int(len(sorted_times) * 0.50)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_time = p50 = p95 = p99 = 0

        # Cost estimation (placeholder)
        total_cost = (stats.completed or 0) * 0.10  # $0.10 per execution
        avg_cost = total_cost / (stats.completed or 1)

        return ExecutionAnalytics(
            timeframe_start=start,
            timeframe_end=now,
            total_executions=stats.total or 0,
            successful_executions=stats.completed or 0,
            failed_executions=stats.failed or 0,
            avg_execution_time_seconds=avg_time,
            execution_time_p50=p50,
            execution_time_p95=p95,
            execution_time_p99=p99,
            total_cost_usd=total_cost,
            avg_cost_per_execution_usd=avg_cost,
            most_common_patterns=[],  # Would need pattern analysis
            cost_by_model={"gpt-3.5-turbo": total_cost}  # Placeholder
        )

    # Trend Analysis

    async def get_trend_analysis(
        self,
        metric: str,
        timeframe: timedelta = timedelta(days=30),
        granularity: str = "day"
    ) -> TrendAnalysis:
        """
        Analyze metric trend over time

        Args:
            metric: Metric to analyze (execution_count, success_rate, etc.)
            timeframe: Time period to analyze
            granularity: Data point granularity (hour, day, week)

        Returns:
            TrendAnalysis with time series and trend detection
        """
        now = datetime.utcnow()
        start = now - timeframe

        # Generate time buckets based on granularity
        if granularity == "hour":
            bucket_size = timedelta(hours=1)
        elif granularity == "day":
            bucket_size = timedelta(days=1)
        elif granularity == "week":
            bucket_size = timedelta(weeks=1)
        else:
            bucket_size = timedelta(days=1)

        # Collect data points
        data_points = []
        current = start
        while current < now:
            next_bucket = current + bucket_size

            if metric == "execution_count":
                count = await self.db.execute(
                    select(func.count(GraphExecutionModel.id))
                    .where(
                        and_(
                            GraphExecutionModel.created_at >= current,
                            GraphExecutionModel.created_at < next_bucket
                        )
                    )
                )
                value = count.scalar() or 0
                data_points.append((current, float(value)))

            current = next_bucket

        # Calculate trend direction
        if len(data_points) >= 2:
            first_half = data_points[:len(data_points)//2]
            second_half = data_points[len(data_points)//2:]

            avg_first = statistics.mean(v for _, v in first_half)
            avg_second = statistics.mean(v for _, v in second_half)

            if avg_second > avg_first * 1.1:
                trend_direction = "up"
                growth_rate = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
            elif avg_second < avg_first * 0.9:
                trend_direction = "down"
                growth_rate = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
            else:
                trend_direction = "stable"
                growth_rate = 0
        else:
            trend_direction = "stable"
            growth_rate = 0

        # Detect anomalies (simple: values > 2 std dev from mean)
        anomalies = []
        if len(data_points) >= 3:
            values = [v for _, v in data_points]
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values)

            for timestamp, value in data_points:
                if abs(value - mean_val) > 2 * std_dev:
                    reason = "spike" if value > mean_val else "drop"
                    anomalies.append((timestamp, value, reason))

        return TrendAnalysis(
            metric_name=metric,
            timeframe_start=start,
            timeframe_end=now,
            granularity=granularity,
            data_points=data_points,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            anomalies=anomalies
        )

    # Forecasting

    async def forecast_usage(
        self,
        horizon: timedelta = timedelta(days=7)
    ) -> UsageForecast:
        """
        Forecast future usage based on historical data

        Uses simple linear extrapolation from recent trend
        """
        now = datetime.utcnow()
        forecast_end = now + horizon

        # Get recent trend (last 30 days)
        trend = await self.get_trend_analysis(
            metric="execution_count",
            timeframe=timedelta(days=30),
            granularity="day"
        )

        # Simple linear forecast
        if len(trend.data_points) >= 7:
            recent_values = [v for _, v in trend.data_points[-7:]]
            avg_daily = statistics.mean(recent_values)

            # Project forward
            days_ahead = horizon.days
            predicted_volume = int(avg_daily * days_ahead)
            predicted_cost = predicted_volume * 0.10  # $0.10 per execution

            # Confidence intervals (±20%)
            confidence_lower = 0.8
            confidence_upper = 1.2
        else:
            predicted_volume = 0
            predicted_cost = 0
            confidence_lower = 0.5
            confidence_upper = 1.5

        return UsageForecast(
            forecast_start=now,
            forecast_end=forecast_end,
            predicted_execution_volume=predicted_volume,
            predicted_cost_usd=predicted_cost,
            predicted_resource_needs={
                "agents": max(1, predicted_volume // 100),
                "connections": max(1, predicted_volume // 50)
            },
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            forecast_method="linear_extrapolation"
        )
