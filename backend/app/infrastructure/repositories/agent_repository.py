"""
Agent Repository
Database operations for agents and their capabilities
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.models import AgentModel, AgentCapabilityModel
from app.infrastructure.repositories.base import BaseRepository
from app.domain.entities import Agent
from app.domain.value_objects import (
    AgentStatus,
    AgentCapability,
    PerformanceMetrics,
    Vector3,
)


class AgentRepository(BaseRepository[AgentModel]):
    """Repository for Agent operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(AgentModel, session)

    async def create_agent(self, agent: Agent) -> AgentModel:
        """
        Create agent with capabilities

        Args:
            agent: Domain Agent entity

        Returns:
            Created AgentModel
        """
        # Create agent model
        agent_model = AgentModel(
            id=agent.id,
            role=agent.role,
            status=agent.status.value,
            avg_response_time=agent.metrics.avg_response_time,
            success_rate=agent.metrics.success_rate,
            total_tasks=agent.metrics.total_tasks,
            current_load=agent.metrics.current_load,
            position_x=agent.position.x if agent.position else None,
            position_y=agent.position.y if agent.position else None,
            position_z=agent.position.z if agent.position else None,
            metadata=agent.metadata,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )

        self.session.add(agent_model)

        # Create capabilities
        for cap in agent.capabilities:
            cap_model = AgentCapabilityModel(
                agent_id=agent.id,
                name=cap.name,
                category=cap.category,
                level=cap.level,
                description=cap.description,
            )
            self.session.add(cap_model)

        await self.session.flush()
        await self.session.refresh(agent_model)

        # Load capabilities relationship
        await self.session.refresh(agent_model, ["capabilities"])

        return agent_model

    async def get_agent_with_capabilities(self, agent_id: str) -> Optional[AgentModel]:
        """
        Get agent with all capabilities loaded

        Args:
            agent_id: Agent ID

        Returns:
            AgentModel with capabilities or None
        """
        result = await self.session.execute(
            select(AgentModel)
            .options(selectinload(AgentModel.capabilities))
            .where(AgentModel.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_all_with_capabilities(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentModel]:
        """
        Get all agents with capabilities loaded

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of AgentModels with capabilities
        """
        result = await self.session.execute(
            select(AgentModel)
            .options(selectinload(AgentModel.capabilities))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: AgentStatus) -> List[AgentModel]:
        """
        Get agents by status

        Args:
            status: Agent status

        Returns:
            List of agents
        """
        result = await self.session.execute(
            select(AgentModel)
            .options(selectinload(AgentModel.capabilities))
            .where(AgentModel.status == status.value)
        )
        return list(result.scalars().all())

    async def get_by_role(self, role: str) -> List[AgentModel]:
        """
        Get agents by role

        Args:
            role: Agent role

        Returns:
            List of agents
        """
        result = await self.session.execute(
            select(AgentModel)
            .options(selectinload(AgentModel.capabilities))
            .where(AgentModel.role == role)
        )
        return list(result.scalars().all())

    async def get_available_agents(self, max_load: float = 0.8) -> List[AgentModel]:
        """
        Get available agents (idle with low load)

        Args:
            max_load: Maximum load threshold

        Returns:
            List of available agents
        """
        result = await self.session.execute(
            select(AgentModel)
            .options(selectinload(AgentModel.capabilities))
            .where(
                AgentModel.status == AgentStatus.IDLE.value,
                AgentModel.current_load < max_load
            )
        )
        return list(result.scalars().all())

    async def update_agent_metrics(
        self,
        agent_id: str,
        metrics: PerformanceMetrics
    ) -> Optional[AgentModel]:
        """
        Update agent performance metrics

        Args:
            agent_id: Agent ID
            metrics: New performance metrics

        Returns:
            Updated agent or None
        """
        return await self.update(
            agent_id,
            avg_response_time=metrics.avg_response_time,
            success_rate=metrics.success_rate,
            total_tasks=metrics.total_tasks,
            current_load=metrics.current_load,
        )

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get agent statistics

        Returns:
            Dict with statistics
        """
        # Count by status
        total_query = select(func.count()).select_from(AgentModel)
        idle_query = total_query.where(AgentModel.status == AgentStatus.IDLE.value)
        busy_query = total_query.where(AgentModel.status == AgentStatus.BUSY.value)
        offline_query = total_query.where(AgentModel.status == AgentStatus.OFFLINE.value)

        total_result = await self.session.execute(total_query)
        idle_result = await self.session.execute(idle_query)
        busy_result = await self.session.execute(busy_query)
        offline_result = await self.session.execute(offline_query)

        total = total_result.scalar_one()
        idle = idle_result.scalar_one()
        busy = busy_result.scalar_one()
        offline = offline_result.scalar_one()

        # Calculate averages
        avg_success_rate = 0.0
        avg_response_time = 0.0

        if total > 0:
            avg_query = select(
                func.avg(AgentModel.success_rate),
                func.avg(AgentModel.avg_response_time)
            )
            avg_result = await self.session.execute(avg_query)
            row = avg_result.one()
            avg_success_rate = float(row[0]) if row[0] else 0.0
            avg_response_time = float(row[1]) if row[1] else 0.0

        return {
            "total_agents": total,
            "idle_agents": idle,
            "busy_agents": busy,
            "offline_agents": offline,
            "avg_success_rate": avg_success_rate,
            "avg_response_time": avg_response_time,
        }

    def to_domain(self, model: AgentModel) -> Agent:
        """
        Convert SQLAlchemy model to domain entity

        Args:
            model: AgentModel

        Returns:
            Domain Agent entity
        """
        capabilities = [
            AgentCapability(
                name=cap.name,
                category=cap.category,
                level=cap.level,
                description=cap.description,
            )
            for cap in model.capabilities
        ]

        position = None
        if model.position_x is not None:
            position = Vector3(
                x=model.position_x,
                y=model.position_y,
                z=model.position_z,
            )

        metrics = PerformanceMetrics(
            avg_response_time=model.avg_response_time,
            success_rate=model.success_rate,
            total_tasks=model.total_tasks,
            current_load=model.current_load,
        )

        agent = Agent(
            role=model.role,
            capabilities=capabilities,
            id=model.id,
            status=AgentStatus(model.status),
            metrics=metrics,
            position=position,
            metadata=model.metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

        return agent
