"""
WebSocket API Endpoint
Real-time event streaming for the Meta-Orchestrator Switchboard
"""

import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.websocket import connection_manager
from app.websocket.events import ConnectedMessage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/events")
async def websocket_endpoint(
    websocket: WebSocket, client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time event streaming

    Connection URL: ws://localhost:8000/ws/events?client_id=xxx

    ## Message Protocol

    ### Client → Server (Subscribe):
    ```json
    {
        "action": "subscribe",
        "event_types": ["task.*", "execution.progress"]
    }
    ```

    ### Client → Server (Unsubscribe):
    ```json
    {
        "action": "unsubscribe",
        "event_types": ["task.*"]
    }
    ```

    ### Client → Server (Ping):
    ```json
    {
        "action": "ping"
    }
    ```

    ### Server → Client (Event):
    ```json
    {
        "type": "task.created",
        "data": { ... },
        "timestamp": "2025-01-15T10:30:00Z"
    }
    ```

    ### Server → Client (Pong):
    ```json
    {
        "type": "pong",
        "timestamp": "2025-01-15T10:30:00Z"
    }
    ```

    ## Event Types

    - Task events: task.created, task.started, task.completed, task.failed, task.deleted
    - Connection events: connection.created, connection.established, connection.disconnected, connection.deleted
    - Graph events: graph.created, graph.executed, graph.deleted
    - Execution events: execution.started, execution.progress, execution.completed, execution.failed
    - Agent events: agent.created, agent.status_changed, agent.deleted

    ## Subscription Patterns

    - Exact match: "task.created" (only task creation events)
    - Wildcard: "task.*" (all task events)
    - Global: "*" (all events)
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())

    logger.info(f"WebSocket connection attempt from client: {client_id}")

    try:
        # Accept connection
        await connection_manager.connect(websocket, client_id)

        # Send welcome message
        welcome_message = ConnectedMessage(
            client_id=client_id,
            message="Connected to Meta-Orchestrator Switchboard 🎭",
            timestamp=datetime.utcnow().isoformat(),
        )
        await websocket.send_json(welcome_message.dict())

        # Message loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe":
                # Subscribe to event types
                event_types = data.get("event_types", [])
                for event_type in event_types:
                    connection_manager.subscribe(client_id, event_type)

                # Send confirmation
                subscriptions = connection_manager.get_subscriptions(client_id)
                await websocket.send_json(
                    {
                        "type": "subscription.success",
                        "active_subscriptions": list(subscriptions),
                        "message": f"Subscribed to {len(event_types)} event type(s)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            elif action == "unsubscribe":
                # Unsubscribe from event types
                event_types = data.get("event_types", [])
                for event_type in event_types:
                    connection_manager.unsubscribe(client_id, event_type)

                # Send confirmation
                subscriptions = connection_manager.get_subscriptions(client_id)
                await websocket.send_json(
                    {
                        "type": "subscription.updated",
                        "active_subscriptions": list(subscriptions),
                        "message": f"Unsubscribed from {len(event_types)} event type(s)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            elif action == "ping":
                # Respond to ping (heartbeat)
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

            elif action == "get_subscriptions":
                # Return current subscriptions
                subscriptions = connection_manager.get_subscriptions(client_id)
                await websocket.send_json(
                    {
                        "type": "subscriptions",
                        "active_subscriptions": list(subscriptions),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            else:
                # Unknown action
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        # Client disconnected normally
        logger.info(f"Client {client_id} disconnected normally")
        connection_manager.disconnect(client_id)

    except Exception as e:
        # Error occurred, disconnect client
        logger.error(f"WebSocket error for client {client_id}: {e}", exc_info=True)
        connection_manager.disconnect(client_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics

    Returns:
    - active_connections: Number of connected clients
    - total_subscriptions: Total number of active subscriptions
    - clients: List of connected clients with their subscriptions
    """
    return connection_manager.get_stats()
