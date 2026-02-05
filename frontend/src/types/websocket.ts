export enum WebSocketEventType {
  // Task events
  TASK_CREATED = 'task.created',
  TASK_STARTED = 'task.started',
  TASK_COMPLETED = 'task.completed',
  TASK_FAILED = 'task.failed',
  TASK_DELETED = 'task.deleted',

  // Connection events
  CONNECTION_CREATED = 'connection.created',
  CONNECTION_ESTABLISHED = 'connection.established',
  CONNECTION_DISCONNECTED = 'connection.disconnected',
  CONNECTION_DELETED = 'connection.deleted',

  // Agent events
  AGENT_CREATED = 'agent.created',
  AGENT_STATUS_CHANGED = 'agent.status_changed',
  AGENT_DELETED = 'agent.deleted',

  // Graph events
  GRAPH_CREATED = 'graph.created',
  GRAPH_EXECUTED = 'graph.executed',
  EXECUTION_STARTED = 'execution.started',
  EXECUTION_PROGRESS = 'execution.progress',
  EXECUTION_COMPLETED = 'execution.completed',
  EXECUTION_FAILED = 'execution.failed',
}

export interface WebSocketEvent<T = any> {
  type: WebSocketEventType | string
  data: T
  timestamp: string
}

export interface WebSocketMessage {
  action: 'subscribe' | 'unsubscribe' | 'ping' | 'get_subscriptions'
  event_types?: string[]
}

export interface WebSocketStats {
  active_connections: number
  total_subscriptions: number
  clients: Array<{
    client_id: string
    connected_at: string
    subscriptions: string[]
    subscription_count: number
  }>
}
