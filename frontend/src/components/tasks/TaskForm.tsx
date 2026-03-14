import React, { useState } from 'react'
import { Button } from '../common/Button'
import { useTasksStore } from '@/store/tasks'

interface TaskFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export const TaskForm: React.FC<TaskFormProps> = ({ onSuccess, onCancel }) => {
  const { createTask } = useTasksStore()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    description: '',
    task_type: 'analysis',
    priority: 1,
    agent_id: '',
    estimated_duration: 0,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await createTask({
        description: formData.description,
        task_type: formData.task_type,
        priority: formData.priority,
        agent_id: formData.agent_id || undefined,
        estimated_duration: formData.estimated_duration || undefined,
      })

      // Reset form
      setFormData({
        description: '',
        task_type: 'analysis',
        priority: 1,
        agent_id: '',
        estimated_duration: 0,
      })

      onSuccess?.()
    } catch (error) {
      console.error('Failed to create task:', error)
      alert('Failed to create task')
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
        Description *
        <input
          type="text"
          style={inputStyle}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Enter task description"
          required
        />
      </label>

      <label style={labelStyle}>
        Task Type *
        <select
          style={inputStyle}
          value={formData.task_type}
          onChange={(e) => setFormData({ ...formData, task_type: e.target.value })}
          required
        >
          <option value="analysis">Analysis</option>
          <option value="processing">Processing</option>
          <option value="generation">Generation</option>
          <option value="validation">Validation</option>
          <option value="test">Test</option>
        </select>
      </label>

      <label style={labelStyle}>
        Priority *
        <input
          type="number"
          style={inputStyle}
          value={formData.priority}
          onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
          min="1"
          max="10"
          required
        />
      </label>

      <label style={labelStyle}>
        Agent ID (optional)
        <input
          type="text"
          style={inputStyle}
          value={formData.agent_id}
          onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
          placeholder="Leave empty for auto-assignment"
        />
      </label>

      <label style={labelStyle}>
        Estimated Duration (seconds, optional)
        <input
          type="number"
          style={inputStyle}
          value={formData.estimated_duration}
          onChange={(e) =>
            setFormData({ ...formData, estimated_duration: parseInt(e.target.value) || 0 })
          }
          min="0"
          placeholder="0 for unknown"
        />
      </label>

      <div style={{ display: 'flex', gap: '8px', marginTop: '20px' }}>
        <Button type="submit" variant="primary" loading={loading} style={{ flex: 1 }}>
          Create Task
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
