"""
Connection Repository
Database operations for connections between agents
"""

from typing import List, Optional, Dict, Any, Set
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import ConnectionModel
from app.infrastructure.repositories.base import BaseRepository
from app.domain.entities import Connection
from app.domain.value_objects import ConnectionStatus


class ConnectionRepository(BaseRepository[ConnectionModel]):
    """Repository for Connection operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(ConnectionModel, session)

    async def create_connection(self, connection: Connection) -> ConnectionModel:
        """
        Create connection

        Args:
            connection: Domain Connection entity

        Returns:
            Created ConnectionModel
        """
        conn_model = ConnectionModel(
            id=connection.id,
            from_agent_id=connection.from_agent_id,
            to_agent_id=connection.to_agent_id,
            status=connection.status.value,
            socket_from=connection.socket_from,
            socket_to=connection.socket_to,
            bandwidth=connection.bandwidth,
            latency_ms=connection.latency_ms,
            metadata=connection.metadata,
            established_at=connection.established_at,
            closed_at=connection.closed_at,
        )

        self.session.add(conn_model)
        await self.session.flush()
        await self.session.refresh(conn_model)

        return conn_model

    async def get_by_status(self, status: ConnectionStatus) -> List[ConnectionModel]:
        """Get connections by status"""
        result = await self.session.execute(
            select(ConnectionModel).where(ConnectionModel.status == status.value)
        )
        return list(result.scalars().all())

    async def get_by_agent(self, agent_id: str) -> List[ConnectionModel]:
        """Get all connections for an agent (from or to)"""
        result = await self.session.execute(
            select(ConnectionModel).where(
                (ConnectionModel.from_agent_id == agent_id) |
                (ConnectionModel.to_agent_id == agent_id)
            )
        )
        return list(result.scalars().all())

    async def get_outgoing(self, agent_id: str) -> List[ConnectionModel]:
        """Get outgoing connections from an agent"""
        result = await self.session.execute(
            select(ConnectionModel).where(ConnectionModel.from_agent_id == agent_id)
        )
        return list(result.scalars().all())

    async def get_incoming(self, agent_id: str) -> List[ConnectionModel]:
        """Get incoming connections to an agent"""
        result = await self.session.execute(
            select(ConnectionModel).where(ConnectionModel.to_agent_id == agent_id)
        )
        return list(result.scalars().all())

    async def get_with_filters(
        self,
        status: Optional[ConnectionStatus] = None,
        agent_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConnectionModel]:
        """Get connections with filters"""
        query = select(ConnectionModel)

        if status:
            query = query.where(ConnectionModel.status == status.value)
        if agent_id:
            query = query.where(
                (ConnectionModel.from_agent_id == agent_id) |
                (ConnectionModel.to_agent_id == agent_id)
            )

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_allocated_sockets(self) -> Set[int]:
        """Get all currently allocated socket numbers"""
        result = await self.session.execute(
            select(ConnectionModel.socket_from, ConnectionModel.socket_to).where(
                ConnectionModel.status == ConnectionStatus.CONNECTED.value
            )
        )

        sockets = set()
        for row in result.all():
            if row[0]:
                sockets.add(row[0])
            if row[1]:
                sockets.add(row[1])

        return sockets

    async def get_statistics(self) -> Dict[str, Any]:
        """Get connection statistics"""
        # Count by status
        total_query = select(func.count()).select_from(ConnectionModel)
        connected_query = total_query.where(ConnectionModel.status == ConnectionStatus.CONNECTED.value)
        disconnected_query = total_query.where(ConnectionModel.status == ConnectionStatus.DISCONNECTED.value)
        transmitting_query = total_query.where(ConnectionModel.status == ConnectionStatus.TRANSMITTING.value)

        total_result = await self.session.execute(total_query)
        connected_result = await self.session.execute(connected_query)
        disconnected_result = await self.session.execute(disconnected_query)
        transmitting_result = await self.session.execute(transmitting_query)

        total = total_result.scalar_one()
        connected = connected_result.scalar_one()
        disconnected = disconnected_result.scalar_one()
        transmitting = transmitting_result.scalar_one()

        # Calculate averages
        avg_bandwidth = 0.0
        avg_latency = 0.0

        if total > 0:
            avg_query = select(
                func.avg(ConnectionModel.bandwidth),
                func.avg(ConnectionModel.latency_ms)
            )
            avg_result = await self.session.execute(avg_query)
            row = avg_result.one()
            avg_bandwidth = float(row[0]) if row[0] else 0.0
            avg_latency = float(row[1]) if row[1] else 0.0

        # Get allocated sockets
        allocated_sockets = await self.get_allocated_sockets()
        available_sockets = 100 - len(allocated_sockets)

        return {
            "total_connections": total,
            "connected": connected,
            "disconnected": disconnected,
            "transmitting": transmitting,
            "available_sockets": available_sockets,
            "avg_bandwidth": round(avg_bandwidth, 3),
            "avg_latency_ms": round(avg_latency, 2),
        }

    def to_domain(self, model: ConnectionModel) -> Connection:
        """Convert SQLAlchemy model to domain entity"""
        connection = Connection(
            from_agent_id=model.from_agent_id,
            to_agent_id=model.to_agent_id,
            id=model.id,
            status=ConnectionStatus(model.status),
            socket_from=model.socket_from,
            socket_to=model.socket_to,
            bandwidth=model.bandwidth,
            latency_ms=model.latency_ms,
            metadata=model.metadata,
            established_at=model.established_at,
            closed_at=model.closed_at,
        )

        return connection
