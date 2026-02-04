"""
Domain Entities (Level 2-3 ⭐⭐⭐)
Core business objects with identity and lifecycle
Based on TECHNICAL_SPEC_PART1_UML.md and PART2_UML.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import uuid4

from app.domain.value_objects import (
    AgentStatus,
    ConnectionStatus,
    TaskStatus,
    AgentCapability,
    PerformanceMetrics,
    Vector3,
)


# ============================================================================
# Level 2: Core Entities (⭐⭐)
# ============================================================================


@dataclass
class Agent:
    """
    Agent Entity (Level 2 ⭐⭐)
    Represents an AI agent in the system with capabilities and metrics
    """
    role: str
    capabilities: List[AgentCapability]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: AgentStatus = AgentStatus.IDLE
    metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    position: Optional[Vector3] = None  # 3D position for visualization
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate agent"""
        if not self.role or not self.role.strip():
            raise ValueError("Agent role cannot be empty")
        if not self.capabilities:
            raise ValueError("Agent must have at least one capability")

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a task type"""
        return any(
            cap.category == task_type or cap.name == task_type
            for cap in self.capabilities
        )

    def is_available(self) -> bool:
        """Check if agent is available for work"""
        return self.status == AgentStatus.IDLE and self.metrics.current_load < 0.8

    def update_metrics(self, **kwargs) -> None:
        """Update performance metrics"""
        metrics_dict = {
            'avg_response_time': kwargs.get('avg_response_time', self.metrics.avg_response_time),
            'success_rate': kwargs.get('success_rate', self.metrics.success_rate),
            'total_tasks': kwargs.get('total_tasks', self.metrics.total_tasks),
            'current_load': kwargs.get('current_load', self.metrics.current_load),
        }
        self.metrics = PerformanceMetrics(**metrics_dict)
        self.updated_at = datetime.utcnow()

    def __str__(self) -> str:
        return f"Agent({self.id[:8]}, role={self.role}, status={self.status.value})"


@dataclass
class Task:
    """
    Task Entity (Level 2 ⭐⭐)
    Represents a unit of work flowing through the system
    """
    description: str
    task_type: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10, higher is more urgent
    assigned_agent_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate task"""
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if not (1 <= self.priority <= 10):
            raise ValueError(f"Priority must be 1-10, got {self.priority}")

    def assign_to(self, agent_id: str) -> None:
        """Assign task to an agent"""
        self.assigned_agent_id = agent_id
        self.status = TaskStatus.QUEUED

    def start(self) -> None:
        """Mark task as started"""
        if self.status != TaskStatus.QUEUED:
            raise ValueError(f"Cannot start task in status: {self.status}")
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, result: Any) -> None:
        """Mark task as completed with result"""
        if self.status != TaskStatus.RUNNING:
            raise ValueError(f"Cannot complete task in status: {self.status}")
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """Mark task as failed with error"""
        if self.status not in [TaskStatus.RUNNING, TaskStatus.QUEUED]:
            raise ValueError(f"Cannot fail task in status: {self.status}")
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __str__(self) -> str:
        return f"Task({self.id[:8]}, type={self.task_type}, status={self.status.value})"


@dataclass
class Connection:
    """
    Connection Entity (Level 2 ⭐⭐)
    Represents a communication link between two agents
    """
    from_agent_id: str
    to_agent_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    socket_from: Optional[int] = None  # Physical socket number on switchboard
    socket_to: Optional[int] = None
    bandwidth: float = 1.0  # Relative bandwidth (0.0-1.0)
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    established_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate connection"""
        if self.from_agent_id == self.to_agent_id:
            raise ValueError("Cannot connect agent to itself")
        if not (0.0 <= self.bandwidth <= 1.0):
            raise ValueError(f"Bandwidth must be 0.0-1.0, got {self.bandwidth}")
        if self.latency_ms < 0:
            raise ValueError("Latency cannot be negative")

    def establish(self, socket_from: int, socket_to: int) -> None:
        """Establish the connection"""
        if self.status != ConnectionStatus.DISCONNECTED:
            raise ValueError(f"Cannot establish connection in status: {self.status}")
        self.socket_from = socket_from
        self.socket_to = socket_to
        self.status = ConnectionStatus.CONNECTED
        self.established_at = datetime.utcnow()

    def disconnect(self) -> None:
        """Disconnect the connection"""
        if self.status not in [ConnectionStatus.CONNECTED, ConnectionStatus.TRANSMITTING]:
            raise ValueError(f"Cannot disconnect connection in status: {self.status}")
        self.status = ConnectionStatus.DISCONNECTED
        self.closed_at = datetime.utcnow()

    def __str__(self) -> str:
        return f"Connection({self.id[:8]}, {self.from_agent_id[:8]}->{self.to_agent_id[:8]})"


# ============================================================================
# Level 3: Composite Entities (⭐⭐⭐)
# ============================================================================


@dataclass
class CommunicationGraph:
    """
    Communication Graph (Level 3 ⭐⭐⭐)
    Directed graph of agent connections for task execution
    """
    root_task_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    nodes: List[str] = field(default_factory=list)  # Agent IDs
    edges: List[Connection] = field(default_factory=list)
    execution_plan: List[str] = field(default_factory=list)  # Ordered task IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_node(self, agent_id: str) -> None:
        """Add agent node to graph"""
        if agent_id not in self.nodes:
            self.nodes.append(agent_id)

    def add_edge(self, connection: Connection) -> None:
        """Add connection edge to graph"""
        # Ensure both agents are nodes
        self.add_node(connection.from_agent_id)
        self.add_node(connection.to_agent_id)
        self.edges.append(connection)

    def get_dependencies(self, agent_id: str) -> List[str]:
        """Get all agents that must complete before this agent"""
        return [
            edge.from_agent_id
            for edge in self.edges
            if edge.to_agent_id == agent_id
        ]

    def get_dependents(self, agent_id: str) -> List[str]:
        """Get all agents that depend on this agent"""
        return [
            edge.to_agent_id
            for edge in self.edges
            if edge.from_agent_id == agent_id
        ]

    def __str__(self) -> str:
        return f"CommunicationGraph({self.id[:8]}, nodes={len(self.nodes)}, edges={len(self.edges)})"


@dataclass
class GraphExecution:
    """
    Graph Execution (Level 3 ⭐⭐⭐)
    Tracks the execution of a communication graph
    """
    graph_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    current_step: int = 0
    completed_tasks: List[str] = field(default_factory=list)  # Task IDs
    failed_tasks: List[str] = field(default_factory=list)
    active_connections: List[str] = field(default_factory=list)  # Connection IDs
    results: Dict[str, Any] = field(default_factory=dict)  # task_id -> result
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self) -> None:
        """Start graph execution"""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start execution in status: {self.status}")
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete_task(self, task_id: str, result: Any) -> None:
        """Mark a task as completed"""
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            self.results[task_id] = result
            self.current_step += 1

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed"""
        if task_id not in self.failed_tasks:
            self.failed_tasks.append(task_id)
            self.results[task_id] = {"error": error}

    def complete(self) -> None:
        """Mark execution as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self) -> None:
        """Mark execution as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()

    @property
    def progress(self) -> float:
        """Calculate execution progress (0.0-1.0)"""
        total = len(self.completed_tasks) + len(self.failed_tasks)
        if total == 0:
            return 0.0
        return len(self.completed_tasks) / total

    def __str__(self) -> str:
        return f"GraphExecution({self.id[:8]}, graph={self.graph_id[:8]}, progress={self.progress:.1%})"
