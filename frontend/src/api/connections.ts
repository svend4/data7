import { apiClient } from './client'
import { Connection, ConnectionCreateRequest, ConnectionStatistics } from '@/types/connection'

export const connectionsApi = {
  // Get all connections
  getConnections: async (params?: {
    status?: string
    agent_id?: string
  }): Promise<Connection[]> => {
    const response = await apiClient.get('/connections', { params })
    return response.data
  },

  // Get single connection
  getConnection: async (id: string): Promise<Connection> => {
    const response = await apiClient.get(`/connections/${id}`)
    return response.data
  },

  // Create connection
  createConnection: async (data: ConnectionCreateRequest): Promise<Connection> => {
    const response = await apiClient.post('/connections', data)
    return response.data
  },

  // Establish connection
  establishConnection: async (id: string): Promise<Connection> => {
    const response = await apiClient.put(`/connections/${id}/establish`)
    return response.data
  },

  // Disconnect connection
  disconnectConnection: async (id: string): Promise<Connection> => {
    const response = await apiClient.put(`/connections/${id}/disconnect`)
    return response.data
  },

  // Delete connection
  deleteConnection: async (id: string): Promise<void> => {
    await apiClient.delete(`/connections/${id}`)
  },

  // Get statistics
  getStatistics: async (): Promise<ConnectionStatistics> => {
    const response = await apiClient.get('/connections/stats/summary')
    return response.data
  },
}
