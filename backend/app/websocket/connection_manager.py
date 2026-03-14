"""
WebSocket Connection Manager
Manages active WebSocket connections, subscriptions, and event broadcasting
"""

from typing import Dict, Set
from fastapi import WebSocket
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConnection:
    """Represents a single WebSocket connection with metadata"""

    websocket: WebSocket
    client_id: str
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)

    def __hash__(self):
        return hash(self.client_id)


class ConnectionManager:
    """
    Manages WebSocket connections and event broadcasting

    Features:
    - Connection lifecycle management (connect, disconnect)
    - Subscription management (subscribe, unsubscribe)
    - Event broadcasting with subscription filtering
    - Wildcard subscription support (e.g., task.*)
    - Automatic cleanup of disconnected clients
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocketConnection] = {}
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Accept and register new WebSocket connection

        Args:
            websocket: FastAPI WebSocket instance
            client_id: Unique identifier for the client
        """
        await websocket.accept()
        connection = WebSocketConnection(websocket=websocket, client_id=client_id)
        self.active_connections[client_id] = connection
        logger.info(
            f"Client {client_id} connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, client_id: str) -> None:
        """
        Remove WebSocket connection

        Args:
            client_id: Client identifier to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(
                f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}"
            )

    def subscribe(self, client_id: str, event_type: str) -> bool:
        """
        Subscribe client to event type

        Args:
            client_id: Client identifier
            event_type: Event type to subscribe to (supports wildcards: task.*)

        Returns:
            True if subscription successful, False if client not found
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].subscriptions.add(event_type)
            logger.debug(f"Client {client_id} subscribed to {event_type}")
            return True
        return False

    def unsubscribe(self, client_id: str, event_type: str) -> bool:
        """
        Unsubscribe client from event type

        Args:
            client_id: Client identifier
            event_type: Event type to unsubscribe from

        Returns:
            True if unsubscription successful, False if client not found
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].subscriptions.discard(event_type)
            logger.debug(f"Client {client_id} unsubscribed from {event_type}")
            return True
        return False

    def get_subscriptions(self, client_id: str) -> Set[str]:
        """
        Get all subscriptions for a client

        Args:
            client_id: Client identifier

        Returns:
            Set of event types the client is subscribed to
        """
        if client_id in self.active_connections:
            return self.active_connections[client_id].subscriptions.copy()
        return set()

    async def send_to_client(self, client_id: str, message: dict) -> bool:
        """
        Send message to specific client

        Args:
            client_id: Client identifier
            message: Message dictionary to send

        Returns:
            True if sent successfully, False otherwise
        """
        if client_id in self.active_connections:
            try:
                conn = self.active_connections[client_id]
                await conn.websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send to client {client_id}: {e}")
                self.disconnect(client_id)
                return False
        return False

    async def broadcast(self, event_type: str, data: dict) -> int:
        """
        Broadcast event to all subscribed clients

        Args:
            event_type: Type of event (e.g., task.created)
            data: Event data payload

        Returns:
            Number of clients that received the event
        """
        sent_count = 0
        disconnected_clients = []

        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for client_id, conn in list(self.active_connections.items()):
            if self._should_send(conn, event_type):
                try:
                    await conn.websocket.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to client {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

        if sent_count > 0:
            logger.debug(
                f"Broadcast {event_type} to {sent_count} clients ({len(disconnected_clients)} failed)"
            )

        return sent_count

    def _should_send(self, conn: WebSocketConnection, event_type: str) -> bool:
        """
        Check if event should be sent to connection based on subscriptions

        Supports:
        - Exact match: "task.created" matches "task.created"
        - Wildcard: "task.*" matches "task.created", "task.started", etc.
        - Global wildcard: "*" matches all events

        Args:
            conn: WebSocket connection
            event_type: Event type to check

        Returns:
            True if event should be sent to this connection
        """
        if not conn.subscriptions:
            return False

        # Global wildcard
        if "*" in conn.subscriptions:
            return True

        # Exact match
        if event_type in conn.subscriptions:
            return True

        # Prefix wildcard match (e.g., "task.*" matches "task.created")
        for subscription in conn.subscriptions:
            if subscription.endswith(".*"):
                prefix = subscription[:-2]
                if event_type.startswith(prefix + "."):
                    return True

        return False

    def get_connection_count(self) -> int:
        """
        Get number of active WebSocket connections

        Returns:
            Number of active connections
        """
        return len(self.active_connections)

    def get_subscription_count(self) -> int:
        """
        Get total number of active subscriptions across all clients

        Returns:
            Total subscription count
        """
        return sum(
            len(conn.subscriptions) for conn in self.active_connections.values()
        )

    def get_stats(self) -> dict:
        """
        Get connection manager statistics

        Returns:
            Dictionary with connection stats
        """
        return {
            "active_connections": self.get_connection_count(),
            "total_subscriptions": self.get_subscription_count(),
            "clients": [
                {
                    "client_id": client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "subscriptions": list(conn.subscriptions),
                    "subscription_count": len(conn.subscriptions),
                }
                for client_id, conn in self.active_connections.items()
            ],
        }
