import React, { useState } from 'react'
import { SystemHealth } from '@/components/dashboard/SystemHealth'
import { PerformanceMetrics } from '@/components/dashboard/PerformanceMetrics'
import { AgentAnalytics } from '@/components/dashboard/AgentAnalytics'

type TimeframeOption = '1h' | '24h' | '7d' | '30d'

export const MonitoringDashboard: React.FC = () => {
  const [performanceTimeframe, setPerformanceTimeframe] = useState<TimeframeOption>('24h')
  const [agentTimeframe, setAgentTimeframe] = useState<'7d' | '30d' | '90d'>('7d')

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* Header */}
      <div
        style={{
          backgroundColor: '#1a1a1a',
          color: '#d4af37',
          padding: '24px 32px',
          borderBottom: '4px solid #d4af37'
        }}
      >
        <h1 style={{ margin: '0 0 8px 0', fontSize: '32px', fontWeight: 700 }}>
          📊 Monitoring Dashboard
        </h1>
        <p style={{ margin: 0, fontSize: '14px', color: '#c0c0c0' }}>
          Real-time system health, performance metrics, and analytics
        </p>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '32px' }}>
        {/* Row 1: System Health + Performance Metrics */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '400px 1fr',
            gap: '24px',
            marginBottom: '24px'
          }}
        >
          {/* System Health Widget */}
          <div>
            <SystemHealth refreshInterval={5000} />
          </div>

          {/* Performance Metrics Chart */}
          <div>
            <div
              style={{
                marginBottom: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
                Performance Trends
              </h2>
              <div style={{ display: 'flex', gap: '8px' }}>
                {(['1h', '24h', '7d', '30d'] as TimeframeOption[]).map((tf) => (
                  <button
                    key={tf}
                    onClick={() => setPerformanceTimeframe(tf)}
                    style={{
                      padding: '6px 12px',
                      fontSize: '12px',
                      fontWeight: 600,
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      backgroundColor:
                        performanceTimeframe === tf ? '#007bff' : '#e9ecef',
                      color: performanceTimeframe === tf ? 'white' : '#495057',
                      transition: 'all 0.2s'
                    }}
                  >
                    {tf.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <PerformanceMetrics
              timeframe={performanceTimeframe}
              metric="execution_count"
            />
          </div>
        </div>

        {/* Row 2: Agent Analytics */}
        <div style={{ marginBottom: '24px' }}>
          <div
            style={{
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
              Agent Performance
            </h2>
            <div style={{ display: 'flex', gap: '8px' }}>
              {(['7d', '30d', '90d'] as ('7d' | '30d' | '90d')[]).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setAgentTimeframe(tf)}
                  style={{
                    padding: '6px 12px',
                    fontSize: '12px',
                    fontWeight: 600,
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor:
                      agentTimeframe === tf ? '#007bff' : '#e9ecef',
                    color: agentTimeframe === tf ? 'white' : '#495057',
                    transition: 'all 0.2s'
                  }}
                >
                  {tf.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          <AgentAnalytics timeframe={agentTimeframe} />
        </div>

        {/* Row 3: Quick Actions & Info */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '24px'
          }}
        >
          {/* Quick Actions */}
          <div
            style={{
              padding: '24px',
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600 }}>
              ⚡ Quick Actions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => window.location.href = '/api/docs'}
                style={{
                  padding: '10px 16px',
                  fontSize: '14px',
                  fontWeight: 500,
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa'
                  e.currentTarget.style.borderColor = '#007bff'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white'
                  e.currentTarget.style.borderColor = '#dee2e6'
                }}
              >
                📖 View API Documentation
              </button>
              <button
                onClick={() => {
                  window.open('/api/analytics/summary', '_blank')
                }}
                style={{
                  padding: '10px 16px',
                  fontSize: '14px',
                  fontWeight: 500,
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa'
                  e.currentTarget.style.borderColor = '#007bff'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white'
                  e.currentTarget.style.borderColor = '#dee2e6'
                }}
              >
                📊 Export Analytics Summary
              </button>
              <button
                onClick={() => window.location.href = '/'}
                style={{
                  padding: '10px 16px',
                  fontSize: '14px',
                  fontWeight: 500,
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa'
                  e.currentTarget.style.borderColor = '#007bff'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white'
                  e.currentTarget.style.borderColor = '#dee2e6'
                }}
              >
                🏠 Back to Main Dashboard
              </button>
            </div>
          </div>

          {/* System Info */}
          <div
            style={{
              padding: '24px',
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600 }}>
              ℹ️ System Information
            </h3>
            <div style={{ fontSize: '14px', color: '#6c757d' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Version:</strong> 1.0.0
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Environment:</strong> Development
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>API:</strong>{' '}
                <a
                  href="/api/docs"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  /api/docs
                </a>
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>WebSocket:</strong>{' '}
                <span style={{ color: '#28a745', fontWeight: 600 }}>Connected</span>
              </div>
              <div>
                <strong>Data Refresh:</strong> 5-30s
              </div>
            </div>
          </div>

          {/* Help & Resources */}
          <div
            style={{
              padding: '24px',
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600 }}>
              📚 Resources
            </h3>
            <div style={{ fontSize: '14px', color: '#6c757d', lineHeight: '1.8' }}>
              <div style={{ marginBottom: '8px' }}>
                • <strong>Optimization:</strong>{' '}
                <a
                  href="/api/optimization/strategies"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  View strategies
                </a>
              </div>
              <div style={{ marginBottom: '8px' }}>
                • <strong>Analytics:</strong>{' '}
                <a
                  href="/api/docs#/analytics"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  API endpoints
                </a>
              </div>
              <div style={{ marginBottom: '8px' }}>
                • <strong>Metrics:</strong> Real-time data
              </div>
              <div>
                • <strong>Forecasting:</strong> 7-30 day horizon
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div
          style={{
            marginTop: '32px',
            padding: '16px',
            backgroundColor: '#e7f3ff',
            borderRadius: '8px',
            borderLeft: '4px solid #007bff',
            fontSize: '13px',
            color: '#004085'
          }}
        >
          <strong>💡 Pro Tip:</strong> Use the timeframe selectors above to adjust the
          date range for performance metrics and agent analytics. Data refreshes
          automatically every 5-30 seconds depending on the widget.
        </div>
      </div>
    </div>
  )
}
