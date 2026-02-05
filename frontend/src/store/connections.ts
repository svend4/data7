import { create } from 'zustand'
import { Connection, ConnectionCreateRequest } from '@/types/connection'
import { connectionsApi } from '@/api/connections'

interface ConnectionsState {
  connections: Connection[]
  loading: boolean
  error: string | null

  // Actions
  fetchConnections: () => Promise<void>
  createConnection: (data: ConnectionCreateRequest) => Promise<void>
  establishConnection: (id: string) => Promise<void>
  disconnectConnection: (id: string) => Promise<void>
  deleteConnection: (id: string) => Promise<void>

  // Real-time updates (called from WebSocket events)
  addConnection: (connection: Connection) => void
  updateConnection: (connection: Connection) => void
  removeConnection: (id: string) => void

  // Helpers
  getAllocatedSockets: () => number[]
}

export const useConnectionsStore = create<ConnectionsState>((set, get) => ({
  connections: [],
  loading: false,
  error: null,

  fetchConnections: async () => {
    set({ loading: true, error: null })
    try {
      const connections = await connectionsApi.getConnections()
      set({ connections, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  createConnection: async (data) => {
    try {
      await connectionsApi.createConnection(data)
      // Connection will be added via WebSocket event
    } catch (error: any) {
      console.error('Failed to create connection:', error)
      throw error
    }
  },

  establishConnection: async (id) => {
    try {
      await connectionsApi.establishConnection(id)
      // Connection will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to establish connection:', error)
      throw error
    }
  },

  disconnectConnection: async (id) => {
    try {
      await connectionsApi.disconnectConnection(id)
      // Connection will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to disconnect connection:', error)
      throw error
    }
  },

  deleteConnection: async (id) => {
    try {
      await connectionsApi.deleteConnection(id)
      // Connection will be removed via WebSocket event
    } catch (error: any) {
      console.error('Failed to delete connection:', error)
      throw error
    }
  },

  // Real-time updates from WebSocket
  addConnection: (connection) => {
    set((state) => ({
      connections: [connection, ...state.connections],
    }))
  },

  updateConnection: (updatedConnection) => {
    set((state) => ({
      connections: state.connections.map((connection) =>
        connection.id === updatedConnection.id ? updatedConnection : connection
      ),
    }))
  },

  removeConnection: (id) => {
    set((state) => ({
      connections: state.connections.filter((connection) => connection.id !== id),
    }))
  },

  // Get all allocated socket numbers
  getAllocatedSockets: () => {
    const { connections } = get()
    const sockets: number[] = []
    
    connections.forEach((conn) => {
      if (conn.status === 'connected' || conn.status === 'transmitting') {
        if (conn.socket_from) sockets.push(conn.socket_from)
        if (conn.socket_to) sockets.push(conn.socket_to)
      }
    })
    
    return sockets
  },
}))
