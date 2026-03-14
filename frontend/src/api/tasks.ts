import { apiClient } from './client'
import { Task, TaskCreateRequest, TaskStatistics } from '@/types/task'

export const tasksApi = {
  // Get all tasks
  getTasks: async (params?: {
    status?: string
    agent_id?: string
    skip?: number
    limit?: number
  }): Promise<Task[]> => {
    const response = await apiClient.get('/tasks', { params })
    return response.data
  },

  // Get single task
  getTask: async (id: string): Promise<Task> => {
    const response = await apiClient.get(`/tasks/${id}`)
    return response.data
  },

  // Create task
  createTask: async (data: TaskCreateRequest): Promise<Task> => {
    const response = await apiClient.post('/tasks', data)
    return response.data
  },

  // Start task
  startTask: async (id: string): Promise<Task> => {
    const response = await apiClient.put(`/tasks/${id}/start`)
    return response.data
  },

  // Complete task
  completeTask: async (id: string, result: any): Promise<Task> => {
    const response = await apiClient.put(`/tasks/${id}/complete`, { result })
    return response.data
  },

  // Fail task
  failTask: async (id: string, error: string): Promise<Task> => {
    const response = await apiClient.put(`/tasks/${id}/fail`, { error })
    return response.data
  },

  // Delete task
  deleteTask: async (id: string): Promise<void> => {
    await apiClient.delete(`/tasks/${id}`)
  },

  // Get statistics
  getStatistics: async (): Promise<TaskStatistics> => {
    const response = await apiClient.get('/tasks/stats/summary')
    return response.data
  },
}
