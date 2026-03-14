"""
Agent API Endpoints
CRUD operations for agents with database persistence
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.domain.entities import Agent
from app.domain.value_objects import AgentCapability, AgentStatus, Vector3
from app.schemas.agent import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
    AgentStatsResponse,
)
from app.infrastructure.repositories import AgentRepository
from app.core.dependencies import get_agent_repository

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
async def create_agent(
    request: AgentCreateRequest,
    repo: AgentRepository = Depends(get_agent_repository)
) -> AgentResponse:
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

    # Save to database
    try:
        agent_model = await repo.create_agent(agent)
        # Convert back to domain entity
        agent = repo.to_domain(agent_model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

    return agent_to_response(agent)


@router.get(
    "",
    response_model=AgentListResponse,
    summary="List Agents",
    description="Get all registered agents"
)
async def list_agents(
    repo: AgentRepository = Depends(get_agent_repository)
) -> AgentListResponse:
    """List all agents"""
    try:
        agent_models = await repo.get_all_with_capabilities()
        agents = [repo.to_domain(model) for model in agent_models]
        agent_responses = [agent_to_response(agent) for agent in agents]
        return AgentListResponse(agents=agent_responses, total=len(agent_responses))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get Agent",
    description="Get agent by ID"
)
async def get_agent(
    agent_id: str,
    repo: AgentRepository = Depends(get_agent_repository)
) -> AgentResponse:
    """Get agent by ID"""
    try:
        agent_model = await repo.get_agent_with_capabilities(agent_id)
        if not agent_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        agent = repo.to_domain(agent_model)
        return agent_to_response(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update Agent",
    description="Update agent properties"
)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    repo: AgentRepository = Depends(get_agent_repository)
) -> AgentResponse:
    """Update agent"""
    try:
        # Check if agent exists
        agent_model = await repo.get_agent_with_capabilities(agent_id)
        if not agent_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )

        # Prepare update data
        update_data = {}

        if request.status:
            update_data["status"] = request.status

        if request.position:
            update_data["position_x"] = request.position.x
            update_data["position_y"] = request.position.y
            update_data["position_z"] = request.position.z

        if request.metadata is not None:
            # Merge metadata
            current_metadata = agent_model.metadata or {}
            current_metadata.update(request.metadata)
            update_data["metadata"] = current_metadata

        # Update in database
        if update_data:
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow()
            agent_model = await repo.update(agent_id, **update_data)

            # Reload with capabilities
            agent_model = await repo.get_agent_with_capabilities(agent_id)

        agent = repo.to_domain(agent_model)
        return agent_to_response(agent)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Agent",
    description="Remove agent from system"
)
async def delete_agent(
    agent_id: str,
    repo: AgentRepository = Depends(get_agent_repository)
):
    """Delete agent"""
    try:
        # Check if agent exists
        exists = await repo.exists(agent_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )

        # Delete from database
        await repo.delete(agent_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=AgentStatsResponse,
    summary="Agent Statistics",
    description="Get aggregate statistics for all agents"
)
async def get_agent_stats(
    repo: AgentRepository = Depends(get_agent_repository)
) -> AgentStatsResponse:
    """Get agent statistics"""
    try:
        stats = await repo.get_statistics()
        return AgentStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
