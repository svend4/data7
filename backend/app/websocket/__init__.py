"""
WebSocket Real-time Events Module
Provides real-time event broadcasting for the switchboard system
"""

from app.websocket.connection_manager import ConnectionManager
from app.websocket.events import EventType, WebSocketEvent

# Global connection manager instance (singleton)
connection_manager = ConnectionManager()

__all__ = ["connection_manager", "ConnectionManager", "EventType", "WebSocketEvent"]
