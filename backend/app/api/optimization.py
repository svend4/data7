"""
Graph Optimization API Endpoints

Provides endpoints for analyzing and optimizing communication graphs
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.services.graph_optimizer import (
    GraphOptimizer,
    OptimizationStrategy,
    OptimizationResult,
    GraphAnalysis,
    ExecutionPrediction
)
from app.infrastructure.repositories.graph_repository import GraphRepository
from app.infrastructure.repositories.agent_repository import AgentRepository
from app.infrastructure.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/optimization", tags=["optimization"])


# Request/Response Models

class OptimizeGraphRequest(BaseModel):
    """Request to optimize a graph"""
    strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_TIME
    constraints: Optional[Dict] = None


class OptimizationResultResponse(BaseModel):
    """Response containing optimization results"""
    original_graph_id: str
    optimized_graph_id: str
    strategy: str
    expected_time_savings: float
    expected_cost_savings: float
    parallel_groups: List[List[str]]
    critical_path: List[str]
    load_distribution: Dict[str, float]
    recommendations: List[str]
    created_at: str


class GraphAnalysisResponse(BaseModel):
    """Response containing graph analysis"""
    graph_id: str
    total_nodes: int
    total_edges: int
    critical_path: List[str]
    critical_path_length: float
    parallel_groups: List[List[str]]
    max_parallelism: int
    bottlenecks: List[str]
    estimated_time_sequential: float
    estimated_time_parallel: float
    speedup_factor: float
    estimated_cost: float
    resource_requirements: Dict[str, int]


class ExecutionPredictionResponse(BaseModel):
    """Response containing execution predictions"""
    graph_id: str
    estimated_time_min: float
    estimated_time_avg: float
    estimated_time_max: float
    estimated_cost_min: float
    estimated_cost_avg: float
    estimated_cost_max: float
    success_probability: float
    risk_factors: List[str]


# Dependency injection

async def get_graph_repository(
    db: AsyncSession = Depends(get_db_session)
) -> GraphRepository:
    """Get graph repository instance"""
    return GraphRepository(db)


async def get_agent_repository(
    db: AsyncSession = Depends(get_db_session)
) -> AgentRepository:
    """Get agent repository instance"""
    return AgentRepository(db)


def get_graph_optimizer() -> GraphOptimizer:
    """Get graph optimizer instance"""
    return GraphOptimizer()


# API Endpoints

@router.post("/graphs/{graph_id}/optimize")
async def optimize_graph(
    graph_id: str,
    request: OptimizeGraphRequest,
    graph_repo: GraphRepository = Depends(get_graph_repository),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    optimizer: GraphOptimizer = Depends(get_graph_optimizer)
) -> OptimizationResultResponse:
    """
    Optimize a communication graph

    Applies heuristic-based optimization to improve execution time, cost,
    load distribution, or parallelism based on selected strategy.

    Args:
        graph_id: ID of the graph to optimize
        request: Optimization request with strategy and constraints

    Returns:
        OptimizationResult with optimized graph and metrics

    Raises:
        404: Graph not found
        400: Invalid optimization request
    """
    # Fetch graph
    graph_model = await graph_repo.get_with_edges(graph_id)
    if not graph_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with ID {graph_id} not found"
        )

    # Convert to domain model
    graph = graph_model.to_domain()

    # Fetch available agents
    agent_models = await agent_repo.get_all()
    available_agents = [a.to_domain() for a in agent_models]

    # Optimize
    try:
        result = optimizer.optimize(
            graph=graph,
            available_agents=available_agents,
            strategy=request.strategy,
            constraints=request.constraints
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Optimization failed: {str(e)}"
        )

    # Save optimized graph
    # (In production, you might want to save the optimized graph to DB)

    return OptimizationResultResponse(
        original_graph_id=result.original_graph_id,
        optimized_graph_id=result.optimized_graph_id,
        strategy=result.strategy.value,
        expected_time_savings=result.expected_time_savings,
        expected_cost_savings=result.expected_cost_savings,
        parallel_groups=result.parallel_groups,
        critical_path=result.critical_path,
        load_distribution=result.load_distribution,
        recommendations=result.recommendations,
        created_at=result.created_at.isoformat()
    )


@router.get("/graphs/{graph_id}/analyze")
async def analyze_graph(
    graph_id: str,
    graph_repo: GraphRepository = Depends(get_graph_repository),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    optimizer: GraphOptimizer = Depends(get_graph_optimizer)
) -> GraphAnalysisResponse:
    """
    Analyze a communication graph

    Provides detailed analysis without optimization:
    - Critical path identification
    - Parallel execution groups
    - Bottleneck detection
    - Resource requirements
    - Time and cost estimates

    Args:
        graph_id: ID of the graph to analyze

    Returns:
        GraphAnalysis with detailed metrics

    Raises:
        404: Graph not found
    """
    # Fetch graph
    graph_model = await graph_repo.get_with_edges(graph_id)
    if not graph_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with ID {graph_id} not found"
        )

    # Convert to domain model
    graph = graph_model.to_domain()

    # Fetch available agents
    agent_models = await agent_repo.get_all()
    available_agents = [a.to_domain() for a in agent_models]

    # Analyze
    try:
        analysis = optimizer.analyze_graph(
            graph=graph,
            available_agents=available_agents
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )

    return GraphAnalysisResponse(
        graph_id=analysis.graph_id,
        total_nodes=analysis.total_nodes,
        total_edges=analysis.total_edges,
        critical_path=analysis.critical_path,
        critical_path_length=analysis.critical_path_length,
        parallel_groups=analysis.parallel_groups,
        max_parallelism=analysis.max_parallelism,
        bottlenecks=analysis.bottlenecks,
        estimated_time_sequential=analysis.estimated_time_sequential,
        estimated_time_parallel=analysis.estimated_time_parallel,
        speedup_factor=analysis.speedup_factor,
        estimated_cost=analysis.estimated_cost,
        resource_requirements=analysis.resource_requirements
    )


@router.post("/graphs/{graph_id}/predict")
async def predict_execution(
    graph_id: str,
    graph_repo: GraphRepository = Depends(get_graph_repository),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    optimizer: GraphOptimizer = Depends(get_graph_optimizer)
) -> ExecutionPredictionResponse:
    """
    Predict execution metrics without running

    Provides best/average/worst case predictions for:
    - Execution time
    - API costs
    - Success probability
    - Risk factors

    Useful for planning and cost estimation before execution.

    Args:
        graph_id: ID of the graph to predict

    Returns:
        ExecutionPrediction with scenarios and risks

    Raises:
        404: Graph not found
    """
    # Fetch graph
    graph_model = await graph_repo.get_with_edges(graph_id)
    if not graph_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with ID {graph_id} not found"
        )

    # Convert to domain model
    graph = graph_model.to_domain()

    # Fetch available agents
    agent_models = await agent_repo.get_all()
    available_agents = [a.to_domain() for a in agent_models]

    # Predict
    try:
        prediction = optimizer.predict_execution(
            graph=graph,
            available_agents=available_agents
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(e)}"
        )

    return ExecutionPredictionResponse(
        graph_id=prediction.graph_id,
        estimated_time_min=prediction.estimated_time_min,
        estimated_time_avg=prediction.estimated_time_avg,
        estimated_time_max=prediction.estimated_time_max,
        estimated_cost_min=prediction.estimated_cost_min,
        estimated_cost_avg=prediction.estimated_cost_avg,
        estimated_cost_max=prediction.estimated_cost_max,
        success_probability=prediction.success_probability,
        risk_factors=prediction.risk_factors
    )


@router.get("/strategies")
async def list_optimization_strategies() -> Dict[str, List[Dict[str, str]]]:
    """
    List available optimization strategies

    Returns:
        Dictionary of strategies with descriptions

    Each strategy optimizes for different goals:
    - MINIMIZE_TIME: Fastest execution
    - MINIMIZE_COST: Lowest LLM API costs
    - BALANCE_LOAD: Even distribution across agents
    - MAXIMIZE_PARALLELISM: Maximum concurrent execution
    """
    strategies = [
        {
            "id": OptimizationStrategy.MINIMIZE_TIME.value,
            "name": "Minimize Time",
            "description": "Optimize for fastest execution by assigning fastest agents to critical path",
            "use_case": "Time-sensitive workflows, real-time applications"
        },
        {
            "id": OptimizationStrategy.MINIMIZE_COST.value,
            "name": "Minimize Cost",
            "description": "Optimize for lowest LLM API costs by using cheaper models where possible",
            "use_case": "Budget-constrained applications, batch processing"
        },
        {
            "id": OptimizationStrategy.BALANCE_LOAD.value,
            "name": "Balance Load",
            "description": "Distribute tasks evenly across agents for balanced utilization",
            "use_case": "Long-running systems, fair resource allocation"
        },
        {
            "id": OptimizationStrategy.MAXIMIZE_PARALLELISM.value,
            "name": "Maximize Parallelism",
            "description": "Maximize concurrent execution by assigning independent tasks to different agents",
            "use_case": "High-throughput systems, large graphs"
        }
    ]

    return {"strategies": strategies}
