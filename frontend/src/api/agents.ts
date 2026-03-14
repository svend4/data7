import { apiClient } from './client'
import { Agent, AgentCreateRequest, AgentStatistics } from '@/types/agent'

export const agentsApi = {
  // Get all agents
  getAgents: async (): Promise<Agent[]> => {
    const response = await apiClient.get('/agents')
    return response.data
  },

  // Get single agent
  getAgent: async (id: string): Promise<Agent> => {
    const response = await apiClient.get(`/agents/${id}`)
    return response.data
  },

  // Create agent
  createAgent: async (data: AgentCreateRequest): Promise<Agent> => {
    const response = await apiClient.post('/agents', data)
    return response.data
  },

  // Update agent
  updateAgent: async (id: string, data: Partial<Agent>): Promise<Agent> => {
    const response = await apiClient.put(`/agents/${id}`, data)
    return response.data
  },

  // Delete agent
  deleteAgent: async (id: string): Promise<void> => {
    await apiClient.delete(`/agents/${id}`)
  },

  // Get statistics
  getStatistics: async (): Promise<AgentStatistics> => {
    const response = await apiClient.get('/agents/stats/summary')
    return response.data
  },
}
