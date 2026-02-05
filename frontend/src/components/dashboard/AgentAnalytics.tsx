import React, { useEffect, useState } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { axiosClient } from '@/api/client'

interface AgentMetrics {
  agent_id: string
  agent_role: string
  total_tasks_completed: number
  total_tasks_failed: number
  avg_response_time_ms: number
  success_rate: number
  utilization: number
  total_cost_usd: number
  cost_per_task_usd: number
  uptime_percentage: number
}

interface AgentAnalyticsProps {
  timeframe?: '7d' | '30d' | '90d'
}

export const AgentAnalytics: React.FC<AgentAnalyticsProps> = ({
  timeframe = '7d'
}) => {
  const [agents, setAgents] = useState<AgentMetrics[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<keyof AgentMetrics>('success_rate')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const fetchAgentAnalytics = async () => {
    try {
      setLoading(true)
      const response = await axiosClient.get('/analytics/agents', {
        params: { timeframe }
      })
      setAgents(response.data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch agent analytics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgentAnalytics()

    // Refresh every 30 seconds
    const interval = setInterval(fetchAgentAnalytics, 30000)

    return () => clearInterval(interval)
  }, [timeframe])

  const handleSort = (field: keyof AgentMetrics) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  // Sort agents
  const sortedAgents = [...agents].sort((a, b) => {
    const aVal = a[sortBy]
    const bVal = b[sortBy]

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    }

    return sortOrder === 'asc'
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal))
  })

  // Top performers
  const topPerformers = [...agents]
    .filter(a => a.total_tasks_completed > 0)
    .sort((a, b) => b.success_rate - a.success_rate)
    .slice(0, 3)

  if (loading) {
    return (
      <Card>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          Loading agent analytics...
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <div style={{ padding: '20px', color: '#dc3545' }}>
          Error: {error}
        </div>
      </Card>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Performers */}
      {topPerformers.length > 0 && (
        <Card>
          <div style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 600 }}>
              🏆 Top Performers (Last {timeframe})
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              {topPerformers.map((agent, index) => (
                <div
                  key={agent.agent_id}
                  style={{
                    padding: '16px',
                    backgroundColor: index === 0 ? '#fff3cd' : '#f8f9fa',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${index === 0 ? '#ffc107' : index === 1 ? '#c0c0c0' : '#cd7f32'}`
                  }}
                >
                  <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#495057', marginBottom: '4px' }}>
                    {agent.agent_role}
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: '#28a745', marginBottom: '4px' }}>
                    {(agent.success_rate * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '11px', color: '#6c757d' }}>
                    {agent.total_tasks_completed} tasks completed
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Agent Table */}
      <Card>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
              Agent Performance ({agents.length} agents)
            </h3>
            <Button onClick={fetchAgentAnalytics} variant="secondary" size="small">
              Refresh
            </Button>
          </div>

          {agents.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#6c757d' }}>
              No agent data available
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                    <th
                      style={{ padding: '12px', textAlign: 'left', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('agent_role')}
                    >
                      Agent Role {sortBy === 'agent_role' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('total_tasks_completed')}
                    >
                      Tasks {sortBy === 'total_tasks_completed' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('success_rate')}
                    >
                      Success % {sortBy === 'success_rate' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('avg_response_time_ms')}
                    >
                      Avg Time {sortBy === 'avg_response_time_ms' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('utilization')}
                    >
                      Utilization {sortBy === 'utilization' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('total_cost_usd')}
                    >
                      Cost {sortBy === 'total_cost_usd' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                    <th
                      style={{ padding: '12px', textAlign: 'right', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort('uptime_percentage')}
                    >
                      Uptime {sortBy === 'uptime_percentage' && (sortOrder === 'asc' ? '▲' : '▼')}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedAgents.map((agent) => (
                    <tr
                      key={agent.agent_id}
                      style={{
                        borderBottom: '1px solid #dee2e6',
                        transition: 'background-color 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f8f9fa'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent'
                      }}
                    >
                      <td style={{ padding: '12px' }}>
                        <div style={{ fontWeight: 600, color: '#495057' }}>
                          {agent.agent_role}
                        </div>
                        <div style={{ fontSize: '11px', color: '#6c757d' }}>
                          {agent.agent_id.slice(0, 8)}...
                        </div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <div style={{ fontWeight: 600, color: '#495057' }}>
                          {agent.total_tasks_completed}
                        </div>
                        {agent.total_tasks_failed > 0 && (
                          <div style={{ fontSize: '11px', color: '#dc3545' }}>
                            {agent.total_tasks_failed} failed
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <span
                          style={{
                            fontWeight: 600,
                            color:
                              agent.success_rate > 0.95
                                ? '#28a745'
                                : agent.success_rate > 0.8
                                ? '#ffc107'
                                : '#dc3545'
                          }}
                        >
                          {(agent.success_rate * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', color: '#495057' }}>
                        {agent.avg_response_time_ms.toFixed(0)}ms
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <span
                          style={{
                            fontWeight: 600,
                            color:
                              agent.utilization > 0.8
                                ? '#dc3545'
                                : agent.utilization > 0.5
                                ? '#ffc107'
                                : '#28a745'
                          }}
                        >
                          {(agent.utilization * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', color: '#495057' }}>
                        ${agent.total_cost_usd.toFixed(2)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <span
                          style={{
                            fontWeight: 600,
                            color: agent.uptime_percentage > 0.98 ? '#28a745' : '#ffc107'
                          }}
                        >
                          {(agent.uptime_percentage * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
