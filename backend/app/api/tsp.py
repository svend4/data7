"""
TSP API Endpoints

Provides endpoints for TSP algorithms and optimization
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.tsp_algorithms import (
    TSPNode,
    TSPDepot,
    TSPCluster,
    TSPSolution,
    MultiDepotTSP,
    DynamicTSP,
    StochasticTSP,
    HierarchicalTSP,
    TwoOptOptimizer,
    SimulatedAnnealingTSP,
    AntColonyTSP,
    GeneticAlgorithmTSP
)


router = APIRouter(prefix="/api/tsp", tags=["tsp"])


# ============================================================================
# Request/Response Models
# ============================================================================

class TSPNodeRequest(BaseModel):
    """Request model for TSP node"""
    id: str
    x: float = 0.0
    y: float = 0.0
    demand: float = 1.0
    service_time: float = 0.0
    priority: int = 0


class TSPDepotRequest(BaseModel):
    """Request model for TSP depot"""
    id: str
    node: TSPNodeRequest
    capacity: float = float('inf')
    available_agents: int = 1


class TSPClusterRequest(BaseModel):
    """Request model for TSP cluster"""
    id: str
    nodes: List[TSPNodeRequest]
    level: int = 0
    parent_cluster: Optional[str] = None


class MultiDepotTSPRequest(BaseModel):
    """Request to solve Multi-depot TSP"""
    nodes: List[TSPNodeRequest]
    depots: List[TSPDepotRequest]
    distance_matrix: Dict[str, float] = Field(
        description="Distance matrix as flat dict with keys like 'node1_node2'"
    )
    algorithm: str = "cluster_first_route_second"


class DynamicTSPRequest(BaseModel):
    """Request for Dynamic TSP"""
    nodes: List[TSPNodeRequest]
    distance_matrix: Dict[str, float]
    start_node_id: str


class DynamicTSPAddNodeRequest(BaseModel):
    """Request to add node to dynamic TSP"""
    node: TSPNodeRequest


class StochasticTSPRequest(BaseModel):
    """Request for Stochastic TSP"""
    nodes: List[TSPNodeRequest]
    presence_probabilities: Dict[str, float]
    distance_matrix: Dict[str, float]
    start_node_id: str
    algorithm: str = "expected_value"  # or "robust"
    risk_factor: float = 0.2


class HierarchicalTSPRequest(BaseModel):
    """Request for Hierarchical TSP"""
    clusters: List[TSPClusterRequest]
    distance_matrix: Dict[str, float]
    inter_cluster_distance: Optional[Dict[str, float]] = None
    algorithm: str = "top_down"  # or "bottom_up", "integrated"


class OptimizationRequest(BaseModel):
    """Request for TSP optimization"""
    route: List[str]
    distance_matrix: Dict[str, float]
    algorithm: str  # "2opt", "simulated_annealing", "ant_colony", "genetic"
    max_iterations: Optional[int] = None


class TSPSolutionResponse(BaseModel):
    """Response containing TSP solution"""
    routes: List[List[str]]
    total_distance: float
    total_cost: float
    total_time: float
    depot_assignment: Dict[str, str] = {}
    metadata: Dict = {}


# ============================================================================
# Helper Functions
# ============================================================================

def parse_distance_matrix(flat_dict: Dict[str, float]) -> Dict[tuple, float]:
    """Convert flat distance matrix to tuple keys"""
    result = {}
    for key, value in flat_dict.items():
        parts = key.split('_', 1)
        if len(parts) == 2:
            result[(parts[0], parts[1])] = value
    return result


def create_tsp_node(node_req: TSPNodeRequest) -> TSPNode:
    """Create TSPNode from request"""
    return TSPNode(
        id=node_req.id,
        x=node_req.x,
        y=node_req.y,
        demand=node_req.demand,
        service_time=node_req.service_time,
        priority=node_req.priority
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/multi-depot/solve")
async def solve_multi_depot_tsp(
    request: MultiDepotTSPRequest
) -> TSPSolutionResponse:
    """
    Solve Multi-depot TSP problem

    Multiple depots (agents) need to visit multiple nodes (tasks).
    Minimizes total distance/cost while assigning nodes to depots.

    Algorithms:
    - cluster_first_route_second: Cluster nodes to nearest depots, then solve TSP
    - savings: Clarke-Wright savings algorithm
    - nearest_neighbor: Nearest neighbor from each depot
    """
    try:
        # Parse inputs
        nodes = [create_tsp_node(n) for n in request.nodes]
        depots = [
            TSPDepot(
                id=d.id,
                node=create_tsp_node(d.node),
                capacity=d.capacity,
                available_agents=d.available_agents
            )
            for d in request.depots
        ]
        distance_matrix = parse_distance_matrix(request.distance_matrix)

        # Solve
        solver = MultiDepotTSP(nodes, depots, distance_matrix)
        solution = solver.solve(algorithm=request.algorithm)

        return TSPSolutionResponse(
            routes=solution.routes,
            total_distance=solution.total_distance,
            total_cost=solution.total_cost,
            total_time=solution.total_time,
            depot_assignment=solution.depot_assignment,
            metadata=solution.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Multi-depot TSP solving failed: {str(e)}"
        )


@router.post("/hierarchical/solve")
async def solve_hierarchical_tsp(
    request: HierarchicalTSPRequest
) -> TSPSolutionResponse:
    """
    Solve Hierarchical TSP problem

    TSP with hierarchy - clusters of nodes at different levels.
    Useful for dissertation structure (chapters → sections → paragraphs).

    Algorithms:
    - top_down: Solve top level first, then sub-levels
    - bottom_up: Solve bottom levels, then aggregate
    - integrated: Solve all levels simultaneously
    """
    try:
        # Parse inputs
        clusters = []
        for c in request.clusters:
            nodes = [create_tsp_node(n) for n in c.nodes]
            cluster = TSPCluster(
                id=c.id,
                nodes=nodes,
                level=c.level,
                parent_cluster=c.parent_cluster
            )
            clusters.append(cluster)

        distance_matrix = parse_distance_matrix(request.distance_matrix)
        inter_cluster = parse_distance_matrix(request.inter_cluster_distance) if request.inter_cluster_distance else None

        # Solve
        solver = HierarchicalTSP(clusters, distance_matrix, inter_cluster)
        solution = solver.solve(algorithm=request.algorithm)

        return TSPSolutionResponse(
            routes=solution.routes,
            total_distance=solution.total_distance,
            total_cost=solution.total_cost,
            total_time=solution.total_time,
            metadata=solution.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hierarchical TSP solving failed: {str(e)}"
        )


@router.post("/stochastic/solve")
async def solve_stochastic_tsp(
    request: StochasticTSPRequest
) -> TSPSolutionResponse:
    """
    Solve Stochastic TSP problem

    TSP where nodes have probability of being present.
    Useful for planning under uncertainty.

    Algorithms:
    - expected_value: Minimize expected distance
    - robust: Minimize worst-case distance (with risk factor)
    """
    try:
        # Parse inputs
        nodes = [create_tsp_node(n) for n in request.nodes]
        start_node = next((n for n in nodes if n.id == request.start_node_id), nodes[0])
        distance_matrix = parse_distance_matrix(request.distance_matrix)

        # Solve
        solver = StochasticTSP(
            nodes,
            request.presence_probabilities,
            distance_matrix,
            start_node
        )

        if request.algorithm == "expected_value":
            solution = solver.solve_expected_value()
        else:  # robust
            solution = solver.solve_robust(risk_factor=request.risk_factor)

        return TSPSolutionResponse(
            routes=solution.routes,
            total_distance=solution.total_distance,
            total_cost=solution.total_cost,
            total_time=solution.total_time,
            metadata=solution.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stochastic TSP solving failed: {str(e)}"
        )


@router.post("/optimize")
async def optimize_route(
    request: OptimizationRequest
) -> TSPSolutionResponse:
    """
    Optimize existing TSP route

    Algorithms:
    - 2opt: Local search (fast, 15-30% improvement)
    - simulated_annealing: Probabilistic optimization (escapes local optima)
    - ant_colony: Bio-inspired (finds diverse solutions)
    - genetic: Evolutionary algorithm (population-based)
    """
    try:
        distance_matrix = parse_distance_matrix(request.distance_matrix)

        if request.algorithm == "2opt":
            max_iter = request.max_iterations or 1000
            optimized_route, distance = TwoOptOptimizer.optimize(
                request.route,
                distance_matrix,
                max_iterations=max_iter
            )
            solution = TSPSolution(
                routes=[optimized_route],
                total_distance=distance,
                total_cost=distance,
                total_time=distance,
                metadata={"algorithm": "2opt", "iterations": max_iter}
            )

        elif request.algorithm == "simulated_annealing":
            # Create nodes from route
            nodes = [TSPNode(id=node_id) for node_id in request.route]
            solver = SimulatedAnnealingTSP(nodes, distance_matrix)
            solution = solver.optimize(initial_route=request.route)

        elif request.algorithm == "ant_colony":
            nodes = [TSPNode(id=node_id) for node_id in request.route]
            solver = AntColonyTSP(nodes, distance_matrix)
            solution = solver.optimize()

        elif request.algorithm == "genetic":
            nodes = [TSPNode(id=node_id) for node_id in request.route]
            solver = GeneticAlgorithmTSP(nodes, distance_matrix)
            solution = solver.optimize(initial_route=request.route)

        else:
            raise ValueError(f"Unknown algorithm: {request.algorithm}")

        return TSPSolutionResponse(
            routes=solution.routes,
            total_distance=solution.total_distance,
            total_cost=solution.total_cost,
            total_time=solution.total_time,
            metadata=solution.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route optimization failed: {str(e)}"
        )


@router.get("/algorithms")
async def list_algorithms() -> Dict:
    """
    List all available TSP algorithms

    Returns information about each algorithm including:
    - Name and description
    - Use cases
    - Time complexity
    - Quality guarantees
    """
    return {
        "multi_depot": {
            "name": "Multi-depot TSP",
            "description": "Multiple depots visiting multiple nodes",
            "algorithms": ["cluster_first_route_second", "savings", "nearest_neighbor"],
            "use_case": "Multi-agent task allocation",
            "complexity": "O(n²) to O(n³)"
        },
        "hierarchical": {
            "name": "Hierarchical TSP",
            "description": "TSP with clustered hierarchy",
            "algorithms": ["top_down", "bottom_up", "integrated"],
            "use_case": "Dissertation structure optimization",
            "complexity": "O(k * n²) where k = num clusters"
        },
        "stochastic": {
            "name": "Stochastic TSP",
            "description": "TSP with probabilistic node presence",
            "algorithms": ["expected_value", "robust"],
            "use_case": "Planning under uncertainty",
            "complexity": "O(n²) to O(n² * s) where s = scenarios"
        },
        "optimization": {
            "name": "Route Optimization",
            "description": "Improve existing routes",
            "algorithms": ["2opt", "simulated_annealing", "ant_colony", "genetic"],
            "use_cases": {
                "2opt": "Fast local improvement (15-30%)",
                "simulated_annealing": "Escape local optima",
                "ant_colony": "Diverse solutions",
                "genetic": "Population-based search"
            },
            "complexity": {
                "2opt": "O(n² * iterations)",
                "simulated_annealing": "O(n * iterations)",
                "ant_colony": "O(ants * iterations * n²)",
                "genetic": "O(population * generations * n)"
            }
        }
    }
