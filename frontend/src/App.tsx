import React, { useEffect } from 'react'
import { useTasksStore } from './store/tasks'
import { wsClient } from './websocket/client'
import { WebSocketEventType } from './types/websocket'
import './styles/global.css'

function App() {
  const { tasks, fetchTasks, addTask, updateTask, removeTask } = useTasksStore()

  useEffect(() => {
    // Fetch initial data
    fetchTasks()

    // Connect WebSocket
    wsClient.connect().then(() => {
      console.log('WebSocket connected, subscribing to events...')
      wsClient.subscribe(['task.*', 'connection.*', 'agent.*'])
    })

    // Setup event handlers
    wsClient.on(WebSocketEventType.TASK_CREATED, (event) => {
      console.log('Task created:', event.data)
      addTask(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_STARTED, (event) => {
      console.log('Task started:', event.data)
      updateTask(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_COMPLETED, (event) => {
      console.log('Task completed:', event.data)
      updateTask(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_FAILED, (event) => {
      console.log('Task failed:', event.data)
      updateTask(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_DELETED, (event) => {
      console.log('Task deleted:', event.data)
      removeTask(event.data.task_id)
    })

    return () => {
      wsClient.disconnect()
    }
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🎭 Meta-Orchestrator Switchboard</h1>
      <p style={{ fontSize: '14px', color: '#666' }}>
        Art Deco 1920s Telephonic Exchange for Multi-Agent AI Coordination
      </p>

      <div style={{ marginTop: '30px' }}>
        <h2>Tasks ({tasks.length})</h2>
        
        {tasks.length === 0 ? (
          <p style={{ color: '#999' }}>No tasks yet. Create one using the REST API:</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
            {tasks.map((task) => (
              <div
                key={task.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '16px',
                  backgroundColor: '#f9f9f9',
                }}
              >
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>{task.description}</h3>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  <p>Status: <strong style={{ color: getStatusColor(task.status) }}>{task.status}</strong></p>
                  <p>Type: {task.task_type}</p>
                  <p>Priority: {task.priority}</p>
                  {task.agent_id && <p>Agent: {task.agent_id}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ marginTop: '40px', padding: '16px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h3>Quick Test</h3>
        <p>Create a test task using curl:</p>
        <pre style={{ backgroundColor: '#fff', padding: '12px', borderRadius: '4px', overflow: 'auto' }}>
{`curl -X POST http://localhost:8000/api/tasks \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "Test task from dashboard",
    "task_type": "test",
    "priority": 1
  }'`}
        </pre>
        <p style={{ marginTop: '12px', fontSize: '14px', color: '#666' }}>
          The task will appear in real-time via WebSocket! ⚡
        </p>
      </div>
    </div>
  )
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'pending':
      return '#666'
    case 'running':
      return '#007bff'
    case 'completed':
      return '#28a745'
    case 'failed':
      return '#dc3545'
    default:
      return '#666'
  }
}

export default App
