/**
 * ActiveAlerts Component
 *
 * Displays active system alerts with severity indicators and actions
 *
 * Features:
 * - Real-time alert list with auto-refresh
 * - Severity color coding (info/warning/error/critical)
 * - Alert acknowledgment and resolution
 * - Detailed alert information
 * - Filter by severity and status
 */

import React, { useState, useEffect } from 'react'
import { axiosClient } from '@/lib/axios'

interface Alert {
  id: string
  rule_id: string
  rule_name: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  status: 'active' | 'acknowledged' | 'resolved' | 'suppressed'
  message: string
  details: {
    conditions: Array<{
      metric: string
      threshold: number
      current_value: number
      operator: string
    }>
    all_metrics: Record<string, number>
    tags: string[]
  }
  triggered_at: string
  acknowledged_at?: string
  acknowledged_by?: string
  resolved_at?: string
  resolved_by?: string
  notification_sent: boolean
  notification_channels: string[]
}

interface ActiveAlertsProps {
  refreshInterval?: number  // milliseconds
  maxAlerts?: number
}

export const ActiveAlerts: React.FC<ActiveAlertsProps> = ({
  refreshInterval = 10000,
  maxAlerts = 20
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('active')

  const fetchAlerts = async () => {
    try {
      const params: any = { limit: maxAlerts }
      if (filterStatus !== 'all') params.status = filterStatus
      if (filterSeverity !== 'all') params.severity = filterSeverity

      const response = await axiosClient.get<Alert[]>('/alerts', { params })
      setAlerts(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch alerts')
      console.error('Error fetching alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, refreshInterval)
    return () => clearInterval(interval)
  }, [refreshInterval, filterSeverity, filterStatus])

  const handleAcknowledge = async (alertId: string) => {
    try {
      await axiosClient.post(`/alerts/${alertId}/acknowledge`, {
        user: 'operator'  // In production, get from auth context
      })
      fetchAlerts()
    } catch (err) {
      console.error('Error acknowledging alert:', err)
    }
  }

  const handleResolve = async (alertId: string) => {
    try {
      await axiosClient.post(`/alerts/${alertId}/resolve`, {
        user: 'operator'  // In production, get from auth context
      })
      fetchAlerts()
    } catch (err) {
      console.error('Error resolving alert:', err)
    }
  }

  const handleSuppress = async (alertId: string) => {
    try {
      await axiosClient.post(`/alerts/${alertId}/suppress`)
      fetchAlerts()
    } catch (err) {
      console.error('Error suppressing alert:', err)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#8b0000'
      case 'error': return '#dc3545'
      case 'warning': return '#ff9800'
      case 'info': return '#17a2b8'
      default: return '#6c757d'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🚨'
      case 'error': return '❌'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      default: return '📢'
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active': return '#dc3545'
      case 'acknowledged': return '#ffc107'
      case 'resolved': return '#28a745'
      case 'suppressed': return '#6c757d'
      default: return '#6c757d'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return `${Math.floor(diffMins / 1440)}d ago`
  }

  if (loading) {
    return (
      <div style={{
        padding: '24px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        Loading alerts...
      </div>
    )
  }

  return (
    <div>
      {/* Header with filters */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
          🚨 Active Alerts
        </h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          {/* Status filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={{
              padding: '6px 12px',
              fontSize: '13px',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>

          {/* Severity filter */}
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            style={{
              padding: '6px 12px',
              fontSize: '13px',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
        </div>
      </div>

      {/* Alerts list */}
      {error ? (
        <div style={{
          padding: '16px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '8px',
          marginBottom: '16px'
        }}>
          {error}
        </div>
      ) : null}

      {alerts.length === 0 ? (
        <div style={{
          padding: '48px 24px',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center',
          color: '#6c757d'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
          <div style={{ fontSize: '18px', fontWeight: 600 }}>No alerts</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>
            System is operating normally
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {alerts.map((alert) => (
            <div
              key={alert.id}
              style={{
                padding: '16px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => setSelectedAlert(selectedAlert?.id === alert.id ? null : alert)}
            >
              {/* Alert header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '20px' }}>{getSeverityIcon(alert.severity)}</span>
                    <span style={{
                      fontSize: '14px',
                      fontWeight: 700,
                      color: getSeverityColor(alert.severity),
                      textTransform: 'uppercase'
                    }}>
                      {alert.severity}
                    </span>
                    <span style={{
                      padding: '2px 8px',
                      fontSize: '11px',
                      fontWeight: 600,
                      backgroundColor: getStatusBadgeColor(alert.status),
                      color: 'white',
                      borderRadius: '4px',
                      textTransform: 'uppercase'
                    }}>
                      {alert.status}
                    </span>
                    <span style={{ fontSize: '12px', color: '#6c757d' }}>
                      {formatTimestamp(alert.triggered_at)}
                    </span>
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>
                    {alert.rule_name}
                  </div>
                  <div style={{ fontSize: '13px', color: '#495057' }}>
                    {alert.message}
                  </div>
                </div>

                {/* Action buttons */}
                {alert.status === 'active' && (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleAcknowledge(alert.id)
                      }}
                      style={{
                        padding: '6px 12px',
                        fontSize: '12px',
                        fontWeight: 600,
                        border: 'none',
                        borderRadius: '4px',
                        backgroundColor: '#ffc107',
                        color: 'white',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      Acknowledge
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleResolve(alert.id)
                      }}
                      style={{
                        padding: '6px 12px',
                        fontSize: '12px',
                        fontWeight: 600,
                        border: 'none',
                        borderRadius: '4px',
                        backgroundColor: '#28a745',
                        color: 'white',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      Resolve
                    </button>
                  </div>
                )}
                {alert.status === 'acknowledged' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleResolve(alert.id)
                    }}
                    style={{
                      padding: '6px 12px',
                      fontSize: '12px',
                      fontWeight: 600,
                      border: 'none',
                      borderRadius: '4px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    Resolve
                  </button>
                )}
              </div>

              {/* Alert details (expanded) */}
              {selectedAlert?.id === alert.id && (
                <div style={{
                  marginTop: '16px',
                  paddingTop: '16px',
                  borderTop: '1px solid #e9ecef'
                }}>
                  <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>
                    Triggered Conditions:
                  </div>
                  {alert.details.conditions.map((condition, idx) => (
                    <div key={idx} style={{
                      padding: '8px 12px',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '4px',
                      fontSize: '12px',
                      marginBottom: '4px',
                      fontFamily: 'monospace'
                    }}>
                      {condition.metric} {condition.operator} {condition.threshold}
                      <span style={{ color: '#dc3545', marginLeft: '8px' }}>
                        (current: {condition.current_value.toFixed(2)})
                      </span>
                    </div>
                  ))}

                  {alert.details.tags.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>
                        Tags:
                      </div>
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {alert.details.tags.map((tag) => (
                          <span
                            key={tag}
                            style={{
                              padding: '2px 8px',
                              fontSize: '11px',
                              backgroundColor: '#e9ecef',
                              color: '#495057',
                              borderRadius: '4px'
                            }}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {alert.notification_channels.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>
                        Notifications sent via:
                      </div>
                      <div style={{ fontSize: '12px', color: '#6c757d' }}>
                        {alert.notification_channels.join(', ')}
                      </div>
                    </div>
                  )}

                  {alert.acknowledged_by && (
                    <div style={{ marginTop: '12px', fontSize: '12px', color: '#6c757d' }}>
                      Acknowledged by {alert.acknowledged_by} at{' '}
                      {new Date(alert.acknowledged_at!).toLocaleString()}
                    </div>
                  )}

                  {alert.resolved_by && (
                    <div style={{ marginTop: '12px', fontSize: '12px', color: '#6c757d' }}>
                      Resolved by {alert.resolved_by} at{' '}
                      {new Date(alert.resolved_at!).toLocaleString()}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
