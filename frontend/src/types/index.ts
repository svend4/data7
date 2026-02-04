/**
 * TypeScript types for Switchboard System
 * Based on backend schemas and domain models
 */

export interface Vector3 {
  x: number
  y: number
  z: number
}

export interface Color {
  r: number
  g: number
  b: number
  a?: number
}

export interface AgentCapability {
  name: string
  category: string
  level: number
  description?: string
}

export interface PerformanceMetrics {
  avg_response_time: number
  success_rate: number
  total_tasks: number
  current_load: number
}

export type AgentStatus = 'idle' | 'busy' | 'offline' | 'error' | 'maintenance'

export interface Agent {
  id: string
  role: string
  status: AgentStatus
  capabilities: AgentCapability[]
  metrics: PerformanceMetrics
  position?: Vector3
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AgentCreateRequest {
  role: string
  capabilities: AgentCapability[]
  position?: Vector3
  metadata?: Record<string, any>
}

export interface AgentUpdateRequest {
  status?: AgentStatus
  position?: Vector3
  metadata?: Record<string, any>
}

export interface AgentStats {
  total_agents: number
  idle_agents: number
  busy_agents: number
  offline_agents: number
  avg_success_rate: number
  avg_response_time: number
}

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
