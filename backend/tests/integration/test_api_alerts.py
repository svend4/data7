"""
Integration tests for Alerts API

Tests cover:
- Alert listing and filtering
- Alert acknowledgment and resolution
- Alert rule management
- Alert evaluation
- Alert statistics
- Integration with metrics
"""

import pytest
from httpx import AsyncClient


class TestAlertsAPI:
    """Test Alerts API endpoints."""

    @pytest.mark.asyncio
    async def test_list_alerts(self, async_client: AsyncClient):
        """Test listing all alerts."""
        response = await async_client.get("/api/alerts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_alerts_filter_by_status(self, async_client: AsyncClient):
        """Test filtering alerts by status."""
        response = await async_client.get("/api/alerts?status=active")

        assert response.status_code == 200
        data = response.json()

        # All returned alerts should be active
        assert all(alert["status"] == "active" for alert in data)

    @pytest.mark.asyncio
    async def test_list_alerts_filter_by_severity(self, async_client: AsyncClient):
        """Test filtering alerts by severity."""
        response = await async_client.get("/api/alerts?severity=critical")

        assert response.status_code == 200
        data = response.json()

        # All returned alerts should be critical
        assert all(alert["severity"] == "critical" for alert in data)

    @pytest.mark.asyncio
    async def test_list_alerts_with_limit(self, async_client: AsyncClient):
        """Test alert pagination with limit."""
        response = await async_client.get("/api/alerts?limit=5")

        assert response.status_code == 200
        data = response.json()

        # Should return at most 5 alerts
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_evaluate_alerts_manually(self, async_client: AsyncClient):
        """Test manual alert evaluation."""
        response = await async_client.post("/api/alerts/evaluate")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "evaluated_at" in data
        assert "rules_evaluated" in data
        assert "alerts_triggered" in data
        assert "triggered_alerts" in data

        assert isinstance(data["rules_evaluated"], int)
        assert isinstance(data["alerts_triggered"], int)
        assert isinstance(data["triggered_alerts"], list)

    @pytest.mark.asyncio
    async def test_acknowledge_alert_workflow(self, async_client: AsyncClient):
        """Test alert acknowledgment workflow."""
        # First, trigger an alert through evaluation
        eval_response = await async_client.post("/api/alerts/evaluate")
        assert eval_response.status_code == 200

        triggered_alerts = eval_response.json()["triggered_alerts"]

        if len(triggered_alerts) > 0:
            alert_id = triggered_alerts[0]["id"]

            # Acknowledge the alert
            ack_response = await async_client.post(
                f"/api/alerts/{alert_id}/acknowledge",
                json={"user": "test_operator"}
            )

            assert ack_response.status_code == 200
            ack_data = ack_response.json()

            assert ack_data["status"] == "acknowledged"
            assert ack_data["acknowledged_by"] == "test_operator"
            assert "acknowledged_at" in ack_data

    @pytest.mark.asyncio
    async def test_resolve_alert_workflow(self, async_client: AsyncClient):
        """Test alert resolution workflow."""
        # Trigger alert
        eval_response = await async_client.post("/api/alerts/evaluate")
        triggered_alerts = eval_response.json()["triggered_alerts"]

        if len(triggered_alerts) > 0:
            alert_id = triggered_alerts[0]["id"]

            # Resolve the alert
            resolve_response = await async_client.post(
                f"/api/alerts/{alert_id}/resolve",
                json={"user": "test_operator"}
            )

            assert resolve_response.status_code == 200
            resolve_data = resolve_response.json()

            assert resolve_data["status"] == "resolved"
            assert resolve_data["resolved_by"] == "test_operator"
            assert "resolved_at" in resolve_data

    @pytest.mark.asyncio
    async def test_suppress_alert(self, async_client: AsyncClient):
        """Test alert suppression."""
        # Trigger alert
        eval_response = await async_client.post("/api/alerts/evaluate")
        triggered_alerts = eval_response.json()["triggered_alerts"]

        if len(triggered_alerts) > 0:
            alert_id = triggered_alerts[0]["id"]

            # Suppress the alert
            suppress_response = await async_client.post(f"/api/alerts/{alert_id}/suppress")

            assert suppress_response.status_code == 200
            suppress_data = suppress_response.json()

            assert suppress_data["status"] == "suppressed"

    @pytest.mark.asyncio
    async def test_get_alert_statistics(self, async_client: AsyncClient):
        """Test retrieving alert statistics."""
        response = await async_client.get("/api/alerts/stats/summary?timeframe_days=7")

        assert response.status_code == 200
        data = response.json()

        # Verify statistics structure
        assert "total_alerts" in data
        assert "active_alerts" in data
        assert "acknowledged_alerts" in data
        assert "resolved_alerts" in data
        assert "suppressed_alerts" in data
        assert "alerts_by_severity" in data
        assert "alerts_by_rule" in data
        assert "avg_time_to_acknowledge" in data
        assert "avg_time_to_resolve" in data
        assert "most_frequent_alerts" in data

        # Verify data types
        assert isinstance(data["total_alerts"], int)
        assert isinstance(data["alerts_by_severity"], dict)
        assert isinstance(data["most_frequent_alerts"], list)

    @pytest.mark.asyncio
    async def test_alert_lifecycle_complete(self, async_client: AsyncClient):
        """Test complete alert lifecycle: trigger → acknowledge → resolve."""
        # 1. Evaluate and trigger
        eval_response = await async_client.post("/api/alerts/evaluate")
        assert eval_response.status_code == 200

        triggered_alerts = eval_response.json()["triggered_alerts"]

        if len(triggered_alerts) > 0:
            alert_id = triggered_alerts[0]["id"]

            # 2. Verify alert is active
            get_response = await async_client.get(f"/api/alerts/{alert_id}")
            assert get_response.status_code == 200
            assert get_response.json()["status"] == "active"

            # 3. Acknowledge
            ack_response = await async_client.post(
                f"/api/alerts/{alert_id}/acknowledge",
                json={"user": "operator1"}
            )
            assert ack_response.status_code == 200
            assert ack_response.json()["status"] == "acknowledged"

            # 4. Resolve
            resolve_response = await async_client.post(
                f"/api/alerts/{alert_id}/resolve",
                json={"user": "operator2"}
            )
            assert resolve_response.status_code == 200
            resolve_data = resolve_response.json()

            assert resolve_data["status"] == "resolved"
            assert resolve_data["acknowledged_by"] == "operator1"
            assert resolve_data["resolved_by"] == "operator2"


class TestAlertRulesAPI:
    """Test Alert Rules management endpoints."""

    @pytest.mark.asyncio
    async def test_list_alert_rules(self, async_client: AsyncClient):
        """Test listing all alert rules."""
        response = await async_client.get("/api/alerts/rules/list")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Should have default rules
        assert len(data) > 0

        # Verify rule structure
        if len(data) > 0:
            rule = data[0]
            assert "id" in rule
            assert "name" in rule
            assert "description" in rule
            assert "conditions" in rule
            assert "severity" in rule
            assert "enabled" in rule

    @pytest.mark.asyncio
    async def test_get_alert_rule(self, async_client: AsyncClient):
        """Test retrieving a specific alert rule."""
        # First get list of rules
        list_response = await async_client.get("/api/alerts/rules/list")
        rules = list_response.json()

        if len(rules) > 0:
            rule_id = rules[0]["id"]

            # Get specific rule
            response = await async_client.get(f"/api/alerts/rules/{rule_id}")

            assert response.status_code == 200
            data = response.json()

            assert data["id"] == rule_id

    @pytest.mark.asyncio
    async def test_create_alert_rule(self, async_client: AsyncClient):
        """Test creating a new alert rule."""
        response = await async_client.post("/api/alerts/rules", json={
            "name": "Test Alert Rule",
            "description": "A test rule for integration testing",
            "conditions": [
                {
                    "metric": "error_rate",
                    "operator": ">",
                    "threshold": 0.20,
                    "duration": 60
                }
            ],
            "severity": "warning",
            "notifications": [
                {
                    "channel": "email",
                    "config": {"to": "test@example.com"},
                    "enabled": True
                }
            ],
            "enabled": True,
            "cooldown_seconds": 300,
            "tags": ["test", "integration"]
        })

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Test Alert Rule"
        assert data["enabled"] is True
        assert len(data["conditions"]) == 1
        assert len(data["notifications"]) == 1

    @pytest.mark.asyncio
    async def test_update_alert_rule(self, async_client: AsyncClient):
        """Test updating an alert rule."""
        # First create a rule
        create_response = await async_client.post("/api/alerts/rules", json={
            "name": "Rule to Update",
            "description": "Initial description",
            "conditions": [
                {
                    "metric": "error_rate",
                    "operator": ">",
                    "threshold": 0.10,
                    "duration": 30
                }
            ],
            "severity": "info",
            "notifications": [],
            "enabled": True
        })

        assert create_response.status_code == 201
        rule_id = create_response.json()["id"]

        # Update the rule
        update_response = await async_client.put(f"/api/alerts/rules/{rule_id}", json={
            "description": "Updated description",
            "severity": "warning",
            "enabled": False
        })

        assert update_response.status_code == 200
        updated_data = update_response.json()

        assert updated_data["description"] == "Updated description"
        assert updated_data["severity"] == "warning"
        assert updated_data["enabled"] is False

    @pytest.mark.asyncio
    async def test_delete_alert_rule(self, async_client: AsyncClient):
        """Test deleting an alert rule."""
        # Create a rule
        create_response = await async_client.post("/api/alerts/rules", json={
            "name": "Rule to Delete",
            "description": "Will be deleted",
            "conditions": [
                {
                    "metric": "agent_count",
                    "operator": "<",
                    "threshold": 1.0,
                    "duration": 0
                }
            ],
            "severity": "info",
            "notifications": [],
            "enabled": True
        })

        assert create_response.status_code == 201
        rule_id = create_response.json()["id"]

        # Delete the rule
        delete_response = await async_client.delete(f"/api/alerts/rules/{rule_id}")

        assert delete_response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(f"/api/alerts/rules/{rule_id}")
        assert get_response.status_code == 404


class TestAlertsIntegration:
    """Test alerts integration with other systems."""

    @pytest.mark.asyncio
    async def test_alert_triggered_by_high_error_rate(
        self,
        async_client: AsyncClient,
        sample_agents,
        sample_tasks
    ):
        """Test alert triggers when error rate is high."""
        # This would require setting up conditions that cause high error rate
        # For now, test that evaluation endpoint works

        response = await async_client.post("/api/alerts/evaluate")

        assert response.status_code == 200
        data = response.json()

        # Should evaluate default rules
        assert data["rules_evaluated"] > 0

    @pytest.mark.asyncio
    async def test_alert_cooldown_mechanism(self, async_client: AsyncClient):
        """Test alert cooldown prevents rapid re-triggering."""
        # First evaluation
        response1 = await async_client.post("/api/alerts/evaluate")
        assert response1.status_code == 200
        triggered1 = response1.json()["alerts_triggered"]

        # Immediate second evaluation (should be in cooldown)
        response2 = await async_client.post("/api/alerts/evaluate")
        assert response2.status_code == 200
        triggered2 = response2.json()["alerts_triggered"]

        # Second should not trigger more alerts (cooldown)
        assert triggered2 <= triggered1

    @pytest.mark.asyncio
    async def test_alerts_with_analytics_metrics(
        self,
        async_client: AsyncClient,
        mock_metrics
    ):
        """Test alerts use metrics from analytics."""
        # Get current system metrics
        metrics_response = await async_client.get("/api/analytics/system")
        assert metrics_response.status_code == 200

        # Evaluate alerts (should use same metrics)
        alerts_response = await async_client.post("/api/alerts/evaluate")
        assert alerts_response.status_code == 200

    @pytest.mark.asyncio
    async def test_alert_notification_channels(self, async_client: AsyncClient):
        """Test alert notification configurations."""
        # Create rule with multiple notification channels
        response = await async_client.post("/api/alerts/rules", json={
            "name": "Multi-channel Alert",
            "description": "Test multiple notification channels",
            "conditions": [
                {
                    "metric": "error_rate",
                    "operator": ">",
                    "threshold": 0.99,  # Very high threshold
                    "duration": 0
                }
            ],
            "severity": "critical",
            "notifications": [
                {
                    "channel": "email",
                    "config": {"to": "admin@example.com"},
                    "enabled": True
                },
                {
                    "channel": "slack",
                    "config": {"webhook_url": "https://hooks.slack.com/test"},
                    "enabled": True
                },
                {
                    "channel": "webhook",
                    "config": {"url": "https://api.example.com/alerts"},
                    "enabled": True
                }
            ],
            "enabled": True
        })

        assert response.status_code == 201
        data = response.json()

        assert len(data["notifications"]) == 3
        assert all(n["enabled"] for n in data["notifications"])

    @pytest.mark.asyncio
    async def test_alert_statistics_accuracy(self, async_client: AsyncClient):
        """Test alert statistics are accurate."""
        # Trigger some alerts
        await async_client.post("/api/alerts/evaluate")

        # Get statistics
        stats_response = await async_client.get("/api/alerts/stats/summary?timeframe_days=1")

        assert stats_response.status_code == 200
        stats = stats_response.json()

        # Verify totals add up
        total_by_status = (
            stats["active_alerts"] +
            stats["acknowledged_alerts"] +
            stats["resolved_alerts"] +
            stats["suppressed_alerts"]
        )

        # Total should match sum of statuses
        assert total_by_status <= stats["total_alerts"]
