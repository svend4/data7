export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  ERROR = 'error',
  OFFLINE = 'offline',
}

export interface AgentCapability {
  name: string
  level: number
  description?: string
}

export interface Agent {
  id: string
  role: string
  status: AgentStatus
  capabilities: AgentCapability[]
  current_load: number
  total_tasks_completed: number
  position_x?: number
  position_y?: number
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AgentCreateRequest {
  role: string
  capabilities: AgentCapability[]
  position_x?: number
  position_y?: number
}

export interface AgentStatistics {
  total_agents: number
  active_agents: number
  idle_agents: number
  average_load: number
  total_completed_tasks: number
}
