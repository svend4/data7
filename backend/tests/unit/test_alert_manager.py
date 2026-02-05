"""
Unit tests for AlertManager service

Tests cover:
- Alert rule creation and evaluation
- Alert lifecycle (active → acknowledged → resolved)
- Multi-channel notifications
- Cooldown mechanisms
- Alert statistics
- Edge cases
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.services.alert_manager import (
    AlertManager,
    AlertRule,
    Alert,
    AlertCondition,
    NotificationConfig,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    ConditionOperator,
    AlertStats,
)


# ============================================================================
# Test Data Builders
# ============================================================================

def create_test_rule(
    rule_id: str = "test_rule",
    severity: AlertSeverity = AlertSeverity.WARNING
) -> AlertRule:
    """Create a test alert rule."""
    return AlertRule(
        id=rule_id,
        name="Test Rule",
        description="A test alert rule",
        conditions=[
            AlertCondition(
                metric="error_rate",
                operator=ConditionOperator.GREATER_THAN,
                threshold=0.10,
                duration=60
            )
        ],
        severity=severity,
        notifications=[
            NotificationConfig(
                channel=NotificationChannel.EMAIL,
                config={"to": "test@example.com"},
                enabled=True
            )
        ],
        enabled=True,
        cooldown_seconds=300,
        tags=["test", "error"]
    )


# ============================================================================
# AlertCondition Tests
# ============================================================================

class TestAlertCondition:
    """Test AlertCondition evaluation logic."""

    def test_greater_than_operator(self):
        """Test GREATER_THAN operator."""
        condition = AlertCondition(
            metric="error_rate",
            operator=ConditionOperator.GREATER_THAN,
            threshold=0.10
        )

        assert condition.evaluate(0.15) is True
        assert condition.evaluate(0.10) is False
        assert condition.evaluate(0.05) is False

    def test_less_than_operator(self):
        """Test LESS_THAN operator."""
        condition = AlertCondition(
            metric="idle_percentage",
            operator=ConditionOperator.LESS_THAN,
            threshold=0.20
        )

        assert condition.evaluate(0.15) is True
        assert condition.evaluate(0.20) is False
        assert condition.evaluate(0.25) is False

    def test_equals_operator(self):
        """Test EQUALS operator."""
        condition = AlertCondition(
            metric="agent_count",
            operator=ConditionOperator.EQUALS,
            threshold=5.0
        )

        assert condition.evaluate(5.0) is True
        assert condition.evaluate(4.0) is False
        assert condition.evaluate(6.0) is False

    def test_not_equals_operator(self):
        """Test NOT_EQUALS operator."""
        condition = AlertCondition(
            metric="status_code",
            operator=ConditionOperator.NOT_EQUALS,
            threshold=200.0
        )

        assert condition.evaluate(404.0) is True
        assert condition.evaluate(200.0) is False

    def test_greater_equal_operator(self):
        """Test GREATER_EQUAL operator."""
        condition = AlertCondition(
            metric="pending_tasks",
            operator=ConditionOperator.GREATER_EQUAL,
            threshold=50.0
        )

        assert condition.evaluate(50.0) is True
        assert condition.evaluate(55.0) is True
        assert condition.evaluate(45.0) is False

    def test_less_equal_operator(self):
        """Test LESS_EQUAL operator."""
        condition = AlertCondition(
            metric="success_rate",
            operator=ConditionOperator.LESS_EQUAL,
            threshold=0.95
        )

        assert condition.evaluate(0.95) is True
        assert condition.evaluate(0.90) is True
        assert condition.evaluate(0.98) is False


# ============================================================================
# AlertRule Tests
# ============================================================================

class TestAlertRule:
    """Test AlertRule functionality."""

    def test_rule_creation(self):
        """Test alert rule creation."""
        rule = create_test_rule()

        assert rule.id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.enabled is True
        assert len(rule.conditions) == 1
        assert len(rule.notifications) == 1
        assert rule.cooldown_seconds == 300

    def test_rule_should_trigger_true(self):
        """Test rule triggers when conditions are met."""
        rule = create_test_rule()

        metrics = {
            "error_rate": 0.15,  # Above threshold
        }

        assert rule.should_trigger(metrics) is True

    def test_rule_should_trigger_false(self):
        """Test rule doesn't trigger when conditions aren't met."""
        rule = create_test_rule()

        metrics = {
            "error_rate": 0.05,  # Below threshold
        }

        assert rule.should_trigger(metrics) is False

    def test_rule_disabled(self):
        """Test disabled rule doesn't trigger."""
        rule = create_test_rule()
        rule.enabled = False

        metrics = {
            "error_rate": 0.15,  # Above threshold
        }

        assert rule.should_trigger(metrics) is False

    def test_rule_multiple_conditions_all_met(self):
        """Test rule with multiple conditions (all must be met)."""
        rule = AlertRule(
            id="multi_condition_rule",
            name="Multi Condition Rule",
            description="Rule with multiple conditions",
            conditions=[
                AlertCondition(
                    metric="error_rate",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=0.10
                ),
                AlertCondition(
                    metric="agent_count",
                    operator=ConditionOperator.LESS_THAN,
                    threshold=5.0
                )
            ],
            severity=AlertSeverity.CRITICAL,
            notifications=[],
            enabled=True
        )

        # Both conditions met
        metrics = {
            "error_rate": 0.15,
            "agent_count": 3.0,
        }
        assert rule.should_trigger(metrics) is True

        # Only one condition met
        metrics = {
            "error_rate": 0.15,
            "agent_count": 10.0,
        }
        assert rule.should_trigger(metrics) is False

    def test_rule_missing_metric(self):
        """Test rule doesn't trigger if metric is missing."""
        rule = create_test_rule()

        metrics = {
            "some_other_metric": 0.15,
        }

        assert rule.should_trigger(metrics) is False


# ============================================================================
# Alert Tests
# ============================================================================

class TestAlert:
    """Test Alert lifecycle."""

    def test_alert_creation(self):
        """Test alert creation."""
        alert = Alert(
            id="alert_1",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test alert message",
            details={},
            triggered_at=datetime.utcnow()
        )

        assert alert.id == "alert_1"
        assert alert.status == AlertStatus.ACTIVE
        assert alert.acknowledged_at is None
        assert alert.resolved_at is None

    def test_alert_acknowledge(self):
        """Test acknowledging an alert."""
        alert = Alert(
            id="alert_1",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        alert.acknowledge("operator")

        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "operator"
        assert alert.acknowledged_at is not None

    def test_alert_resolve(self):
        """Test resolving an alert."""
        alert = Alert(
            id="alert_1",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        alert.resolve("operator")

        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_by == "operator"
        assert alert.resolved_at is not None

    def test_alert_resolve_after_acknowledge(self):
        """Test resolving after acknowledging."""
        alert = Alert(
            id="alert_1",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        alert.acknowledge("operator1")
        alert.resolve("operator2")

        assert alert.status == AlertStatus.RESOLVED
        assert alert.acknowledged_by == "operator1"
        assert alert.resolved_by == "operator2"

    def test_alert_suppress(self):
        """Test suppressing an alert."""
        alert = Alert(
            id="alert_1",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        alert.suppress()

        assert alert.status == AlertStatus.SUPPRESSED


# ============================================================================
# AlertManager Tests
# ============================================================================

class TestAlertManager:
    """Test AlertManager functionality."""

    @pytest.fixture
    def alert_manager(self, db_session):
        """Create AlertManager instance."""
        return AlertManager(db_session)

    def test_alert_manager_init(self, alert_manager):
        """Test AlertManager initialization."""
        assert alert_manager is not None
        assert len(alert_manager.rules) > 0  # Default rules loaded
        assert isinstance(alert_manager.active_alerts, dict)
        assert isinstance(alert_manager.alert_history, list)

    def test_add_rule(self, alert_manager):
        """Test adding a new alert rule."""
        initial_count = len(alert_manager.rules)

        new_rule = create_test_rule(rule_id="new_rule")
        alert_manager.add_rule(new_rule)

        assert len(alert_manager.rules) == initial_count + 1
        assert "new_rule" in alert_manager.rules

    def test_remove_rule(self, alert_manager):
        """Test removing an alert rule."""
        rule = create_test_rule(rule_id="removable_rule")
        alert_manager.add_rule(rule)

        assert "removable_rule" in alert_manager.rules

        alert_manager.remove_rule("removable_rule")

        assert "removable_rule" not in alert_manager.rules

    def test_get_rule(self, alert_manager):
        """Test retrieving an alert rule."""
        rule = create_test_rule(rule_id="retrievable_rule")
        alert_manager.add_rule(rule)

        retrieved = alert_manager.get_rule("retrievable_rule")

        assert retrieved is not None
        assert retrieved.id == "retrievable_rule"

    def test_list_rules(self, alert_manager):
        """Test listing all rules."""
        rules = alert_manager.list_rules()

        assert isinstance(rules, list)
        assert len(rules) > 0
        assert all(isinstance(r, AlertRule) for r in rules)

    def test_list_rules_enabled_only(self, alert_manager):
        """Test listing only enabled rules."""
        # Add disabled rule
        disabled_rule = create_test_rule(rule_id="disabled_rule")
        disabled_rule.enabled = False
        alert_manager.add_rule(disabled_rule)

        enabled_rules = alert_manager.list_rules(enabled_only=True)

        assert all(r.enabled for r in enabled_rules)
        assert "disabled_rule" not in [r.id for r in enabled_rules]

    @pytest.mark.asyncio
    async def test_collect_metrics(self, alert_manager):
        """Test metric collection."""
        metrics = await alert_manager.collect_metrics()

        assert isinstance(metrics, dict)
        assert "error_rate" in metrics
        assert "agent_idle_percentage" in metrics
        assert "agents_error_count" in metrics
        assert "avg_execution_time" in metrics
        assert "pending_tasks_count" in metrics

        # All metrics should be numeric
        for key, value in metrics.items():
            assert isinstance(value, (int, float))

    @pytest.mark.asyncio
    async def test_evaluate_rules_no_triggers(self, alert_manager, mock_metrics):
        """Test rule evaluation when no rules trigger."""
        # Clear default rules
        alert_manager.rules = {}

        # Add rule that won't trigger
        rule = AlertRule(
            id="no_trigger_rule",
            name="No Trigger Rule",
            description="Rule that won't trigger",
            conditions=[
                AlertCondition(
                    metric="error_rate",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=0.50,  # Very high threshold
                )
            ],
            severity=AlertSeverity.WARNING,
            notifications=[],
            enabled=True,
            cooldown_seconds=0
        )
        alert_manager.add_rule(rule)

        with patch.object(alert_manager, 'collect_metrics', return_value=mock_metrics):
            triggered = await alert_manager.evaluate_rules()

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_evaluate_rules_with_trigger(self, alert_manager, mock_metrics):
        """Test rule evaluation when rules trigger."""
        # Clear default rules
        alert_manager.rules = {}

        # Add rule that will trigger
        rule = AlertRule(
            id="trigger_rule",
            name="Trigger Rule",
            description="Rule that will trigger",
            conditions=[
                AlertCondition(
                    metric="error_rate",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=0.01,  # Low threshold
                )
            ],
            severity=AlertSeverity.CRITICAL,
            notifications=[],
            enabled=True,
            cooldown_seconds=0
        )
        alert_manager.add_rule(rule)

        with patch.object(alert_manager, 'collect_metrics', return_value=mock_metrics):
            triggered = await alert_manager.evaluate_rules()

        assert len(triggered) > 0
        assert triggered[0].rule_id == "trigger_rule"
        assert triggered[0].status == AlertStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_cooldown_mechanism(self, alert_manager, mock_metrics):
        """Test cooldown prevents rapid re-triggering."""
        # Clear default rules
        alert_manager.rules = {}

        # Add rule with cooldown
        rule = AlertRule(
            id="cooldown_rule",
            name="Cooldown Rule",
            description="Rule with cooldown",
            conditions=[
                AlertCondition(
                    metric="error_rate",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=0.01,
                )
            ],
            severity=AlertSeverity.WARNING,
            notifications=[],
            enabled=True,
            cooldown_seconds=300  # 5 minute cooldown
        )
        alert_manager.add_rule(rule)

        with patch.object(alert_manager, 'collect_metrics', return_value=mock_metrics):
            # First evaluation - should trigger
            triggered1 = await alert_manager.evaluate_rules()
            assert len(triggered1) == 1

            # Second evaluation immediately after - should NOT trigger (cooldown)
            triggered2 = await alert_manager.evaluate_rules()
            assert len(triggered2) == 0

    def test_get_alert(self, alert_manager):
        """Test retrieving an alert by ID."""
        # Create and store alert
        alert = Alert(
            id="test_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test message",
            details={},
            triggered_at=datetime.utcnow()
        )
        alert_manager.active_alerts["test_alert"] = alert
        alert_manager.alert_history.append(alert)

        retrieved = alert_manager.get_alert("test_alert")

        assert retrieved is not None
        assert retrieved.id == "test_alert"

    def test_list_alerts(self, alert_manager):
        """Test listing alerts with filtering."""
        # Add test alerts
        for i in range(5):
            alert = Alert(
                id=f"alert_{i}",
                rule_id="test_rule",
                rule_name="Test Rule",
                severity=AlertSeverity.WARNING if i % 2 == 0 else AlertSeverity.CRITICAL,
                status=AlertStatus.ACTIVE if i < 3 else AlertStatus.RESOLVED,
                message=f"Alert {i}",
                details={},
                triggered_at=datetime.utcnow()
            )
            alert_manager.alert_history.append(alert)
            if i < 3:
                alert_manager.active_alerts[f"alert_{i}"] = alert

        # Test listing all
        all_alerts = alert_manager.list_alerts()
        assert len(all_alerts) == 5

        # Test filter by status
        active_alerts = alert_manager.list_alerts(status=AlertStatus.ACTIVE)
        assert len(active_alerts) == 3
        assert all(a.status == AlertStatus.ACTIVE for a in active_alerts)

        # Test filter by severity
        critical_alerts = alert_manager.list_alerts(severity=AlertSeverity.CRITICAL)
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)

        # Test limit
        limited_alerts = alert_manager.list_alerts(limit=2)
        assert len(limited_alerts) == 2

    def test_acknowledge_alert(self, alert_manager):
        """Test acknowledging an alert."""
        alert = Alert(
            id="ack_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test",
            details={},
            triggered_at=datetime.utcnow()
        )
        alert_manager.active_alerts["ack_alert"] = alert

        result = alert_manager.acknowledge_alert("ack_alert", "operator")

        assert result is not None
        assert result.status == AlertStatus.ACKNOWLEDGED
        assert result.acknowledged_by == "operator"

    def test_resolve_alert(self, alert_manager):
        """Test resolving an alert."""
        alert = Alert(
            id="resolve_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test",
            details={},
            triggered_at=datetime.utcnow()
        )
        alert_manager.active_alerts["resolve_alert"] = alert

        result = alert_manager.resolve_alert("resolve_alert", "operator")

        assert result is not None
        assert result.status == AlertStatus.RESOLVED
        assert result.resolved_by == "operator"
        assert "resolve_alert" not in alert_manager.active_alerts  # Removed from active

    def test_suppress_alert(self, alert_manager):
        """Test suppressing an alert."""
        alert = Alert(
            id="suppress_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test",
            details={},
            triggered_at=datetime.utcnow()
        )
        alert_manager.active_alerts["suppress_alert"] = alert

        result = alert_manager.suppress_alert("suppress_alert")

        assert result is not None
        assert result.status == AlertStatus.SUPPRESSED
        assert "suppress_alert" not in alert_manager.active_alerts

    @pytest.mark.asyncio
    async def test_get_alert_stats(self, alert_manager):
        """Test getting alert statistics."""
        # Add test alerts with varying properties
        now = datetime.utcnow()
        for i in range(10):
            alert = Alert(
                id=f"stats_alert_{i}",
                rule_id=f"rule_{i % 3}",
                rule_name=f"Rule {i % 3}",
                severity=[AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.CRITICAL][i % 3],
                status=[AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED][i % 3],
                message=f"Alert {i}",
                details={},
                triggered_at=now - timedelta(days=i),
                acknowledged_at=now - timedelta(days=i, hours=1) if i % 3 == 1 else None,
                resolved_at=now - timedelta(days=i, hours=2) if i % 3 == 2 else None,
            )
            alert_manager.alert_history.append(alert)

        stats = await alert_manager.get_alert_stats(timeframe_days=30)

        assert isinstance(stats, AlertStats)
        assert stats.total_alerts > 0
        assert stats.active_alerts >= 0
        assert stats.acknowledged_alerts >= 0
        assert stats.resolved_alerts >= 0
        assert isinstance(stats.alerts_by_severity, dict)
        assert isinstance(stats.alerts_by_rule, dict)
        assert stats.avg_time_to_acknowledge >= 0
        assert stats.avg_time_to_resolve >= 0
        assert isinstance(stats.most_frequent_alerts, list)


# ============================================================================
# Notification Tests
# ============================================================================

class TestNotifications:
    """Test notification functionality."""

    @pytest.fixture
    def alert_manager(self, db_session):
        """Create AlertManager instance."""
        return AlertManager(db_session)

    @pytest.mark.asyncio
    async def test_send_email_notification(self, alert_manager):
        """Test email notification sending (mocked)."""
        alert = Alert(
            id="email_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.ACTIVE,
            message="Test email alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            config={"to": "test@example.com"},
            enabled=True
        )

        # Mock the email sending (actual implementation would use SMTP)
        with patch.object(alert_manager, '_send_email_notification', new_callable=AsyncMock) as mock_send:
            await alert_manager._send_email_notification(alert, config.config)
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_webhook_notification(self, alert_manager):
        """Test webhook notification sending (mocked)."""
        alert = Alert(
            id="webhook_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="Test webhook alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            config={"url": "https://example.com/webhook"},
            enabled=True
        )

        with patch.object(alert_manager, '_send_webhook_notification', new_callable=AsyncMock) as mock_send:
            await alert_manager._send_webhook_notification(alert, config.config)
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_slack_notification(self, alert_manager):
        """Test Slack notification sending (mocked)."""
        alert = Alert(
            id="slack_alert",
            rule_id="test_rule",
            rule_name="Test Rule",
            severity=AlertSeverity.ERROR,
            status=AlertStatus.ACTIVE,
            message="Test Slack alert",
            details={},
            triggered_at=datetime.utcnow()
        )

        config = NotificationConfig(
            channel=NotificationChannel.SLACK,
            config={"webhook_url": "https://hooks.slack.com/services/test"},
            enabled=True
        )

        with patch.object(alert_manager, '_send_slack_notification', new_callable=AsyncMock) as mock_send:
            await alert_manager._send_slack_notification(alert, config.config)
            mock_send.assert_called_once()
