"""
WebSocket Event Types and Schemas
Real-time event definitions for the switchboard system
"""

from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class EventType(str, Enum):
    """WebSocket event types for real-time updates"""

    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_DELETED = "task.deleted"

    # Connection events
    CONNECTION_CREATED = "connection.created"
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_DISCONNECTED = "connection.disconnected"
    CONNECTION_DELETED = "connection.deleted"

    # Graph events
    GRAPH_CREATED = "graph.created"
    GRAPH_EXECUTED = "graph.executed"
    GRAPH_DELETED = "graph.deleted"

    # Execution events
    EXECUTION_STARTED = "execution.started"
    EXECUTION_PROGRESS = "execution.progress"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    EXECUTION_CANCELLED = "execution.cancelled"

    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_STATUS_CHANGED = "agent.status_changed"
    AGENT_DELETED = "agent.deleted"

    # System events
    SYSTEM_STATS = "system.stats"
    SYSTEM_HEALTH = "system.health"


class WebSocketEvent(BaseModel):
    """WebSocket event message sent to clients"""

    type: str = Field(..., description="Event type (e.g., task.created)")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp when event occurred",
    )


class SubscriptionRequest(BaseModel):
    """Client subscription request message"""

    action: str = Field(..., description="Action: subscribe or unsubscribe")
    event_types: list[str] = Field(
        ..., description="List of event types to subscribe to (supports wildcards: task.*)"
    )


class SubscriptionResponse(BaseModel):
    """Server subscription response message"""

    type: str = Field(..., description="Response type")
    active_subscriptions: list[str] = Field(
        ..., description="Currently active subscriptions for this client"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp",
    )


class PingRequest(BaseModel):
    """Client ping request"""

    action: str = Field(default="ping", description="Action type")


class PongResponse(BaseModel):
    """Server pong response"""

    type: str = Field(default="pong", description="Response type")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp",
    )


class ConnectedMessage(BaseModel):
    """Welcome message sent when client connects"""

    type: str = Field(default="connected", description="Message type")
    client_id: str = Field(..., description="Unique client identifier")
    message: str = Field(..., description="Welcome message")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp",
    )
