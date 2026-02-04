# Technical Specification Part 2: Advanced Components & Architecture

**Version**: 8.1 (continued)
**Date**: 2026-02-04
**Continuation from**: TECHNICAL_SPEC_PART1_UML.md

---

## 🔷 LEVEL 4: Core System Components (Сложное)

### 4.1. CommunicationSwitchboard (Телефонный коммутатор)

```python
"""
CommunicationSwitchboard - Central switchboard for managing connections
Like a telephone operator connecting agents
"""

from typing import Dict, List, Optional, Tuple


class Socket:
    """
    Socket (розетка) на коммутаторе
    Represents a connection point for an agent
    """

    def __init__(self, socket_id: int):
        self.id: int = socket_id
        self.agent_id: Optional[str] = None
        self.status: str = "free"  # free/assigned/busy
        self.position: Vector3 = Vector3(0, 0, 0)  # для визуализации

    def is_free(self) -> bool:
        return self.status == "free"

    def is_ready(self) -> bool:
        return self.status == "assigned"

    def assign(self, agent_id: str) -> None:
        """Assign socket to agent"""
        if not self.is_free():
            raise ValueError(f"Socket {self.id} is not free")
        self.agent_id = agent_id
        self.status = "assigned"

    def set_busy(self) -> None:
        """Mark socket as busy (connection active)"""
        self.status = "busy"

    def release(self) -> None:
        """Release socket back to assigned state"""
        if self.status == "busy":
            self.status = "assigned"

    def free(self) -> None:
        """Free socket completely"""
        self.agent_id = None
        self.status = "free"

    def __repr__(self) -> str:
        return f"Socket({self.id}, {self.status}, agent={self.agent_id})"


class CommunicationSwitchboard:
    """
    Центральный коммутатор для управления соединениями

    Responsibilities:
    - Выделение розеток для агентов
    - Создание/разрыв соединений
    - Мониторинг активных соединений
    - Управление ёмкостью (capacity management)
    """

    def __init__(self, capacity: int = 100):
        self.capacity: int = capacity

        # Create sockets
        self.sockets: List[Socket] = [Socket(i) for i in range(capacity)]

        # Active connections
        self.active_connections: Dict[str, Connection] = {}  # conn_id -> Connection

        # Mapping: agent_id -> socket_id
        self.agent_to_socket: Dict[str, int] = {}

    # === Socket Management ===

    def allocate_socket(self, agent_id: str, position: Optional[Vector3] = None) -> Socket:
        """
        Allocate a socket for an agent
        Returns the allocated socket
        """
        # Check if agent already has socket
        if agent_id in self.agent_to_socket:
            socket_id = self.agent_to_socket[agent_id]
            return self.sockets[socket_id]

        # Find free socket
        for socket in self.sockets:
            if socket.is_free():
                socket.assign(agent_id)
                if position:
                    socket.position = position
                self.agent_to_socket[agent_id] = socket.id
                return socket

        raise CapacityError("No free sockets available")

    def deallocate_socket(self, agent_id: str) -> None:
        """Deallocate socket for an agent"""
        if agent_id not in self.agent_to_socket:
            raise ValueError(f"Agent {agent_id} has no allocated socket")

        socket_id = self.agent_to_socket[agent_id]
        socket = self.sockets[socket_id]
        socket.free()
        del self.agent_to_socket[agent_id]

    def get_socket(self, agent_id: str) -> Optional[Socket]:
        """Get socket for an agent"""
        socket_id = self.agent_to_socket.get(agent_id)
        return self.sockets[socket_id] if socket_id is not None else None

    # === Connection Management ===

    def connect(
        self,
        agent_a: Agent,
        agent_b: Agent,
        parameters: ChannelParameters
    ) -> Connection:
        """
        Create connection between two agents
        Like inserting a wire between two sockets
        """
        # Get sockets for both agents
        socket_a = self.get_socket(agent_a.id)
        socket_b = self.get_socket(agent_b.id)

        if not socket_a or not socket_b:
            raise ValueError("Both agents must have allocated sockets")

        if not (socket_a.is_ready() and socket_b.is_ready()):
            raise ValueError("Sockets are not ready")

        # Create connection
        connection = Connection(agent_a, agent_b, parameters)

        # Mark sockets as busy
        socket_a.set_busy()
        socket_b.set_busy()

        # Open connection
        connection.open()

        # Register connection
        self.active_connections[connection.id] = connection

        return connection

    def disconnect(self, connection_id: str) -> None:
        """
        Disconnect and remove connection
        Like pulling out the wire
        """
        if connection_id not in self.active_connections:
            raise ValueError(f"Connection {connection_id} not found")

        connection = self.active_connections[connection_id]

        # Close connection
        connection.close()

        # Release sockets
        socket_a = self.get_socket(connection.agent_a.id)
        socket_b = self.get_socket(connection.agent_b.id)
        if socket_a:
            socket_a.release()
        if socket_b:
            socket_b.release()

        # Unregister
        del self.active_connections[connection_id]

    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get active connection by ID"""
        return self.active_connections.get(connection_id)

    def get_connections_for_agent(self, agent_id: str) -> List[Connection]:
        """Get all connections for specific agent"""
        return [
            conn for conn in self.active_connections.values()
            if conn.agent_a.id == agent_id or conn.agent_b.id == agent_id
        ]

    # === Monitoring ===

    def get_utilization(self) -> float:
        """Get switchboard utilization (0.0-1.0)"""
        active = len(self.active_connections)
        return active / self.capacity

    def get_free_capacity(self) -> int:
        """Get number of free sockets"""
        return sum(1 for s in self.sockets if s.is_free())

    def get_stats(self) -> dict:
        """Get switchboard statistics"""
        return {
            "capacity": self.capacity,
            "active_connections": len(self.active_connections),
            "utilization": self.get_utilization(),
            "free_sockets": self.get_free_capacity(),
            "assigned_sockets": sum(1 for s in self.sockets if s.status == "assigned"),
            "busy_sockets": sum(1 for s in self.sockets if s.status == "busy")
        }

    def __repr__(self) -> str:
        return (
            f"CommunicationSwitchboard("
            f"{len(self.active_connections)}/{self.capacity} connections, "
            f"{self.get_utilization():.1%} utilization)"
        )


class CapacityError(Exception):
    """Raised when switchboard is at capacity"""
    pass


# === UML CLASS DIAGRAM ===

"""
┌────────────────────────────────────────────┐
│    CommunicationSwitchboard                │
├────────────────────────────────────────────┤
│ - capacity: int                            │
│ - sockets: List[Socket]                    │
│ - active_connections: Dict[str, Connection]│
│ - agent_to_socket: Dict[str, int]          │
├────────────────────────────────────────────┤
│ + allocate_socket(agent_id): Socket        │
│ + deallocate_socket(agent_id)              │
│ + get_socket(agent_id): Socket?            │
│ + connect(agent_a, agent_b, params): Conn  │
│ + disconnect(connection_id)                │
│ + get_connection(id): Connection?          │
│ + get_connections_for_agent(id): List      │
│ + get_utilization(): float                 │
│ + get_free_capacity(): int                 │
│ + get_stats(): dict                        │
└────────────────────────────────────────────┘
        │                    │
        │ manages            │ manages
        ↓                    ↓
┌───────────┐        ┌──────────────┐
│  Socket   │        │  Connection  │
├───────────┤        └──────────────┘
│ + id      │
│ + agent_id│
│ + status  │
│ + position│
└───────────┘

Relationship:
- Switchboard creates Connections
- Switchboard manages Sockets
- Socket is assigned to Agent
- Connection connects two Agents through Sockets
"""
```

**Complexity**: ⭐⭐⭐⭐ (4/5) - Сложная координация + capacity management
**Dependencies**: Socket, Connection, Agent, ChannelParameters
**Key Responsibilities**:
- Resource allocation (sockets)
- Connection lifecycle
- Capacity management

### 4.2. CommunicationGraph (Граф коммуникаций)

```python
"""
CommunicationGraph - Represents the communication structure
Directed or undirected graph of agent connections
"""

from typing import Set, Dict, List, Tuple, Optional
import networkx as nx  # для графовых алгоритмов


class GraphNode:
    """Node in communication graph (represents an agent)"""

    def __init__(self, agent_id: str, metadata: AgentMetadata):
        self.agent_id: str = agent_id
        self.metadata: AgentMetadata = metadata

    def __hash__(self):
        return hash(self.agent_id)

    def __eq__(self, other):
        return isinstance(other, GraphNode) and self.agent_id == other.agent_id

    def __repr__(self):
        return f"GraphNode({self.agent_id}, role={self.metadata.role})"


class GraphEdge:
    """Edge in communication graph (represents a connection)"""

    def __init__(
        self,
        source: str,
        target: str,
        parameters: ChannelParameters,
        weight: float = 1.0
    ):
        self.source: str = source
        self.target: str = target
        self.parameters: ChannelParameters = parameters
        self.weight: float = weight  # для алгоритмов оптимизации

    def __repr__(self):
        return f"GraphEdge({self.source} → {self.target}, priority={self.parameters.priority})"


class CommunicationGraph:
    """
    Граф коммуникаций между агентами

    Responsibilities:
    - Построение графа связей
    - Топологический анализ
    - Поиск путей
    - Оптимизация графа
    - Экспорт в различные форматы
    """

    def __init__(self, directed: bool = True):
        self.directed: bool = directed

        # Graph structure
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

        # NetworkX graph for algorithms
        self._nx_graph: Optional[nx.DiGraph] = None
        self._needs_rebuild = True

    # === Node Management ===

    def add_node(self, agent_id: str, metadata: AgentMetadata) -> GraphNode:
        """Add node to graph"""
        if agent_id in self.nodes:
            raise ValueError(f"Node {agent_id} already exists")

        node = GraphNode(agent_id, metadata)
        self.nodes[agent_id] = node
        self._needs_rebuild = True
        return node

    def remove_node(self, agent_id: str) -> None:
        """Remove node and all connected edges"""
        if agent_id not in self.nodes:
            raise ValueError(f"Node {agent_id} not found")

        # Remove node
        del self.nodes[agent_id]

        # Remove connected edges
        self.edges = [
            e for e in self.edges
            if e.source != agent_id and e.target != agent_id
        ]
        self._needs_rebuild = True

    def get_node(self, agent_id: str) -> Optional[GraphNode]:
        """Get node by agent ID"""
        return self.nodes.get(agent_id)

    # === Edge Management ===

    def add_edge(
        self,
        source: str,
        target: str,
        parameters: ChannelParameters,
        weight: float = 1.0
    ) -> GraphEdge:
        """Add edge to graph"""
        # Validate nodes exist
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Both source and target must exist as nodes")

        edge = GraphEdge(source, target, parameters, weight)
        self.edges.append(edge)
        self._needs_rebuild = True
        return edge

    def remove_edge(self, source: str, target: str) -> None:
        """Remove edge between two nodes"""
        self.edges = [
            e for e in self.edges
            if not (e.source == source and e.target == target)
        ]
        self._needs_rebuild = True

    def get_edges_from(self, agent_id: str) -> List[GraphEdge]:
        """Get all outgoing edges from node"""
        return [e for e in self.edges if e.source == agent_id]

    def get_edges_to(self, agent_id: str) -> List[GraphEdge]:
        """Get all incoming edges to node"""
        return [e for e in self.edges if e.target == agent_id]

    # === Graph Analysis ===

    def _build_nx_graph(self) -> None:
        """Build NetworkX graph for analysis"""
        if not self._needs_rebuild:
            return

        G = nx.DiGraph() if self.directed else nx.Graph()

        # Add nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id, metadata=node.metadata)

        # Add edges
        for edge in self.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight, params=edge.parameters)

        self._nx_graph = G
        self._needs_rebuild = False

    def topological_sort(self) -> List[str]:
        """
        Topological sort (for directed acyclic graphs)
        Returns execution order
        """
        if not self.directed:
            raise ValueError("Topological sort only works on directed graphs")

        self._build_nx_graph()

        try:
            return list(nx.topological_sort(self._nx_graph))
        except nx.NetworkXError:
            raise ValueError("Graph contains cycles, cannot topologically sort")

    def is_acyclic(self) -> bool:
        """Check if graph is acyclic (DAG)"""
        if not self.directed:
            return False

        self._build_nx_graph()
        return nx.is_directed_acyclic_graph(self._nx_graph)

    def find_cycles(self) -> List[List[str]]:
        """Find all cycles in graph"""
        if not self.directed:
            raise ValueError("Cycle detection only for directed graphs")

        self._build_nx_graph()
        try:
            return list(nx.find_cycle(self._nx_graph))
        except nx.NetworkXNoCycle:
            return []

    def shortest_path(self, source: str, target: str) -> List[str]:
        """Find shortest path between two nodes"""
        self._build_nx_graph()
        try:
            return nx.shortest_path(self._nx_graph, source, target, weight='weight')
        except nx.NetworkXNoPath:
            raise ValueError(f"No path from {source} to {target}")

    def get_critical_path(self) -> Tuple[List[str], float]:
        """
        Get critical path (longest path in DAG)
        Returns (path, total_weight)
        """
        if not self.is_acyclic():
            raise ValueError("Critical path only for DAGs")

        self._build_nx_graph()

        # For DAG, critical path is longest path
        longest_path = nx.dag_longest_path(self._nx_graph, weight='weight')
        path_length = nx.dag_longest_path_length(self._nx_graph, weight='weight')

        return longest_path, path_length

    def identify_parallel_groups(self) -> List[List[str]]:
        """
        Identify groups of nodes that can execute in parallel
        """
        if not self.is_acyclic():
            raise ValueError("Parallel grouping only for DAGs")

        self._build_nx_graph()

        # Nodes at same topological level can execute in parallel
        levels = list(nx.topological_generations(self._nx_graph))
        return levels

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get graph statistics"""
        self._build_nx_graph()

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "is_directed": self.directed,
            "is_acyclic": self.is_acyclic() if self.directed else None,
            "density": nx.density(self._nx_graph),
            "avg_degree": (
                sum(dict(self._nx_graph.degree()).values()) / len(self.nodes)
                if self.nodes else 0
            )
        }

    # === Export ===

    def to_dict(self) -> dict:
        """Export graph to dictionary"""
        return {
            "directed": self.directed,
            "nodes": [
                {
                    "agent_id": node.agent_id,
                    "role": node.metadata.role,
                    "capabilities": [c.name for c in node.metadata.capabilities]
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "priority": edge.parameters.priority.name,
                    "protocol": edge.parameters.protocol.name,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }

    def __repr__(self):
        return (
            f"CommunicationGraph("
            f"{len(self.nodes)} nodes, {len(self.edges)} edges, "
            f"{'directed' if self.directed else 'undirected'})"
        )


# === UML CLASS DIAGRAM ===

"""
┌────────────────────────────────────────────┐
│       CommunicationGraph                   │
├────────────────────────────────────────────┤
│ - directed: bool                           │
│ - nodes: Dict[str, GraphNode]              │
│ - edges: List[GraphEdge]                   │
│ - _nx_graph: nx.DiGraph?                   │
│ - _needs_rebuild: bool                     │
├────────────────────────────────────────────┤
│ + add_node(id, metadata): GraphNode        │
│ + remove_node(id)                          │
│ + add_edge(src, tgt, params): GraphEdge    │
│ + remove_edge(src, tgt)                    │
│ + topological_sort(): List[str]            │
│ + is_acyclic(): bool                       │
│ + find_cycles(): List[List[str]]           │
│ + shortest_path(src, tgt): List[str]       │
│ + get_critical_path(): (List[str], float)  │
│ + identify_parallel_groups(): List[List]   │
│ + get_stats(): dict                        │
│ + to_dict(): dict                          │
│ - _build_nx_graph()                        │
└────────────────────────────────────────────┘
        │                    │
        │ contains           │ contains
        ↓                    ↓
┌───────────┐        ┌──────────────┐
│ GraphNode │        │  GraphEdge   │
├───────────┤        ├──────────────┤
│ + agent_id│        │ + source     │
│ + metadata│        │ + target     │
└───────────┘        │ + parameters │
                     │ + weight     │
                     └──────────────┘
"""
```

**Complexity**: ⭐⭐⭐⭐ (4/5) - Графовые алгоритмы + оптимизация
**Dependencies**: GraphNode, GraphEdge, AgentMetadata, ChannelParameters, NetworkX
**Key Responsibilities**:
- Graph construction
- Topological analysis
- Path finding
- Parallel execution planning

---

## 🔷 LEVEL 5: High-Level Systems (Наиболее Сложное)

### 5.1. GraphExecutor (Исполнитель графа)

```python
"""
GraphExecutor - Executes communication graph
Orchestrates parallel execution of agent communications
"""

from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Dict, Any
import time


class ExecutionPlan:
    """План выполнения графа"""

    def __init__(
        self,
        order: List[str],
        parallel_groups: List[List[str]],
        estimated_time: float
    ):
        self.order: List[str] = order
        self.parallel_groups: List[List[str]] = parallel_groups
        self.estimated_time: float = estimated_time

    def __repr__(self):
        return (
            f"ExecutionPlan("
            f"{len(self.order)} steps, "
            f"{len(self.parallel_groups)} parallel groups, "
            f"~{self.estimated_time:.1f}s)"
        )


class ExecutionResult:
    """Результат выполнения"""

    def __init__(
        self,
        results: Dict[str, Any],
        total_time: float,
        success_rate: float,
        communication_graph: CommunicationGraph
    ):
        self.results: Dict[str, Any] = results
        self.total_time: float = total_time
        self.success_rate: float = success_rate
        self.communication_graph: CommunicationGraph = communication_graph
        self.message_count: int = 0
        self.error_count: int = 0

    def __repr__(self):
        return (
            f"ExecutionResult("
            f"{len(self.results)} results, "
            f"{self.total_time:.1f}s, "
            f"{self.success_rate:.1%} success)"
        )


class GraphExecutor:
    """
    Исполнитель графа коммуникаций

    Responsibilities:
    - Создание плана выполнения из графа
    - Параллельное выполнение где возможно
    - Управление соединениями через switchboard
    - Обработка ошибок и retry
    - Сбор метрик выполнения
    """

    def __init__(
        self,
        switchboard: CommunicationSwitchboard,
        max_workers: int = 10
    ):
        self.switchboard: CommunicationSwitchboard = switchboard
        self.max_workers: int = max_workers

        # Active tasks tracking
        self.active_tasks: Dict[str, Future] = {}

    def create_plan(self, graph: CommunicationGraph) -> ExecutionPlan:
        """
        Create execution plan from graph

        Strategy:
        1. Topological sort for order
        2. Identify parallel groups (same level in DAG)
        3. Estimate time based on edge weights
        """
        # Get execution order
        try:
            order = graph.topological_sort()
        except ValueError:
            # Graph has cycles - use best-effort ordering
            order = list(graph.nodes.keys())

        # Identify parallel groups
        try:
            parallel_groups = graph.identify_parallel_groups()
        except ValueError:
            # Not a DAG - execute sequentially
            parallel_groups = [[node_id] for node_id in order]

        # Estimate time (critical path length)
        try:
            _, estimated_time = graph.get_critical_path()
        except ValueError:
            # Can't calculate critical path - estimate from total edges
            estimated_time = len(graph.edges) * 10.0  # 10s per edge (rough estimate)

        return ExecutionPlan(order, parallel_groups, estimated_time)

    def execute(
        self,
        plan: ExecutionPlan,
        graph: CommunicationGraph,
        monitor: 'SystemMonitor'
    ) -> ExecutionResult:
        """
        Execute the plan

        Process:
        1. For each parallel group
        2. Create connections for all edges in group
        3. Execute communications in parallel
        4. Wait for completion
        5. Move to next group
        """
        start_time = time.time()
        all_results = {}
        success_count = 0
        failure_count = 0

        # Execute each parallel group
        for group_idx, group in enumerate(plan.parallel_groups):
            print(f"Executing group {group_idx + 1}/{len(plan.parallel_groups)}: {group}")

            # Get edges for this group
            group_edges = self._get_edges_for_group(group, graph)

            if not group_edges:
                continue

            # Execute group in parallel
            group_results = self._execute_parallel_group(
                group_edges,
                graph,
                monitor
            )

            # Aggregate results
            all_results.update(group_results)

            # Count successes/failures
            for result in group_results.values():
                if result and not result.get('error'):
                    success_count += 1
                else:
                    failure_count += 1

            # Check if should stop
            if monitor.should_stop():
                print("Monitor signaled stop")
                break

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate success rate
        total_operations = success_count + failure_count
        success_rate = success_count / total_operations if total_operations > 0 else 0.0

        return ExecutionResult(
            results=all_results,
            total_time=total_time,
            success_rate=success_rate,
            communication_graph=graph
        )

    def _get_edges_for_group(
        self,
        group: List[str],
        graph: CommunicationGraph
    ) -> List[GraphEdge]:
        """Get all edges involving nodes in this group"""
        edges = []
        for node_id in group:
            edges.extend(graph.get_edges_from(node_id))
        return edges

    def _execute_parallel_group(
        self,
        edges: List[GraphEdge],
        graph: CommunicationGraph,
        monitor: 'SystemMonitor'
    ) -> Dict[str, Any]:
        """
        Execute a group of edges in parallel

        For each edge:
        1. Create connection via switchboard
        2. Send message
        3. Wait for response
        4. Record metrics
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for edge in edges:
                future = executor.submit(
                    self._execute_single_edge,
                    edge,
                    graph,
                    monitor
                )
                futures[edge] = future

            # Wait for completion
            for edge, future in futures.items():
                try:
                    result = future.result(timeout=edge.parameters.timeout)
                    results[edge.source + "->" + edge.target] = result
                    monitor.log_success(edge)
                except TimeoutError:
                    monitor.log_timeout(edge)
                    results[edge.source + "->" + edge.target] = {
                        "error": "timeout",
                        "edge": f"{edge.source} -> {edge.target}"
                    }
                except Exception as e:
                    monitor.log_error(edge, e)
                    results[edge.source + "->" + edge.target] = {
                        "error": str(e),
                        "edge": f"{edge.source} -> {edge.target}"
                    }

        return results

    def _execute_single_edge(
        self,
        edge: GraphEdge,
        graph: CommunicationGraph,
        monitor: 'SystemMonitor'
    ) -> Dict[str, Any]:
        """
        Execute communication for single edge

        Steps:
        1. Get agents from graph
        2. Create connection via switchboard
        3. Create and send message
        4. Wait for response
        5. Close connection
        6. Return result
        """
        # Get nodes
        source_node = graph.get_node(edge.source)
        target_node = graph.get_node(edge.target)

        if not source_node or not target_node:
            raise ValueError(f"Invalid edge: {edge}")

        # Note: In real implementation, we would get Agent objects from AgentRegistry
        # For now, we'll simulate

        # Create message
        message = Message(
            message_id=str(uuid4()),
            from_agent=edge.source,
            to_agent=edge.target,
            message_type=MessageType.REQUEST,
            content=f"Task for {edge.target}",
            timestamp=Timestamp.now(),
            metadata={"edge_weight": edge.weight}
        )

        # Simulate processing (in real implementation, would use actual agents)
        time.sleep(0.1)  # simulate work

        return {
            "message_id": message.message_id,
            "from": edge.source,
            "to": edge.target,
            "status": "success",
            "processing_time": 0.1
        }

    def get_active_task_count(self) -> int:
        """Get number of currently active tasks"""
        return len([f for f in self.active_tasks.values() if not f.done()])


# === UML CLASS DIAGRAM ===

"""
┌────────────────────────────────────────────┐
│          GraphExecutor                     │
├────────────────────────────────────────────┤
│ - switchboard: CommunicationSwitchboard    │
│ - max_workers: int                         │
│ - active_tasks: Dict[str, Future]          │
├────────────────────────────────────────────┤
│ + create_plan(graph): ExecutionPlan        │
│ + execute(plan, graph, monitor): Result    │
│ + get_active_task_count(): int             │
│ - _get_edges_for_group(group, graph)       │
│ - _execute_parallel_group(edges, ...)      │
│ - _execute_single_edge(edge, graph, ...)   │
└────────────────────────────────────────────┘
        │                    │
        │ uses               │ creates
        ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ Switchboard      │  │ ExecutionPlan    │
└──────────────────┘  └──────────────────┘
        │                    │
        │ uses               │ produces
        ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ CommunicationGr  │  │ ExecutionResult  │
└──────────────────┘  └──────────────────┘
"""
```

**Complexity**: ⭐⭐⭐⭐⭐ (5/5) - Сложнейшая оркестрация + параллелизм
**Dependencies**: CommunicationGraph, CommunicationSwitchboard, SystemMonitor
**Key Responsibilities**:
- Plan creation from graph
- Parallel execution management
- Error handling and retries
- Metrics collection

---

Создана детальная UML документация от простого к сложному (Levels 1-5). Продолжить с API спецификациями и data schemas?
