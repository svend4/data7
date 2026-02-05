import React, { useEffect, useState } from 'react'
import { useTasksStore } from './store/tasks'
import { useAgentsStore } from './store/agents'
import { useConnectionsStore } from './store/connections'
import { wsClient } from './websocket/client'
import { WebSocketEventType } from './types/websocket'
import { TaskCard } from './components/tasks/TaskCard'
import { SocketBoard } from './components/connections/SocketBoard'
import { Statistics } from './components/dashboard/Statistics'
import { Card } from './components/common/Card'
import './styles/global.css'

function App() {
  const [wsConnected, setWsConnected] = useState(false)
  
  // Task store
  const { 
    tasks, 
    fetchTasks, 
    addTask, 
    updateTask: updateTaskState, 
    removeTask 
  } = useTasksStore()

  // Agent store
  const {
    agents,
    fetchAgents,
    addAgent,
    updateAgentState,
    removeAgent,
  } = useAgentsStore()

  // Connection store
  const {
    connections,
    fetchConnections,
    addConnection,
    updateConnection,
    removeConnection,
    getAllocatedSockets,
  } = useConnectionsStore()

  useEffect(() => {
    // Fetch initial data
    fetchTasks()
    fetchAgents()
    fetchConnections()

    // Connect WebSocket
    wsClient.connect().then(() => {
      console.log('✅ WebSocket connected, subscribing to events...')
      setWsConnected(true)
      wsClient.subscribe(['*']) // Subscribe to all events
    }).catch((error) => {
      console.error('❌ Failed to connect WebSocket:', error)
      setWsConnected(false)
    })

    // Task events
    wsClient.on(WebSocketEventType.TASK_CREATED, (event) => {
      console.log('📨 Task created:', event.data)
      addTask(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_STARTED, (event) => {
      console.log('📨 Task started:', event.data)
      updateTaskState(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_COMPLETED, (event) => {
      console.log('📨 Task completed:', event.data)
      updateTaskState(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_FAILED, (event) => {
      console.log('📨 Task failed:', event.data)
      updateTaskState(event.data)
    })

    wsClient.on(WebSocketEventType.TASK_DELETED, (event) => {
      console.log('📨 Task deleted:', event.data)
      removeTask(event.data.task_id)
    })

    // Agent events
    wsClient.on(WebSocketEventType.AGENT_CREATED, (event) => {
      console.log('📨 Agent created:', event.data)
      addAgent(event.data)
    })

    wsClient.on(WebSocketEventType.AGENT_STATUS_CHANGED, (event) => {
      console.log('📨 Agent status changed:', event.data)
      updateAgentState(event.data)
    })

    wsClient.on(WebSocketEventType.AGENT_DELETED, (event) => {
      console.log('📨 Agent deleted:', event.data)
      removeAgent(event.data.agent_id)
    })

    // Connection events
    wsClient.on(WebSocketEventType.CONNECTION_CREATED, (event) => {
      console.log('📨 Connection created:', event.data)
      addConnection(event.data)
    })

    wsClient.on(WebSocketEventType.CONNECTION_ESTABLISHED, (event) => {
      console.log('📨 Connection established:', event.data)
      updateConnection(event.data)
    })

    wsClient.on(WebSocketEventType.CONNECTION_DISCONNECTED, (event) => {
      console.log('📨 Connection disconnected:', event.data)
      updateConnection(event.data)
    })

    wsClient.on(WebSocketEventType.CONNECTION_DELETED, (event) => {
      console.log('📨 Connection deleted:', event.data)
      removeConnection(event.data.connection_id)
    })

    return () => {
      wsClient.disconnect()
    }
  }, [])

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <header
        style={{
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '20px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 700 }}>
            🎭 Meta-Orchestrator Switchboard
          </h1>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
            Art Deco 1920s Telephonic Exchange for Multi-Agent AI Coordination
          </p>
          <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 12px',
                backgroundColor: wsConnected ? '#28a745' : '#dc3545',
                borderRadius: '16px',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  animation: wsConnected ? 'pulse 2s infinite' : 'none',
                }}
              />
              {wsConnected ? 'LIVE' : 'DISCONNECTED'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '30px 20px' }}>
        {/* Statistics */}
        <div style={{ marginBottom: '30px' }}>
          <Statistics />
        </div>

        {/* Socket Board */}
        <div style={{ marginBottom: '30px' }}>
          <SocketBoard allocatedSockets={getAllocatedSockets()} />
        </div>

        {/* Tasks Section */}
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: 600 }}>
            📋 Tasks ({tasks.length})
          </h2>
          
          {tasks.length === 0 ? (
            <Card>
              <div style={{ textAlign: 'center', padding: '40px', color: '#6c757d' }}>
                <p style={{ fontSize: '18px', marginBottom: '16px' }}>
                  No tasks yet. Create one using the REST API!
                </p>
                <div style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
                  <pre style={{ backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px', overflow: 'auto' }}>
{`curl -X POST http://localhost:8000/api/tasks \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "Test task from dashboard",
    "task_type": "test",
    "priority": 1
  }'`}
                  </pre>
                </div>
                <p style={{ marginTop: '16px', fontSize: '14px' }}>
                  ⚡ Tasks will appear here in real-time via WebSocket!
                </p>
              </div>
            </Card>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '20px',
              }}
            >
              {tasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          )}
        </div>

        {/* Agents Section */}
        {agents.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h2 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: 600 }}>
              🤖 Agents ({agents.length})
            </h2>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '20px',
              }}
            >
              {agents.map((agent) => (
                <Card key={agent.id}>
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600 }}>
                    {agent.role}
                  </h3>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>Status:</strong>{' '}
                    <span
                      style={{
                        color:
                          agent.status === 'idle'
                            ? '#6c757d'
                            : agent.status === 'busy'
                            ? '#007bff'
                            : agent.status === 'error'
                            ? '#dc3545'
                            : '#495057',
                        fontWeight: 600,
                      }}
                    >
                      {agent.status.toUpperCase()}
                    </span>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>Load:</strong> {(agent.current_load * 100).toFixed(1)}%
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>Tasks Completed:</strong> {agent.total_tasks_completed}
                  </p>
                  {agent.capabilities.length > 0 && (
                    <div style={{ marginTop: '8px' }}>
                      <strong style={{ fontSize: '14px' }}>Capabilities:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                        {agent.capabilities.map((cap, i) => (
                          <span
                            key={i}
                            style={{
                              padding: '2px 8px',
                              backgroundColor: '#e9ecef',
                              borderRadius: '4px',
                              fontSize: '12px',
                            }}
                          >
                            {cap.name} (L{cap.level})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Connections Section */}
        {connections.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h2 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: 600 }}>
              🔌 Connections ({connections.length})
            </h2>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '20px',
              }}
            >
              {connections.map((connection) => (
                <Card key={connection.id}>
                  <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                      Connection {connection.id.slice(0, 8)}...
                    </h3>
                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        backgroundColor:
                          connection.status === 'connected'
                            ? '#28a745'
                            : connection.status === 'transmitting'
                            ? '#17a2b8'
                            : '#6c757d',
                        color: 'white',
                      }}
                    >
                      {connection.status}
                    </span>
                  </div>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>From:</strong> {connection.from_agent_id}
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>To:</strong> {connection.to_agent_id}
                  </p>
                  {connection.socket_from && connection.socket_to && (
                    <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                      <strong>Sockets:</strong> {connection.socket_from} ↔ {connection.socket_to}
                    </p>
                  )}
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    <strong>Protocol:</strong> {connection.protocol}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '20px',
          textAlign: 'center',
          marginTop: '40px',
        }}
      >
        <p style={{ margin: 0, fontSize: '14px', opacity: 0.8 }}>
          Meta-Orchestrator Switchboard &copy; 2025 | Phase 5: Frontend Integration
        </p>
      </footer>
    </div>
  )
}

export default App
