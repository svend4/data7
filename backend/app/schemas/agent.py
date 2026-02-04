"""
Agent API Schemas
Request/response models for Agent endpoints
Based on TECHNICAL_SPEC_PART3_API.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.common import (
    Vector3Schema,
    AgentCapabilitySchema,
    PerformanceMetricsSchema
)


# ============================================================================
# Request Schemas
# ============================================================================


class AgentCreateRequest(BaseModel):
    """Request to create a new agent"""
    role: str = Field(min_length=1, max_length=100)
    capabilities: List[AgentCapabilitySchema] = Field(min_items=1)
    position: Optional[Vector3Schema] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "Budget Analyst",
                "capabilities": [
                    {
                        "name": "financial_analysis",
                        "category": "analysis",
                        "level": 4,
                        "description": "Analyze budget allocations and spending"
                    }
                ],
                "position": {"x": 0.0, "y": 1.5, "z": -2.0},
                "metadata": {"department": "finance", "priority": "high"}
            }
        }


class AgentUpdateRequest(BaseModel):
    """Request to update agent properties"""
    status: Optional[str] = None
    position: Optional[Vector3Schema] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "idle",
                "metadata": {"last_task": "task_123"}
            }
        }


# ============================================================================
# Response Schemas
# ============================================================================


class AgentResponse(BaseModel):
    """Agent entity response"""
    id: str
    role: str
    status: str
    capabilities: List[AgentCapabilitySchema]
    metrics: PerformanceMetricsSchema
    position: Optional[Vector3Schema] = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "agent_abc123def456",
                "role": "Budget Analyst",
                "status": "idle",
                "capabilities": [
                    {
                        "name": "financial_analysis",
                        "category": "analysis",
                        "level": 4
                    }
                ],
                "metrics": {
                    "avg_response_time": 1.25,
                    "success_rate": 0.94,
                    "total_tasks": 127,
                    "current_load": 0.15
                },
                "position": {"x": 0.0, "y": 1.5, "z": -2.0},
                "metadata": {"department": "finance"},
                "created_at": "2026-02-04T22:00:00Z",
                "updated_at": "2026-02-04T22:30:00Z"
            }
        }


class AgentListResponse(BaseModel):
    """List of agents response"""
    agents: List[AgentResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "agents": [],
                "total": 15
            }
        }


class AgentStatsResponse(BaseModel):
    """Agent statistics summary"""
    total_agents: int
    idle_agents: int
    busy_agents: int
    offline_agents: int
    avg_success_rate: float
    avg_response_time: float

    class Config:
        json_schema_extra = {
            "example": {
                "total_agents": 25,
                "idle_agents": 18,
                "busy_agents": 5,
                "offline_agents": 2,
                "avg_success_rate": 0.92,
                "avg_response_time": 1.8
            }
        }
