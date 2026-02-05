"""
Pytest configuration and fixtures for Meta-Orchestrator Switchboard tests
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import get_db, Base
from app.models.database import (
    AgentModel,
    TaskModel,
    ExecutionModel,
    ConnectionModel,
    GraphModel,
    GraphEdgeModel,
)


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create a fresh database engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
async def sample_agent(db_session: AsyncSession) -> AgentModel:
    """Create a sample agent for testing."""
    agent = AgentModel(
        role="code_reviewer",
        model="gpt-4",
        temperature=0.7,
        max_tokens=2000,
        status="idle",
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest.fixture
async def sample_agents(db_session: AsyncSession) -> list[AgentModel]:
    """Create multiple sample agents for testing."""
    agents = [
        AgentModel(
            role=f"agent_{i}",
            model="gpt-4" if i % 2 == 0 else "claude-3-sonnet",
            temperature=0.7,
            max_tokens=2000,
            status="idle" if i % 3 == 0 else "busy",
        )
        for i in range(5)
    ]
    db_session.add_all(agents)
    await db_session.commit()
    for agent in agents:
        await db_session.refresh(agent)
    return agents


@pytest.fixture
async def sample_task(db_session: AsyncSession, sample_agent: AgentModel) -> TaskModel:
    """Create a sample task for testing."""
    task = TaskModel(
        name="Review code",
        description="Review Python code for best practices",
        priority=2,
        status="pending",
        agent_id=sample_agent.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def sample_tasks(db_session: AsyncSession, sample_agents: list[AgentModel]) -> list[TaskModel]:
    """Create multiple sample tasks for testing."""
    tasks = [
        TaskModel(
            name=f"Task {i}",
            description=f"Description for task {i}",
            priority=i % 3 + 1,
            status=["pending", "in_progress", "completed"][i % 3],
            agent_id=sample_agents[i % len(sample_agents)].id,
        )
        for i in range(10)
    ]
    db_session.add_all(tasks)
    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)
    return tasks


@pytest.fixture
async def sample_execution(
    db_session: AsyncSession,
    sample_task: TaskModel,
    sample_agent: AgentModel
) -> ExecutionModel:
    """Create a sample execution for testing."""
    execution = ExecutionModel(
        task_id=sample_task.id,
        agent_id=sample_agent.id,
        status="completed",
        execution_time=15.5,
        tokens_used=1500,
        cost=0.045,
    )
    db_session.add(execution)
    await db_session.commit()
    await db_session.refresh(execution)
    return execution


@pytest.fixture
async def sample_graph(db_session: AsyncSession) -> GraphModel:
    """Create a sample graph for testing."""
    graph = GraphModel(
        name="Test Workflow",
        description="A test workflow graph",
        status="pending",
    )
    db_session.add(graph)
    await db_session.commit()
    await db_session.refresh(graph)
    return graph


@pytest.fixture
async def sample_graph_with_edges(
    db_session: AsyncSession,
    sample_graph: GraphModel,
    sample_tasks: list[TaskModel]
) -> GraphModel:
    """Create a sample graph with edges for testing."""
    # Create edges connecting first 5 tasks
    edges = [
        GraphEdgeModel(
            graph_id=sample_graph.id,
            from_task_id=sample_tasks[i].id,
            to_task_id=sample_tasks[i + 1].id,
        )
        for i in range(4)
    ]
    db_session.add_all(edges)
    await db_session.commit()

    # Refresh graph to include edges
    await db_session.refresh(sample_graph)
    return sample_graph


@pytest.fixture
async def sample_connection(
    db_session: AsyncSession,
    sample_agents: list[AgentModel]
) -> ConnectionModel:
    """Create a sample connection for testing."""
    connection = ConnectionModel(
        from_agent_id=sample_agents[0].id,
        to_agent_id=sample_agents[1].id,
        connection_type="dependency",
        status="connected",
    )
    db_session.add(connection)
    await db_session.commit()
    await db_session.refresh(connection)
    return connection


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the LLM.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150,
        },
    }


@pytest.fixture
def mock_optimization_result():
    """Mock optimization result."""
    from app.services.graph_optimizer import OptimizationResult, OptimizationStrategy

    return OptimizationResult(
        strategy=OptimizationStrategy.MINIMIZE_TIME,
        original_estimated_time=100.0,
        optimized_estimated_time=70.0,
        time_saved=30.0,
        time_saved_percentage=30.0,
        original_estimated_cost=5.0,
        optimized_estimated_cost=4.0,
        cost_saved=1.0,
        cost_saved_percentage=20.0,
        critical_path=["task_1", "task_2", "task_3"],
        bottlenecks=["task_2"],
        recommendations=[
            "Assign fastest agent to task_2 (bottleneck)",
            "Use parallel execution where possible",
        ],
    )


@pytest.fixture
def mock_metrics():
    """Mock system metrics."""
    return {
        "error_rate": 0.05,
        "agent_idle_percentage": 0.30,
        "agents_error_count": 1.0,
        "avg_execution_time": 12.5,
        "pending_tasks_count": 25.0,
        "total_agents": 10.0,
        "idle_agents": 3.0,
        "total_tasks": 100.0,
        "failed_tasks": 5.0,
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def anyio_backend():
    """Set anyio backend to asyncio."""
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_sequences(db_session):
    """Reset database sequences after each test (for consistent IDs)."""
    yield
    # Cleanup happens automatically with in-memory database
