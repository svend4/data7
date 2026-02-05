import axios, { AxiosInstance, AxiosError } from 'axios'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        this.handleError(error)
        return Promise.reject(error)
      }
    )
  }

  private handleError(error: AxiosError) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status
      const message = (error.response.data as any)?.detail || 'An error occurred'

      console.error(`API Error [${status}]:`, message)
    } else if (error.request) {
      // Request made but no response
      console.error('Network error: No response from server')
    } else {
      // Something else happened
      console.error('An unexpected error occurred:', error.message)
    }
  }

  get instance() {
    return this.client
  }
}

export const apiClient = new ApiClient().instance
