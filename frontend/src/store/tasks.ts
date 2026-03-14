import { create } from 'zustand'
import { Task, TaskStatus, TaskCreateRequest } from '@/types/task'
import { tasksApi } from '@/api/tasks'

interface TasksState {
  tasks: Task[]
  loading: boolean
  error: string | null

  // Actions
  fetchTasks: () => Promise<void>
  createTask: (data: TaskCreateRequest) => Promise<void>
  startTask: (id: string) => Promise<void>
  completeTask: (id: string, result: any) => Promise<void>
  failTask: (id: string, error: string) => Promise<void>
  deleteTask: (id: string) => Promise<void>

  // Real-time updates (called from WebSocket events)
  addTask: (task: Task) => void
  updateTask: (task: Task) => void
  removeTask: (id: string) => void
}

export const useTasksStore = create<TasksState>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null })
    try {
      const tasks = await tasksApi.getTasks()
      set({ tasks, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  createTask: async (data) => {
    try {
      await tasksApi.createTask(data)
      // Task will be added via WebSocket event
    } catch (error: any) {
      console.error('Failed to create task:', error)
      throw error
    }
  },

  startTask: async (id) => {
    try {
      await tasksApi.startTask(id)
      // Task will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to start task:', error)
      throw error
    }
  },

  completeTask: async (id, result) => {
    try {
      await tasksApi.completeTask(id, result)
      // Task will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to complete task:', error)
      throw error
    }
  },

  failTask: async (id, error) => {
    try {
      await tasksApi.failTask(id, error)
      // Task will be updated via WebSocket event
    } catch (error: any) {
      console.error('Failed to fail task:', error)
      throw error
    }
  },

  deleteTask: async (id) => {
    try {
      await tasksApi.deleteTask(id)
      // Task will be removed via WebSocket event
    } catch (error: any) {
      console.error('Failed to delete task:', error)
      throw error
    }
  },

  // Real-time updates from WebSocket
  addTask: (task) => {
    set((state) => ({
      tasks: [task, ...state.tasks],
    }))
  },

  updateTask: (updatedTask) => {
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === updatedTask.id ? updatedTask : task
      ),
    }))
  },

  removeTask: (id) => {
    set((state) => ({
      tasks: state.tasks.filter((task) => task.id !== id),
    }))
  },
}))
