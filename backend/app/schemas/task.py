"""
Task API Schemas
Request/response models for Task endpoints
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    """Request to create a new task"""
    description: str = Field(min_length=1)
    task_type: str = Field(min_length=1)
    priority: int = Field(ge=1, le=10, default=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Analyze Q4 budget variance report",
                "task_type": "analysis",
                "priority": 7,
                "metadata": {"quarter": "Q4", "year": 2026}
            }
        }


class TaskResponse(BaseModel):
    """Task entity response"""
    id: str
    description: str
    task_type: str
    status: str
    priority: int
    assigned_agent_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_xyz789abc",
                "description": "Analyze Q4 budget variance",
                "task_type": "analysis",
                "status": "completed",
                "priority": 7,
                "assigned_agent_id": "agent_abc123",
                "result": {"variance": -5.2, "recommendation": "investigate"},
                "error": None,
                "metadata": {"quarter": "Q4"},
                "created_at": "2026-02-04T22:00:00Z",
                "started_at": "2026-02-04T22:01:00Z",
                "completed_at": "2026-02-04T22:02:30Z",
                "duration_seconds": 90.0
            }
        }
