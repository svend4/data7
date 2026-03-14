"""
Multi-Agent Coordination API Endpoints

Provides endpoints for coordinating multiple AI agents
"""

from typing import List, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.multi_agent_coordinator import (
    MultiAgentCoordinator,
    Task,
    CoordinationStrategy,
    CoordinationResult
)
from app.domain.models import Agent


router = APIRouter(prefix="/api/multi-agent", tags=["multi-agent"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AgentRequest(BaseModel):
    """Request model for agent"""
    id: str
    name: str
    role: str
    backend_type: str = "gpt-3.5-turbo"
    current_load: float = 0.0
    status: str = "idle"
    capabilities: List[str] = []


class TaskRequest(BaseModel):
    """Request model for task"""
    id: str
    name: str
    description: str
    estimated_time: float
    estimated_cost: float
    required_capabilities: List[str] = []
    priority: int = 0
    dependencies: List[str] = []


class CoordinateRequest(BaseModel):
    """Request to coordinate agents"""
    agents: List[AgentRequest]
    tasks: List[TaskRequest]
    strategy: str = "minimize_time"  # minimize_time, minimize_cost, balance_load, maximize_throughput


class RebalanceRequest(BaseModel):
    """Request to rebalance assignments"""
    current_assignments: List[Dict]  # Simplified
    new_tasks: List[TaskRequest]
    agents: List[AgentRequest]


class AgentAssignmentResponse(BaseModel):
    """Response for agent assignment"""
    agent_id: str
    tasks: List[str]  # Task IDs
    total_time: float
    total_cost: float
    route: List[str]


class CoordinationResponse(BaseModel):
    """Response for coordination"""
    assignments: List[AgentAssignmentResponse]
    total_time: float
    total_cost: float
    load_balance_score: float
    parallelism_factor: float
    metadata: Dict = {}


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/coordinate")
async def coordinate_agents(
    request: CoordinateRequest
) -> CoordinationResponse:
    """
    Coordinate multiple AI agents to handle tasks

    Uses Multi-depot TSP optimization to optimally assign tasks to agents.

    Strategies:
    - minimize_time: Fastest completion (assigns to fastest agents)
    - minimize_cost: Lowest LLM API costs (uses cheaper models where possible)
    - balance_load: Equal distribution across agents
    - maximize_throughput: Maximum parallelism

    Returns optimal task assignments with metrics.
    """
    try:
        # Convert request to domain models
        agents = [
            Agent(
                id=a.id,
                name=a.name,
                role=a.role,
                backend_type=a.backend_type,
                current_load=a.current_load,
                status=a.status,
                capabilities=a.capabilities
            )
            for a in request.agents
        ]

        tasks = [
            Task(
                id=t.id,
                name=t.name,
                description=t.description,
                estimated_time=t.estimated_time,
                estimated_cost=t.estimated_cost,
                required_capabilities=t.required_capabilities,
                priority=t.priority,
                dependencies=t.dependencies
            )
            for t in request.tasks
        ]

        # Parse strategy
        strategy_map = {
            "minimize_time": CoordinationStrategy.MINIMIZE_TIME,
            "minimize_cost": CoordinationStrategy.MINIMIZE_COST,
            "balance_load": CoordinationStrategy.BALANCE_LOAD,
            "maximize_throughput": CoordinationStrategy.MAXIMIZE_THROUGHPUT
        }
        strategy = strategy_map.get(request.strategy, CoordinationStrategy.MINIMIZE_TIME)

        # Coordinate
        coordinator = MultiAgentCoordinator()
        result = coordinator.coordinate(agents, tasks, strategy)

        # Convert to response
        assignments = [
            AgentAssignmentResponse(
                agent_id=a.agent_id,
                tasks=[t.id for t in a.tasks],
                total_time=a.total_time,
                total_cost=a.total_cost,
                route=a.route
            )
            for a in result.assignments
        ]

        return CoordinationResponse(
            assignments=assignments,
            total_time=result.total_time,
            total_cost=result.total_cost,
            load_balance_score=result.load_balance_score,
            parallelism_factor=result.parallelism_factor,
            metadata=result.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coordination failed: {str(e)}"
        )


@router.post("/predict")
async def predict_completion_time(
    request: CoordinateRequest
) -> Dict:
    """
    Predict task completion time without actually coordinating

    Returns best/average/worst case predictions.
    Useful for planning and cost estimation.
    """
    try:
        # Convert to domain models (same as coordinate)
        agents = [Agent(**a.dict()) for a in request.agents]
        tasks = [Task(**t.dict()) for t in request.tasks]

        strategy_map = {
            "minimize_time": CoordinationStrategy.MINIMIZE_TIME,
            "minimize_cost": CoordinationStrategy.MINIMIZE_COST,
            "balance_load": CoordinationStrategy.BALANCE_LOAD,
            "maximize_throughput": CoordinationStrategy.MAXIMIZE_THROUGHPUT
        }
        strategy = strategy_map.get(request.strategy, CoordinationStrategy.MINIMIZE_TIME)

        # Coordinate to get assignments
        coordinator = MultiAgentCoordinator()
        result = coordinator.coordinate(agents, tasks, strategy)

        # Predict
        min_time, avg_time, max_time = coordinator.predict_completion_time(result.assignments)

        return {
            "estimated_time_min": min_time,
            "estimated_time_avg": avg_time,
            "estimated_time_max": max_time,
            "estimated_cost_min": result.total_cost * 0.9,
            "estimated_cost_avg": result.total_cost,
            "estimated_cost_max": result.total_cost * 1.2,
            "num_agents": len(request.agents),
            "num_tasks": len(request.tasks),
            "parallelism_factor": result.parallelism_factor
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/strategies")
async def list_strategies() -> Dict:
    """
    List available coordination strategies

    Returns information about each strategy including:
    - Name and description
    - Use cases
    - Trade-offs
    """
    return {
        "strategies": [
            {
                "id": "minimize_time",
                "name": "Minimize Time",
                "description": "Optimize for fastest completion",
                "approach": "Assigns tasks to fastest agents, prioritizes critical path",
                "use_case": "Time-sensitive workflows, real-time applications",
                "trade_offs": "May use more expensive models, uneven load distribution"
            },
            {
                "id": "minimize_cost",
                "name": "Minimize Cost",
                "description": "Optimize for lowest LLM API costs",
                "approach": "Uses cheaper models where possible, batches requests",
                "use_case": "Budget-constrained applications, batch processing",
                "trade_offs": "Slower execution, may compromise quality slightly"
            },
            {
                "id": "balance_load",
                "name": "Balance Load",
                "description": "Distribute tasks evenly across agents",
                "approach": "Aims for equal utilization of all agents",
                "use_case": "Long-running systems, fair resource allocation",
                "trade_offs": "May not be fastest or cheapest"
            },
            {
                "id": "maximize_throughput",
                "name": "Maximize Throughput",
                "description": "Maximize concurrent task execution",
                "approach": "Assigns independent tasks to different agents",
                "use_case": "High-throughput systems, large task queues",
                "trade_offs": "Requires many available agents"
            }
        ]
    }


@router.get("/metrics")
async def get_metrics_info() -> Dict:
    """
    Get information about coordination metrics

    Explains what each metric means and how it's calculated.
    """
    return {
        "metrics": {
            "total_time": {
                "name": "Total Time",
                "description": "Maximum time across all agent assignments (parallel execution)",
                "unit": "seconds",
                "formula": "max(agent.total_time for agent in assignments)"
            },
            "total_cost": {
                "name": "Total Cost",
                "description": "Sum of all LLM API costs",
                "unit": "USD",
                "formula": "sum(agent.total_cost for agent in assignments)"
            },
            "load_balance_score": {
                "name": "Load Balance Score",
                "description": "How evenly tasks are distributed (0-1, higher is better)",
                "range": "0.0 to 1.0",
                "formula": "exp(-cv) where cv = std_dev / mean",
                "interpretation": {
                    "1.0": "Perfect balance (all agents equal load)",
                    "0.9+": "Excellent balance",
                    "0.7-0.9": "Good balance",
                    "< 0.7": "Uneven distribution"
                }
            },
            "parallelism_factor": {
                "name": "Parallelism Factor",
                "description": "Speedup vs sequential execution",
                "range": "1.0 to num_agents",
                "formula": "sequential_time / parallel_time",
                "interpretation": {
                    "1.0": "No parallelism (all sequential)",
                    "2.0": "2x speedup",
                    "N": "Perfect parallelism (N agents)"
                }
            }
        }
    }
