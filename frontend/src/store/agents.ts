import { create } from 'zustand'
import { Agent, AgentCreateRequest } from '@/types/agent'
import { agentsApi } from '@/api/agents'

interface AgentsState {
  agents: Agent[]
  loading: boolean
  error: string | null

  // Actions
  fetchAgents: () => Promise<void>
  createAgent: (data: AgentCreateRequest) => Promise<void>
  updateAgent: (id: string, data: Partial<Agent>) => Promise<void>
  deleteAgent: (id: string) => Promise<void>

  // Real-time updates (called from WebSocket events)
  addAgent: (agent: Agent) => void
  updateAgentState: (agent: Agent) => void
  removeAgent: (id: string) => void
}

export const useAgentsStore = create<AgentsState>((set, get) => ({
  agents: [],
  loading: false,
  error: null,

  fetchAgents: async () => {
    set({ loading: true, error: null })
    try {
      const agents = await agentsApi.getAgents()
      set({ agents, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  createAgent: async (data) => {
    try {
      await agentsApi.createAgent(data)
      // Agent will be added via WebSocket event
    } catch (error: any) {
      console.error('Failed to create agent:', error)
      throw error
    }
  },

  updateAgent: async (id, data) => {
    try {
      await agentsApi.updateAgent(id, data)
      // Agent will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to update agent:', error)
      throw error
    }
  },

  deleteAgent: async (id) => {
    try {
      await agentsApi.deleteAgent(id)
      // Agent will be removed via WebSocket event
    } catch (error: any) {
      console.error('Failed to delete agent:', error)
      throw error
    }
  },

  // Real-time updates from WebSocket
  addAgent: (agent) => {
    set((state) => ({
      agents: [agent, ...state.agents],
    }))
  },

  updateAgentState: (updatedAgent) => {
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === updatedAgent.id ? updatedAgent : agent
      ),
    }))
  },

  removeAgent: (id) => {
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id),
    }))
  },
}))
