import React, { useEffect, useState } from 'react'
import { Card } from '../common/Card'
import { axiosClient } from '@/api/client'

interface SystemHealthData {
  timestamp: string
  total_agents: number
  agents_idle: number
  agents_busy: number
  agents_error: number
  agents_offline: number
  total_connections: number
  connections_active: number
  connections_pending: number
  active_executions: number
  avg_response_time_ms: number
  error_rate: number
  cpu_usage: number
  memory_usage: number
}

interface SystemHealthProps {
  refreshInterval?: number // milliseconds
}

export const SystemHealth: React.FC<SystemHealthProps> = ({
  refreshInterval = 5000
}) => {
  const [health, setHealth] = useState<SystemHealthData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHealth = async () => {
    try {
      const response = await axiosClient.get('/analytics/system')
      setHealth(response.data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch system health')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()

    const interval = setInterval(fetchHealth, refreshInterval)

    return () => clearInterval(interval)
  }, [refreshInterval])

  if (loading) {
    return (
      <Card>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          Loading system health...
        </div>
      </Card>
    )
  }

  if (error || !health) {
    return (
      <Card>
        <div style={{ padding: '20px', color: '#dc3545' }}>
          Error: {error || 'No data available'}
        </div>
      </Card>
    )
  }

  // Calculate overall system status
  const getSystemStatus = () => {
    if (health.error_rate > 0.15) return { label: 'Critical', color: '#dc3545' }
    if (health.error_rate > 0.05) return { label: 'Degraded', color: '#ffc107' }
    if (health.agents_error > 0) return { label: 'Warning', color: '#ff9800' }
    return { label: 'Healthy', color: '#28a745' }
  }

  const status = getSystemStatus()

  return (
    <Card>
      <div style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
            System Health
          </h3>
          <div
            style={{
              padding: '6px 16px',
              borderRadius: '16px',
              backgroundColor: status.color,
              color: 'white',
              fontSize: '12px',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}
          >
            {status.label}
          </div>
        </div>

        {/* Agents */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#495057' }}>
            Agents ({health.total_agents} total)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
            <div
              style={{
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #6c757d'
              }}
            >
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#6c757d' }}>
                {health.agents_idle}
              </div>
              <div style={{ fontSize: '12px', color: '#6c757d' }}>Idle</div>
            </div>
            <div
              style={{
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #007bff'
              }}
            >
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#007bff' }}>
                {health.agents_busy}
              </div>
              <div style={{ fontSize: '12px', color: '#007bff' }}>Busy</div>
            </div>
            <div
              style={{
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #dc3545'
              }}
            >
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#dc3545' }}>
                {health.agents_error}
              </div>
              <div style={{ fontSize: '12px', color: '#dc3545' }}>Error</div>
            </div>
            <div
              style={{
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #343a40'
              }}
            >
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#343a40' }}>
                {health.agents_offline}
              </div>
              <div style={{ fontSize: '12px', color: '#343a40' }}>Offline</div>
            </div>
          </div>
        </div>

        {/* Connections */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#495057' }}>
            Connections
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <div
              style={{
                flex: 1,
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #28a745'
              }}
            >
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#28a745' }}>
                {health.connections_active}
              </div>
              <div style={{ fontSize: '12px', color: '#28a745' }}>Active</div>
            </div>
            <div
              style={{
                flex: 1,
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                borderLeft: '4px solid #ffc107'
              }}
            >
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#ffc107' }}>
                {health.connections_pending}
              </div>
              <div style={{ fontSize: '12px', color: '#ffc107' }}>Pending</div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#495057' }}>
            Performance
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
            <div style={{ padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#17a2b8' }}>
                {health.avg_response_time_ms.toFixed(0)}ms
              </div>
              <div style={{ fontSize: '12px', color: '#6c757d' }}>Avg Response Time</div>
            </div>
            <div style={{ padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
              <div
                style={{
                  fontSize: '18px',
                  fontWeight: 700,
                  color: health.error_rate > 0.05 ? '#dc3545' : '#28a745'
                }}
              >
                {(health.error_rate * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '12px', color: '#6c757d' }}>Error Rate</div>
            </div>
          </div>
        </div>

        {/* Active Executions */}
        <div style={{ padding: '12px', backgroundColor: '#e7f3ff', borderRadius: '6px', borderLeft: '4px solid #007bff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '12px', color: '#007bff', fontWeight: 600 }}>
                Active Executions
              </div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#007bff' }}>
                {health.active_executions}
              </div>
            </div>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: '#007bff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '24px'
              }}
            >
              ⚡
            </div>
          </div>
        </div>

        {/* Last Updated */}
        <div style={{ marginTop: '16px', fontSize: '11px', color: '#6c757d', textAlign: 'right' }}>
          Last updated: {new Date(health.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </Card>
  )
}
