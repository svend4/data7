export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTED = 'connected',
  TRANSMITTING = 'transmitting',
}

export interface Connection {
  id: string
  from_agent_id: string
  to_agent_id: string
  status: ConnectionStatus
  socket_from?: number
  socket_to?: number
  protocol: string
  established_at?: string
  closed_at?: string
  created_at: string
}

export interface ConnectionCreateRequest {
  from_agent_id: string
  to_agent_id: string
  protocol?: string
}

export interface ConnectionStatistics {
  total_connections: number
  active_connections: number
  allocated_sockets: number
  by_status: Record<ConnectionStatus, number>
}
