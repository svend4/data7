"""
AlertManager Service - Real-time alerting and notification system

Provides:
- Alert rule evaluation based on system metrics
- Multi-channel notifications (email, webhook, Slack)
- Alert history and acknowledgment
- Alert severity levels and escalation
- Configurable thresholds and conditions
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.database import (
    AgentModel,
    TaskModel,
    ExecutionModel,
    ConnectionModel,
)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert lifecycle status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationChannel(str, Enum):
    """Supported notification channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SMS = "sms"


class ConditionOperator(str, Enum):
    """Comparison operators for alert conditions"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


@dataclass
class AlertCondition:
    """Alert triggering condition"""
    metric: str  # e.g., "error_rate", "agent_idle_count", "avg_execution_time"
    operator: ConditionOperator
    threshold: float
    duration: int = 0  # seconds - condition must be true for this duration

    def evaluate(self, current_value: float) -> bool:
        """Evaluate if condition is met"""
        if self.operator == ConditionOperator.GREATER_THAN:
            return current_value > self.threshold
        elif self.operator == ConditionOperator.LESS_THAN:
            return current_value < self.threshold
        elif self.operator == ConditionOperator.EQUALS:
            return current_value == self.threshold
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return current_value != self.threshold
        elif self.operator == ConditionOperator.GREATER_EQUAL:
            return current_value >= self.threshold
        elif self.operator == ConditionOperator.LESS_EQUAL:
            return current_value <= self.threshold
        return False


@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    channel: NotificationChannel
    config: Dict[str, Any]  # Channel-specific config (email address, webhook URL, etc.)
    enabled: bool = True


@dataclass
class AlertRule:
    """Alert rule definition"""
    id: str
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity
    notifications: List[NotificationConfig]
    enabled: bool = True
    cooldown_seconds: int = 300  # Don't re-trigger for this duration
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def should_trigger(self, metric_values: Dict[str, float]) -> bool:
        """Check if all conditions are met"""
        if not self.enabled:
            return False

        for condition in self.conditions:
            if condition.metric not in metric_values:
                return False
            if not condition.evaluate(metric_values[condition.metric]):
                return False

        return True


@dataclass
class Alert:
    """Active or historical alert"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    details: Dict[str, Any]
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notification_sent: bool = False
    notification_channels: List[NotificationChannel] = field(default_factory=list)

    def acknowledge(self, user: str):
        """Acknowledge the alert"""
        if self.status == AlertStatus.ACTIVE:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_at = datetime.utcnow()
            self.acknowledged_by = user

    def resolve(self, user: str):
        """Resolve the alert"""
        if self.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
            self.status = AlertStatus.RESOLVED
            self.resolved_at = datetime.utcnow()
            self.resolved_by = user

    def suppress(self):
        """Suppress the alert"""
        self.status = AlertStatus.SUPPRESSED


@dataclass
class AlertStats:
    """Alert statistics"""
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    suppressed_alerts: int
    alerts_by_severity: Dict[AlertSeverity, int]
    alerts_by_rule: Dict[str, int]
    avg_time_to_acknowledge: float  # seconds
    avg_time_to_resolve: float  # seconds
    most_frequent_alerts: List[Dict[str, Any]]


class AlertManager:
    """
    Alert management system

    Features:
    - Real-time metric monitoring
    - Configurable alert rules
    - Multi-channel notifications
    - Alert lifecycle management
    - Alert history and analytics
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_trigger_times: Dict[str, datetime] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default alert rules"""

        # High error rate alert
        self.add_rule(AlertRule(
            id="high_error_rate",
            name="High Error Rate",
            description="Error rate exceeds 15% threshold",
            conditions=[
                AlertCondition(
                    metric="error_rate",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=0.15,
                    duration=60
                )
            ],
            severity=AlertSeverity.CRITICAL,
            notifications=[
                NotificationConfig(
                    channel=NotificationChannel.EMAIL,
                    config={"to": "admin@example.com"}
                ),
                NotificationConfig(
                    channel=NotificationChannel.SLACK,
                    config={"webhook_url": "https://hooks.slack.com/..."}
                )
            ],
            cooldown_seconds=600,
            tags=["error", "system-health"]
        ))

        # Low agent availability
        self.add_rule(AlertRule(
            id="low_agent_availability",
            name="Low Agent Availability",
            description="Less than 20% of agents are idle/available",
            conditions=[
                AlertCondition(
                    metric="agent_idle_percentage",
                    operator=ConditionOperator.LESS_THAN,
                    threshold=0.20,
                    duration=120
                )
            ],
            severity=AlertSeverity.WARNING,
            notifications=[
                NotificationConfig(
                    channel=NotificationChannel.EMAIL,
                    config={"to": "ops@example.com"}
                )
            ],
            cooldown_seconds=300,
            tags=["capacity", "agents"]
        ))

        # Agent failure spike
        self.add_rule(AlertRule(
            id="agent_failure_spike",
            name="Agent Failure Spike",
            description="More than 2 agents in error state",
            conditions=[
                AlertCondition(
                    metric="agents_error_count",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=2,
                    duration=30
                )
            ],
            severity=AlertSeverity.ERROR,
            notifications=[
                NotificationConfig(
                    channel=NotificationChannel.WEBHOOK,
                    config={"url": "https://api.example.com/alerts"}
                )
            ],
            cooldown_seconds=300,
            tags=["agents", "failure"]
        ))

        # Slow execution performance
        self.add_rule(AlertRule(
            id="slow_execution_performance",
            name="Slow Execution Performance",
            description="Average execution time exceeds 30 seconds",
            conditions=[
                AlertCondition(
                    metric="avg_execution_time",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=30.0,
                    duration=180
                )
            ],
            severity=AlertSeverity.WARNING,
            notifications=[
                NotificationConfig(
                    channel=NotificationChannel.EMAIL,
                    config={"to": "performance@example.com"}
                )
            ],
            cooldown_seconds=600,
            tags=["performance", "execution"]
        ))

        # High task queue
        self.add_rule(AlertRule(
            id="high_task_queue",
            name="High Task Queue",
            description="More than 50 pending tasks in queue",
            conditions=[
                AlertCondition(
                    metric="pending_tasks_count",
                    operator=ConditionOperator.GREATER_THAN,
                    threshold=50,
                    duration=300
                )
            ],
            severity=AlertSeverity.WARNING,
            notifications=[
                NotificationConfig(
                    channel=NotificationChannel.SLACK,
                    config={"webhook_url": "https://hooks.slack.com/..."}
                )
            ],
            cooldown_seconds=300,
            tags=["capacity", "tasks"]
        ))

    def add_rule(self, rule: AlertRule):
        """Add or update an alert rule"""
        self.rules[rule.id] = rule

    def remove_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        return self.rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> List[AlertRule]:
        """List all alert rules"""
        rules = list(self.rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    async def collect_metrics(self) -> Dict[str, float]:
        """Collect current system metrics for alert evaluation"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # Agent statistics
        agent_stats_result = await self.db.execute(
            select(
                func.count(AgentModel.id).label('total'),
                func.sum(func.cast(AgentModel.status == 'idle', type_=func.Integer)).label('idle'),
                func.sum(func.cast(AgentModel.status == 'error', type_=func.Integer)).label('error'),
            )
        )
        agent_stats = agent_stats_result.first()

        total_agents = agent_stats.total or 0
        idle_agents = agent_stats.idle or 0
        error_agents = agent_stats.error or 0

        # Task statistics
        task_stats_result = await self.db.execute(
            select(
                func.count(TaskModel.id).label('total'),
                func.sum(func.cast(TaskModel.status == 'pending', type_=func.Integer)).label('pending'),
                func.sum(func.cast(TaskModel.status == 'failed', type_=func.Integer)).label('failed'),
            ).where(TaskModel.created_at >= hour_ago)
        )
        task_stats = task_stats_result.first()

        total_tasks = task_stats.total or 1  # Avoid division by zero
        pending_tasks = task_stats.pending or 0
        failed_tasks = task_stats.failed or 0

        # Execution statistics
        exec_stats_result = await self.db.execute(
            select(
                func.avg(ExecutionModel.execution_time).label('avg_time'),
            ).where(
                and_(
                    ExecutionModel.created_at >= hour_ago,
                    ExecutionModel.execution_time.isnot(None)
                )
            )
        )
        exec_stats = exec_stats_result.first()
        avg_exec_time = float(exec_stats.avg_time or 0)

        # Calculate derived metrics
        error_rate = failed_tasks / total_tasks if total_tasks > 0 else 0.0
        agent_idle_percentage = idle_agents / total_agents if total_agents > 0 else 0.0

        return {
            "error_rate": error_rate,
            "agent_idle_percentage": agent_idle_percentage,
            "agents_error_count": float(error_agents),
            "avg_execution_time": avg_exec_time,
            "pending_tasks_count": float(pending_tasks),
            "total_agents": float(total_agents),
            "idle_agents": float(idle_agents),
            "total_tasks": float(total_tasks),
            "failed_tasks": float(failed_tasks),
        }

    async def evaluate_rules(self) -> List[Alert]:
        """Evaluate all enabled rules and trigger alerts"""
        metrics = await self.collect_metrics()
        triggered_alerts: List[Alert] = []
        now = datetime.utcnow()

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.id in self.last_trigger_times:
                last_trigger = self.last_trigger_times[rule.id]
                if (now - last_trigger).total_seconds() < rule.cooldown_seconds:
                    continue

            # Evaluate conditions
            if rule.should_trigger(metrics):
                alert = self._create_alert(rule, metrics)
                triggered_alerts.append(alert)
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)
                self.last_trigger_times[rule.id] = now

                # Send notifications asynchronously
                asyncio.create_task(self._send_notifications(alert, rule))

        return triggered_alerts

    def _create_alert(self, rule: AlertRule, metrics: Dict[str, float]) -> Alert:
        """Create alert instance from triggered rule"""
        alert_id = f"{rule.id}_{int(datetime.utcnow().timestamp())}"

        # Build detailed message
        condition_details = []
        for condition in rule.conditions:
            current_value = metrics.get(condition.metric, 0)
            condition_details.append({
                "metric": condition.metric,
                "threshold": condition.threshold,
                "current_value": current_value,
                "operator": condition.operator.value
            })

        message = f"{rule.name}: {rule.description}"

        return Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=message,
            details={
                "conditions": condition_details,
                "all_metrics": metrics,
                "tags": rule.tags
            },
            triggered_at=datetime.utcnow(),
            notification_channels=[nc.channel for nc in rule.notifications if nc.enabled]
        )

    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications through configured channels"""
        for notification_config in rule.notifications:
            if not notification_config.enabled:
                continue

            try:
                if notification_config.channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(alert, notification_config.config)
                elif notification_config.channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(alert, notification_config.config)
                elif notification_config.channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(alert, notification_config.config)
                # SMS would be implemented similarly

                alert.notification_sent = True
            except Exception as e:
                # Log notification failure but don't block
                print(f"Failed to send {notification_config.channel.value} notification: {e}")

    async def _send_email_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send email notification (placeholder - requires email service integration)"""
        # In production, integrate with SendGrid, AWS SES, or similar
        print(f"[EMAIL] To: {config.get('to')}")
        print(f"[EMAIL] Subject: [{alert.severity.value.upper()}] {alert.rule_name}")
        print(f"[EMAIL] Body: {alert.message}")
        print(f"[EMAIL] Details: {json.dumps(alert.details, indent=2)}")

    async def _send_webhook_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send webhook notification (placeholder - requires HTTP client)"""
        # In production, use aiohttp to POST to webhook URL
        webhook_url = config.get('url')
        payload = {
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "details": alert.details,
            "triggered_at": alert.triggered_at.isoformat()
        }
        print(f"[WEBHOOK] URL: {webhook_url}")
        print(f"[WEBHOOK] Payload: {json.dumps(payload, indent=2)}")

    async def _send_slack_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send Slack notification (placeholder - requires Slack SDK)"""
        # In production, use aiohttp to POST to Slack webhook
        webhook_url = config.get('webhook_url')

        # Slack message formatting
        color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9800",
            AlertSeverity.ERROR: "#dc3545",
            AlertSeverity.CRITICAL: "#8b0000"
        }.get(alert.severity, "#808080")

        slack_message = {
            "attachments": [{
                "color": color,
                "title": f"[{alert.severity.value.upper()}] {alert.rule_name}",
                "text": alert.message,
                "fields": [
                    {"title": "Alert ID", "value": alert.id, "short": True},
                    {"title": "Triggered", "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                ],
                "footer": "Meta-Orchestrator Switchboard",
                "ts": int(alert.triggered_at.timestamp())
            }]
        }

        print(f"[SLACK] Webhook: {webhook_url}")
        print(f"[SLACK] Message: {json.dumps(slack_message, indent=2)}")

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        # Check active alerts first
        if alert_id in self.active_alerts:
            return self.active_alerts[alert_id]

        # Search history
        for alert in self.alert_history:
            if alert.id == alert_id:
                return alert

        return None

    def list_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        rule_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Alert]:
        """List alerts with optional filtering"""
        alerts = list(self.active_alerts.values()) + self.alert_history

        # Remove duplicates (active alerts are also in history)
        seen_ids = set()
        unique_alerts = []
        for alert in alerts:
            if alert.id not in seen_ids:
                seen_ids.add(alert.id)
                unique_alerts.append(alert)

        # Apply filters
        if status:
            unique_alerts = [a for a in unique_alerts if a.status == status]
        if severity:
            unique_alerts = [a for a in unique_alerts if a.severity == severity]
        if rule_id:
            unique_alerts = [a for a in unique_alerts if a.rule_id == rule_id]

        # Sort by triggered_at descending
        unique_alerts.sort(key=lambda a: a.triggered_at, reverse=True)

        return unique_alerts[:limit]

    def acknowledge_alert(self, alert_id: str, user: str) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = self.get_alert(alert_id)
        if alert:
            alert.acknowledge(user)
            return alert
        return None

    def resolve_alert(self, alert_id: str, user: str) -> Optional[Alert]:
        """Resolve an alert"""
        alert = self.get_alert(alert_id)
        if alert:
            alert.resolve(user)
            # Remove from active alerts
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
            return alert
        return None

    def suppress_alert(self, alert_id: str) -> Optional[Alert]:
        """Suppress an alert"""
        alert = self.get_alert(alert_id)
        if alert:
            alert.suppress()
            # Remove from active alerts
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
            return alert
        return None

    async def get_alert_stats(self, timeframe_days: int = 7) -> AlertStats:
        """Get alert statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)

        # Filter alerts within timeframe
        recent_alerts = [a for a in self.alert_history if a.triggered_at >= cutoff_date]

        # Count by status
        active_count = len([a for a in recent_alerts if a.status == AlertStatus.ACTIVE])
        acknowledged_count = len([a for a in recent_alerts if a.status == AlertStatus.ACKNOWLEDGED])
        resolved_count = len([a for a in recent_alerts if a.status == AlertStatus.RESOLVED])
        suppressed_count = len([a for a in recent_alerts if a.status == AlertStatus.SUPPRESSED])

        # Count by severity
        alerts_by_severity = {}
        for severity in AlertSeverity:
            alerts_by_severity[severity] = len([a for a in recent_alerts if a.severity == severity])

        # Count by rule
        alerts_by_rule = {}
        for alert in recent_alerts:
            if alert.rule_id not in alerts_by_rule:
                alerts_by_rule[alert.rule_id] = 0
            alerts_by_rule[alert.rule_id] += 1

        # Calculate average times
        acknowledged_alerts = [a for a in recent_alerts if a.acknowledged_at]
        if acknowledged_alerts:
            ack_times = [(a.acknowledged_at - a.triggered_at).total_seconds() for a in acknowledged_alerts]
            avg_time_to_ack = sum(ack_times) / len(ack_times)
        else:
            avg_time_to_ack = 0.0

        resolved_alerts = [a for a in recent_alerts if a.resolved_at]
        if resolved_alerts:
            resolve_times = [(a.resolved_at - a.triggered_at).total_seconds() for a in resolved_alerts]
            avg_time_to_resolve = sum(resolve_times) / len(resolve_times)
        else:
            avg_time_to_resolve = 0.0

        # Most frequent alerts
        most_frequent = sorted(
            [{"rule_id": k, "count": v, "rule_name": self.rules.get(k, AlertRule(id=k, name=k, description="", conditions=[], severity=AlertSeverity.INFO, notifications=[])).name}
             for k, v in alerts_by_rule.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]

        return AlertStats(
            total_alerts=len(recent_alerts),
            active_alerts=active_count,
            acknowledged_alerts=acknowledged_count,
            resolved_alerts=resolved_count,
            suppressed_alerts=suppressed_count,
            alerts_by_severity=alerts_by_severity,
            alerts_by_rule=alerts_by_rule,
            avg_time_to_acknowledge=avg_time_to_ack,
            avg_time_to_resolve=avg_time_to_resolve,
            most_frequent_alerts=most_frequent
        )


# Singleton instance (in production, use dependency injection)
_alert_manager_instance: Optional[AlertManager] = None


def get_alert_manager(db: AsyncSession) -> AlertManager:
    """Get or create AlertManager singleton"""
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager(db)
    return _alert_manager_instance
