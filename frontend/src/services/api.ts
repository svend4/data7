/**
 * API Service
 * HTTP client for backend communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Agent,
  AgentCreateRequest,
  AgentUpdateRequest,
  AgentStats,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.message)
        return Promise.reject(error)
      }
    )
  }

  // ========================================================================
  // Agent Endpoints
  // ========================================================================

  async createAgent(data: AgentCreateRequest): Promise<Agent> {
    const response = await this.client.post<Agent>('/agents', data)
    return response.data
  }

  async listAgents(): Promise<Agent[]> {
    const response = await this.client.get<{ agents: Agent[]; total: number }>('/agents')
    return response.data.agents
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.client.get<Agent>(`/agents/${agentId}`)
    return response.data
  }

  async updateAgent(agentId: string, data: AgentUpdateRequest): Promise<Agent> {
    const response = await this.client.put<Agent>(`/agents/${agentId}`, data)
    return response.data
  }

  async deleteAgent(agentId: string): Promise<void> {
    await this.client.delete(`/agents/${agentId}`)
  }

  async getAgentStats(): Promise<AgentStats> {
    const response = await this.client.get<AgentStats>('/agents/stats/summary')
    return response.data
  }

  // ========================================================================
  // Health Check
  // ========================================================================

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService
