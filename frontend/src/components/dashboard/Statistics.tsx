import React from 'react'
import { Card } from '../common/Card'
import { useTasksStore } from '@/store/tasks'
import { useAgentsStore } from '@/store/agents'
import { useConnectionsStore } from '@/store/connections'

export const Statistics: React.FC = () => {
  const tasks = useTasksStore((state) => state.tasks)
  const agents = useAgentsStore((state) => state.agents)
  const connections = useConnectionsStore((state) => state.connections)

  const taskStats = {
    total: tasks.length,
    pending: tasks.filter((t) => t.status === 'pending').length,
    running: tasks.filter((t) => t.status === 'running').length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    failed: tasks.filter((t) => t.status === 'failed').length,
  }

  const agentStats = {
    total: agents.length,
    idle: agents.filter((a) => a.status === 'idle').length,
    busy: agents.filter((a) => a.status === 'busy').length,
    error: agents.filter((a) => a.status === 'error').length,
    offline: agents.filter((a) => a.status === 'offline').length,
  }

  const connectionStats = {
    total: connections.length,
    disconnected: connections.filter((c) => c.status === 'disconnected').length,
    connected: connections.filter((c) => c.status === 'connected').length,
    transmitting: connections.filter((c) => c.status === 'transmitting').length,
  }

  const StatItem: React.FC<{ label: string; value: number; color?: string }> = ({
    label,
    value,
    color = '#495057',
  }) => (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '32px', fontWeight: 700, color, marginBottom: '8px' }}>
        {value}
      </div>
      <div style={{ fontSize: '14px', color: '#6c757d', textTransform: 'uppercase' }}>
        {label}
      </div>
    </div>
  )

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
      {/* Task Statistics */}
      <Card title="📋 Tasks">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <StatItem label="Total" value={taskStats.total} color="#495057" />
          <StatItem label="Running" value={taskStats.running} color="#007bff" />
          <StatItem label="Completed" value={taskStats.completed} color="#28a745" />
          <StatItem label="Pending" value={taskStats.pending} color="#ffc107" />
          <StatItem label="Failed" value={taskStats.failed} color="#dc3545" />
        </div>
      </Card>

      {/* Agent Statistics */}
      <Card title="🤖 Agents">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <StatItem label="Total" value={agentStats.total} color="#495057" />
          <StatItem label="Idle" value={agentStats.idle} color="#6c757d" />
          <StatItem label="Busy" value={agentStats.busy} color="#007bff" />
          <StatItem label="Error" value={agentStats.error} color="#dc3545" />
          <StatItem label="Offline" value={agentStats.offline} color="#343a40" />
        </div>
      </Card>

      {/* Connection Statistics */}
      <Card title="🔌 Connections">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <StatItem label="Total" value={connectionStats.total} color="#495057" />
          <StatItem label="Connected" value={connectionStats.connected} color="#28a745" />
          <StatItem label="Transmitting" value={connectionStats.transmitting} color="#17a2b8" />
          <StatItem label="Disconnected" value={connectionStats.disconnected} color="#6c757d" />
        </div>
      </Card>
    </div>
  )
}
