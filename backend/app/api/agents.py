"""
Agent API Endpoints
CRUD operations for agents
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List, Dict
from fastapi import APIRouter, HTTPException, status

from app.domain.entities import Agent
from app.domain.value_objects import AgentCapability, PerformanceMetrics, Vector3
from app.schemas.agent import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
    AgentStatsResponse,
)

# In-memory storage for MVP
# TODO: Replace with database in Phase 1
agents_db: Dict[str, Agent] = {}

router = APIRouter(prefix="/agents", tags=["agents"])


def agent_to_response(agent: Agent) -> AgentResponse:
    """Convert domain Agent to API response"""
    return AgentResponse(
        id=agent.id,
        role=agent.role,
        status=agent.status.value,
        capabilities=[
            {
                "name": cap.name,
                "category": cap.category,
                "level": cap.level,
                "description": cap.description,
            }
            for cap in agent.capabilities
        ],
        metrics={
            "avg_response_time": agent.metrics.avg_response_time,
            "success_rate": agent.metrics.success_rate,
            "total_tasks": agent.metrics.total_tasks,
            "current_load": agent.metrics.current_load,
        },
        position={
            "x": agent.position.x,
            "y": agent.position.y,
            "z": agent.position.z,
        } if agent.position else None,
        metadata=agent.metadata,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent",
    description="Register a new agent in the switchboard system"
)
async def create_agent(request: AgentCreateRequest) -> AgentResponse:
    """Create a new agent"""
    # Convert schema to domain objects
    capabilities = [
        AgentCapability(
            name=cap.name,
            category=cap.category,
            level=cap.level,
            description=cap.description,
        )
        for cap in request.capabilities
    ]

    position = None
    if request.position:
        position = Vector3(
            x=request.position.x,
            y=request.position.y,
            z=request.position.z,
        )

    # Create domain entity
    agent = Agent(
        role=request.role,
        capabilities=capabilities,
        position=position,
        metadata=request.metadata,
    )

    # Store in database
    agents_db[agent.id] = agent

    return agent_to_response(agent)


@router.get(
    "",
    response_model=AgentListResponse,
    summary="List Agents",
    description="Get all registered agents"
)
async def list_agents() -> AgentListResponse:
    """List all agents"""
    agents = [agent_to_response(agent) for agent in agents_db.values()]
    return AgentListResponse(agents=agents, total=len(agents))


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get Agent",
    description="Get agent by ID"
)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get agent by ID"""
    agent = agents_db.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return agent_to_response(agent)


@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update Agent",
    description="Update agent properties"
)
async def update_agent(agent_id: str, request: AgentUpdateRequest) -> AgentResponse:
    """Update agent"""
    agent = agents_db.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    # Update fields
    if request.status:
        from app.domain.value_objects import AgentStatus
        agent.status = AgentStatus(request.status)

    if request.position:
        agent.position = Vector3(
            x=request.position.x,
            y=request.position.y,
            z=request.position.z,
        )

    if request.metadata is not None:
        agent.metadata.update(request.metadata)

    from datetime import datetime
    agent.updated_at = datetime.utcnow()

    return agent_to_response(agent)


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Agent",
    description="Remove agent from system"
)
async def delete_agent(agent_id: str):
    """Delete agent"""
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    del agents_db[agent_id]


@router.get(
    "/stats/summary",
    response_model=AgentStatsResponse,
    summary="Agent Statistics",
    description="Get aggregate statistics for all agents"
)
async def get_agent_stats() -> AgentStatsResponse:
    """Get agent statistics"""
    from app.domain.value_objects import AgentStatus

    agents = list(agents_db.values())
    total = len(agents)

    if total == 0:
        return AgentStatsResponse(
            total_agents=0,
            idle_agents=0,
            busy_agents=0,
            offline_agents=0,
            avg_success_rate=0.0,
            avg_response_time=0.0,
        )

    idle = sum(1 for a in agents if a.status == AgentStatus.IDLE)
    busy = sum(1 for a in agents if a.status == AgentStatus.BUSY)
    offline = sum(1 for a in agents if a.status == AgentStatus.OFFLINE)

    avg_success = sum(a.metrics.success_rate for a in agents) / total
    avg_response = sum(a.metrics.avg_response_time for a in agents) / total

    return AgentStatsResponse(
        total_agents=total,
        idle_agents=idle,
        busy_agents=busy,
        offline_agents=offline,
        avg_success_rate=avg_success,
        avg_response_time=avg_response,
    )
