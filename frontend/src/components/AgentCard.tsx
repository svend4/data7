/**
 * Agent Card Component
 * Displays individual agent information
 */

import { Agent } from '../types'
import './AgentCard.css'

interface AgentCardProps {
  agent: Agent
  onDelete: (agentId: string) => void
}

export function AgentCard({ agent, onDelete }: AgentCardProps) {
  const getStatusClass = (status: string) => {
    return `status-badge status-${status}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="agent-card">
      <div className="agent-card-header">
        <h3 className="agent-role">{agent.role}</h3>
        <span className={getStatusClass(agent.status)}>
          {agent.status.toUpperCase()}
        </span>
      </div>

      <div className="agent-card-body">
        <div className="agent-info-row">
          <span className="info-label">ID:</span>
          <span className="info-value monospace">{agent.id.slice(0, 12)}...</span>
        </div>

        <div className="agent-section">
          <h4 className="section-title">Capabilities</h4>
          <div className="capabilities-list">
            {agent.capabilities.map((cap, idx) => (
              <div key={idx} className="capability-item">
                <span className="capability-name">{cap.name}</span>
                <span className="capability-level">
                  {'⭐'.repeat(cap.level)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="agent-section">
          <h4 className="section-title">Performance Metrics</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-value">
                {(agent.metrics.success_rate * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Success Rate</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">
                {agent.metrics.avg_response_time.toFixed(2)}s
              </div>
              <div className="metric-label">Avg Response</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{agent.metrics.total_tasks}</div>
              <div className="metric-label">Total Tasks</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">
                {(agent.metrics.current_load * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Current Load</div>
            </div>
          </div>
        </div>

        {agent.position && (
          <div className="agent-section">
            <h4 className="section-title">3D Position</h4>
            <div className="position-value monospace">
              ({agent.position.x.toFixed(2)}, {agent.position.y.toFixed(2)},{' '}
              {agent.position.z.toFixed(2)})
            </div>
          </div>
        )}

        <div className="agent-footer">
          <span className="agent-date">
            Created: {formatDate(agent.created_at)}
          </span>
          <button
            className="btn-delete"
            onClick={() => onDelete(agent.id)}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
