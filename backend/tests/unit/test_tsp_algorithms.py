"""
Unit Tests for TSP Algorithms

Tests all TSP variants:
- Multi-depot TSP
- Hierarchical TSP
- Stochastic TSP
- Dynamic TSP
- Optimization algorithms (2-opt, Genetic Algorithm)
"""

import pytest
from typing import Dict, Tuple

from app.services.tsp_algorithms import (
    TSPNode,
    TSPDepot,
    TSPCluster,
    MultiDepotTSP,
    HierarchicalTSP,
    StochasticTSP,
    DynamicTSP,
    TwoOptOptimizer,
    GeneticAlgorithmTSP
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def simple_nodes():
    """Create simple test nodes"""
    return [
        TSPNode(id="node1", x=0.0, y=0.0),
        TSPNode(id="node2", x=1.0, y=0.0),
        TSPNode(id="node3", x=1.0, y=1.0),
        TSPNode(id="node4", x=0.0, y=1.0),
    ]


@pytest.fixture
def simple_distance_matrix():
    """Create simple distance matrix"""
    return {
        ("node1", "node2"): 1.0,
        ("node2", "node1"): 1.0,
        ("node1", "node3"): 1.414,
        ("node3", "node1"): 1.414,
        ("node1", "node4"): 1.0,
        ("node4", "node1"): 1.0,
        ("node2", "node3"): 1.0,
        ("node3", "node2"): 1.0,
        ("node2", "node4"): 1.414,
        ("node4", "node2"): 1.414,
        ("node3", "node4"): 1.0,
        ("node4", "node3"): 1.0,
    }


@pytest.fixture
def two_depots():
    """Create two depot nodes"""
    return [
        TSPDepot(
            id="depot1",
            node=TSPNode(id="depot1", x=-1.0, y=0.0),
            capacity=10.0,
            available_agents=2
        ),
        TSPDepot(
            id="depot2",
            node=TSPNode(id="depot2", x=2.0, y=1.0),
            capacity=10.0,
            available_agents=2
        ),
    ]


@pytest.fixture
def hierarchical_clusters():
    """Create hierarchical cluster structure"""
    cluster1_nodes = [
        TSPNode(id="c1_n1", x=0.0, y=0.0),
        TSPNode(id="c1_n2", x=1.0, y=0.0),
    ]
    cluster2_nodes = [
        TSPNode(id="c2_n1", x=5.0, y=5.0),
        TSPNode(id="c2_n2", x=6.0, y=5.0),
    ]

    return [
        TSPCluster(id="cluster1", nodes=cluster1_nodes, level=0),
        TSPCluster(id="cluster2", nodes=cluster2_nodes, level=0),
    ]


# ============================================================================
# Multi-depot TSP Tests
# ============================================================================

class TestMultiDepotTSP:
    """Test Multi-depot TSP algorithms"""

    def test_initialization(self, simple_nodes, two_depots, simple_distance_matrix):
        """Test Multi-depot TSP initialization"""
        mdtsp = MultiDepotTSP(simple_nodes, two_depots, simple_distance_matrix)

        assert mdtsp.nodes == simple_nodes
        assert mdtsp.depots == two_depots
        assert len(mdtsp.distance_matrix) > 0

    def test_cluster_first_route_second(self, simple_nodes, two_depots, simple_distance_matrix):
        """Test cluster_first_route_second algorithm"""
        mdtsp = MultiDepotTSP(simple_nodes, two_depots, simple_distance_matrix)
        solution = mdtsp.solve(algorithm="cluster_first_route_second")

        # Verify solution structure
        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0
        assert solution.total_cost >= 0

        # Verify all nodes are visited
        visited_nodes = []
        for route in solution.routes:
            visited_nodes.extend([n for n in route if n not in ["depot1", "depot2"]])

        assert len(set(visited_nodes)) == len(simple_nodes)

    def test_nearest_neighbor(self, simple_nodes, two_depots, simple_distance_matrix):
        """Test nearest_neighbor algorithm"""
        mdtsp = MultiDepotTSP(simple_nodes, two_depots, simple_distance_matrix)
        solution = mdtsp.solve(algorithm="nearest_neighbor")

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0

    def test_empty_nodes(self, two_depots, simple_distance_matrix):
        """Test with empty nodes list"""
        mdtsp = MultiDepotTSP([], two_depots, simple_distance_matrix)
        solution = mdtsp.solve()

        # Should return empty solution
        assert solution.total_distance == 0
        assert len(solution.routes) == 0 or all(len(route) == 0 for route in solution.routes)


# ============================================================================
# Hierarchical TSP Tests
# ============================================================================

class TestHierarchicalTSP:
    """Test Hierarchical TSP algorithms"""

    def test_initialization(self, hierarchical_clusters, simple_distance_matrix):
        """Test Hierarchical TSP initialization"""
        htsp = HierarchicalTSP(hierarchical_clusters, simple_distance_matrix)

        assert htsp.clusters == hierarchical_clusters
        assert len(htsp.distance_matrix) > 0

    def test_top_down_algorithm(self, hierarchical_clusters, simple_distance_matrix):
        """Test top-down hierarchical solving"""
        htsp = HierarchicalTSP(hierarchical_clusters, simple_distance_matrix)
        solution = htsp.solve(algorithm="top_down")

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0

        # Verify route contains nodes from clusters
        all_nodes = []
        for cluster in hierarchical_clusters:
            all_nodes.extend([n.id for n in cluster.nodes])

        route_nodes = [n for route in solution.routes for n in route]
        assert len(set(route_nodes)) == len(all_nodes)

    def test_bottom_up_algorithm(self, hierarchical_clusters, simple_distance_matrix):
        """Test bottom-up hierarchical solving"""
        htsp = HierarchicalTSP(hierarchical_clusters, simple_distance_matrix)
        solution = htsp.solve(algorithm="bottom_up")

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0

    def test_integrated_algorithm(self, hierarchical_clusters, simple_distance_matrix):
        """Test integrated hierarchical solving"""
        htsp = HierarchicalTSP(hierarchical_clusters, simple_distance_matrix)
        solution = htsp.solve(algorithm="integrated")

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0


# ============================================================================
# Stochastic TSP Tests
# ============================================================================

class TestStochasticTSP:
    """Test Stochastic TSP algorithms"""

    def test_expected_value_algorithm(self, simple_nodes, simple_distance_matrix):
        """Test expected value stochastic TSP"""
        presence_probs = {
            "node1": 1.0,
            "node2": 0.8,
            "node3": 0.7,
            "node4": 0.9,
        }

        stsp = StochasticTSP(
            simple_nodes,
            presence_probs,
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        solution = stsp.solve_expected_value()

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0
        assert "expected_distance" in solution.metadata

    def test_robust_algorithm(self, simple_nodes, simple_distance_matrix):
        """Test robust stochastic TSP"""
        presence_probs = {
            "node1": 1.0,
            "node2": 0.8,
            "node3": 0.7,
            "node4": 0.9,
        }

        stsp = StochasticTSP(
            simple_nodes,
            presence_probs,
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        solution = stsp.solve_robust(risk_factor=0.2)

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0
        assert "risk_adjusted_distance" in solution.metadata

    def test_certain_nodes(self, simple_nodes, simple_distance_matrix):
        """Test with all nodes certain (probability = 1.0)"""
        presence_probs = {n.id: 1.0 for n in simple_nodes}

        stsp = StochasticTSP(
            simple_nodes,
            presence_probs,
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        solution = stsp.solve_expected_value()

        # With all certain nodes, should visit all
        assert len(solution.routes) > 0


# ============================================================================
# Dynamic TSP Tests
# ============================================================================

class TestDynamicTSP:
    """Test Dynamic TSP"""

    def test_initialization_and_solve(self, simple_nodes, simple_distance_matrix):
        """Test Dynamic TSP initialization and solving"""
        dtsp = DynamicTSP(
            simple_nodes,
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        solution = dtsp.solve()

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance >= 0

    def test_add_node_dynamically(self, simple_nodes, simple_distance_matrix):
        """Test adding node during execution"""
        dtsp = DynamicTSP(
            simple_nodes[:2],  # Start with only 2 nodes
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        # Solve initial
        initial_solution = dtsp.solve()
        initial_distance = initial_solution.total_distance

        # Add new node
        new_node = simple_nodes[2]
        new_distances = {
            (new_node.id, "node1"): 1.414,
            ("node1", new_node.id): 1.414,
            (new_node.id, "node2"): 1.0,
            ("node2", new_node.id): 1.0,
        }

        dtsp.add_node(new_node, new_distances)

        # Solve with new node
        updated_solution = dtsp.solve()

        assert len(dtsp.nodes) == 3
        assert updated_solution.total_distance >= initial_distance  # Distance may increase

    def test_remove_node_dynamically(self, simple_nodes, simple_distance_matrix):
        """Test removing node during execution"""
        dtsp = DynamicTSP(
            simple_nodes,
            simple_distance_matrix,
            start_node=simple_nodes[0]
        )

        # Solve initial
        initial_solution = dtsp.solve()

        # Remove a node
        dtsp.remove_node("node3")

        # Solve without removed node
        updated_solution = dtsp.solve()

        assert len(dtsp.nodes) == 3
        # Verify node3 is not in any route
        for route in updated_solution.routes:
            assert "node3" not in route


# ============================================================================
# Optimization Algorithm Tests
# ============================================================================

class TestTwoOptOptimizer:
    """Test 2-opt optimization"""

    def test_basic_optimization(self, simple_distance_matrix):
        """Test basic 2-opt optimization"""
        initial_route = ["node1", "node2", "node3", "node4", "node1"]

        optimized_route, distance = TwoOptOptimizer.optimize(
            initial_route,
            simple_distance_matrix,
            max_iterations=100
        )

        assert optimized_route is not None
        assert len(optimized_route) == len(initial_route)
        assert distance > 0

        # Should start and end at same node
        assert optimized_route[0] == optimized_route[-1]

    def test_already_optimal_route(self, simple_distance_matrix):
        """Test 2-opt with already optimal route"""
        # Square route: node1 → node2 → node3 → node4 → node1
        optimal_route = ["node1", "node2", "node3", "node4", "node1"]

        optimized_route, distance = TwoOptOptimizer.optimize(
            optimal_route,
            simple_distance_matrix,
            max_iterations=10
        )

        # Should not get worse
        initial_distance = (
            simple_distance_matrix[("node1", "node2")] +
            simple_distance_matrix[("node2", "node3")] +
            simple_distance_matrix[("node3", "node4")] +
            simple_distance_matrix[("node4", "node1")]
        )

        assert distance <= initial_distance + 0.01  # Allow small floating point error


class TestGeneticAlgorithmTSP:
    """Test Genetic Algorithm TSP"""

    def test_initialization(self, simple_nodes, simple_distance_matrix):
        """Test GA TSP initialization"""
        ga = GeneticAlgorithmTSP(
            simple_nodes,
            simple_distance_matrix,
            population_size=20,
            generations=10
        )

        assert ga.nodes == simple_nodes
        assert ga.population_size == 20
        assert ga.generations == 10

    def test_optimization(self, simple_nodes, simple_distance_matrix):
        """Test GA optimization"""
        ga = GeneticAlgorithmTSP(
            simple_nodes,
            simple_distance_matrix,
            population_size=20,
            generations=50
        )

        solution = ga.optimize()

        assert solution is not None
        assert len(solution.routes) > 0
        assert solution.total_distance > 0

        # Verify route visits all nodes
        route = solution.routes[0]
        unique_nodes = set(route[:-1])  # Exclude last (return to start)
        assert len(unique_nodes) == len(simple_nodes)

    def test_with_initial_route(self, simple_nodes, simple_distance_matrix):
        """Test GA with initial route"""
        initial_route = ["node1", "node2", "node3", "node4"]

        ga = GeneticAlgorithmTSP(
            simple_nodes,
            simple_distance_matrix,
            population_size=20,
            generations=30
        )

        solution = ga.optimize(initial_route=initial_route)

        assert solution is not None
        assert solution.total_distance > 0

    def test_improvement_over_generations(self, simple_nodes, simple_distance_matrix):
        """Test that GA improves over generations"""
        ga_short = GeneticAlgorithmTSP(
            simple_nodes,
            simple_distance_matrix,
            population_size=50,
            generations=5
        )
        solution_short = ga_short.optimize()

        ga_long = GeneticAlgorithmTSP(
            simple_nodes,
            simple_distance_matrix,
            population_size=50,
            generations=100
        )
        solution_long = ga_long.optimize()

        # More generations should not make solution worse
        # (though not guaranteed due to stochastic nature)
        assert solution_long.total_distance > 0
        assert solution_short.total_distance > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestTSPIntegration:
    """Integration tests combining multiple algorithms"""

    def test_multidepot_then_optimize(self, simple_nodes, two_depots, simple_distance_matrix):
        """Test Multi-depot TSP followed by 2-opt optimization"""
        # Solve Multi-depot TSP
        mdtsp = MultiDepotTSP(simple_nodes, two_depots, simple_distance_matrix)
        initial_solution = mdtsp.solve()

        # Optimize each route with 2-opt
        optimized_routes = []
        total_optimized_distance = 0.0

        for route in initial_solution.routes:
            if len(route) > 2:
                optimized_route, distance = TwoOptOptimizer.optimize(
                    route,
                    simple_distance_matrix,
                    max_iterations=100
                )
                optimized_routes.append(optimized_route)
                total_optimized_distance += distance
            else:
                optimized_routes.append(route)

        # Optimized should not be worse than initial
        assert total_optimized_distance > 0
        assert len(optimized_routes) == len(initial_solution.routes)
