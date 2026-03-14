/**
 * Create Agent Modal Component
 * Form for registering new agents
 */

import { useState } from 'react'
import { AgentCreateRequest, AgentCapability } from '../types'
import './CreateAgentModal.css'

interface CreateAgentModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: AgentCreateRequest) => void
  isLoading: boolean
}

export function CreateAgentModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: CreateAgentModalProps) {
  const [role, setRole] = useState('')
  const [capabilityName, setCapabilityName] = useState('')
  const [capabilityCategory, setCapabilityCategory] = useState('analysis')
  const [capabilityLevel, setCapabilityLevel] = useState(3)
  const [capabilities, setCapabilities] = useState<AgentCapability[]>([])

  const handleAddCapability = () => {
    if (!capabilityName.trim()) return

    const newCap: AgentCapability = {
      name: capabilityName,
      category: capabilityCategory,
      level: capabilityLevel,
    }

    setCapabilities([...capabilities, newCap])
    setCapabilityName('')
    setCapabilityLevel(3)
  }

  const handleRemoveCapability = (index: number) => {
    setCapabilities(capabilities.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!role.trim() || capabilities.length === 0) {
      alert('Please provide a role and at least one capability')
      return
    }

    onSubmit({
      role,
      capabilities,
      metadata: {},
    })

    // Reset form
    setRole('')
    setCapabilities([])
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Register New Agent</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="role">Agent Role *</label>
            <input
              id="role"
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g., Budget Analyst, Data Processor"
              required
              className="form-input"
            />
          </div>

          <div className="form-section">
            <h3 className="section-heading">Capabilities *</h3>

            <div className="capability-form">
              <div className="form-row">
                <div className="form-group flex-1">
                  <label htmlFor="cap-name">Capability Name</label>
                  <input
                    id="cap-name"
                    type="text"
                    value={capabilityName}
                    onChange={(e) => setCapabilityName(e.target.value)}
                    placeholder="e.g., financial_analysis"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="cap-category">Category</label>
                  <select
                    id="cap-category"
                    value={capabilityCategory}
                    onChange={(e) => setCapabilityCategory(e.target.value)}
                    className="form-select"
                  >
                    <option value="analysis">Analysis</option>
                    <option value="generation">Generation</option>
                    <option value="transformation">Transformation</option>
                    <option value="validation">Validation</option>
                    <option value="optimization">Optimization</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="cap-level">Level (1-5)</label>
                  <input
                    id="cap-level"
                    type="number"
                    min="1"
                    max="5"
                    value={capabilityLevel}
                    onChange={(e) => setCapabilityLevel(parseInt(e.target.value))}
                    className="form-input"
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={handleAddCapability}
                className="btn-add-capability"
                disabled={!capabilityName.trim()}
              >
                + Add Capability
              </button>
            </div>

            {capabilities.length > 0 && (
              <div className="capabilities-preview">
                <h4>Added Capabilities:</h4>
                <ul className="capabilities-list">
                  {capabilities.map((cap, idx) => (
                    <li key={idx} className="capability-preview-item">
                      <span>
                        <strong>{cap.name}</strong> ({cap.category}) {'⭐'.repeat(cap.level)}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveCapability(idx)}
                        className="btn-remove"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading || !role.trim() || capabilities.length === 0}
            >
              {isLoading ? 'Creating...' : 'Create Agent'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
