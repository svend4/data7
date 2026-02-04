"""
Connection API Schemas
Request/response models for Connection endpoints
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ConnectionCreateRequest(BaseModel):
    """Request to create a connection between agents"""
    from_agent_id: str = Field(min_length=1)
    to_agent_id: str = Field(min_length=1)
    bandwidth: float = Field(ge=0.0, le=1.0, default=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "from_agent_id": "agent_abc123",
                "to_agent_id": "agent_def456",
                "bandwidth": 0.8,
                "metadata": {"priority": "high"}
            }
        }


class ConnectionResponse(BaseModel):
    """Connection entity response"""
    id: str
    from_agent_id: str
    to_agent_id: str
    status: str
    socket_from: Optional[int] = None
    socket_to: Optional[int] = None
    bandwidth: float
    latency_ms: float
    metadata: Dict[str, Any]
    established_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "conn_xyz789",
                "from_agent_id": "agent_abc123",
                "to_agent_id": "agent_def456",
                "status": "connected",
                "socket_from": 15,
                "socket_to": 42,
                "bandwidth": 0.8,
                "latency_ms": 12.5,
                "metadata": {},
                "established_at": "2026-02-04T22:00:00Z",
                "closed_at": None
            }
        }
