import React from 'react'
import { Task } from '@/types/task'
import { Button } from '../common/Button'
import { Card } from '../common/Card'
import { StatusBadge } from '../common/StatusBadge'
import { useTasksStore } from '@/store/tasks'
import { formatDistanceToNow } from 'date-fns'

interface TaskCardProps {
  task: Task
}

export const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  const { startTask, completeTask, failTask, deleteTask } = useTasksStore()

  const handleStart = async () => {
    try {
      await startTask(task.id)
    } catch (error) {
      console.error('Failed to start task:', error)
    }
  }

  const handleComplete = async () => {
    try {
      await completeTask(task.id, { success: true })
    } catch (error) {
      console.error('Failed to complete task:', error)
    }
  }

  const handleFail = async () => {
    try {
      await failTask(task.id, 'Manual failure')
    } catch (error) {
      console.error('Failed to fail task:', error)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await deleteTask(task.id)
      } catch (error) {
        console.error('Failed to delete task:', error)
      }
    }
  }

  return (
    <Card>
      <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
          {task.description}
        </h3>
        <StatusBadge status={task.status} />
      </div>

      <div style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
        <p style={{ margin: '4px 0' }}>
          <strong>Type:</strong> {task.task_type}
        </p>
        <p style={{ margin: '4px 0' }}>
          <strong>Priority:</strong> {task.priority}
        </p>
        {task.agent_id && (
          <p style={{ margin: '4px 0' }}>
            <strong>Agent:</strong> {task.agent_id}
          </p>
        )}
        <p style={{ margin: '4px 0' }}>
          <strong>Created:</strong> {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
        </p>
        {task.started_at && (
          <p style={{ margin: '4px 0' }}>
            <strong>Started:</strong> {formatDistanceToNow(new Date(task.started_at), { addSuffix: true })}
          </p>
        )}
        {task.completed_at && (
          <p style={{ margin: '4px 0' }}>
            <strong>Completed:</strong> {formatDistanceToNow(new Date(task.completed_at), { addSuffix: true })}
          </p>
        )}
        {task.error && (
          <p style={{ margin: '4px 0', color: '#dc3545' }}>
            <strong>Error:</strong> {task.error}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {task.status === 'pending' && (
          <Button onClick={handleStart} size="small" variant="primary">
            Start
          </Button>
        )}
        {task.status === 'running' && (
          <>
            <Button onClick={handleComplete} size="small" variant="success">
              Complete
            </Button>
            <Button onClick={handleFail} size="small" variant="danger">
              Fail
            </Button>
          </>
        )}
        <Button onClick={handleDelete} size="small" variant="danger">
          Delete
        </Button>
      </div>
    </Card>
  )
}
