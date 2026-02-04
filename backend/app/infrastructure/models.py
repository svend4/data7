"""
SQLAlchemy ORM Models
Database models for all entities based on TECHNICAL_SPEC_PART4_SCHEMAS.md
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class AgentModel(Base):
    """Agent ORM Model"""
    __tablename__ = "agents"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Core fields
    role = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="idle")

    # Metrics
    avg_response_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=1.0)
    total_tasks = Column(Integer, default=0)
    current_load = Column(Float, default=0.0)

    # Position (3D coordinates)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    position_z = Column(Float, nullable=True)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    capabilities = relationship("AgentCapabilityModel", back_populates="agent", cascade="all, delete-orphan")
    tasks_assigned = relationship("TaskModel", back_populates="agent", foreign_keys="TaskModel.assigned_agent_id")

    # Indexes
    __table_args__ = (
        Index("idx_agents_status", "status"),
        Index("idx_agents_role", "role"),
        Index("idx_agents_created_at", "created_at"),
        CheckConstraint("current_load >= 0.0 AND current_load <= 1.0", name="check_load_range"),
        CheckConstraint("success_rate >= 0.0 AND success_rate <= 1.0", name="check_success_rate"),
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, role={self.role}, status={self.status})>"


class AgentCapabilityModel(Base):
    """Agent Capability ORM Model"""
    __tablename__ = "agent_capabilities"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    agent_id = Column(String(255), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)

    # Fields
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    # Relationship
    agent = relationship("AgentModel", back_populates="capabilities")

    # Indexes
    __table_args__ = (
        Index("idx_capabilities_agent", "agent_id"),
        Index("idx_capabilities_category", "category"),
        CheckConstraint("level >= 1 AND level <= 5", name="check_capability_level"),
    )

    def __repr__(self) -> str:
        return f"<Capability(name={self.name}, category={self.category}, level={self.level})>"


class TaskModel(Base):
    """Task ORM Model"""
    __tablename__ = "tasks"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Core fields
    description = Column(Text, nullable=False)
    task_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    priority = Column(Integer, nullable=False, default=5)

    # Assignment
    assigned_agent_id = Column(String(255), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)

    # Result
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("AgentModel", back_populates="tasks_assigned", foreign_keys=[assigned_agent_id])

    # Indexes
    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_type", "task_type"),
        Index("idx_tasks_agent", "assigned_agent_id"),
        Index("idx_tasks_priority", "priority"),
        Index("idx_tasks_created_at", "created_at"),
        CheckConstraint("priority >= 1 AND priority <= 10", name="check_priority_range"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, type={self.task_type}, status={self.status})>"


class ConnectionModel(Base):
    """Connection ORM Model"""
    __tablename__ = "connections"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Agent references
    from_agent_id = Column(String(255), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    to_agent_id = Column(String(255), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)

    # Status
    status = Column(String(20), nullable=False, default="disconnected")

    # Socket allocation
    socket_from = Column(Integer, nullable=True)
    socket_to = Column(Integer, nullable=True)

    # Performance
    bandwidth = Column(Float, nullable=False, default=1.0)
    latency_ms = Column(Float, nullable=False, default=0.0)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    established_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    from_agent = relationship("AgentModel", foreign_keys=[from_agent_id])
    to_agent = relationship("AgentModel", foreign_keys=[to_agent_id])

    # Indexes
    __table_args__ = (
        Index("idx_connections_status", "status"),
        Index("idx_connections_from_agent", "from_agent_id"),
        Index("idx_connections_to_agent", "to_agent_id"),
        Index("idx_connections_sockets", "socket_from", "socket_to"),
        CheckConstraint("bandwidth >= 0.0 AND bandwidth <= 1.0", name="check_bandwidth_range"),
        CheckConstraint("latency_ms >= 0.0", name="check_latency_positive"),
        CheckConstraint("from_agent_id != to_agent_id", name="check_no_self_connection"),
    )

    def __repr__(self) -> str:
        return f"<Connection(id={self.id}, {self.from_agent_id}->{self.to_agent_id})>"


class CommunicationGraphModel(Base):
    """Communication Graph ORM Model"""
    __tablename__ = "communication_graphs"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Root task
    root_task_id = Column(String(255), nullable=False)

    # Graph structure (stored as JSON)
    nodes = Column(JSON, nullable=False, default=[])  # List of agent IDs
    execution_plan = Column(JSON, nullable=False, default=[])  # List of task IDs

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    edges = relationship("GraphEdgeModel", back_populates="graph", cascade="all, delete-orphan")
    executions = relationship("GraphExecutionModel", back_populates="graph", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_graphs_root_task", "root_task_id"),
        Index("idx_graphs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Graph(id={self.id}, root_task={self.root_task_id})>"


class GraphEdgeModel(Base):
    """Graph Edge ORM Model (stores connections in a graph)"""
    __tablename__ = "graph_edges"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    graph_id = Column(String(255), ForeignKey("communication_graphs.id", ondelete="CASCADE"), nullable=False)

    # Connection reference
    connection_id = Column(String(255), ForeignKey("connections.id", ondelete="CASCADE"), nullable=False)

    # Relationship
    graph = relationship("CommunicationGraphModel", back_populates="edges")
    connection = relationship("ConnectionModel")

    # Indexes
    __table_args__ = (
        Index("idx_edges_graph", "graph_id"),
        Index("idx_edges_connection", "connection_id"),
    )


class GraphExecutionModel(Base):
    """Graph Execution ORM Model"""
    __tablename__ = "graph_executions"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Foreign key
    graph_id = Column(String(255), ForeignKey("communication_graphs.id", ondelete="CASCADE"), nullable=False)

    # Status
    status = Column(String(20), nullable=False, default="pending")
    current_step = Column(Integer, nullable=False, default=0)

    # Progress tracking (stored as JSON arrays)
    completed_tasks = Column(JSON, nullable=False, default=[])  # List of task IDs
    failed_tasks = Column(JSON, nullable=False, default=[])  # List of task IDs
    active_connections = Column(JSON, nullable=False, default=[])  # List of connection IDs

    # Results
    results = Column(JSON, nullable=False, default={})  # Dict: task_id -> result

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    graph = relationship("CommunicationGraphModel", back_populates="executions")

    # Indexes
    __table_args__ = (
        Index("idx_executions_graph", "graph_id"),
        Index("idx_executions_status", "status"),
        Index("idx_executions_started_at", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<Execution(id={self.id}, graph={self.graph_id}, status={self.status})>"


# Event log for audit trail (future Phase 3)
class EventLogModel(Base):
    """Event Log ORM Model for audit trail"""
    __tablename__ = "event_logs"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event info
    event_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(255), nullable=False)

    # Event data
    data = Column(JSON, nullable=False, default={})

    # Correlation ID for tracking related events
    correlation_id = Column(String(255), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_events_type", "event_type"),
        Index("idx_events_entity", "entity_type", "entity_id"),
        Index("idx_events_correlation", "correlation_id"),
        Index("idx_events_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Event(type={self.event_type}, entity={self.entity_type}:{self.entity_id})>"
