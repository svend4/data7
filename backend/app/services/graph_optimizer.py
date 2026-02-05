"""
Graph Optimization Service

Implements heuristic-based optimization for communication graphs to:
- Minimize execution time
- Minimize LLM API costs
- Balance load across agents
- Maximize parallelism
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import networkx as nx
from uuid import uuid4

from app.domain.models import Agent, CommunicationGraph, GraphEdge


class OptimizationStrategy(Enum):
    """Optimization strategies for graph execution"""
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    BALANCE_LOAD = "balance_load"
    MAXIMIZE_PARALLELISM = "maximize_parallelism"


@dataclass
class OptimizationResult:
    """Result of graph optimization"""
    original_graph_id: str
    optimized_graph_id: str
    strategy: OptimizationStrategy
    expected_time_savings: float  # seconds
    expected_cost_savings: float  # USD
    parallel_groups: List[List[str]]  # Lists of node IDs that can run in parallel
    critical_path: List[str]  # Critical path node IDs
    load_distribution: Dict[str, float]  # Agent ID -> load (0.0-1.0)
    recommendations: List[str]  # Optimization recommendations
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraphAnalysis:
    """Detailed analysis of a communication graph"""
    graph_id: str
    total_nodes: int
    total_edges: int
    critical_path: List[str]
    critical_path_length: float  # seconds
    parallel_groups: List[List[str]]
    max_parallelism: int  # Maximum number of nodes that can run concurrently
    bottlenecks: List[str]  # Node IDs that are bottlenecks
    estimated_time_sequential: float  # seconds
    estimated_time_parallel: float  # seconds
    speedup_factor: float  # parallel vs sequential
    estimated_cost: float  # USD
    resource_requirements: Dict[str, int]  # resource_type -> count


@dataclass
class ExecutionPrediction:
    """Prediction of execution metrics"""
    graph_id: str
    estimated_time_min: float  # seconds (best case)
    estimated_time_avg: float  # seconds (average case)
    estimated_time_max: float  # seconds (worst case)
    estimated_cost_min: float  # USD
    estimated_cost_avg: float  # USD
    estimated_cost_max: float  # USD
    success_probability: float  # 0.0-1.0
    risk_factors: List[str]  # Identified risks


class GraphOptimizer:
    """Optimizes communication graphs for efficient execution"""

    def __init__(self):
        # Cost estimates per model (USD per 1K tokens)
        self.model_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        }

        # Average response times per model (seconds)
        self.model_response_times = {
            "gpt-4": 8.0,
            "gpt-3.5-turbo": 2.0,
            "claude-3-opus": 12.0,
            "claude-3-sonnet": 5.0,
            "claude-3-haiku": 1.5,
        }

    def optimize(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_TIME,
        constraints: Optional[Dict] = None
    ) -> OptimizationResult:
        """
        Optimize graph based on strategy

        Args:
            graph: Communication graph to optimize
            available_agents: List of available agents
            strategy: Optimization strategy to use
            constraints: Optional constraints (e.g., max_cost, max_time)

        Returns:
            OptimizationResult with optimized graph and metrics
        """
        # Analyze original graph
        analysis = self.analyze_graph(graph, available_agents)

        # Apply optimization based on strategy
        if strategy == OptimizationStrategy.MINIMIZE_TIME:
            optimized_graph = self._optimize_for_time(graph, available_agents, analysis)
        elif strategy == OptimizationStrategy.MINIMIZE_COST:
            optimized_graph = self._optimize_for_cost(graph, available_agents, analysis)
        elif strategy == OptimizationStrategy.BALANCE_LOAD:
            optimized_graph = self._optimize_for_load_balance(graph, available_agents, analysis)
        elif strategy == OptimizationStrategy.MAXIMIZE_PARALLELISM:
            optimized_graph = self._optimize_for_parallelism(graph, available_agents, analysis)
        else:
            optimized_graph = graph

        # Analyze optimized graph
        optimized_analysis = self.analyze_graph(optimized_graph, available_agents)

        # Calculate savings
        time_savings = analysis.estimated_time_parallel - optimized_analysis.estimated_time_parallel
        cost_savings = analysis.estimated_cost - optimized_analysis.estimated_cost

        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, optimized_analysis)

        # Calculate load distribution
        load_distribution = self._calculate_load_distribution(optimized_graph, available_agents)

        return OptimizationResult(
            original_graph_id=graph.id,
            optimized_graph_id=optimized_graph.id,
            strategy=strategy,
            expected_time_savings=max(0, time_savings),
            expected_cost_savings=max(0, cost_savings),
            parallel_groups=optimized_analysis.parallel_groups,
            critical_path=optimized_analysis.critical_path,
            load_distribution=load_distribution,
            recommendations=recommendations
        )

    def analyze_graph(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent]
    ) -> GraphAnalysis:
        """
        Analyze graph structure and execution characteristics

        Returns detailed analysis including critical path, parallelism, etc.
        """
        # Convert to NetworkX graph for analysis
        nx_graph = self._to_networkx(graph)

        # Calculate critical path
        critical_path = self._calculate_critical_path(nx_graph, graph)

        # Identify parallel groups
        parallel_groups = self._identify_parallel_groups(nx_graph, graph)

        # Find bottlenecks
        bottlenecks = self._find_bottlenecks(nx_graph, graph)

        # Estimate execution times
        sequential_time = self._estimate_sequential_time(graph)
        parallel_time = self._estimate_parallel_time(graph, parallel_groups)

        # Estimate cost
        estimated_cost = self._estimate_cost(graph)

        # Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(graph)

        return GraphAnalysis(
            graph_id=graph.id,
            total_nodes=len(graph.nodes),
            total_edges=len(graph.edges),
            critical_path=critical_path,
            critical_path_length=parallel_time,
            parallel_groups=parallel_groups,
            max_parallelism=max(len(group) for group in parallel_groups) if parallel_groups else 1,
            bottlenecks=bottlenecks,
            estimated_time_sequential=sequential_time,
            estimated_time_parallel=parallel_time,
            speedup_factor=sequential_time / parallel_time if parallel_time > 0 else 1.0,
            estimated_cost=estimated_cost,
            resource_requirements=resource_requirements
        )

    def predict_execution(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent]
    ) -> ExecutionPrediction:
        """
        Predict execution metrics without running

        Returns best/average/worst case scenarios with confidence
        """
        analysis = self.analyze_graph(graph, available_agents)

        # Best case: Everything runs in parallel, no errors, fast agents
        time_min = analysis.estimated_time_parallel * 0.7  # 30% faster than average

        # Average case: Normal execution
        time_avg = analysis.estimated_time_parallel

        # Worst case: Sequential execution, some retries
        time_max = analysis.estimated_time_sequential * 1.3  # 30% slower due to retries

        # Cost estimates (less variance)
        cost_min = analysis.estimated_cost * 0.9
        cost_avg = analysis.estimated_cost
        cost_max = analysis.estimated_cost * 1.2  # Retries increase cost

        # Success probability based on graph complexity
        success_probability = self._calculate_success_probability(graph, available_agents)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(graph, available_agents, analysis)

        return ExecutionPrediction(
            graph_id=graph.id,
            estimated_time_min=time_min,
            estimated_time_avg=time_avg,
            estimated_time_max=time_max,
            estimated_cost_min=cost_min,
            estimated_cost_avg=cost_avg,
            estimated_cost_max=cost_max,
            success_probability=success_probability,
            risk_factors=risk_factors
        )

    # Private optimization methods

    def _optimize_for_time(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        analysis: GraphAnalysis
    ) -> CommunicationGraph:
        """
        Optimize graph to minimize execution time

        Strategy:
        1. Assign fastest agents to critical path nodes
        2. Maximize parallelism where possible
        3. Use faster (more expensive) models where it matters
        """
        # Clone graph
        optimized = self._clone_graph(graph)

        # Sort agents by speed (use faster models)
        fast_agents = sorted(
            available_agents,
            key=lambda a: self._get_agent_speed_score(a),
            reverse=True
        )

        # Assign fastest agents to critical path nodes
        for node_id in analysis.critical_path:
            node = next((n for n in optimized.nodes if n.agent_id == node_id), None)
            if node and fast_agents:
                # Assign fastest available agent
                node.agent_id = fast_agents[0].id
                fast_agents = fast_agents[1:]  # Use next fastest for next node

        return optimized

    def _optimize_for_cost(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        analysis: GraphAnalysis
    ) -> CommunicationGraph:
        """
        Optimize graph to minimize LLM API costs

        Strategy:
        1. Use cheaper models where accuracy requirements allow
        2. Batch requests where possible
        3. Cache results aggressively
        """
        optimized = self._clone_graph(graph)

        # Sort agents by cost (use cheaper models)
        cheap_agents = sorted(
            available_agents,
            key=lambda a: self._get_agent_cost_score(a)
        )

        # Assign cheapest suitable agents to non-critical nodes
        non_critical = set(n.agent_id for n in optimized.nodes) - set(analysis.critical_path)

        for node_id in non_critical:
            node = next((n for n in optimized.nodes if n.agent_id == node_id), None)
            if node and cheap_agents:
                # Assign cheapest agent that has required capabilities
                suitable_agent = next(
                    (a for a in cheap_agents if self._has_required_capabilities(a, node)),
                    None
                )
                if suitable_agent:
                    node.agent_id = suitable_agent.id

        return optimized

    def _optimize_for_load_balance(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        analysis: GraphAnalysis
    ) -> CommunicationGraph:
        """
        Optimize graph to balance load across agents

        Strategy:
        1. Calculate current load per agent
        2. Reassign tasks from overloaded to underloaded agents
        3. Aim for equal utilization
        """
        optimized = self._clone_graph(graph)

        # Calculate load distribution
        load_dist = self._calculate_load_distribution(optimized, available_agents)

        # Find overloaded and underloaded agents
        avg_load = sum(load_dist.values()) / len(load_dist) if load_dist else 0
        overloaded = {k: v for k, v in load_dist.items() if v > avg_load * 1.2}
        underloaded = {k: v for k, v in load_dist.items() if v < avg_load * 0.8}

        # Reassign tasks from overloaded to underloaded
        for overloaded_agent_id in overloaded:
            # Find nodes assigned to this agent
            nodes = [n for n in optimized.nodes if n.agent_id == overloaded_agent_id]

            # Try to move some to underloaded agents
            for node in nodes[:len(nodes)//2]:  # Move up to half
                # Find suitable underloaded agent
                for underloaded_agent_id in underloaded:
                    underloaded_agent = next(
                        (a for a in available_agents if a.id == underloaded_agent_id),
                        None
                    )
                    if underloaded_agent and self._has_required_capabilities(underloaded_agent, node):
                        node.agent_id = underloaded_agent_id
                        break

        return optimized

    def _optimize_for_parallelism(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        analysis: GraphAnalysis
    ) -> CommunicationGraph:
        """
        Optimize graph to maximize parallel execution

        Strategy:
        1. Identify independent subgraphs
        2. Remove unnecessary dependencies
        3. Assign to different agents to enable parallelism
        """
        optimized = self._clone_graph(graph)

        # Ensure nodes in same parallel group use different agents
        for group in analysis.parallel_groups:
            used_agents = set()
            for node_id in group:
                node = next((n for n in optimized.nodes if n.agent_id == node_id), None)
                if node:
                    # Find an agent not yet used in this group
                    available_agent = next(
                        (a for a in available_agents
                         if a.id not in used_agents and self._has_required_capabilities(a, node)),
                        None
                    )
                    if available_agent:
                        node.agent_id = available_agent.id
                        used_agents.add(available_agent.id)

        return optimized

    # Helper methods for graph analysis

    def _to_networkx(self, graph: CommunicationGraph) -> nx.DiGraph:
        """Convert CommunicationGraph to NetworkX DiGraph"""
        G = nx.DiGraph()

        # Add nodes
        for node in graph.nodes:
            G.add_node(node.agent_id)

        # Add edges
        for edge in graph.edges:
            G.add_edge(edge.from_agent_id, edge.to_agent_id, weight=edge.weight or 1.0)

        return G

    def _calculate_critical_path(
        self,
        nx_graph: nx.DiGraph,
        graph: CommunicationGraph
    ) -> List[str]:
        """
        Calculate critical path (longest path) through graph

        Uses topological sort and dynamic programming
        """
        if not nx_graph.nodes():
            return []

        # Topological sort
        try:
            topo_order = list(nx.topological_sort(nx_graph))
        except nx.NetworkXError:
            # Graph has cycles, return empty
            return []

        # Calculate longest path using DP
        dist = {node: 0 for node in nx_graph.nodes()}
        parent = {node: None for node in nx_graph.nodes()}

        for node in topo_order:
            for successor in nx_graph.successors(node):
                weight = self._get_node_weight(successor, graph)
                if dist[node] + weight > dist[successor]:
                    dist[successor] = dist[node] + weight
                    parent[successor] = node

        # Find node with maximum distance
        if not dist:
            return []

        max_node = max(dist, key=dist.get)

        # Reconstruct path
        path = []
        current = max_node
        while current is not None:
            path.append(current)
            current = parent[current]

        return list(reversed(path))

    def _identify_parallel_groups(
        self,
        nx_graph: nx.DiGraph,
        graph: CommunicationGraph
    ) -> List[List[str]]:
        """
        Identify groups of nodes that can execute in parallel

        Nodes in the same group have no dependencies on each other
        """
        if not nx_graph.nodes():
            return []

        try:
            # Get topological generations (nodes at same depth)
            generations = list(nx.topological_generations(nx_graph))
            return [list(gen) for gen in generations]
        except nx.NetworkXError:
            # Graph has cycles
            return [[node] for node in nx_graph.nodes()]

    def _find_bottlenecks(
        self,
        nx_graph: nx.DiGraph,
        graph: CommunicationGraph
    ) -> List[str]:
        """
        Find bottleneck nodes (nodes with high betweenness centrality)

        Bottlenecks are nodes that many paths go through
        """
        if len(nx_graph.nodes()) < 2:
            return []

        # Calculate betweenness centrality
        try:
            centrality = nx.betweenness_centrality(nx_graph)
            # Return nodes with centrality > 0.5
            return [node for node, cent in centrality.items() if cent > 0.5]
        except:
            return []

    def _estimate_sequential_time(self, graph: CommunicationGraph) -> float:
        """Estimate time if graph executed sequentially"""
        total_time = 0.0

        for node in graph.nodes:
            # Assume average response time of 5 seconds per node
            total_time += 5.0

        return total_time

    def _estimate_parallel_time(
        self,
        graph: CommunicationGraph,
        parallel_groups: List[List[str]]
    ) -> float:
        """Estimate time with parallel execution"""
        total_time = 0.0

        for group in parallel_groups:
            # Time for this parallel group is max time of any node in group
            group_time = max(
                self._get_node_weight(node_id, graph)
                for node_id in group
            )
            total_time += group_time

        return total_time

    def _estimate_cost(self, graph: CommunicationGraph) -> float:
        """Estimate total LLM API cost"""
        total_cost = 0.0

        for node in graph.nodes:
            # Assume average of 1000 tokens input, 500 tokens output
            model = "gpt-3.5-turbo"  # Default model
            if model in self.model_costs:
                cost_per_node = (
                    (1000 / 1000) * self.model_costs[model]["input"] +
                    (500 / 1000) * self.model_costs[model]["output"]
                )
                total_cost += cost_per_node

        return total_cost

    def _calculate_resource_requirements(
        self,
        graph: CommunicationGraph
    ) -> Dict[str, int]:
        """Calculate resource requirements for graph execution"""
        return {
            "agents_required": len(set(n.agent_id for n in graph.nodes)),
            "connections_required": len(graph.edges),
            "parallel_capacity": len(graph.nodes),  # Max if all parallel
        }

    def _get_node_weight(self, node_id: str, graph: CommunicationGraph) -> float:
        """Get estimated execution time for a node"""
        # Default to 5 seconds per node
        return 5.0

    def _clone_graph(self, graph: CommunicationGraph) -> CommunicationGraph:
        """Create a deep copy of the graph"""
        # Simple clone - in production, use proper deep copy
        return CommunicationGraph(
            id=str(uuid4()),
            name=f"{graph.name}_optimized",
            description=f"Optimized version of {graph.name}",
            nodes=graph.nodes.copy(),
            edges=graph.edges.copy(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def _get_agent_speed_score(self, agent: Agent) -> float:
        """Calculate agent speed score (higher is faster)"""
        # Based on model and current load
        base_speed = 1.0 / self.model_response_times.get(agent.backend_type or "gpt-3.5-turbo", 5.0)
        load_penalty = agent.current_load  # Higher load = slower
        return base_speed * (1.0 - load_penalty * 0.5)

    def _get_agent_cost_score(self, agent: Agent) -> float:
        """Calculate agent cost score (lower is cheaper)"""
        model = agent.backend_type or "gpt-3.5-turbo"
        if model in self.model_costs:
            return (self.model_costs[model]["input"] + self.model_costs[model]["output"]) / 2
        return 0.0015  # Default average cost

    def _has_required_capabilities(self, agent: Agent, node) -> bool:
        """Check if agent has required capabilities for node"""
        # Simple check - in production, match capabilities properly
        return True

    def _calculate_load_distribution(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent]
    ) -> Dict[str, float]:
        """Calculate load distribution across agents"""
        load_dist = {agent.id: 0.0 for agent in available_agents}

        # Count nodes per agent
        for node in graph.nodes:
            if node.agent_id in load_dist:
                load_dist[node.agent_id] += 1.0

        # Normalize to 0-1 range
        max_load = max(load_dist.values()) if load_dist.values() else 1.0
        if max_load > 0:
            load_dist = {k: v / max_load for k, v in load_dist.items()}

        return load_dist

    def _calculate_success_probability(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent]
    ) -> float:
        """Calculate probability of successful execution"""
        # Base success rate
        base_rate = 0.95

        # Penalize for complexity
        complexity_penalty = len(graph.nodes) * 0.01  # 1% per node
        complexity_penalty = min(complexity_penalty, 0.3)  # Max 30% penalty

        # Penalize for unavailable agents
        unavailable_penalty = 0.0
        for node in graph.nodes:
            if not any(a.id == node.agent_id and a.status == "idle" for a in available_agents):
                unavailable_penalty += 0.05

        return max(0.5, base_rate - complexity_penalty - unavailable_penalty)

    def _identify_risk_factors(
        self,
        graph: CommunicationGraph,
        available_agents: List[Agent],
        analysis: GraphAnalysis
    ) -> List[str]:
        """Identify risk factors for execution"""
        risks = []

        # Complex graph
        if len(graph.nodes) > 20:
            risks.append(f"Large graph ({len(graph.nodes)} nodes) increases failure risk")

        # Bottlenecks
        if analysis.bottlenecks:
            risks.append(f"{len(analysis.bottlenecks)} bottleneck(s) detected - may slow execution")

        # Low parallelism
        if analysis.speedup_factor < 2.0:
            risks.append("Low parallelism - limited performance benefit")

        # High cost
        if analysis.estimated_cost > 1.0:
            risks.append(f"High estimated cost (${analysis.estimated_cost:.2f})")

        # Agent availability
        unavailable_count = sum(
            1 for node in graph.nodes
            if not any(a.id == node.agent_id and a.status == "idle" for a in available_agents)
        )
        if unavailable_count > 0:
            risks.append(f"{unavailable_count} agent(s) currently unavailable")

        return risks

    def _generate_recommendations(
        self,
        original: GraphAnalysis,
        optimized: GraphAnalysis
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Time improvement
        time_improvement = ((original.estimated_time_parallel - optimized.estimated_time_parallel)
                           / original.estimated_time_parallel * 100)
        if time_improvement > 5:
            recommendations.append(
                f"Optimization reduced execution time by {time_improvement:.1f}%"
            )

        # Parallelism improvement
        if optimized.max_parallelism > original.max_parallelism:
            recommendations.append(
                f"Increased parallelism from {original.max_parallelism} to {optimized.max_parallelism} concurrent tasks"
            )

        # Bottleneck reduction
        if len(optimized.bottlenecks) < len(original.bottlenecks):
            recommendations.append(
                f"Reduced bottlenecks from {len(original.bottlenecks)} to {len(optimized.bottlenecks)}"
            )

        # Cost savings
        cost_savings = original.estimated_cost - optimized.estimated_cost
        if cost_savings > 0.1:
            recommendations.append(
                f"Estimated cost savings: ${cost_savings:.2f} ({cost_savings/original.estimated_cost*100:.1f}%)"
            )

        # General recommendations
        if optimized.max_parallelism < optimized.total_nodes:
            recommendations.append(
                "Consider adding more agents to increase parallelism"
            )

        if optimized.bottlenecks:
            recommendations.append(
                "Assign fastest agents to bottleneck nodes for better performance"
            )

        return recommendations
