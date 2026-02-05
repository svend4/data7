import React, { useState } from 'react'
import { Button } from '../common/Button'
import { useConnectionsStore } from '@/store/connections'
import { useAgentsStore } from '@/store/agents'

interface ConnectionFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({ onSuccess, onCancel }) => {
  const { createConnection, establishConnection } = useConnectionsStore()
  const agents = useAgentsStore((state) => state.agents)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    from_agent_id: '',
    to_agent_id: '',
    protocol: 'TCP',
    auto_establish: true,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.from_agent_id === formData.to_agent_id) {
      alert('Cannot connect agent to itself')
      return
    }

    setLoading(true)

    try {
      await createConnection({
        from_agent_id: formData.from_agent_id,
        to_agent_id: formData.to_agent_id,
        protocol: formData.protocol,
      })

      // Note: Connection will be created and if auto_establish is true,
      // the backend should handle establishment automatically
      // For MVP, we'll let the user manually establish via the UI

      // Reset form
      setFormData({
        from_agent_id: '',
        to_agent_id: '',
        protocol: 'TCP',
        auto_establish: true,
      })

      onSuccess?.()
    } catch (error) {
      console.error('Failed to create connection:', error)
      alert('Failed to create connection')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '14px',
    marginTop: '4px',
  }

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '12px',
    fontSize: '14px',
    fontWeight: 500,
  }

  return (
    <form onSubmit={handleSubmit}>
      {agents.length === 0 ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>
          <p>No agents available. Create agents first before establishing connections.</p>
        </div>
      ) : (
        <>
          <label style={labelStyle}>
            From Agent *
            <select
              style={inputStyle}
              value={formData.from_agent_id}
              onChange={(e) => setFormData({ ...formData, from_agent_id: e.target.value })}
              required
            >
              <option value="">Select agent...</option>
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.role} ({agent.id.slice(0, 8)}...)
                </option>
              ))}
            </select>
          </label>

          <label style={labelStyle}>
            To Agent *
            <select
              style={inputStyle}
              value={formData.to_agent_id}
              onChange={(e) => setFormData({ ...formData, to_agent_id: e.target.value })}
              required
            >
              <option value="">Select agent...</option>
              {agents
                .filter((agent) => agent.id !== formData.from_agent_id)
                .map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.role} ({agent.id.slice(0, 8)}...)
                  </option>
                ))}
            </select>
          </label>

          <label style={labelStyle}>
            Protocol *
            <select
              style={inputStyle}
              value={formData.protocol}
              onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
              required
            >
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="HTTP">HTTP</option>
              <option value="WebSocket">WebSocket</option>
              <option value="gRPC">gRPC</option>
            </select>
          </label>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
              <input
                type="checkbox"
                checked={formData.auto_establish}
                onChange={(e) => setFormData({ ...formData, auto_establish: e.target.checked })}
              />
              Auto-establish connection (allocate sockets immediately)
            </label>
          </div>

          <div style={{ display: 'flex', gap: '8px', marginTop: '20px' }}>
            <Button type="submit" variant="primary" loading={loading} style={{ flex: 1 }}>
              Create Connection
            </Button>
            {onCancel && (
              <Button type="button" variant="secondary" onClick={onCancel} style={{ flex: 1 }}>
                Cancel
              </Button>
            )}
          </div>
        </>
      )}
    </form>
  )
}
