"""
Dependency Injection
FastAPI dependencies for database sessions and repositories
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session
from app.infrastructure.repositories import (
    AgentRepository,
    TaskRepository,
    ConnectionRepository,
    GraphRepository,
    ExecutionRepository,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async for session in get_session():
        yield session


async def get_agent_repository(
    db: AsyncSession = Depends(get_db)
) -> AgentRepository:
    """Dependency for AgentRepository"""
    return AgentRepository(db)


async def get_task_repository(
    db: AsyncSession = Depends(get_db)
) -> TaskRepository:
    """Dependency for TaskRepository"""
    return TaskRepository(db)


async def get_connection_repository(
    db: AsyncSession = Depends(get_db)
) -> ConnectionRepository:
    """Dependency for ConnectionRepository"""
    return ConnectionRepository(db)


async def get_graph_repository(
    db: AsyncSession = Depends(get_db)
) -> GraphRepository:
    """Dependency for GraphRepository"""
    return GraphRepository(db)


async def get_execution_repository(
    db: AsyncSession = Depends(get_db)
) -> ExecutionRepository:
    """Dependency for ExecutionRepository"""
    return ExecutionRepository(db)
