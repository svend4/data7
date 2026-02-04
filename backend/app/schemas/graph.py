"""
Graph API Schemas
Request/response models for Communication Graph endpoints
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GraphEdgeRequest(BaseModel):
    """Edge in communication graph"""
    from_agent_id: str
    to_agent_id: str
    bandwidth: float = Field(ge=0.0, le=1.0, default=1.0)


class GraphCreateRequest(BaseModel):
    """Request to create a communication graph"""
    root_task_id: str = Field(min_length=1)
    nodes: List[str] = Field(min_items=1)  # Agent IDs
    edges: List[GraphEdgeRequest] = Field(default_factory=list)
    execution_plan: List[str] = Field(default_factory=list)  # Task IDs in order
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "root_task_id": "task_root123",
                "nodes": ["agent_1", "agent_2", "agent_3"],
                "edges": [
                    {"from_agent_id": "agent_1", "to_agent_id": "agent_2", "bandwidth": 1.0},
                    {"from_agent_id": "agent_2", "to_agent_id": "agent_3", "bandwidth": 0.8}
                ],
                "execution_plan": ["task_1", "task_2", "task_3"],
                "metadata": {"priority": "high"}
            }
        }


class GraphEdgeResponse(BaseModel):
    """Edge response"""
    id: str
    from_agent_id: str
    to_agent_id: str
    status: str
    bandwidth: float


class GraphResponse(BaseModel):
    """Communication graph response"""
    id: str
    root_task_id: str
    nodes: List[str]
    edges: List[GraphEdgeResponse]
    execution_plan: List[str]
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "graph_abc123",
                "root_task_id": "task_root123",
                "nodes": ["agent_1", "agent_2", "agent_3"],
                "edges": [
                    {
                        "id": "conn_1",
                        "from_agent_id": "agent_1",
                        "to_agent_id": "agent_2",
                        "status": "connected",
                        "bandwidth": 1.0
                    }
                ],
                "execution_plan": ["task_1", "task_2", "task_3"],
                "metadata": {},
                "created_at": "2026-02-04T22:00:00Z"
            }
        }


class ExecutionStartRequest(BaseModel):
    """Request to start graph execution"""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """Graph execution response"""
    id: str
    graph_id: str
    status: str
    current_step: int
    completed_tasks: List[str]
    failed_tasks: List[str]
    active_connections: List[str]
    results: Dict[str, Any]
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "exec_xyz789",
                "graph_id": "graph_abc123",
                "status": "running",
                "current_step": 2,
                "completed_tasks": ["task_1"],
                "failed_tasks": [],
                "active_connections": ["conn_1", "conn_2"],
                "results": {"task_1": {"output": "result data"}},
                "progress": 0.33,
                "started_at": "2026-02-04T22:00:00Z",
                "completed_at": None
            }
        }


class GraphListResponse(BaseModel):
    """List of graphs"""
    graphs: List[GraphResponse]
    total: int
