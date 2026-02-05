export enum TaskStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Task {
  id: string
  description: string
  task_type: string
  status: TaskStatus
  priority: number
  agent_id?: string
  result?: any
  error?: string
  created_at: string
  started_at?: string
  completed_at?: string
  estimated_duration?: number
}

export interface TaskCreateRequest {
  description: string
  task_type: string
  priority?: number
  agent_id?: string
  estimated_duration?: number
}

export interface TaskStatistics {
  total: number
  by_status: Record<TaskStatus, number>
  average_duration: number
  success_rate: number
}
