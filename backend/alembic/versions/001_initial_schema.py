"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-02-04 23:00:00

Creates all tables for the switchboard meta-orchestrator system:
- agents (with capabilities)
- tasks
- connections
- communication_graphs (with edges and executions)
- event_logs (for audit trail)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables"""

    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='idle'),
        sa.Column('avg_response_time', sa.Float(), server_default='0.0'),
        sa.Column('success_rate', sa.Float(), server_default='1.0'),
        sa.Column('total_tasks', sa.Integer(), server_default='0'),
        sa.Column('current_load', sa.Float(), server_default='0.0'),
        sa.Column('position_x', sa.Float(), nullable=True),
        sa.Column('position_y', sa.Float(), nullable=True),
        sa.Column('position_z', sa.Float(), nullable=True),
        sa.Column('metadata', JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('current_load >= 0.0 AND current_load <= 1.0', name='check_load_range'),
        sa.CheckConstraint('success_rate >= 0.0 AND success_rate <= 1.0', name='check_success_rate'),
    )

    op.create_index('idx_agents_status', 'agents', ['status'])
    op.create_index('idx_agents_role', 'agents', ['role'])
    op.create_index('idx_agents_created_at', 'agents', ['created_at'])

    # Create agent_capabilities table
    op.create_table(
        'agent_capabilities',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('agent_id', sa.String(255), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.CheckConstraint('level >= 1 AND level <= 5', name='check_capability_level'),
    )

    op.create_index('idx_capabilities_agent', 'agent_capabilities', ['agent_id'])
    op.create_index('idx_capabilities_category', 'agent_capabilities', ['category'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('assigned_agent_id', sa.String(255), sa.ForeignKey('agents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('result', JSON, nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('metadata', JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('priority >= 1 AND priority <= 10', name='check_priority_range'),
    )

    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_type', 'tasks', ['task_type'])
    op.create_index('idx_tasks_agent', 'tasks', ['assigned_agent_id'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])

    # Create connections table
    op.create_table(
        'connections',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('from_agent_id', sa.String(255), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('to_agent_id', sa.String(255), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='disconnected'),
        sa.Column('socket_from', sa.Integer(), nullable=True),
        sa.Column('socket_to', sa.Integer(), nullable=True),
        sa.Column('bandwidth', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('metadata', JSON, server_default='{}'),
        sa.Column('established_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('bandwidth >= 0.0 AND bandwidth <= 1.0', name='check_bandwidth_range'),
        sa.CheckConstraint('latency_ms >= 0.0', name='check_latency_positive'),
        sa.CheckConstraint('from_agent_id != to_agent_id', name='check_no_self_connection'),
    )

    op.create_index('idx_connections_status', 'connections', ['status'])
    op.create_index('idx_connections_from_agent', 'connections', ['from_agent_id'])
    op.create_index('idx_connections_to_agent', 'connections', ['to_agent_id'])
    op.create_index('idx_connections_sockets', 'connections', ['socket_from', 'socket_to'])

    # Create communication_graphs table
    op.create_table(
        'communication_graphs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('root_task_id', sa.String(255), nullable=False),
        sa.Column('nodes', JSON, nullable=False, server_default='[]'),
        sa.Column('execution_plan', JSON, nullable=False, server_default='[]'),
        sa.Column('metadata', JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    op.create_index('idx_graphs_root_task', 'communication_graphs', ['root_task_id'])
    op.create_index('idx_graphs_created_at', 'communication_graphs', ['created_at'])

    # Create graph_edges table
    op.create_table(
        'graph_edges',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('graph_id', sa.String(255), sa.ForeignKey('communication_graphs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connection_id', sa.String(255), sa.ForeignKey('connections.id', ondelete='CASCADE'), nullable=False),
    )

    op.create_index('idx_edges_graph', 'graph_edges', ['graph_id'])
    op.create_index('idx_edges_connection', 'graph_edges', ['connection_id'])

    # Create graph_executions table
    op.create_table(
        'graph_executions',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('graph_id', sa.String(255), sa.ForeignKey('communication_graphs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_tasks', JSON, nullable=False, server_default='[]'),
        sa.Column('failed_tasks', JSON, nullable=False, server_default='[]'),
        sa.Column('active_connections', JSON, nullable=False, server_default='[]'),
        sa.Column('results', JSON, nullable=False, server_default='{}'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_index('idx_executions_graph', 'graph_executions', ['graph_id'])
    op.create_index('idx_executions_status', 'graph_executions', ['status'])
    op.create_index('idx_executions_started_at', 'graph_executions', ['started_at'])

    # Create event_logs table (for future audit trail)
    op.create_table(
        'event_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('data', JSON, nullable=False, server_default='{}'),
        sa.Column('correlation_id', sa.String(255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    op.create_index('idx_events_type', 'event_logs', ['event_type'])
    op.create_index('idx_events_entity', 'event_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_events_correlation', 'event_logs', ['correlation_id'])
    op.create_index('idx_events_timestamp', 'event_logs', ['timestamp'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('event_logs')
    op.drop_table('graph_executions')
    op.drop_table('graph_edges')
    op.drop_table('communication_graphs')
    op.drop_table('connections')
    op.drop_table('tasks')
    op.drop_table('agent_capabilities')
    op.drop_table('agents')
