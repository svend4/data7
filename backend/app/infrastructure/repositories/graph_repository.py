"""
Graph Repository
Database operations for communication graphs and executions
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.models import (
    CommunicationGraphModel,
    GraphEdgeModel,
    GraphExecutionModel,
)
from app.infrastructure.repositories.base import BaseRepository
from app.domain.entities import CommunicationGraph, GraphExecution
from app.domain.value_objects import TaskStatus


class GraphRepository(BaseRepository[CommunicationGraphModel]):
    """Repository for CommunicationGraph operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(CommunicationGraphModel, session)

    async def create_graph(self, graph: CommunicationGraph) -> CommunicationGraphModel:
        """
        Create communication graph with edges

        Args:
            graph: Domain CommunicationGraph entity

        Returns:
            Created CommunicationGraphModel
        """
        graph_model = CommunicationGraphModel(
            id=graph.id,
            root_task_id=graph.root_task_id,
            nodes=graph.nodes,
            execution_plan=graph.execution_plan,
            metadata=graph.metadata,
            created_at=graph.created_at,
        )

        self.session.add(graph_model)

        # Create edges (connections)
        for connection in graph.edges:
            edge_model = GraphEdgeModel(
                graph_id=graph.id,
                connection_id=connection.id,
            )
            self.session.add(edge_model)

        await self.session.flush()
        await self.session.refresh(graph_model)

        return graph_model

    async def get_with_edges(self, graph_id: str) -> Optional[CommunicationGraphModel]:
        """Get graph with edges loaded"""
        result = await self.session.execute(
            select(CommunicationGraphModel)
            .options(selectinload(CommunicationGraphModel.edges))
            .where(CommunicationGraphModel.id == graph_id)
        )
        return result.scalar_one_or_none()

    async def get_all_with_edges(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommunicationGraphModel]:
        """Get all graphs with edges loaded"""
        result = await self.session.execute(
            select(CommunicationGraphModel)
            .options(selectinload(CommunicationGraphModel.edges))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    def to_domain(self, model: CommunicationGraphModel) -> CommunicationGraph:
        """Convert SQLAlchemy model to domain entity"""
        graph = CommunicationGraph(
            root_task_id=model.root_task_id,
            id=model.id,
            nodes=model.nodes.copy() if model.nodes else [],
            execution_plan=model.execution_plan.copy() if model.execution_plan else [],
            metadata=model.metadata or {},
            created_at=model.created_at,
        )

        # Note: edges (connections) are loaded separately
        # They need to be fetched from ConnectionRepository

        return graph


class ExecutionRepository(BaseRepository[GraphExecutionModel]):
    """Repository for GraphExecution operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(GraphExecutionModel, session)

    async def create_execution(self, execution: GraphExecution) -> GraphExecutionModel:
        """
        Create graph execution

        Args:
            execution: Domain GraphExecution entity

        Returns:
            Created GraphExecutionModel
        """
        exec_model = GraphExecutionModel(
            id=execution.id,
            graph_id=execution.graph_id,
            status=execution.status.value,
            current_step=execution.current_step,
            completed_tasks=execution.completed_tasks,
            failed_tasks=execution.failed_tasks,
            active_connections=execution.active_connections,
            results=execution.results,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
        )

        self.session.add(exec_model)
        await self.session.flush()
        await self.session.refresh(exec_model)

        return exec_model

    async def get_by_graph(self, graph_id: str) -> List[GraphExecutionModel]:
        """Get all executions for a graph"""
        result = await self.session.execute(
            select(GraphExecutionModel)
            .where(GraphExecutionModel.graph_id == graph_id)
            .order_by(GraphExecutionModel.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_running_executions(self) -> List[GraphExecutionModel]:
        """Get all currently running executions"""
        result = await self.session.execute(
            select(GraphExecutionModel).where(
                GraphExecutionModel.status == TaskStatus.RUNNING.value
            )
        )
        return list(result.scalars().all())

    def to_domain(self, model: GraphExecutionModel) -> GraphExecution:
        """Convert SQLAlchemy model to domain entity"""
        execution = GraphExecution(
            graph_id=model.graph_id,
            id=model.id,
            status=TaskStatus(model.status),
            current_step=model.current_step,
            completed_tasks=model.completed_tasks.copy() if model.completed_tasks else [],
            failed_tasks=model.failed_tasks.copy() if model.failed_tasks else [],
            active_connections=model.active_connections.copy() if model.active_connections else [],
            results=model.results.copy() if model.results else {},
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

        return execution
