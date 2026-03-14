import React, { useEffect, useState } from 'react'
import { Card } from '../common/Card'
import { axiosClient } from '@/api/client'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

interface TrendData {
  metric_name: string
  timeframe_start: string
  timeframe_end: string
  granularity: string
  data_points: Array<{
    timestamp: string
    value: number
  }>
  trend_direction: string
  growth_rate: number
  anomalies: Array<{
    timestamp: string
    value: number
    reason: string
  }>
}

interface PerformanceMetricsProps {
  timeframe: '1h' | '24h' | '7d' | '30d'
  metric?: 'execution_count' | 'success_rate' | 'response_time'
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  timeframe,
  metric = 'execution_count'
}) => {
  const [trendData, setTrendData] = useState<TrendData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTrend = async () => {
    try {
      setLoading(true)

      // Map timeframe to granularity
      let granularity = 'hour'
      if (timeframe === '7d' || timeframe === '30d') {
        granularity = 'day'
      }

      const response = await axiosClient.get(`/analytics/trends/${metric}`, {
        params: {
          timeframe,
          granularity
        }
      })

      setTrendData(response.data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch trend data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTrend()

    // Refresh every 30 seconds
    const interval = setInterval(fetchTrend, 30000)

    return () => clearInterval(interval)
  }, [timeframe, metric])

  if (loading) {
    return (
      <Card>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          Loading performance metrics...
        </div>
      </Card>
    )
  }

  if (error || !trendData) {
    return (
      <Card>
        <div style={{ padding: '20px', color: '#dc3545' }}>
          Error: {error || 'No data available'}
        </div>
      </Card>
    )
  }

  // Format data for chart
  const chartData = trendData.data_points.map(point => ({
    time: new Date(point.timestamp).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: timeframe === '1h' || timeframe === '24h' ? '2-digit' : undefined,
      minute: timeframe === '1h' ? '2-digit' : undefined
    }),
    value: point.value
  }))

  // Trend indicator
  const getTrendIndicator = () => {
    if (trendData.trend_direction === 'up') {
      return {
        icon: '📈',
        color: '#28a745',
        label: `+${trendData.growth_rate.toFixed(1)}%`
      }
    } else if (trendData.trend_direction === 'down') {
      return {
        icon: '📉',
        color: '#dc3545',
        label: `${trendData.growth_rate.toFixed(1)}%`
      }
    } else {
      return {
        icon: '➡️',
        color: '#6c757d',
        label: 'Stable'
      }
    }
  }

  const trend = getTrendIndicator()

  // Metric display name
  const metricName = metric === 'execution_count'
    ? 'Execution Count'
    : metric === 'success_rate'
    ? 'Success Rate'
    : 'Response Time'

  return (
    <Card>
      <div style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
              {metricName}
            </h3>
            <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
              Last {timeframe}
            </div>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              borderRadius: '8px',
              backgroundColor: '#f8f9fa'
            }}
          >
            <span style={{ fontSize: '20px' }}>{trend.icon}</span>
            <span style={{ fontSize: '16px', fontWeight: 600, color: trend.color }}>
              {trend.label}
            </span>
          </div>
        </div>

        {/* Chart */}
        <div style={{ width: '100%', height: '300px' }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
              <XAxis
                dataKey="time"
                stroke="#6c757d"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#6c757d"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '6px',
                  color: 'white'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                name={metricName}
                stroke="#007bff"
                strokeWidth={2}
                dot={{ fill: '#007bff', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Anomalies */}
        {trendData.anomalies.length > 0 && (
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff3cd', borderRadius: '6px', borderLeft: '4px solid #ffc107' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#856404', marginBottom: '8px' }}>
              ⚠️ {trendData.anomalies.length} Anomal{trendData.anomalies.length > 1 ? 'ies' : 'y'} Detected
            </div>
            {trendData.anomalies.slice(0, 3).map((anomaly, i) => (
              <div key={i} style={{ fontSize: '11px', color: '#856404', marginBottom: '4px' }}>
                • {new Date(anomaly.timestamp).toLocaleString()}: {anomaly.reason} (value: {anomaly.value.toFixed(2)})
              </div>
            ))}
          </div>
        )}

        {/* Stats */}
        <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
          <div style={{ padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
            <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>
              Data Points
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#495057' }}>
              {trendData.data_points.length}
            </div>
          </div>
          <div style={{ padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
            <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>
              Trend
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: trend.color }}>
              {trendData.trend_direction.toUpperCase()}
            </div>
          </div>
          <div style={{ padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
            <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>
              Granularity
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#495057' }}>
              {trendData.granularity}
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
