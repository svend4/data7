/**
 * useWebSocket Hook
 *
 * React hook for WebSocket real-time updates from backend.
 * Handles connection, reconnection, channel subscriptions, and message handling.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface WebSocketMessage {
  type: string;
  data: any;
  channel?: string;
  timestamp: string;
}

export interface WebSocketConfig {
  url?: string;
  channels?: string[];
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface WebSocketState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
  reconnectAttempts: number;
}

// ============================================================================
// Default Configuration
// ============================================================================

const DEFAULT_CONFIG: Required<Omit<WebSocketConfig, 'onMessage' | 'onOpen' | 'onClose' | 'onError'>> = {
  url: 'ws://localhost:8000/ws/events',
  channels: [],
  reconnect: true,
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
};

// ============================================================================
// useWebSocket Hook
// ============================================================================

export const useWebSocket = (config: WebSocketConfig = {}) => {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // State
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    connecting: false,
    error: null,
    lastMessage: null,
    reconnectAttempts: 0,
  });

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef<boolean>(true);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    setState((prev) => ({ ...prev, connecting: true, error: null }));

    try {
      const ws = new WebSocket(mergedConfig.url);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setState((prev) => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null,
          reconnectAttempts: 0,
        }));

        // Subscribe to channels
        if (mergedConfig.channels.length > 0) {
          ws.send(
            JSON.stringify({
              type: 'subscribe',
              channels: mergedConfig.channels,
            })
          );
        }

        config.onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setState((prev) => ({ ...prev, lastMessage: message }));
          config.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setState((prev) => ({
          ...prev,
          connected: false,
          connecting: false,
        }));

        config.onClose?.();

        // Attempt reconnection
        if (
          shouldReconnectRef.current &&
          mergedConfig.reconnect &&
          state.reconnectAttempts < mergedConfig.maxReconnectAttempts
        ) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setState((prev) => ({
              ...prev,
              reconnectAttempts: prev.reconnectAttempts + 1,
            }));
            connect();
          }, mergedConfig.reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setState((prev) => ({
          ...prev,
          error: 'WebSocket connection error',
          connecting: false,
        }));

        config.onError?.(error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setState((prev) => ({
        ...prev,
        error: 'Failed to create WebSocket connection',
        connecting: false,
      }));
    }
  }, [mergedConfig.url, mergedConfig.channels, mergedConfig.reconnect, mergedConfig.reconnectInterval, mergedConfig.maxReconnectAttempts]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      connected: false,
      connecting: false,
    }));
  }, []);

  // Send message
  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        typeof message === 'string' ? message : JSON.stringify(message)
      );
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }, []);

  // Subscribe to channel
  const subscribe = useCallback((channel: string) => {
    send({
      type: 'subscribe',
      channels: [channel],
    });
  }, [send]);

  // Unsubscribe from channel
  const unsubscribe = useCallback((channel: string) => {
    send({
      type: 'unsubscribe',
      channels: [channel],
    });
  }, [send]);

  // Send ping
  const ping = useCallback(() => {
    send({
      type: 'ping',
    });
  }, [send]);

  // Effect: Connect on mount
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Effect: Send periodic pings
  useEffect(() => {
    if (!state.connected) return;

    const pingInterval = setInterval(() => {
      ping();
    }, 30000); // Ping every 30 seconds

    return () => {
      clearInterval(pingInterval);
    };
  }, [state.connected, ping]);

  return {
    ...state,
    send,
    subscribe,
    unsubscribe,
    connect,
    disconnect,
    ping,
  };
};

// ============================================================================
// Convenience Hooks
// ============================================================================

/**
 * Hook for subscribing to agent updates
 */
export const useAgentUpdates = (onUpdate: (agent: any) => void) => {
  return useWebSocket({
    channels: ['agents'],
    onMessage: (message) => {
      if (message.type === 'agent.updated') {
        onUpdate(message.data);
      }
    },
  });
};

/**
 * Hook for subscribing to task updates
 */
export const useTaskUpdates = (onUpdate: (task: any) => void) => {
  return useWebSocket({
    channels: ['tasks'],
    onMessage: (message) => {
      if (message.type === 'task.updated') {
        onUpdate(message.data);
      }
    },
  });
};

/**
 * Hook for subscribing to alerts
 */
export const useAlertUpdates = (onAlert: (alert: any) => void) => {
  return useWebSocket({
    channels: ['alerts'],
    onMessage: (message) => {
      if (message.type === 'alert.triggered') {
        onAlert(message.data);
      }
    },
  });
};

/**
 * Hook for subscribing to system health updates
 */
export const useSystemHealthUpdates = (onUpdate: (health: any) => void) => {
  return useWebSocket({
    channels: ['system'],
    onMessage: (message) => {
      if (message.type === 'system.health_updated') {
        onUpdate(message.data);
      }
    },
  });
};

/**
 * Hook for subscribing to optimization progress
 */
export const useOptimizationProgress = (
  graphId: string,
  onProgress: (progress: any) => void
) => {
  return useWebSocket({
    channels: ['optimization'],
    onMessage: (message) => {
      if (
        message.type === 'optimization.progress' &&
        message.data.graph_id === graphId
      ) {
        onProgress(message.data);
      }
    },
  });
};
