import { WebSocketEvent, WebSocketMessage } from '@/types/websocket'

type EventHandler = (event: WebSocketEvent) => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectInterval = 3000
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private handlers: Map<string, Set<EventHandler>> = new Map()
  private isIntentionallyClosed = false

  constructor(url: string = 'ws://localhost:8000/ws/events') {
    this.url = url
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.isIntentionallyClosed = false
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        reject(error)
      }

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        if (!this.isIntentionallyClosed) {
          this.reconnect()
        }
      }
    })
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Reconnecting... (Attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch(console.error)
    }, this.reconnectInterval)
  }

  disconnect() {
    this.isIntentionallyClosed = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(eventTypes: string[]) {
    this.send({
      action: 'subscribe',
      event_types: eventTypes,
    })
  }

  unsubscribe(eventTypes: string[]) {
    this.send({
      action: 'unsubscribe',
      event_types: eventTypes,
    })
  }

  ping() {
    this.send({ action: 'ping' })
  }

  on(eventType: string, handler: EventHandler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)
  }

  off(eventType: string, handler: EventHandler) {
    const handlers = this.handlers.get(eventType)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  private send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
    }
  }

  private handleMessage(data: any) {
    const eventType = data.type

    // Handle system messages
    if (eventType === 'connected') {
      console.log('Connected with client ID:', data.client_id)
      return
    }

    if (eventType === 'pong') {
      return
    }

    if (eventType === 'subscription.success' || eventType === 'subscription.updated') {
      console.log('Subscriptions updated:', data.active_subscriptions)
      return
    }

    // Handle event broadcasts
    const event: WebSocketEvent = {
      type: eventType,
      data: data.data,
      timestamp: data.timestamp,
    }

    // Notify specific handlers
    const handlers = this.handlers.get(eventType)
    if (handlers) {
      handlers.forEach((handler) => handler(event))
    }

    // Notify wildcard handlers
    const wildcardHandlers = this.handlers.get('*')
    if (wildcardHandlers) {
      wildcardHandlers.forEach((handler) => handler(event))
    }
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Singleton instance
export const wsClient = new WebSocketClient()
