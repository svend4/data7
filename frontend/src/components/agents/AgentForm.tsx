import React, { useState } from 'react'
import { Button } from '../common/Button'
import { useAgentsStore } from '@/store/agents'
import { AgentCapability } from '@/types/agent'

interface AgentFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export const AgentForm: React.FC<AgentFormProps> = ({ onSuccess, onCancel }) => {
  const { createAgent } = useAgentsStore()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    role: '',
    capabilities: [] as AgentCapability[],
    position_x: 0,
    position_y: 0,
  })
  const [newCapability, setNewCapability] = useState({ name: '', level: 1, description: '' })

  const handleAddCapability = () => {
    if (newCapability.name) {
      setFormData({
        ...formData,
        capabilities: [
          ...formData.capabilities,
          {
            name: newCapability.name,
            level: newCapability.level,
            description: newCapability.description || undefined,
          },
        ],
      })
      setNewCapability({ name: '', level: 1, description: '' })
    }
  }

  const handleRemoveCapability = (index: number) => {
    setFormData({
      ...formData,
      capabilities: formData.capabilities.filter((_, i) => i !== index),
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await createAgent({
        role: formData.role,
        capabilities: formData.capabilities,
        position_x: formData.position_x || undefined,
        position_y: formData.position_y || undefined,
      })

      // Reset form
      setFormData({
        role: '',
        capabilities: [],
        position_x: 0,
        position_y: 0,
      })

      onSuccess?.()
    } catch (error) {
      console.error('Failed to create agent:', error)
      alert('Failed to create agent')
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
      <label style={labelStyle}>
        Role *
        <input
          type="text"
          style={inputStyle}
          value={formData.role}
          onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          placeholder="e.g., Data Analyst, Task Coordinator"
          required
        />
      </label>

      <div style={{ marginBottom: '12px' }}>
        <label style={{ fontSize: '14px', fontWeight: 500, display: 'block', marginBottom: '8px' }}>
          Capabilities
        </label>
        
        {formData.capabilities.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            {formData.capabilities.map((cap, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '4px',
                  marginBottom: '4px',
                }}
              >
                <span style={{ flex: 1, fontSize: '14px' }}>
                  {cap.name} (Level {cap.level})
                  {cap.description && ` - ${cap.description}`}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveCapability(index)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#dc3545',
                    cursor: 'pointer',
                    fontSize: '18px',
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '8px', marginBottom: '8px' }}>
          <input
            type="text"
            style={inputStyle}
            value={newCapability.name}
            onChange={(e) => setNewCapability({ ...newCapability, name: e.target.value })}
            placeholder="Capability name"
          />
          <input
            type="number"
            style={inputStyle}
            value={newCapability.level}
            onChange={(e) =>
              setNewCapability({ ...newCapability, level: parseInt(e.target.value) || 1 })
            }
            min="1"
            max="10"
            placeholder="Level"
          />
        </div>
        <input
          type="text"
          style={{ ...inputStyle, marginBottom: '8px' }}
          value={newCapability.description}
          onChange={(e) => setNewCapability({ ...newCapability, description: e.target.value })}
          placeholder="Description (optional)"
        />
        <Button type="button" variant="secondary" size="small" onClick={handleAddCapability}>
          Add Capability
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <label style={labelStyle}>
          Position X (optional)
          <input
            type="number"
            style={inputStyle}
            value={formData.position_x}
            onChange={(e) =>
              setFormData({ ...formData, position_x: parseInt(e.target.value) || 0 })
            }
            placeholder="0"
          />
        </label>

        <label style={labelStyle}>
          Position Y (optional)
          <input
            type="number"
            style={inputStyle}
            value={formData.position_y}
            onChange={(e) =>
              setFormData({ ...formData, position_y: parseInt(e.target.value) || 0 })
            }
            placeholder="0"
          />
        </label>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginTop: '20px' }}>
        <Button type="submit" variant="primary" loading={loading} style={{ flex: 1 }}>
          Create Agent
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} style={{ flex: 1 }}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
