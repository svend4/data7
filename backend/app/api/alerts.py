"""
Alerts API - Alert management and notification endpoints

Endpoints:
- GET /api/alerts - List alerts with filtering
- GET /api/alerts/{id} - Get alert details
- POST /api/alerts/{id}/acknowledge - Acknowledge alert
- POST /api/alerts/{id}/resolve - Resolve alert
- POST /api/alerts/{id}/suppress - Suppress alert
- GET /api/alerts/stats - Get alert statistics
- GET /api/alerts/rules - List alert rules
- POST /api/alerts/rules - Create alert rule
- PUT /api/alerts/rules/{id} - Update alert rule
- DELETE /api/alerts/rules/{id} - Delete alert rule
- POST /api/alerts/evaluate - Manually trigger alert evaluation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.alert_manager import (
    AlertManager,
    get_alert_manager,
    Alert,
    AlertRule,
    AlertCondition,
    NotificationConfig,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    ConditionOperator,
    AlertStats,
)


router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AlertConditionRequest(BaseModel):
    """Alert condition request model"""
    metric: str = Field(..., description="Metric to monitor")
    operator: ConditionOperator = Field(..., description="Comparison operator")
    threshold: float = Field(..., description="Threshold value")
    duration: int = Field(0, description="Duration in seconds")


class NotificationConfigRequest(BaseModel):
    """Notification configuration request model"""
    channel: NotificationChannel = Field(..., description="Notification channel")
    config: dict = Field(..., description="Channel-specific configuration")
    enabled: bool = Field(True, description="Enable/disable this notification")


class CreateAlertRuleRequest(BaseModel):
    """Create alert rule request"""
    name: str = Field(..., description="Rule name")
    description: str = Field("", description="Rule description")
    conditions: List[AlertConditionRequest] = Field(..., description="Alert conditions")
    severity: AlertSeverity = Field(..., description="Alert severity")
    notifications: List[NotificationConfigRequest] = Field(..., description="Notification channels")
    enabled: bool = Field(True, description="Enable rule")
    cooldown_seconds: int = Field(300, description="Cooldown between triggers")
    tags: List[str] = Field(default_factory=list, description="Alert tags")


class UpdateAlertRuleRequest(BaseModel):
    """Update alert rule request"""
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    conditions: Optional[List[AlertConditionRequest]] = Field(None, description="Alert conditions")
    severity: Optional[AlertSeverity] = Field(None, description="Alert severity")
    notifications: Optional[List[NotificationConfigRequest]] = Field(None, description="Notification channels")
    enabled: Optional[bool] = Field(None, description="Enable rule")
    cooldown_seconds: Optional[int] = Field(None, description="Cooldown between triggers")
    tags: Optional[List[str]] = Field(None, description="Alert tags")


class AcknowledgeAlertRequest(BaseModel):
    """Acknowledge alert request"""
    user: str = Field(..., description="User acknowledging the alert")


class ResolveAlertRequest(BaseModel):
    """Resolve alert request"""
    user: str = Field(..., description="User resolving the alert")


class AlertConditionResponse(BaseModel):
    """Alert condition response"""
    metric: str
    operator: str
    threshold: float
    duration: int


class NotificationConfigResponse(BaseModel):
    """Notification configuration response"""
    channel: str
    config: dict
    enabled: bool


class AlertRuleResponse(BaseModel):
    """Alert rule response"""
    id: str
    name: str
    description: str
    conditions: List[AlertConditionResponse]
    severity: str
    notifications: List[NotificationConfigResponse]
    enabled: bool
    cooldown_seconds: int
    tags: List[str]
    created_at: str


class AlertResponse(BaseModel):
    """Alert response"""
    id: str
    rule_id: str
    rule_name: str
    severity: str
    status: str
    message: str
    details: dict
    triggered_at: str
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    notification_sent: bool
    notification_channels: List[str]


class AlertStatsResponse(BaseModel):
    """Alert statistics response"""
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    suppressed_alerts: int
    alerts_by_severity: dict
    alerts_by_rule: dict
    avg_time_to_acknowledge: float
    avg_time_to_resolve: float
    most_frequent_alerts: List[dict]


class EvaluateAlertsResponse(BaseModel):
    """Evaluate alerts response"""
    evaluated_at: str
    rules_evaluated: int
    alerts_triggered: int
    triggered_alerts: List[AlertResponse]


# ============================================================================
# Helper Functions
# ============================================================================

def alert_to_response(alert: Alert) -> AlertResponse:
    """Convert Alert to response model"""
    return AlertResponse(
        id=alert.id,
        rule_id=alert.rule_id,
        rule_name=alert.rule_name,
        severity=alert.severity.value,
        status=alert.status.value,
        message=alert.message,
        details=alert.details,
        triggered_at=alert.triggered_at.isoformat(),
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        acknowledged_by=alert.acknowledged_by,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        resolved_by=alert.resolved_by,
        notification_sent=alert.notification_sent,
        notification_channels=[ch.value for ch in alert.notification_channels]
    )


def rule_to_response(rule: AlertRule) -> AlertRuleResponse:
    """Convert AlertRule to response model"""
    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        conditions=[
            AlertConditionResponse(
                metric=c.metric,
                operator=c.operator.value,
                threshold=c.threshold,
                duration=c.duration
            ) for c in rule.conditions
        ],
        severity=rule.severity.value,
        notifications=[
            NotificationConfigResponse(
                channel=n.channel.value,
                config=n.config,
                enabled=n.enabled
            ) for n in rule.notifications
        ],
        enabled=rule.enabled,
        cooldown_seconds=rule.cooldown_seconds,
        tags=rule.tags,
        created_at=rule.created_at.isoformat()
    )


# ============================================================================
# Alert Endpoints
# ============================================================================

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts"),
    db: AsyncSession = Depends(get_db)
):
    """
    List alerts with optional filtering

    Returns recent alerts sorted by triggered time (newest first)
    """
    alert_manager = get_alert_manager(db)
    alerts = alert_manager.list_alerts(
        status=status,
        severity=severity,
        rule_id=rule_id,
        limit=limit
    )

    return [alert_to_response(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert details by ID
    """
    alert_manager = get_alert_manager(db)
    alert = alert_manager.get_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

    return alert_to_response(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeAlertRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Acknowledge an alert

    Marks the alert as acknowledged by the specified user
    """
    alert_manager = get_alert_manager(db)
    alert = alert_manager.acknowledge_alert(alert_id, request.user)

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

    return alert_to_response(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    request: ResolveAlertRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve an alert

    Marks the alert as resolved by the specified user
    """
    alert_manager = get_alert_manager(db)
    alert = alert_manager.resolve_alert(alert_id, request.user)

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

    return alert_to_response(alert)


@router.post("/{alert_id}/suppress", response_model=AlertResponse)
async def suppress_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Suppress an alert

    Suppresses the alert without resolving it
    """
    alert_manager = get_alert_manager(db)
    alert = alert_manager.suppress_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

    return alert_to_response(alert)


@router.get("/stats/summary", response_model=AlertStatsResponse)
async def get_alert_stats(
    timeframe_days: int = Query(7, ge=1, le=90, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert statistics

    Returns aggregated statistics for the specified timeframe
    """
    alert_manager = get_alert_manager(db)
    stats = await alert_manager.get_alert_stats(timeframe_days)

    return AlertStatsResponse(
        total_alerts=stats.total_alerts,
        active_alerts=stats.active_alerts,
        acknowledged_alerts=stats.acknowledged_alerts,
        resolved_alerts=stats.resolved_alerts,
        suppressed_alerts=stats.suppressed_alerts,
        alerts_by_severity={k.value: v for k, v in stats.alerts_by_severity.items()},
        alerts_by_rule=stats.alerts_by_rule,
        avg_time_to_acknowledge=stats.avg_time_to_acknowledge,
        avg_time_to_resolve=stats.avg_time_to_resolve,
        most_frequent_alerts=stats.most_frequent_alerts
    )


# ============================================================================
# Alert Rule Endpoints
# ============================================================================

@router.get("/rules/list", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    enabled_only: bool = Query(False, description="Only return enabled rules"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all alert rules
    """
    alert_manager = get_alert_manager(db)
    rules = alert_manager.list_rules(enabled_only=enabled_only)

    return [rule_to_response(rule) for rule in rules]


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert rule by ID
    """
    alert_manager = get_alert_manager(db)
    rule = alert_manager.get_rule(rule_id)

    if not rule:
        raise HTTPException(status_code=404, detail=f"Alert rule with ID {rule_id} not found")

    return rule_to_response(rule)


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    request: CreateAlertRuleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert rule

    Creates and enables a new alert rule with the specified conditions and notifications
    """
    alert_manager = get_alert_manager(db)

    # Generate rule ID from name
    rule_id = request.name.lower().replace(" ", "_")

    # Check if rule already exists
    existing_rule = alert_manager.get_rule(rule_id)
    if existing_rule:
        raise HTTPException(status_code=409, detail=f"Alert rule with ID {rule_id} already exists")

    # Create rule
    rule = AlertRule(
        id=rule_id,
        name=request.name,
        description=request.description,
        conditions=[
            AlertCondition(
                metric=c.metric,
                operator=c.operator,
                threshold=c.threshold,
                duration=c.duration
            ) for c in request.conditions
        ],
        severity=request.severity,
        notifications=[
            NotificationConfig(
                channel=n.channel,
                config=n.config,
                enabled=n.enabled
            ) for n in request.notifications
        ],
        enabled=request.enabled,
        cooldown_seconds=request.cooldown_seconds,
        tags=request.tags,
        created_at=datetime.utcnow()
    )

    alert_manager.add_rule(rule)

    return rule_to_response(rule)


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    request: UpdateAlertRuleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing alert rule

    Updates the specified fields of an alert rule
    """
    alert_manager = get_alert_manager(db)
    rule = alert_manager.get_rule(rule_id)

    if not rule:
        raise HTTPException(status_code=404, detail=f"Alert rule with ID {rule_id} not found")

    # Update fields
    if request.name is not None:
        rule.name = request.name
    if request.description is not None:
        rule.description = request.description
    if request.conditions is not None:
        rule.conditions = [
            AlertCondition(
                metric=c.metric,
                operator=c.operator,
                threshold=c.threshold,
                duration=c.duration
            ) for c in request.conditions
        ]
    if request.severity is not None:
        rule.severity = request.severity
    if request.notifications is not None:
        rule.notifications = [
            NotificationConfig(
                channel=n.channel,
                config=n.config,
                enabled=n.enabled
            ) for n in request.notifications
        ]
    if request.enabled is not None:
        rule.enabled = request.enabled
    if request.cooldown_seconds is not None:
        rule.cooldown_seconds = request.cooldown_seconds
    if request.tags is not None:
        rule.tags = request.tags

    return rule_to_response(rule)


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an alert rule

    Removes the alert rule from the system
    """
    alert_manager = get_alert_manager(db)
    rule = alert_manager.get_rule(rule_id)

    if not rule:
        raise HTTPException(status_code=404, detail=f"Alert rule with ID {rule_id} not found")

    alert_manager.remove_rule(rule_id)


# ============================================================================
# Alert Evaluation Endpoints
# ============================================================================

@router.post("/evaluate", response_model=EvaluateAlertsResponse)
async def evaluate_alerts(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger alert evaluation

    Evaluates all enabled alert rules against current system metrics
    """
    alert_manager = get_alert_manager(db)

    triggered_alerts = await alert_manager.evaluate_rules()

    return EvaluateAlertsResponse(
        evaluated_at=datetime.utcnow().isoformat(),
        rules_evaluated=len(alert_manager.list_rules(enabled_only=True)),
        alerts_triggered=len(triggered_alerts),
        triggered_alerts=[alert_to_response(alert) for alert in triggered_alerts]
    )
