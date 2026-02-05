"""
Domain Models

Re-exports domain entities for convenience.
Also provides compatibility layer for services.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Re-export core entities
from app.domain.entities import (
    Agent as BaseAgent,
    Task,
    Connection,
    CommunicationGraph,
    GraphExecution
)

from app.domain.value_objects import (
    AgentStatus,
    AgentCapability,
    ConnectionStatus,
    TaskStatus,
    PerformanceMetrics,
    Vector3
)


# ============================================================================
# Compatibility Layer
# ============================================================================

@dataclass
class Agent:
    """
    Agent model with compatibility for services

    Extends base Agent with additional fields needed by services
    """
    id: str
    role: str
    name: str = ""
    backend_type: Optional[str] = None  # e.g., "gpt-4", "claude-3-sonnet"
    current_load: float = 0.0  # 0.0-1.0
    status: str = "idle"  # "idle", "busy", "offline"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure name is set"""
        if not self.name:
            self.name = f"Agent_{self.role}"

    @classmethod
    def from_base(cls, base_agent: BaseAgent):
        """Create from base Agent entity"""
        return cls(
            id=base_agent.id,
            role=base_agent.role,
            name=base_agent.metadata.get('name', f"Agent_{base_agent.role}"),
            backend_type=base_agent.metadata.get('backend_type'),
            current_load=base_agent.metrics.current_load,
            status=base_agent.status.value,
            capabilities=[cap.name for cap in base_agent.capabilities],
            metadata=base_agent.metadata
        )

    def to_base(self) -> BaseAgent:
        """Convert to base Agent entity"""
        caps = [AgentCapability(name=c, category=c, level=1.0) for c in self.capabilities]
        return BaseAgent(
            id=self.id,
            role=self.role,
            capabilities=caps,
            status=AgentStatus(self.status) if self.status in ['idle', 'busy'] else AgentStatus.IDLE,
            metrics=PerformanceMetrics(current_load=self.current_load),
            metadata={
                **self.metadata,
                'name': self.name,
                'backend_type': self.backend_type
            }
        )


@dataclass
class GraphNode:
    """Node in communication graph (simplified)"""
    agent_id: str
    position: int = 0
    metadata: Dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge in communication graph (simplified)"""
    from_agent_id: str
    to_agent_id: str
    weight: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


# Note: CommunicationGraph from entities doesn't have name/description
# Services may need to work with entity directly or wrap it


# Also re-export everything for convenience
__all__ = [
    # Core entities
    'Agent',
    'BaseAgent',
    'Task',
    'Connection',
    'CommunicationGraph',
    'GraphExecution',
    'GraphNode',
    'GraphEdge',
    # Value objects
    'AgentStatus',
    'AgentCapability',
    'ConnectionStatus',
    'TaskStatus',
    'PerformanceMetrics',
    'Vector3',
]
