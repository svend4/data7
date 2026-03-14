/**
 * Switchboard Statistics Component
 * Displays aggregate stats for all agents
 */

import { useQuery } from '@tanstack/react-query'
import { apiService } from '../services/api'
import './SwitchboardStats.css'

export function SwitchboardStats() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['agent-stats'],
    queryFn: () => apiService.getAgentStats(),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  if (isLoading) {
    return (
      <div className="stats-container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="stats-container">
        <div className="error-message">
          Failed to load statistics
        </div>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="stats-container">
      <h2 className="stats-title">Switchboard Statistics</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_agents}</div>
          <div className="stat-label">Total Agents</div>
        </div>

        <div className="stat-card stat-success">
          <div className="stat-value">{stats.idle_agents}</div>
          <div className="stat-label">Idle</div>
        </div>

        <div className="stat-card stat-warning">
          <div className="stat-value">{stats.busy_agents}</div>
          <div className="stat-label">Busy</div>
        </div>

        <div className="stat-card stat-error">
          <div className="stat-value">{stats.offline_agents}</div>
          <div className="stat-label">Offline</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">
            {(stats.avg_success_rate * 100).toFixed(1)}%
          </div>
          <div className="stat-label">Avg Success Rate</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">
            {stats.avg_response_time.toFixed(2)}s
          </div>
          <div className="stat-label">Avg Response Time</div>
        </div>
      </div>
    </div>
  )
}
