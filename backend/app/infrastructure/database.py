"""
Database Configuration and Session Management
PostgreSQL + SQLAlchemy setup with connection pooling
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# Base class for SQLAlchemy models
Base = declarative_base()


# Database engines
_engine: AsyncEngine | None = None
_sync_engine = None
_session_maker: async_sessionmaker[AsyncSession] | None = None
_sync_session_maker = None


def get_database_url(async_driver: bool = True) -> str:
    """
    Get database URL for SQLAlchemy

    Args:
        async_driver: If True, use asyncpg; if False, use psycopg2

    Returns:
        Database URL string
    """
    if settings.DATABASE_URL:
        # Replace postgres:// with postgresql+asyncpg:// or postgresql://
        url = settings.DATABASE_URL
        if async_driver:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            url = url.replace("postgres://", "postgresql+asyncpg://")
        else:
            url = url.replace("postgresql+asyncpg://", "postgresql://")
            url = url.replace("postgres://", "postgresql://")
        return url

    # Build from components
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    db = settings.POSTGRES_DB

    driver = "postgresql+asyncpg" if async_driver else "postgresql"
    return f"{driver}://{user}:{password}@{host}:{port}/{db}"


def create_database_engine() -> AsyncEngine:
    """
    Create async database engine with connection pooling

    Returns:
        AsyncEngine instance
    """
    url = get_database_url(async_driver=True)

    # Connection pool settings
    pool_size = settings.DB_POOL_SIZE
    max_overflow = settings.DB_MAX_OVERFLOW
    pool_pre_ping = True  # Verify connections before using
    pool_recycle = 3600  # Recycle connections after 1 hour

    engine = create_async_engine(
        url,
        echo=settings.DB_ECHO,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
    )

    return engine


def create_sync_engine():
    """Create synchronous engine for Alembic migrations"""
    url = get_database_url(async_driver=False)

    engine = create_engine(
        url,
        echo=settings.DB_ECHO,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    return engine


async def init_database() -> None:
    """
    Initialize database engine and session maker
    Should be called on application startup
    """
    global _engine, _session_maker, _sync_engine, _sync_session_maker

    # Async engine for application
    _engine = create_database_engine()
    _session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Sync engine for migrations
    _sync_engine = create_sync_engine()
    _sync_session_maker = sessionmaker(
        _sync_engine,
        autocommit=False,
        autoflush=False,
    )

    print(f"📊 Database initialized: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")


async def close_database() -> None:
    """
    Close database connections
    Should be called on application shutdown
    """
    global _engine, _sync_engine

    if _engine:
        await _engine.dispose()
        print("📊 Async database connection closed")

    if _sync_engine:
        _sync_engine.dispose()
        print("📊 Sync database connection closed")


def get_engine() -> AsyncEngine:
    """Get async database engine"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine


def get_sync_engine():
    """Get sync database engine (for Alembic)"""
    if _sync_engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _sync_engine


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session

    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    """
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with _session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session() -> AsyncSession:
    """
    Get async database session (for dependency injection)

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with _session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session() -> Session:
    """Get sync database session (for Alembic migrations)"""
    if _sync_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    with _sync_session_maker() as session:
        try:
            yield session
        finally:
            session.close()


# Health check function
async def check_database_connection() -> bool:
    """
    Check if database is accessible

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
