"""
WebSocket Manager

Manages WebSocket connections and real-time updates.
Implements room-based subscriptions and message broadcasting.
"""

from typing import Dict, Set, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from app.middleware.prometheus import update_websocket_connections, record_websocket_message


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class WebSocketConnection:
    """WebSocket connection data."""
    websocket: WebSocket
    user_id: Optional[str] = None
    channels: Set[str] = None
    connected_at: datetime = None

    def __post_init__(self):
        if self.channels is None:
            self.channels = set()
        if self.connected_at is None:
            self.connected_at = datetime.utcnow()


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: str
    data: Any
    channel: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat()
        })


# ============================================================================
# WebSocket Manager
# ============================================================================

class WebSocketManager:
    """
    WebSocket connection manager.

    Manages connections, channels, and message broadcasting.
    """

    def __init__(self):
        # Connection storage: {connection_id: WebSocketConnection}
        self.connections: Dict[str, WebSocketConnection] = {}

        # Channel subscriptions: {channel: {connection_id, ...}}
        self.channels: Dict[str, Set[str]] = {}

        # User connections: {user_id: {connection_id, ...}}
        self.user_connections: Dict[str, Set[str]] = {}

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def connect(
        self,
        connection_id: str,
        websocket: WebSocket,
        user_id: Optional[str] = None
    ):
        """
        Accept and register a WebSocket connection.

        Args:
            connection_id: Unique connection ID
            websocket: WebSocket instance
            user_id: Optional user ID
        """
        await websocket.accept()

        async with self.lock:
            connection = WebSocketConnection(
                websocket=websocket,
                user_id=user_id
            )

            self.connections[connection_id] = connection

            # Track user connections
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)

        # Send welcome message
        await self.send_to_connection(
            connection_id,
            WebSocketMessage(
                type="connection.established",
                data={
                    "connection_id": connection_id,
                    "message": "Connected to Meta-Orchestrator Switchboard"
                }
            )
        )

        print(f"WebSocket connection established: {connection_id}")

    async def disconnect(self, connection_id: str):
        """
        Disconnect and cleanup a WebSocket connection.

        Args:
            connection_id: Connection ID
        """
        async with self.lock:
            connection = self.connections.get(connection_id)

            if not connection:
                return

            # Unsubscribe from all channels
            for channel in connection.channels.copy():
                await self._unsubscribe(connection_id, channel)

            # Remove user tracking
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            # Remove connection
            del self.connections[connection_id]

        print(f"WebSocket connection closed: {connection_id}")

    async def subscribe(self, connection_id: str, channel: str):
        """
        Subscribe connection to a channel.

        Args:
            connection_id: Connection ID
            channel: Channel name
        """
        async with self.lock:
            await self._subscribe(connection_id, channel)

        # Send subscription confirmation
        await self.send_to_connection(
            connection_id,
            WebSocketMessage(
                type="subscription.confirmed",
                data={
                    "channel": channel,
                    "message": f"Subscribed to {channel}"
                },
                channel=channel
            )
        )

    async def _subscribe(self, connection_id: str, channel: str):
        """Internal subscribe (without lock)."""
        connection = self.connections.get(connection_id)

        if not connection:
            return

        # Add to channel
        if channel not in self.channels:
            self.channels[channel] = set()

        self.channels[channel].add(connection_id)
        connection.channels.add(channel)

        # Update metrics
        update_websocket_connections(channel, len(self.channels[channel]))

    async def unsubscribe(self, connection_id: str, channel: str):
        """
        Unsubscribe connection from a channel.

        Args:
            connection_id: Connection ID
            channel: Channel name
        """
        async with self.lock:
            await self._unsubscribe(connection_id, channel)

        # Send unsubscription confirmation
        await self.send_to_connection(
            connection_id,
            WebSocketMessage(
                type="subscription.cancelled",
                data={
                    "channel": channel,
                    "message": f"Unsubscribed from {channel}"
                },
                channel=channel
            )
        )

    async def _unsubscribe(self, connection_id: str, channel: str):
        """Internal unsubscribe (without lock)."""
        connection = self.connections.get(connection_id)

        if not connection:
            return

        # Remove from channel
        if channel in self.channels:
            self.channels[channel].discard(connection_id)

            if not self.channels[channel]:
                del self.channels[channel]
            else:
                update_websocket_connections(channel, len(self.channels[channel]))

        connection.channels.discard(channel)

    async def send_to_connection(
        self,
        connection_id: str,
        message: WebSocketMessage
    ):
        """
        Send message to specific connection.

        Args:
            connection_id: Connection ID
            message: Message to send
        """
        connection = self.connections.get(connection_id)

        if not connection:
            return

        try:
            await connection.websocket.send_text(message.to_json())
            record_websocket_message("sent", message.type)

        except Exception as e:
            print(f"Error sending to connection {connection_id}: {e}")
            await self.disconnect(connection_id)

    async def broadcast_to_channel(
        self,
        channel: str,
        message: WebSocketMessage
    ):
        """
        Broadcast message to all connections in a channel.

        Args:
            channel: Channel name
            message: Message to broadcast
        """
        connection_ids = self.channels.get(channel, set()).copy()

        message.channel = channel

        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)

    async def broadcast_to_user(
        self,
        user_id: str,
        message: WebSocketMessage
    ):
        """
        Broadcast message to all connections of a user.

        Args:
            user_id: User ID
            message: Message to send
        """
        connection_ids = self.user_connections.get(user_id, set()).copy()

        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)

    async def broadcast_to_all(self, message: WebSocketMessage):
        """
        Broadcast message to all connections.

        Args:
            message: Message to broadcast
        """
        connection_ids = list(self.connections.keys())

        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)

    async def handle_message(
        self,
        connection_id: str,
        message: str
    ):
        """
        Handle incoming message from connection.

        Args:
            connection_id: Connection ID
            message: Raw message string
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")

            record_websocket_message("received", message_type)

            # Handle different message types
            if message_type == "subscribe":
                channels = data.get("channels", [])
                for channel in channels:
                    await self.subscribe(connection_id, channel)

            elif message_type == "unsubscribe":
                channels = data.get("channels", [])
                for channel in channels:
                    await self.unsubscribe(connection_id, channel)

            elif message_type == "ping":
                await self.send_to_connection(
                    connection_id,
                    WebSocketMessage(type="pong", data={"timestamp": datetime.utcnow().isoformat()})
                )

            else:
                print(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            print(f"Invalid JSON from connection {connection_id}: {message}")

        except Exception as e:
            print(f"Error handling message from {connection_id}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "total_connections": len(self.connections),
            "total_channels": len(self.channels),
            "channels": {
                channel: len(connections)
                for channel, connections in self.channels.items()
            },
            "users_online": len(self.user_connections)
        }


# ============================================================================
# Global WebSocket Manager
# ============================================================================

websocket_manager = WebSocketManager()


# ============================================================================
# WebSocket Endpoint Handler
# ============================================================================

async def websocket_endpoint(
    websocket: WebSocket,
    connection_id: str,
    user_id: Optional[str] = None
):
    """
    WebSocket endpoint handler.

    Args:
        websocket: WebSocket instance
        connection_id: Unique connection ID
        user_id: Optional user ID (from authentication)
    """
    await websocket_manager.connect(connection_id, websocket, user_id)

    try:
        while True:
            # Receive message
            message = await websocket.receive_text()

            # Handle message
            await websocket_manager.handle_message(connection_id, message)

    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_id)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket_manager.disconnect(connection_id)


# ============================================================================
# Helper Functions
# ============================================================================

async def notify_agent_update(agent_id: str, agent_data: Dict[str, Any]):
    """
    Notify about agent update via WebSocket.

    Args:
        agent_id: Agent ID
        agent_data: Agent data
    """
    message = WebSocketMessage(
        type="agent.updated",
        data={
            "id": agent_id,
            **agent_data
        }
    )

    await websocket_manager.broadcast_to_channel("agents", message)


async def notify_task_update(task_id: str, task_data: Dict[str, Any]):
    """
    Notify about task update via WebSocket.

    Args:
        task_id: Task ID
        task_data: Task data
    """
    message = WebSocketMessage(
        type="task.updated",
        data={
            "id": task_id,
            **task_data
        }
    )

    await websocket_manager.broadcast_to_channel("tasks", message)


async def notify_alert_triggered(alert_id: str, alert_data: Dict[str, Any]):
    """
    Notify about alert trigger via WebSocket.

    Args:
        alert_id: Alert ID
        alert_data: Alert data
    """
    message = WebSocketMessage(
        type="alert.triggered",
        data={
            "id": alert_id,
            **alert_data
        }
    )

    await websocket_manager.broadcast_to_channel("alerts", message)


async def notify_system_health(health_data: Dict[str, Any]):
    """
    Notify about system health update via WebSocket.

    Args:
        health_data: System health data
    """
    message = WebSocketMessage(
        type="system.health_updated",
        data=health_data
    )

    await websocket_manager.broadcast_to_channel("system", message)


async def notify_optimization_progress(
    graph_id: str,
    progress: int,
    status: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Notify about optimization progress via WebSocket.

    Args:
        graph_id: Graph ID
        progress: Progress percentage (0-100)
        status: Status message
        details: Optional additional details
    """
    message = WebSocketMessage(
        type="optimization.progress",
        data={
            "graph_id": graph_id,
            "progress": progress,
            "status": status,
            "details": details or {}
        }
    )

    await websocket_manager.broadcast_to_channel("optimization", message)
