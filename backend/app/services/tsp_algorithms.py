"""
TSP Algorithm Implementations

Implements various TSP variants and optimization algorithms:
- Multi-depot TSP (for multi-agent coordination)
- Dynamic TSP (adaptation during execution)
- Stochastic TSP (probabilistic estimates)
- Optimization algorithms (2-opt, Ant Colony, Simulated Annealing)
"""

from typing import List, Dict, Tuple, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import math
import random
from datetime import datetime


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TSPNode:
    """Node in TSP graph"""
    id: str
    x: float = 0.0  # Position for visualization
    y: float = 0.0
    demand: float = 1.0  # Resource demand
    time_window: Optional[Tuple[float, float]] = None  # (earliest, latest)
    service_time: float = 0.0  # Time to service this node
    priority: int = 0  # Priority level


@dataclass
class TSPEdge:
    """Edge between TSP nodes"""
    from_node: str
    to_node: str
    distance: float
    cost: float = 0.0
    time: float = 0.0
    probability: float = 1.0  # For stochastic TSP


@dataclass
class TSPDepot:
    """Depot for Multi-depot TSP"""
    id: str
    node: TSPNode
    capacity: float = float('inf')
    available_agents: int = 1


@dataclass
class TSPSolution:
    """Solution to TSP problem"""
    routes: List[List[str]]  # List of routes (each route is list of node IDs)
    total_distance: float
    total_cost: float
    total_time: float
    depot_assignment: Dict[str, str] = field(default_factory=dict)  # node_id -> depot_id
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Multi-Depot TSP
# ============================================================================

class MultiDepotTSP:
    """
    Multi-depot TSP solver

    Problem: Multiple depots (agents) need to visit multiple cities (tasks)
    Goal: Minimize total distance/cost while assigning cities to depots

    Use case: Multi-agent coordination in MMO AI Bridge v8.0
    """

    def __init__(
        self,
        nodes: List[TSPNode],
        depots: List[TSPDepot],
        distance_matrix: Dict[Tuple[str, str], float]
    ):
        self.nodes = nodes
        self.depots = depots
        self.distance_matrix = distance_matrix

    def solve(
        self,
        algorithm: str = "cluster_first_route_second"
    ) -> TSPSolution:
        """
        Solve Multi-depot TSP

        Args:
            algorithm: Solution algorithm
                - "cluster_first_route_second": Cluster nodes to depots, then solve TSP
                - "savings": Clarke-Wright savings algorithm
                - "nearest_neighbor": Nearest neighbor from each depot

        Returns:
            TSPSolution with routes for each depot
        """
        if algorithm == "cluster_first_route_second":
            return self._cluster_first_route_second()
        elif algorithm == "savings":
            return self._savings_algorithm()
        else:
            return self._nearest_neighbor_multi_depot()

    def _cluster_first_route_second(self) -> TSPSolution:
        """
        Cluster-first, route-second heuristic

        1. Assign nodes to nearest depots (clustering)
        2. Solve TSP for each depot's cluster
        """
        # Step 1: Assign nodes to nearest depots
        depot_clusters: Dict[str, List[TSPNode]] = {d.id: [] for d in self.depots}

        for node in self.nodes:
            # Find nearest depot
            nearest_depot = min(
                self.depots,
                key=lambda d: self._get_distance(node.id, d.node.id)
            )
            depot_clusters[nearest_depot.id].append(node)

        # Step 2: Solve TSP for each cluster
        routes = []
        total_distance = 0.0
        total_cost = 0.0
        total_time = 0.0
        depot_assignment = {}

        for depot in self.depots:
            cluster_nodes = depot_clusters[depot.id]
            if not cluster_nodes:
                continue

            # Solve TSP for this cluster using nearest neighbor
            route = self._nearest_neighbor_tsp(depot.node, cluster_nodes)
            routes.append(route)

            # Calculate metrics
            route_distance = self._calculate_route_distance(route)
            total_distance += route_distance
            total_cost += route_distance  # Assuming cost = distance
            total_time += route_distance + sum(n.service_time for n in cluster_nodes)

            # Record depot assignment
            for node_id in route:
                depot_assignment[node_id] = depot.id

        return TSPSolution(
            routes=routes,
            total_distance=total_distance,
            total_cost=total_cost,
            total_time=total_time,
            depot_assignment=depot_assignment,
            metadata={"algorithm": "cluster_first_route_second"}
        )

    def _savings_algorithm(self) -> TSPSolution:
        """
        Clarke-Wright savings algorithm for Multi-depot TSP

        Iteratively merges routes based on savings from combining them
        """
        # Initialize: Each node is its own route from nearest depot
        routes: List[List[str]] = []
        depot_assignment = {}

        for node in self.nodes:
            nearest_depot = min(
                self.depots,
                key=lambda d: self._get_distance(node.id, d.node.id)
            )
            routes.append([nearest_depot.node.id, node.id, nearest_depot.node.id])
            depot_assignment[node.id] = nearest_depot.id

        # Calculate savings for all pairs
        savings: List[Tuple[float, int, int]] = []
        for i, route1 in enumerate(routes):
            for j, route2 in enumerate(routes[i+1:], i+1):
                # Savings from merging route1 and route2
                node1 = route1[-2]  # Last customer in route1
                node2 = route2[1]   # First customer in route2
                depot = route1[0]

                saving = (
                    self._get_distance(node1, depot) +
                    self._get_distance(depot, node2) -
                    self._get_distance(node1, node2)
                )
                savings.append((saving, i, j))

        # Sort by savings (descending)
        savings.sort(reverse=True)

        # Merge routes based on savings
        for saving, i, j in savings:
            if i >= len(routes) or j >= len(routes):
                continue

            # Check if routes can be merged (same depot, capacity constraints)
            if routes[i][0] == routes[j][0]:
                # Merge: remove depot from middle
                merged = routes[i][:-1] + routes[j][1:]
                routes[i] = merged
                routes.pop(j)

        # Calculate final metrics
        total_distance = sum(self._calculate_route_distance(r) for r in routes)

        return TSPSolution(
            routes=routes,
            total_distance=total_distance,
            total_cost=total_distance,
            total_time=total_distance,
            depot_assignment=depot_assignment,
            metadata={"algorithm": "savings"}
        )

    def _nearest_neighbor_multi_depot(self) -> TSPSolution:
        """
        Nearest neighbor heuristic starting from each depot
        """
        routes = []
        unvisited = set(n.id for n in self.nodes)
        depot_assignment = {}

        for depot in self.depots:
            if not unvisited:
                break

            route = [depot.node.id]
            current = depot.node.id

            # Assign nodes to this depot using nearest neighbor
            depot_capacity = depot.capacity

            while unvisited and depot_capacity > 0:
                # Find nearest unvisited node
                nearest = min(
                    unvisited,
                    key=lambda n: self._get_distance(current, n)
                )

                route.append(nearest)
                unvisited.remove(nearest)
                depot_assignment[nearest] = depot.id
                current = nearest
                depot_capacity -= 1

            route.append(depot.node.id)  # Return to depot
            routes.append(route)

        total_distance = sum(self._calculate_route_distance(r) for r in routes)

        return TSPSolution(
            routes=routes,
            total_distance=total_distance,
            total_cost=total_distance,
            total_time=total_distance,
            depot_assignment=depot_assignment,
            metadata={"algorithm": "nearest_neighbor_multi_depot"}
        )

    def _nearest_neighbor_tsp(
        self,
        start: TSPNode,
        nodes: List[TSPNode]
    ) -> List[str]:
        """Solve single TSP using nearest neighbor"""
        route = [start.id]
        unvisited = set(n.id for n in nodes)
        current = start.id

        while unvisited:
            nearest = min(unvisited, key=lambda n: self._get_distance(current, n))
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        route.append(start.id)  # Return to start
        return route

    def _get_distance(self, from_node: str, to_node: str) -> float:
        """Get distance between two nodes"""
        return self.distance_matrix.get((from_node, to_node), float('inf'))

    def _calculate_route_distance(self, route: List[str]) -> float:
        """Calculate total distance of a route"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += self._get_distance(route[i], route[i+1])
        return distance


# ============================================================================
# Dynamic TSP
# ============================================================================

class DynamicTSP:
    """
    Dynamic TSP solver

    Problem: TSP where nodes are added/removed during execution
    Goal: Adapt route dynamically as problem changes

    Use case: Real-time task allocation where new tasks arrive
    """

    def __init__(
        self,
        nodes: List[TSPNode],
        distance_matrix: Dict[Tuple[str, str], float],
        start_node: TSPNode
    ):
        self.nodes = {n.id: n for n in nodes}
        self.distance_matrix = distance_matrix
        self.start_node = start_node
        self.current_route: List[str] = []
        self.current_position: Optional[str] = None
        self.visited: Set[str] = set()

    def initialize_route(self) -> List[str]:
        """Initialize route using nearest neighbor"""
        self.current_route = self._nearest_neighbor()
        self.current_position = self.start_node.id
        return self.current_route

    def add_node(self, new_node: TSPNode) -> List[str]:
        """
        Add new node to route dynamically

        Strategy: Insert new node at position that minimizes distance increase
        """
        self.nodes[new_node.id] = new_node

        if not self.current_route:
            self.current_route = [self.start_node.id, new_node.id, self.start_node.id]
            return self.current_route

        # Find best insertion position
        best_position = 1
        best_increase = float('inf')

        for i in range(len(self.current_route) - 1):
            # Cost of inserting new_node between position i and i+1
            old_distance = self._get_distance(
                self.current_route[i],
                self.current_route[i+1]
            )
            new_distance = (
                self._get_distance(self.current_route[i], new_node.id) +
                self._get_distance(new_node.id, self.current_route[i+1])
            )
            increase = new_distance - old_distance

            if increase < best_increase:
                best_increase = increase
                best_position = i + 1

        # Insert at best position
        self.current_route.insert(best_position, new_node.id)
        return self.current_route

    def remove_node(self, node_id: str) -> List[str]:
        """Remove node from route"""
        if node_id in self.current_route:
            self.current_route.remove(node_id)
        if node_id in self.nodes:
            del self.nodes[node_id]
        return self.current_route

    def update_position(self, current_node_id: str) -> None:
        """Update current position in route"""
        self.current_position = current_node_id
        self.visited.add(current_node_id)

    def reoptimize_remaining(self) -> List[str]:
        """
        Reoptimize remaining route from current position

        Uses 2-opt on unvisited portion
        """
        if not self.current_position:
            return self.current_route

        # Find current position in route
        try:
            current_idx = self.current_route.index(self.current_position)
        except ValueError:
            return self.current_route

        # Get remaining route
        remaining = self.current_route[current_idx:]

        # Apply 2-opt to remaining
        optimized_remaining = self._two_opt(remaining)

        # Reconstruct full route
        self.current_route = self.current_route[:current_idx] + optimized_remaining
        return self.current_route

    def _nearest_neighbor(self) -> List[str]:
        """Initial route using nearest neighbor"""
        route = [self.start_node.id]
        unvisited = set(self.nodes.keys()) - {self.start_node.id}
        current = self.start_node.id

        while unvisited:
            nearest = min(unvisited, key=lambda n: self._get_distance(current, n))
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        route.append(self.start_node.id)
        return route

    def _two_opt(self, route: List[str]) -> List[str]:
        """Apply 2-opt local search"""
        improved = True
        best_route = route[:]

        while improved:
            improved = False
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route) - 1):
                    # Try reversing segment [i:j+1]
                    new_route = best_route[:i] + best_route[i:j+1][::-1] + best_route[j+1:]

                    if self._route_distance(new_route) < self._route_distance(best_route):
                        best_route = new_route
                        improved = True

        return best_route

    def _get_distance(self, from_node: str, to_node: str) -> float:
        """Get distance between nodes"""
        return self.distance_matrix.get((from_node, to_node), float('inf'))

    def _route_distance(self, route: List[str]) -> float:
        """Calculate total route distance"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += self._get_distance(route[i], route[i+1])
        return distance


# ============================================================================
# Stochastic TSP
# ============================================================================

class StochasticTSP:
    """
    Stochastic TSP solver

    Problem: TSP with probabilistic node presence
    Each node has probability of being present/requiring visit

    Goal: Find robust route that performs well across scenarios

    Use case: Planning under uncertainty (tasks may be cancelled, delays)
    """

    def __init__(
        self,
        nodes: List[TSPNode],
        presence_probabilities: Dict[str, float],
        distance_matrix: Dict[Tuple[str, str], float],
        start_node: TSPNode
    ):
        self.nodes = nodes
        self.presence_probs = presence_probabilities
        self.distance_matrix = distance_matrix
        self.start_node = start_node

    def solve_expected_value(self) -> TSPSolution:
        """
        Solve using expected value approach

        Minimize expected distance across all scenarios
        """
        # Build expected distance matrix
        expected_distances = {}
        for (i, j), dist in self.distance_matrix.items():
            # Expected distance accounts for probability of visiting both nodes
            prob_i = self.presence_probs.get(i, 1.0)
            prob_j = self.presence_probs.get(j, 1.0)
            expected_distances[(i, j)] = dist * prob_i * prob_j

        # Solve TSP with expected distances using nearest neighbor
        route = self._nearest_neighbor_stochastic(expected_distances)

        # Calculate expected metrics
        total_expected_distance = self._calculate_expected_distance(route)

        return TSPSolution(
            routes=[route],
            total_distance=total_expected_distance,
            total_cost=total_expected_distance,
            total_time=total_expected_distance,
            metadata={
                "algorithm": "stochastic_expected_value",
                "presence_probabilities": self.presence_probs
            }
        )

    def solve_robust(self, risk_factor: float = 0.2) -> TSPSolution:
        """
        Solve using robust optimization

        Minimize worst-case distance (with risk_factor percentile)

        Args:
            risk_factor: Percentile for worst-case (0.2 = 80th percentile)
        """
        # Generate scenarios
        scenarios = self._generate_scenarios(num_scenarios=100)

        # For each possible route, evaluate across scenarios
        # Use nearest neighbor as base route
        base_route = self._nearest_neighbor_stochastic(self.distance_matrix)

        # Evaluate this route across scenarios
        scenario_distances = []
        for scenario in scenarios:
            # Filter route to nodes present in scenario
            scenario_route = [n for n in base_route if n in scenario or n == self.start_node.id]
            distance = self._route_distance(scenario_route)
            scenario_distances.append(distance)

        # Calculate robust metrics
        scenario_distances.sort()
        risk_idx = int(len(scenario_distances) * (1 - risk_factor))
        robust_distance = scenario_distances[risk_idx]

        return TSPSolution(
            routes=[base_route],
            total_distance=robust_distance,
            total_cost=robust_distance,
            total_time=robust_distance,
            metadata={
                "algorithm": "stochastic_robust",
                "risk_factor": risk_factor,
                "worst_case_distance": max(scenario_distances),
                "best_case_distance": min(scenario_distances)
            }
        )

    def _nearest_neighbor_stochastic(
        self,
        distance_matrix: Dict[Tuple[str, str], float]
    ) -> List[str]:
        """Nearest neighbor with stochastic distances"""
        route = [self.start_node.id]
        unvisited = set(n.id for n in self.nodes)
        current = self.start_node.id

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda n: distance_matrix.get((current, n), float('inf'))
            )
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        route.append(self.start_node.id)
        return route

    def _generate_scenarios(self, num_scenarios: int) -> List[Set[str]]:
        """Generate scenarios based on presence probabilities"""
        scenarios = []
        for _ in range(num_scenarios):
            scenario = set()
            for node in self.nodes:
                if random.random() < self.presence_probs.get(node.id, 1.0):
                    scenario.add(node.id)
            scenarios.append(scenario)
        return scenarios

    def _calculate_expected_distance(self, route: List[str]) -> float:
        """Calculate expected distance for a route"""
        expected = 0.0
        for i in range(len(route) - 1):
            dist = self.distance_matrix.get((route[i], route[i+1]), 0.0)
            prob_i = self.presence_probs.get(route[i], 1.0)
            prob_j = self.presence_probs.get(route[i+1], 1.0)
            expected += dist * prob_i * prob_j
        return expected

    def _route_distance(self, route: List[str]) -> float:
        """Calculate total route distance"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += self.distance_matrix.get((route[i], route[i+1]), 0.0)
        return distance


# ============================================================================
# Optimization Algorithms
# ============================================================================

class TwoOptOptimizer:
    """
    2-opt local search algorithm

    Iteratively improves tour by removing crossing edges
    """

    @staticmethod
    def optimize(
        route: List[str],
        distance_matrix: Dict[Tuple[str, str], float],
        max_iterations: int = 1000
    ) -> Tuple[List[str], float]:
        """
        Apply 2-opt optimization to route

        Returns: (optimized_route, distance)
        """
        best_route = route[:]
        best_distance = TwoOptOptimizer._calculate_distance(best_route, distance_matrix)
        improved = True
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route) - 1):
                    # Try reversing segment [i:j+1]
                    new_route = best_route[:i] + best_route[i:j+1][::-1] + best_route[j+1:]
                    new_distance = TwoOptOptimizer._calculate_distance(new_route, distance_matrix)

                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        break

                if improved:
                    break

        return best_route, best_distance

    @staticmethod
    def _calculate_distance(route: List[str], distance_matrix: Dict[Tuple[str, str], float]) -> float:
        """Calculate total route distance"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += distance_matrix.get((route[i], route[i+1]), float('inf'))
        return distance


class SimulatedAnnealingTSP:
    """
    Simulated Annealing for TSP

    Probabilistic optimization that accepts worse solutions early to escape local optima
    """

    def __init__(
        self,
        nodes: List[TSPNode],
        distance_matrix: Dict[Tuple[str, str], float],
        initial_temp: float = 1000.0,
        cooling_rate: float = 0.995,
        min_temp: float = 1.0
    ):
        self.nodes = nodes
        self.distance_matrix = distance_matrix
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp

    def optimize(self, initial_route: Optional[List[str]] = None) -> TSPSolution:
        """
        Optimize using simulated annealing

        Returns: Best solution found
        """
        # Initialize
        if initial_route is None:
            current_route = [n.id for n in self.nodes]
            random.shuffle(current_route)
            if self.nodes:
                current_route.append(current_route[0])  # Close the tour
        else:
            current_route = initial_route[:]

        current_distance = self._calculate_distance(current_route)
        best_route = current_route[:]
        best_distance = current_distance

        temperature = self.initial_temp

        # Annealing loop
        while temperature > self.min_temp:
            # Generate neighbor solution (2-opt move)
            new_route = self._generate_neighbor(current_route)
            new_distance = self._calculate_distance(new_route)

            # Calculate acceptance probability
            delta = new_distance - current_distance

            if delta < 0:
                # Always accept better solution
                current_route = new_route
                current_distance = new_distance

                if current_distance < best_distance:
                    best_route = current_route[:]
                    best_distance = current_distance
            else:
                # Accept worse solution with probability
                acceptance_prob = math.exp(-delta / temperature)
                if random.random() < acceptance_prob:
                    current_route = new_route
                    current_distance = new_distance

            # Cool down
            temperature *= self.cooling_rate

        return TSPSolution(
            routes=[best_route],
            total_distance=best_distance,
            total_cost=best_distance,
            total_time=best_distance,
            metadata={
                "algorithm": "simulated_annealing",
                "initial_temp": self.initial_temp,
                "final_temp": temperature
            }
        )

    def _generate_neighbor(self, route: List[str]) -> List[str]:
        """Generate neighbor solution using 2-opt move"""
        new_route = route[:]
        i = random.randint(1, len(route) - 3)
        j = random.randint(i + 1, len(route) - 2)
        new_route[i:j+1] = reversed(new_route[i:j+1])
        return new_route

    def _calculate_distance(self, route: List[str]) -> float:
        """Calculate total route distance"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += self.distance_matrix.get((route[i], route[i+1]), float('inf'))
        return distance


class AntColonyTSP:
    """
    Ant Colony Optimization for TSP

    Bio-inspired algorithm where ants deposit pheromones on good paths
    """

    def __init__(
        self,
        nodes: List[TSPNode],
        distance_matrix: Dict[Tuple[str, str], float],
        num_ants: int = 10,
        num_iterations: int = 100,
        alpha: float = 1.0,  # Pheromone importance
        beta: float = 2.0,   # Distance importance
        evaporation: float = 0.5,
        pheromone_deposit: float = 1.0
    ):
        self.nodes = nodes
        self.distance_matrix = distance_matrix
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.pheromone_deposit = pheromone_deposit

        # Initialize pheromone matrix
        self.pheromones: Dict[Tuple[str, str], float] = {}
        for (i, j) in distance_matrix.keys():
            self.pheromones[(i, j)] = 1.0

    def optimize(self) -> TSPSolution:
        """
        Optimize using ant colony optimization

        Returns: Best solution found
        """
        best_route = None
        best_distance = float('inf')

        for iteration in range(self.num_iterations):
            # Each ant constructs a solution
            routes = []
            distances = []

            for ant in range(self.num_ants):
                route = self._construct_solution()
                distance = self._calculate_distance(route)
                routes.append(route)
                distances.append(distance)

                if distance < best_distance:
                    best_route = route
                    best_distance = distance

            # Update pheromones
            self._update_pheromones(routes, distances)

        return TSPSolution(
            routes=[best_route],
            total_distance=best_distance,
            total_cost=best_distance,
            total_time=best_distance,
            metadata={
                "algorithm": "ant_colony",
                "num_ants": self.num_ants,
                "iterations": self.num_iterations
            }
        )

    def _construct_solution(self) -> List[str]:
        """Construct solution for one ant"""
        if not self.nodes:
            return []

        route = [self.nodes[0].id]
        unvisited = set(n.id for n in self.nodes[1:])

        while unvisited:
            current = route[-1]

            # Calculate probabilities for next node
            probabilities = {}
            total_prob = 0.0

            for next_node in unvisited:
                pheromone = self.pheromones.get((current, next_node), 1.0)
                distance = self.distance_matrix.get((current, next_node), float('inf'))

                if distance == 0:
                    distance = 0.001  # Avoid division by zero

                # Probability = (pheromone^alpha) * (1/distance^beta)
                prob = (pheromone ** self.alpha) * ((1.0 / distance) ** self.beta)
                probabilities[next_node] = prob
                total_prob += prob

            # Normalize probabilities
            if total_prob > 0:
                probabilities = {k: v/total_prob for k, v in probabilities.items()}
            else:
                # Uniform distribution if all probabilities are 0
                probabilities = {k: 1.0/len(unvisited) for k in unvisited}

            # Select next node using roulette wheel selection
            rand = random.random()
            cumulative = 0.0
            next_node = None

            for node, prob in probabilities.items():
                cumulative += prob
                if rand <= cumulative:
                    next_node = node
                    break

            if next_node is None:
                next_node = random.choice(list(unvisited))

            route.append(next_node)
            unvisited.remove(next_node)

        # Close the tour
        route.append(route[0])
        return route

    def _update_pheromones(
        self,
        routes: List[List[str]],
        distances: List[float]
    ) -> None:
        """Update pheromone levels"""
        # Evaporation
        for key in self.pheromones:
            self.pheromones[key] *= (1 - self.evaporation)

        # Deposit new pheromones
        for route, distance in zip(routes, distances):
            if distance == 0:
                continue

            deposit = self.pheromone_deposit / distance

            for i in range(len(route) - 1):
                edge = (route[i], route[i+1])
                if edge in self.pheromones:
                    self.pheromones[edge] += deposit

    def _calculate_distance(self, route: List[str]) -> float:
        """Calculate total route distance"""
        distance = 0.0
        for i in range(len(route) - 1):
            distance += self.distance_matrix.get((route[i], route[i+1]), float('inf'))
        return distance
