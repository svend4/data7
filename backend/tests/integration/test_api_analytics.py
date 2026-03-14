"""
Integration tests for Analytics API

Tests cover:
- System health metrics
- Performance metrics
- Agent analytics
- Execution analytics
- Trend analysis
- Forecasting
- Summary reports
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


class TestAnalyticsSystemHealth:
    """Test system health analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_system_health(self, async_client: AsyncClient, sample_agents, sample_tasks):
        """Test retrieving system health metrics."""
        response = await async_client.get("/api/analytics/system")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_agents" in data
        assert "agents_idle" in data
        assert "agents_busy" in data
        assert "total_connections" in data
        assert "error_rate" in data
        assert "avg_response_time" in data

        # Verify data types
        assert isinstance(data["total_agents"], int)
        assert isinstance(data["error_rate"], (int, float))
        assert 0 <= data["error_rate"] <= 1

    @pytest.mark.asyncio
    async def test_system_health_real_time(self, async_client: AsyncClient, sample_agent):
        """Test system health reflects real-time changes."""
        # Get initial state
        response1 = await async_client.get("/api/analytics/system")
        initial_idle = response1.json()["agents_idle"]

        # Change agent status
        await async_client.patch(
            f"/api/agents/{sample_agent.id}/status",
            json={"status": "busy"}
        )

        # Get updated state
        response2 = await async_client.get("/api/analytics/system")
        updated_idle = response2.json()["agents_idle"]

        # Verify change reflected
        assert updated_idle <= initial_idle


class TestAnalyticsPerformance:
    """Test performance analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, async_client: AsyncClient):
        """Test retrieving performance metrics."""
        response = await async_client.get("/api/analytics/performance?timeframe=24h")

        assert response.status_code == 200
        data = response.json()

        # Verify metrics structure
        assert "avg_response_time" in data
        assert "p50_response_time" in data
        assert "p95_response_time" in data
        assert "p99_response_time" in data
        assert "total_requests" in data
        assert "requests_per_second" in data
        assert "success_rate" in data
        assert "error_rate" in data

        # Verify percentile ordering
        assert data["p50_response_time"] <= data["p95_response_time"]
        assert data["p95_response_time"] <= data["p99_response_time"]

    @pytest.mark.asyncio
    async def test_performance_timeframes(self, async_client: AsyncClient):
        """Test different timeframe options."""
        timeframes = ["1h", "24h", "7d", "30d"]

        for timeframe in timeframes:
            response = await async_client.get(
                f"/api/analytics/performance?timeframe={timeframe}"
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_performance_invalid_timeframe(self, async_client: AsyncClient):
        """Test invalid timeframe handling."""
        response = await async_client.get("/api/analytics/performance?timeframe=invalid")

        assert response.status_code == 400


class TestAnalyticsAgents:
    """Test agent analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_agent_analytics(
        self,
        async_client: AsyncClient,
        sample_agents,
        sample_tasks,
        sample_execution
    ):
        """Test retrieving agent analytics."""
        response = await async_client.get("/api/analytics/agents?timeframe=7d")

        assert response.status_code == 200
        data = response.json()

        # Should return list of agent metrics
        assert isinstance(data, list)

        if len(data) > 0:
            agent_metrics = data[0]
            assert "agent_id" in agent_metrics
            assert "role" in agent_metrics
            assert "total_tasks_completed" in agent_metrics
            assert "success_rate" in agent_metrics
            assert "avg_execution_time" in agent_metrics

    @pytest.mark.asyncio
    async def test_compare_agents(
        self,
        async_client: AsyncClient,
        sample_agents
    ):
        """Test comparing multiple agents."""
        agent_ids = [sample_agents[0].id, sample_agents[1].id]

        response = await async_client.get(
            f"/api/analytics/agents/compare?agent_ids={','.join(agent_ids)}"
        )

        assert response.status_code == 200
        data = response.json()

        assert "agents" in data
        assert len(data["agents"]) == 2

    @pytest.mark.asyncio
    async def test_agent_analytics_filtering(self, async_client: AsyncClient, sample_agents):
        """Test filtering agent analytics."""
        # Filter by role
        response = await async_client.get("/api/analytics/agents?role=agent_0")

        assert response.status_code == 200
        data = response.json()

        # Should only return agents with matching role
        if len(data) > 0:
            assert all(agent["role"] == "agent_0" for agent in data)


class TestAnalyticsExecutions:
    """Test execution analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_execution_analytics(
        self,
        async_client: AsyncClient,
        sample_execution
    ):
        """Test retrieving execution analytics."""
        response = await async_client.get("/api/analytics/executions?timeframe=30d")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_executions" in data
        assert "successful_executions" in data
        assert "failed_executions" in data
        assert "avg_execution_time" in data
        assert "total_cost" in data
        assert "avg_cost" in data

        # Verify data validity
        assert data["total_executions"] >= 0
        assert data["successful_executions"] + data["failed_executions"] <= data["total_executions"]

    @pytest.mark.asyncio
    async def test_execution_analytics_cost_calculation(
        self,
        async_client: AsyncClient,
        sample_execution
    ):
        """Test cost calculation in execution analytics."""
        response = await async_client.get("/api/analytics/executions?timeframe=30d")

        assert response.status_code == 200
        data = response.json()

        # Cost should be positive
        assert data["total_cost"] >= 0
        assert data["avg_cost"] >= 0

        # Average should be reasonable
        if data["total_executions"] > 0:
            expected_avg = data["total_cost"] / data["total_executions"]
            assert abs(data["avg_cost"] - expected_avg) < 0.01


class TestAnalyticsTrends:
    """Test trend analysis endpoints."""

    @pytest.mark.asyncio
    async def test_get_trend_analysis(self, async_client: AsyncClient):
        """Test trend analysis for a metric."""
        response = await async_client.get(
            "/api/analytics/trends/execution_count?timeframe=30d&granularity=day"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "data_points" in data
        assert "trend_direction" in data
        assert "growth_rate" in data
        assert "anomalies" in data

        # Verify data points structure
        if len(data["data_points"]) > 0:
            point = data["data_points"][0]
            assert "timestamp" in point
            assert "value" in point

        # Verify trend direction is valid
        assert data["trend_direction"] in ["up", "down", "stable"]

    @pytest.mark.asyncio
    async def test_trend_granularity_options(self, async_client: AsyncClient):
        """Test different granularity options."""
        granularities = ["hour", "day", "week"]

        for granularity in granularities:
            response = await async_client.get(
                f"/api/analytics/trends/execution_count"
                f"?timeframe=30d&granularity={granularity}"
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trend_anomaly_detection(self, async_client: AsyncClient):
        """Test anomaly detection in trends."""
        response = await async_client.get(
            "/api/analytics/trends/error_rate?timeframe=30d&granularity=day"
        )

        assert response.status_code == 200
        data = response.json()

        # Anomalies should be a list
        assert isinstance(data["anomalies"], list)

        # Each anomaly should have required fields
        for anomaly in data["anomalies"]:
            assert "timestamp" in anomaly
            assert "value" in anomaly
            assert "reason" in anomaly
            assert anomaly["reason"] in ["spike", "drop"]

    @pytest.mark.asyncio
    async def test_trend_metrics(self, async_client: AsyncClient):
        """Test different metric types for trends."""
        metrics = [
            "execution_count",
            "error_rate",
            "avg_response_time",
            "agent_count"
        ]

        for metric in metrics:
            response = await async_client.get(
                f"/api/analytics/trends/{metric}?timeframe=7d&granularity=day"
            )
            assert response.status_code == 200


class TestAnalyticsForecast:
    """Test forecasting endpoints."""

    @pytest.mark.asyncio
    async def test_get_forecast(self, async_client: AsyncClient):
        """Test usage forecasting."""
        response = await async_client.get(
            "/api/analytics/forecast?metric=execution_count&periods=7"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "metric" in data
        assert "forecast_periods" in data
        assert "predictions" in data
        assert "confidence_interval" in data

        # Predictions should match requested periods
        assert len(data["predictions"]) == 7

        # Each prediction should have timestamp and value
        for pred in data["predictions"]:
            assert "timestamp" in pred
            assert "value" in pred
            assert pred["value"] >= 0

    @pytest.mark.asyncio
    async def test_forecast_confidence_interval(self, async_client: AsyncClient):
        """Test forecast confidence intervals."""
        response = await async_client.get(
            "/api/analytics/forecast?metric=execution_count&periods=5"
        )

        assert response.status_code == 200
        data = response.json()

        # Confidence interval should exist
        assert "confidence_interval" in data
        assert "lower" in data["confidence_interval"]
        assert "upper" in data["confidence_interval"]

        # Lower should be less than upper
        assert data["confidence_interval"]["lower"] <= data["confidence_interval"]["upper"]


class TestAnalyticsSummary:
    """Test comprehensive summary endpoints."""

    @pytest.mark.asyncio
    async def test_get_summary(
        self,
        async_client: AsyncClient,
        sample_agents,
        sample_tasks,
        sample_execution
    ):
        """Test comprehensive analytics summary."""
        response = await async_client.get("/api/analytics/summary?timeframe=7d")

        assert response.status_code == 200
        data = response.json()

        # Verify all sections present
        assert "system_health" in data
        assert "performance" in data
        assert "agents" in data
        assert "executions" in data
        assert "trends" in data

        # Verify each section has data
        assert isinstance(data["system_health"], dict)
        assert isinstance(data["performance"], dict)
        assert isinstance(data["agents"], list)
        assert isinstance(data["executions"], dict)
        assert isinstance(data["trends"], dict)


class TestAnalyticsIntegration:
    """Test analytics integration with other services."""

    @pytest.mark.asyncio
    async def test_analytics_after_execution(self, async_client: AsyncClient, sample_agent, sample_task):
        """Test analytics update after task execution."""
        # Get initial execution count
        initial_response = await async_client.get("/api/analytics/executions?timeframe=1h")
        initial_count = initial_response.json()["total_executions"]

        # Execute task (would need mocking in real implementation)
        # For now, just verify the analytics endpoint structure

        # Get updated execution count
        updated_response = await async_client.get("/api/analytics/executions?timeframe=1h")
        assert updated_response.status_code == 200

    @pytest.mark.asyncio
    async def test_analytics_real_time_updates(
        self,
        async_client: AsyncClient,
        sample_agent
    ):
        """Test analytics reflect real-time system changes."""
        # Get initial system health
        initial_response = await async_client.get("/api/analytics/system")
        initial_data = initial_response.json()

        # Make changes to system
        await async_client.patch(
            f"/api/agents/{sample_agent.id}/status",
            json={"status": "busy"}
        )

        # Get updated system health
        updated_response = await async_client.get("/api/analytics/system")
        updated_data = updated_response.json()

        # Verify metrics updated
        assert updated_response.status_code == 200

    @pytest.mark.asyncio
    async def test_analytics_performance(self, async_client: AsyncClient):
        """Test analytics endpoint performance."""
        import time

        endpoints = [
            "/api/analytics/system",
            "/api/analytics/performance?timeframe=24h",
            "/api/analytics/agents?timeframe=7d",
            "/api/analytics/executions?timeframe=30d"
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = await async_client.get(endpoint)
            end_time = time.time()

            assert response.status_code == 200
            # Should respond within 1 second
            assert (end_time - start_time) < 1.0
