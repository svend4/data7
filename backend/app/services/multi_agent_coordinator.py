"""
Multi-Agent Coordinator using Multi-depot TSP

Coordinates multiple AI agents to handle tasks efficiently using
Multi-depot TSP optimization.

Critical component for MMO AI Bridge v8.0 Meta-Orchestrator.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import math

from app.services.tsp_algorithms import (
    TSPNode, TSPDepot, TSPSolution, MultiDepotTSP
)
from app.domain.models import Agent


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Task:
    """Task to be assigned to agents"""
    id: str
    name: str
    description: str
    estimated_time: float  # seconds
    estimated_cost: float  # USD
    required_capabilities: List[str] = field(default_factory=list)
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentAssignment:
    """Assignment of tasks to an agent"""
    agent_id: str
    tasks: List[Task]
    total_time: float
    total_cost: float
    route: List[str]  # Execution order (task IDs)


@dataclass
class CoordinationResult:
    """Result of multi-agent coordination"""
    assignments: List[AgentAssignment]
    total_time: float
    total_cost: float
    load_balance_score: float  # 0-1, higher is better
    parallelism_factor: float  # Speedup vs sequential
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class CoordinationStrategy(Enum):
    """Strategy for coordinating agents"""
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    BALANCE_LOAD = "balance_load"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"


# ============================================================================
# Multi-Agent Coordinator
# ============================================================================

class MultiAgentCoordinator:
    """
    Coordinates multiple AI agents using Multi-depot TSP

    Each agent is a "depot" and each task is a "city" to visit.
    Optimally assigns tasks to agents to minimize time/cost.

    Key innovation: Applying Multi-depot TSP to AI agent coordination
    """

    def __init__(self):
        self.task_similarity_cache: Dict[Tuple[str, str], float] = {}

    def coordinate(
        self,
        agents: List[Agent],
        tasks: List[Task],
        strategy: CoordinationStrategy = CoordinationStrategy.MINIMIZE_TIME
    ) -> CoordinationResult:
        """
        Coordinate agents to handle tasks

        Args:
            agents: Available AI agents
            tasks: Tasks to be completed
            strategy: Coordination strategy

        Returns:
            CoordinationResult with optimal task assignments
        """
        if not agents or not tasks:
            return CoordinationResult(
                assignments=[],
                total_time=0.0,
                total_cost=0.0,
                load_balance_score=1.0,
                parallelism_factor=1.0,
                metadata={"strategy": strategy.value, "error": "No agents or tasks"}
            )

        # Convert tasks to TSP nodes
        tsp_nodes = self._tasks_to_tsp_nodes(tasks)

        # Convert agents to TSP depots
        tsp_depots = self._agents_to_tsp_depots(agents)

        # Build distance matrix (task similarity/transition cost)
        distance_matrix = self._build_distance_matrix(tasks)

        # Solve Multi-depot TSP
        mdtsp = MultiDepotTSP(tsp_nodes, tsp_depots, distance_matrix)
        tsp_solution = mdtsp.solve(algorithm="cluster_first_route_second")

        # Convert TSP solution to agent assignments
        assignments = self._tsp_solution_to_assignments(
            tsp_solution, agents, tasks
        )

        # Calculate metrics
        total_time = max(a.total_time for a in assignments) if assignments else 0.0
        total_cost = sum(a.total_cost for a in assignments)
        load_balance_score = self._calculate_load_balance(assignments)
        parallelism_factor = self._calculate_parallelism_factor(assignments, tasks)

        return CoordinationResult(
            assignments=assignments,
            total_time=total_time,
            total_cost=total_cost,
            load_balance_score=load_balance_score,
            parallelism_factor=parallelism_factor,
            metadata={
                "strategy": strategy.value,
                "num_agents": len(agents),
                "num_tasks": len(tasks),
                "tsp_algorithm": tsp_solution.metadata.get("algorithm")
            }
        )

    def rebalance(
        self,
        current_assignments: List[AgentAssignment],
        new_tasks: List[Task],
        agents: List[Agent]
    ) -> CoordinationResult:
        """
        Rebalance task assignments when new tasks arrive

        Uses Dynamic TSP approach to adapt assignments
        """
        # Combine current and new tasks
        all_tasks = []
        for assignment in current_assignments:
            all_tasks.extend(assignment.tasks)
        all_tasks.extend(new_tasks)

        # Re-coordinate with all tasks
        return self.coordinate(agents, all_tasks)

    def predict_completion_time(
        self,
        assignments: List[AgentAssignment]
    ) -> Tuple[float, float, float]:
        """
        Predict completion time (min, avg, max)

        Accounts for uncertainty in task durations
        """
        if not assignments:
            return (0.0, 0.0, 0.0)

        # Best case: All tasks complete 20% faster
        min_time = max(a.total_time * 0.8 for a in assignments)

        # Average case: As planned
        avg_time = max(a.total_time for a in assignments)

        # Worst case: Some delays, 30% slower
        max_time = max(a.total_time * 1.3 for a in assignments)

        return (min_time, avg_time, max_time)

    # Private helper methods

    def _tasks_to_tsp_nodes(self, tasks: List[Task]) -> List[TSPNode]:
        """Convert tasks to TSP nodes"""
        nodes = []
        for task in tasks:
            node = TSPNode(
                id=task.id,
                demand=task.estimated_time,  # Resource demand = time
                service_time=task.estimated_time,
                priority=task.priority
            )
            nodes.append(node)
        return nodes

    def _agents_to_tsp_depots(self, agents: List[Agent]) -> List[TSPDepot]:
        """Convert agents to TSP depots"""
        depots = []
        for agent in agents:
            # Each agent is a depot with capacity
            # Capacity = max tasks it can handle (based on current load)
            capacity = max(1, int(10 * (1.0 - agent.current_load)))

            depot_node = TSPNode(
                id=f"depot_{agent.id}",
                x=0.0,
                y=0.0
            )

            depot = TSPDepot(
                id=agent.id,
                node=depot_node,
                capacity=float(capacity),
                available_agents=1
            )
            depots.append(depot)

        return depots

    def _build_distance_matrix(self, tasks: List[Task]) -> Dict[Tuple[str, str], float]:
        """
        Build distance matrix between tasks

        Distance = context switching cost + semantic distance
        """
        distance_matrix = {}

        for i, task1 in enumerate(tasks):
            for j, task2 in enumerate(tasks):
                if i == j:
                    distance_matrix[(task1.id, task2.id)] = 0.0
                    continue

                # Calculate similarity/transition cost
                distance = self._calculate_task_distance(task1, task2)
                distance_matrix[(task1.id, task2.id)] = distance

        # Add depot-to-task distances
        for task in tasks:
            # Depot nodes (agents) are named "depot_<agent_id>"
            # For simplicity, depot-to-task distance = base cost
            base_cost = task.estimated_time * 0.1
            distance_matrix[(f"depot_{task.id}", task.id)] = base_cost
            distance_matrix[(task.id, f"depot_{task.id}")] = base_cost

        return distance_matrix

    def _calculate_task_distance(self, task1: Task, task2: Task) -> float:
        """
        Calculate distance (context switching cost) between two tasks

        Lower distance = more similar tasks (better to do sequentially)
        """
        # Check cache
        cache_key = (task1.id, task2.id)
        if cache_key in self.task_similarity_cache:
            return self.task_similarity_cache[cache_key]

        # Base distance: average of task times
        base_distance = (task1.estimated_time + task2.estimated_time) / 2

        # Capability overlap bonus (similar tasks are closer)
        caps1 = set(task1.required_capabilities)
        caps2 = set(task2.required_capabilities)

        if caps1 and caps2:
            overlap = len(caps1 & caps2) / len(caps1 | caps2)
            similarity_bonus = overlap * base_distance * 0.5
            base_distance -= similarity_bonus

        # Priority penalty (high priority tasks should be done first)
        priority_penalty = abs(task1.priority - task2.priority) * base_distance * 0.1
        base_distance += priority_penalty

        # Cache result
        self.task_similarity_cache[cache_key] = base_distance

        return base_distance

    def _tsp_solution_to_assignments(
        self,
        tsp_solution: TSPSolution,
        agents: List[Agent],
        tasks: List[Task]
    ) -> List[AgentAssignment]:
        """Convert TSP solution to agent assignments"""
        assignments = []
        task_map = {t.id: t for t in tasks}
        agent_map = {a.id: a for a in agents}

        # Group routes by depot (agent)
        depot_routes: Dict[str, List[str]] = {}
        for task_id, depot_id in tsp_solution.depot_assignment.items():
            if depot_id not in depot_routes:
                depot_routes[depot_id] = []
            depot_routes[depot_id].append(task_id)

        # Create assignments
        for agent in agents:
            task_ids = depot_routes.get(agent.id, [])
            assigned_tasks = [task_map[tid] for tid in task_ids if tid in task_map]

            if assigned_tasks:
                total_time = sum(t.estimated_time for t in assigned_tasks)
                total_cost = sum(t.estimated_cost for t in assigned_tasks)

                assignment = AgentAssignment(
                    agent_id=agent.id,
                    tasks=assigned_tasks,
                    total_time=total_time,
                    total_cost=total_cost,
                    route=task_ids
                )
                assignments.append(assignment)

        return assignments

    def _calculate_load_balance(self, assignments: List[AgentAssignment]) -> float:
        """
        Calculate load balance score (0-1, higher is better)

        Perfect balance = all agents have equal load
        """
        if not assignments:
            return 1.0

        loads = [a.total_time for a in assignments]
        if not loads:
            return 1.0

        avg_load = sum(loads) / len(loads)
        if avg_load == 0:
            return 1.0

        # Calculate variance
        variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
        std_dev = math.sqrt(variance)

        # Coefficient of variation (normalized std dev)
        cv = std_dev / avg_load if avg_load > 0 else 0

        # Convert to 0-1 score (lower CV = better balance)
        # CV of 0 = perfect balance (score 1.0)
        # CV of 1 = high imbalance (score ~0.37)
        balance_score = math.exp(-cv)

        return balance_score

    def _calculate_parallelism_factor(
        self,
        assignments: List[AgentAssignment],
        tasks: List[Task]
    ) -> float:
        """
        Calculate parallelism factor (speedup vs sequential)

        Factor of N = N times faster than sequential
        """
        if not assignments or not tasks:
            return 1.0

        # Sequential time = sum of all task times
        sequential_time = sum(t.estimated_time for t in tasks)

        # Parallel time = max time across all agents
        parallel_time = max(a.total_time for a in assignments)

        if parallel_time == 0:
            return 1.0

        return sequential_time / parallel_time


# ============================================================================
# Usage Example (for documentation)
# ============================================================================

def example_usage():
    """
    Example: Coordinating 3 AI agents to handle 10 tasks

    This demonstrates how to use MultiAgentCoordinator for v8.0
    """
    # Create agents
    agents = [
        Agent(
            id="agent_1",
            name="Fast Agent",
            role="general",
            backend_type="gpt-3.5-turbo",
            current_load=0.2,
            status="idle"
        ),
        Agent(
            id="agent_2",
            name="Accurate Agent",
            role="specialist",
            backend_type="gpt-4",
            current_load=0.5,
            status="idle"
        ),
        Agent(
            id="agent_3",
            name="Cheap Agent",
            role="general",
            backend_type="claude-3-haiku",
            current_load=0.1,
            status="idle"
        ),
    ]

    # Create tasks
    tasks = [
        Task(
            id=f"task_{i}",
            name=f"Task {i}",
            description=f"Complete task {i}",
            estimated_time=5.0 + i,
            estimated_cost=0.1 + i * 0.05,
            required_capabilities=["text_analysis"] if i % 2 == 0 else ["code_gen"],
            priority=i % 3
        )
        for i in range(10)
    ]

    # Coordinate
    coordinator = MultiAgentCoordinator()
    result = coordinator.coordinate(
        agents=agents,
        tasks=tasks,
        strategy=CoordinationStrategy.MINIMIZE_TIME
    )

    # Results
    print(f"Coordination Result:")
    print(f"  Total time: {result.total_time:.1f}s")
    print(f"  Total cost: ${result.total_cost:.2f}")
    print(f"  Load balance: {result.load_balance_score:.2f}")
    print(f"  Parallelism: {result.parallelism_factor:.1f}x speedup")
    print(f"\nAssignments:")
    for assignment in result.assignments:
        print(f"  Agent {assignment.agent_id}: {len(assignment.tasks)} tasks, {assignment.total_time:.1f}s")

    return result


if __name__ == "__main__":
    # Run example
    example_usage()
