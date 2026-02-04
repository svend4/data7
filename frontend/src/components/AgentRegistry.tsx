/**
 * Agent Registry Component
 * Main interface for viewing and managing agents
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService } from '../services/api'
import { Agent, AgentCreateRequest } from '../types'
import { AgentCard } from './AgentCard'
import { CreateAgentModal } from './CreateAgentModal'
import './AgentRegistry.css'

export function AgentRegistry() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const queryClient = useQueryClient()

  // Query for agents list
  const {
    data: agents,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['agents'],
    queryFn: () => apiService.listAgents(),
    refetchInterval: 3000, // Refresh every 3 seconds
  })

  // Mutation for creating agent
  const createMutation = useMutation({
    mutationFn: (data: AgentCreateRequest) => apiService.createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['agent-stats'] })
      setIsModalOpen(false)
    },
  })

  // Mutation for deleting agent
  const deleteMutation = useMutation({
    mutationFn: (agentId: string) => apiService.deleteAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['agent-stats'] })
    },
  })

  const handleCreateAgent = (data: AgentCreateRequest) => {
    createMutation.mutate(data)
  }

  const handleDeleteAgent = (agentId: string) => {
    if (confirm('Are you sure you want to delete this agent?')) {
      deleteMutation.mutate(agentId)
    }
  }

  if (isLoading) {
    return (
      <div className="registry-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading agents...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="registry-container">
        <div className="error-message">
          Failed to load agents. Make sure the backend is running on port 8000.
        </div>
      </div>
    )
  }

  return (
    <div className="registry-container">
      <div className="registry-header">
        <h2 className="registry-title">Agent Registry</h2>
        <button
          className="btn-primary"
          onClick={() => setIsModalOpen(true)}
          disabled={createMutation.isPending}
        >
          + Register New Agent
        </button>
      </div>

      {agents && agents.length === 0 ? (
        <div className="empty-state">
          <p className="empty-message">No agents registered yet.</p>
          <p className="empty-hint">Click "Register New Agent" to get started.</p>
        </div>
      ) : (
        <div className="agents-grid">
          {agents?.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onDelete={handleDeleteAgent}
            />
          ))}
        </div>
      )}

      {isModalOpen && (
        <CreateAgentModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateAgent}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  )
}
