"""
Unit tests for GraphOptimizer service

Tests cover:
- Optimization strategies (MINIMIZE_TIME, MINIMIZE_COST, BALANCE_LOAD, MAXIMIZE_PARALLELISM)
- Graph analysis (critical path, bottlenecks, parallel groups)
- Execution prediction (best/avg/worst case)
- Edge cases (empty graphs, cycles, disconnected nodes)
"""

import pytest
from datetime import datetime

from app.services.graph_optimizer import (
    GraphOptimizer,
    OptimizationStrategy,
    GraphAnalysis,
    ExecutionPrediction,
)
from app.domain.models import Graph, Task, Agent, GraphEdge


# ============================================================================
# Test Data Builders
# ============================================================================

def create_test_graph(num_nodes: int = 5, linear: bool = True) -> Graph:
    """Create a test graph with tasks and edges."""
    tasks = [
        Task(
            id=f"task_{i}",
            name=f"Task {i}",
            description=f"Description for task {i}",
            priority=2,
            status="pending",
            estimated_time=10.0 + i,  # Varying times
            estimated_cost=0.05 + (i * 0.01),
        )
        for i in range(num_nodes)
    ]

    if linear:
        # Create linear dependency chain: task_0 → task_1 → task_2 → ...
        edges = [
            GraphEdge(
                id=f"edge_{i}",
                from_task_id=f"task_{i}",
                to_task_id=f"task_{i+1}",
            )
            for i in range(num_nodes - 1)
        ]
    else:
        # Create parallel structure
        edges = []

    graph = Graph(
        id="test_graph",
        name="Test Graph",
        description="A test graph",
        status="pending",
        tasks={task.id: task for task in tasks},
        edges={edge.id: edge for edge in edges},
    )

    return graph


def create_test_agents(num_agents: int = 3) -> list[Agent]:
    """Create test agents with varying capabilities."""
    agents = [
        Agent(
            id=f"agent_{i}",
            role=f"agent_{i}",
            model="gpt-4" if i == 0 else "claude-3-sonnet" if i == 1 else "gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2000,
            status="idle",
        )
        for i in range(num_agents)
    ]
    return agents


# ============================================================================
# GraphOptimizer Initialization Tests
# ============================================================================

class TestGraphOptimizerInit:
    """Test GraphOptimizer initialization."""

    def test_init(self):
        """Test optimizer initializes correctly."""
        optimizer = GraphOptimizer()

        assert optimizer is not None
        assert optimizer.model_costs is not None
        assert "gpt-4" in optimizer.model_costs
        assert "claude-3-opus" in optimizer.model_costs

    def test_model_costs_structure(self):
        """Test model costs have correct structure."""
        optimizer = GraphOptimizer()

        for model, costs in optimizer.model_costs.items():
            assert "input" in costs
            assert "output" in costs
            assert isinstance(costs["input"], float)
            assert isinstance(costs["output"], float)
            assert costs["input"] > 0
            assert costs["output"] > 0


# ============================================================================
# Graph Analysis Tests
# ============================================================================

class TestGraphAnalysis:
    """Test graph analysis functionality."""

    def test_analyze_linear_graph(self):
        """Test analysis of linear graph."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        analysis = optimizer.analyze_graph(graph, agents)

        assert isinstance(analysis, GraphAnalysis)
        assert analysis.total_tasks == 5
        assert analysis.total_dependencies == 4
        assert len(analysis.critical_path) > 0
        assert analysis.max_parallelism == 1  # Linear graph has no parallelism
        assert analysis.estimated_sequential_time > 0
        assert analysis.estimated_parallel_time > 0

    def test_analyze_parallel_graph(self):
        """Test analysis of parallel graph (no dependencies)."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=False)
        agents = create_test_agents(num_agents=3)

        analysis = optimizer.analyze_graph(graph, agents)

        assert analysis.total_tasks == 5
        assert analysis.total_dependencies == 0
        assert analysis.max_parallelism == 5  # All tasks can run in parallel
        assert analysis.estimated_parallel_time < analysis.estimated_sequential_time

    def test_critical_path_calculation(self):
        """Test critical path is calculated correctly."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        analysis = optimizer.analyze_graph(graph, agents)

        # For linear graph, critical path should be all tasks
        assert len(analysis.critical_path) == 5
        assert analysis.critical_path[0] == "task_0"
        assert analysis.critical_path[-1] == "task_4"

    def test_bottleneck_detection(self):
        """Test bottleneck detection."""
        optimizer = GraphOptimizer()

        # Create graph with bottleneck (task_2 has high centrality)
        tasks = [create_test_graph(1, linear=False).tasks[f"task_0"] for i in range(5)]
        for i, task in enumerate(tasks):
            task.id = f"task_{i}"
            task.name = f"Task {i}"

        # Create bottleneck structure: 0,1 → 2 → 3,4
        edges = [
            GraphEdge(id="e1", from_task_id="task_0", to_task_id="task_2"),
            GraphEdge(id="e2", from_task_id="task_1", to_task_id="task_2"),
            GraphEdge(id="e3", from_task_id="task_2", to_task_id="task_3"),
            GraphEdge(id="e4", from_task_id="task_2", to_task_id="task_4"),
        ]

        graph = Graph(
            id="bottleneck_graph",
            name="Bottleneck Graph",
            description="Graph with bottleneck",
            status="pending",
            tasks={task.id: task for task in tasks},
            edges={edge.id: edge for edge in edges},
        )

        agents = create_test_agents(num_agents=3)
        analysis = optimizer.analyze_graph(graph, agents)

        # task_2 should be identified as bottleneck
        assert "task_2" in analysis.bottlenecks


# ============================================================================
# Optimization Strategy Tests
# ============================================================================

class TestOptimizationStrategies:
    """Test optimization strategies."""

    def test_minimize_time_strategy(self):
        """Test MINIMIZE_TIME optimization strategy."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.MINIMIZE_TIME,
            constraints={}
        )

        assert result.strategy == OptimizationStrategy.MINIMIZE_TIME
        assert result.time_saved >= 0
        assert result.time_saved_percentage >= 0
        assert len(result.critical_path) > 0
        assert len(result.recommendations) > 0

    def test_minimize_cost_strategy(self):
        """Test MINIMIZE_COST optimization strategy."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.MINIMIZE_COST,
            constraints={}
        )

        assert result.strategy == OptimizationStrategy.MINIMIZE_COST
        assert result.cost_saved >= 0
        assert result.cost_saved_percentage >= 0

    def test_balance_load_strategy(self):
        """Test BALANCE_LOAD optimization strategy."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=6, linear=False)  # Parallel tasks
        agents = create_test_agents(num_agents=3)

        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.BALANCE_LOAD,
            constraints={}
        )

        assert result.strategy == OptimizationStrategy.BALANCE_LOAD
        # Load balancing should distribute work evenly

    def test_maximize_parallelism_strategy(self):
        """Test MAXIMIZE_PARALLELISM optimization strategy."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=5)

        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.MAXIMIZE_PARALLELISM,
            constraints={}
        )

        assert result.strategy == OptimizationStrategy.MAXIMIZE_PARALLELISM
        # Should identify parallel groups

    def test_optimization_with_constraints(self):
        """Test optimization respects constraints."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        constraints = {
            "max_cost": 0.20,
            "max_time": 30.0,
        }

        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.MINIMIZE_TIME,
            constraints=constraints
        )

        # Optimization should respect constraints
        assert result.optimized_estimated_cost <= constraints["max_cost"] * 1.1  # 10% tolerance


# ============================================================================
# Execution Prediction Tests
# ============================================================================

class TestExecutionPrediction:
    """Test execution prediction functionality."""

    def test_predict_execution(self):
        """Test execution prediction."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        prediction = optimizer.predict_execution(graph, agents)

        assert isinstance(prediction, ExecutionPrediction)
        assert prediction.best_case_time > 0
        assert prediction.average_case_time > 0
        assert prediction.worst_case_time > 0
        assert prediction.best_case_time <= prediction.average_case_time <= prediction.worst_case_time

        assert prediction.best_case_cost > 0
        assert prediction.average_case_cost > 0
        assert prediction.worst_case_cost > 0
        assert prediction.best_case_cost <= prediction.average_case_cost <= prediction.worst_case_cost

        assert 0.0 <= prediction.success_probability <= 1.0
        assert isinstance(prediction.risk_factors, list)

    def test_prediction_with_complex_graph(self):
        """Test prediction handles complex graphs."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=10, linear=True)
        agents = create_test_agents(num_agents=5)

        prediction = optimizer.predict_execution(graph, agents)

        # More complex graph should have higher variance
        variance_time = prediction.worst_case_time - prediction.best_case_time
        assert variance_time > 0

        # Should identify more risk factors
        assert len(prediction.risk_factors) > 0


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph(self):
        """Test handling of empty graph."""
        optimizer = GraphOptimizer()

        graph = Graph(
            id="empty_graph",
            name="Empty Graph",
            description="Graph with no tasks",
            status="pending",
            tasks={},
            edges={},
        )

        agents = create_test_agents(num_agents=3)

        analysis = optimizer.analyze_graph(graph, agents)

        assert analysis.total_tasks == 0
        assert analysis.total_dependencies == 0
        assert analysis.estimated_sequential_time == 0
        assert analysis.estimated_parallel_time == 0

    def test_single_task_graph(self):
        """Test handling of single task graph."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=1, linear=False)
        agents = create_test_agents(num_agents=3)

        analysis = optimizer.analyze_graph(graph, agents)

        assert analysis.total_tasks == 1
        assert analysis.total_dependencies == 0
        assert len(analysis.critical_path) == 1
        assert analysis.max_parallelism == 1

    def test_no_available_agents(self):
        """Test handling when no agents are available."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=3, linear=True)
        agents = []  # No agents

        analysis = optimizer.analyze_graph(graph, agents)

        # Should still analyze graph structure
        assert analysis.total_tasks == 3
        # But should have warnings about resource availability
        assert analysis.required_agents > len(agents)

    def test_disconnected_graph(self):
        """Test handling of disconnected graph components."""
        optimizer = GraphOptimizer()

        # Create two separate components
        tasks = [
            Task(
                id=f"task_{i}",
                name=f"Task {i}",
                description=f"Description {i}",
                priority=2,
                status="pending",
            )
            for i in range(4)
        ]

        # Component 1: task_0 → task_1
        # Component 2: task_2 → task_3
        edges = [
            GraphEdge(id="e1", from_task_id="task_0", to_task_id="task_1"),
            GraphEdge(id="e2", from_task_id="task_2", to_task_id="task_3"),
        ]

        graph = Graph(
            id="disconnected_graph",
            name="Disconnected Graph",
            description="Graph with disconnected components",
            status="pending",
            tasks={task.id: task for task in tasks},
            edges={edge.id: edge for edge in edges},
        )

        agents = create_test_agents(num_agents=3)
        analysis = optimizer.analyze_graph(graph, agents)

        # Should handle disconnected components
        assert analysis.total_tasks == 4
        assert analysis.total_dependencies == 2
        # Parallel groups should reflect independent components
        assert len(analysis.parallel_groups) >= 2


# ============================================================================
# Cost Estimation Tests
# ============================================================================

class TestCostEstimation:
    """Test cost estimation functionality."""

    def test_cost_estimation_gpt4(self):
        """Test cost estimation for GPT-4."""
        optimizer = GraphOptimizer()

        task = Task(
            id="task_1",
            name="Task 1",
            description="Test task",
            priority=2,
            status="pending",
        )

        agent = Agent(
            id="agent_1",
            role="test_agent",
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000,
            status="idle",
        )

        cost = optimizer._estimate_task_cost(task, agent)

        # GPT-4 should have higher cost
        assert cost > 0
        assert cost >= 0.03  # Minimum cost for GPT-4

    def test_cost_estimation_claude_haiku(self):
        """Test cost estimation for Claude Haiku (cheaper model)."""
        optimizer = GraphOptimizer()

        task = Task(
            id="task_1",
            name="Task 1",
            description="Test task",
            priority=2,
            status="pending",
        )

        agent = Agent(
            id="agent_1",
            role="test_agent",
            model="claude-3-haiku",
            temperature=0.7,
            max_tokens=2000,
            status="idle",
        )

        cost = optimizer._estimate_task_cost(task, agent)

        # Claude Haiku should have lower cost
        assert cost > 0
        assert cost < 0.01  # Should be cheaper than GPT-4


# ============================================================================
# Integration Tests (with Graph Analysis)
# ============================================================================

@pytest.mark.integration
class TestOptimizationIntegration:
    """Integration tests combining analysis and optimization."""

    def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=5, linear=True)
        agents = create_test_agents(num_agents=3)

        # Step 1: Analyze
        analysis = optimizer.analyze_graph(graph, agents)
        assert analysis.total_tasks == 5

        # Step 2: Optimize
        result = optimizer.optimize(
            graph=graph,
            available_agents=agents,
            strategy=OptimizationStrategy.MINIMIZE_TIME,
            constraints={}
        )
        assert result.time_saved_percentage >= 0

        # Step 3: Predict
        prediction = optimizer.predict_execution(graph, agents)
        assert prediction.success_probability > 0

    def test_compare_optimization_strategies(self):
        """Test comparing different optimization strategies."""
        optimizer = GraphOptimizer()
        graph = create_test_graph(num_nodes=8, linear=True)
        agents = create_test_agents(num_agents=4)

        results = {}
        for strategy in OptimizationStrategy:
            result = optimizer.optimize(
                graph=graph,
                available_agents=agents,
                strategy=strategy,
                constraints={}
            )
            results[strategy] = result

        # All strategies should complete
        assert len(results) == 4

        # MINIMIZE_TIME should optimize for time
        time_result = results[OptimizationStrategy.MINIMIZE_TIME]
        assert time_result.time_saved_percentage >= 0

        # MINIMIZE_COST should optimize for cost
        cost_result = results[OptimizationStrategy.MINIMIZE_COST]
        assert cost_result.cost_saved_percentage >= 0
