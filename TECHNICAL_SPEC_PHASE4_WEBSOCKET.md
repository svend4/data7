# Technical Specification: Phase 4 - WebSocket Real-time Updates

**Status**: 🔄 In Progress
**Timeline**: Week 6-8 of 32-week roadmap
**Dependencies**: Phase 3 (API ↔ Database Integration) ✅ Complete

---

## 🎯 Phase 4 Mission

**Goal**: Add real-time bidirectional communication for live system updates

**Problem**: Current REST API requires polling for status updates, causing:
- Inefficient network usage (repeated requests)
- Delayed updates (polling interval lag)
- Increased server load (unnecessary requests)
- Poor user experience (not truly real-time)

**Solution**: WebSocket-based event broadcasting system for instant updates

---

## 📋 Requirements

### Functional Requirements

1. **WebSocket Connection Management**
   - Single endpoint: `/ws/events`
   - Support multiple concurrent clients
   - Automatic reconnection handling
   - Connection lifecycle tracking (connect, disconnect, heartbeat)

2. **Event Broadcasting**
   - Broadcast task lifecycle events (created, started, completed, failed)
   - Broadcast connection state changes (established, disconnected)
   - Broadcast graph execution progress updates
   - Broadcast agent status changes
   - Event filtering by subscription type

3. **Client Subscriptions**
   - Subscribe to specific event types
   - Subscribe to specific entity IDs (e.g., task-123 updates only)
   - Unsubscribe mechanism
   - Wildcard subscriptions (all events)

4. **Event Types**
   - `task.created`, `task.started`, `task.completed`, `task.failed`
   - `connection.established`, `connection.disconnected`
   - `graph.created`, `graph.executed`
   - `execution.started`, `execution.progress`, `execution.completed`, `execution.failed`
   - `agent.created`, `agent.status_changed`, `agent.deleted`

### Non-Functional Requirements

1. **Performance**
   - Support 100+ concurrent WebSocket connections
   - Sub-100ms event delivery latency
   - Minimal memory overhead per connection

2. **Reliability**
   - Graceful handling of client disconnections
   - No message loss for connected clients
   - Automatic cleanup of stale connections

3. **Scalability**
   - Single-server implementation for MVP
   - Redis pub/sub ready for multi-server scaling (future)

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  REST API    │      │  WebSocket   │                     │
│  │  Endpoints   │      │   Endpoint   │                     │
│  │              │      │  /ws/events  │                     │
│  └──────┬───────┘      └──────┬───────┘                     │
│         │                     │                              │
│         │                     │                              │
│         └──────┬──────────────┘                              │
│                │                                              │
│         ┌──────▼──────────────────┐                         │
│         │  Event Broadcaster       │                         │
│         │  (In-Memory for MVP)     │                         │
│         │                          │                         │
│         │  - Connection Manager    │                         │
│         │  - Event Queue           │                         │
│         │  - Subscription Manager  │                         │
│         └──────────────────────────┘                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘

         │                              │
         │                              │
         ▼                              ▼
┌─────────────────┐          ┌─────────────────┐
│  WebSocket      │          │  WebSocket      │
│  Client 1       │          │  Client 2       │
│                 │          │                 │
│  Subscriptions: │          │  Subscriptions: │
│  - task.*       │          │  - execution.*  │
│  - agent.*      │          │  - graph.*      │
└─────────────────┘          └─────────────────┘
```

### Event Flow

```
1. REST API Endpoint (e.g., POST /tasks)
         │
         ▼
2. Create Task → Database
         │
         ▼
3. Emit Event → EventBroadcaster.broadcast("task.created", {...})
         │
         ▼
4. EventBroadcaster iterates active WebSocket connections
         │
         ▼
5. Check subscription filters for each connection
         │
         ▼
6. Send JSON event to matching subscribers
         │
         ▼
7. WebSocket Client receives event in real-time
```

---

## 📦 Implementation Plan

### 1. WebSocket Infrastructure (Week 6 - Day 1-2)

#### File: `backend/app/websocket/connection_manager.py`

**Purpose**: Manage WebSocket connections and subscriptions

```python
from typing import Dict, Set, List
from fastapi import WebSocket
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class WebSocketConnection:
    """Represents a single WebSocket connection"""
    websocket: WebSocket
    client_id: str
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)

class ConnectionManager:
    """Manages all active WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocketConnection] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        connection = WebSocketConnection(
            websocket=websocket,
            client_id=client_id
        )
        self.active_connections[client_id] = connection

    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    def subscribe(self, client_id: str, event_type: str):
        """Subscribe client to event type"""
        if client_id in self.active_connections:
            self.active_connections[client_id].subscriptions.add(event_type)

    def unsubscribe(self, client_id: str, event_type: str):
        """Unsubscribe client from event type"""
        if client_id in self.active_connections:
            self.active_connections[client_id].subscriptions.discard(event_type)

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast event to all subscribed clients"""
        for client_id, conn in list(self.active_connections.items()):
            if self._should_send(conn, event_type):
                try:
                    await conn.websocket.send_json({
                        "type": event_type,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    # Client disconnected, remove it
                    self.disconnect(client_id)

    def _should_send(self, conn: WebSocketConnection, event_type: str) -> bool:
        """Check if event should be sent to connection"""
        if "*" in conn.subscriptions:  # Wildcard subscription
            return True
        if event_type in conn.subscriptions:  # Exact match
            return True
        # Prefix match (e.g., "task.*" matches "task.created")
        for sub in conn.subscriptions:
            if sub.endswith(".*"):
                prefix = sub[:-2]
                if event_type.startswith(prefix + "."):
                    return True
        return False

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
```

#### File: `backend/app/websocket/events.py`

**Purpose**: Event types and schemas

```python
from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel
from datetime import datetime

class EventType(str, Enum):
    """WebSocket event types"""
    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_DELETED = "task.deleted"

    # Connection events
    CONNECTION_CREATED = "connection.created"
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_DISCONNECTED = "connection.disconnected"
    CONNECTION_DELETED = "connection.deleted"

    # Graph events
    GRAPH_CREATED = "graph.created"
    GRAPH_EXECUTED = "graph.executed"
    GRAPH_DELETED = "graph.deleted"

    # Execution events
    EXECUTION_STARTED = "execution.started"
    EXECUTION_PROGRESS = "execution.progress"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"

    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_STATUS_CHANGED = "agent.status_changed"
    AGENT_DELETED = "agent.deleted"

    # System events
    SYSTEM_STATS = "system.stats"

class WebSocketEvent(BaseModel):
    """WebSocket event message"""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class SubscriptionRequest(BaseModel):
    """Client subscription request"""
    action: str  # "subscribe" or "unsubscribe"
    event_types: list[str]  # ["task.*", "execution.progress"]

class SubscriptionResponse(BaseModel):
    """Server subscription response"""
    status: str  # "success" or "error"
    message: str
    active_subscriptions: list[str]
```

#### File: `backend/app/websocket/__init__.py`

```python
"""WebSocket real-time events module"""

from app.websocket.connection_manager import ConnectionManager
from app.websocket.events import EventType, WebSocketEvent

# Global connection manager instance
connection_manager = ConnectionManager()

__all__ = ["connection_manager", "ConnectionManager", "EventType", "WebSocketEvent"]
```

---

### 2. WebSocket Endpoint (Week 6 - Day 2-3)

#### File: `backend/app/api/websocket.py`

**Purpose**: WebSocket endpoint implementation

```python
"""WebSocket API Endpoint for Real-time Events"""

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from app.websocket import connection_manager
from app.websocket.events import SubscriptionRequest, SubscriptionResponse

router = APIRouter()

@router.websocket("/ws/events")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time event streaming

    Connection URL: ws://localhost:8000/ws/events?client_id=xxx

    Message Protocol:

    Client → Server (Subscribe):
    {
        "action": "subscribe",
        "event_types": ["task.*", "execution.progress"]
    }

    Client → Server (Unsubscribe):
    {
        "action": "unsubscribe",
        "event_types": ["task.*"]
    }

    Client → Server (Ping):
    {
        "action": "ping"
    }

    Server → Client (Event):
    {
        "type": "task.created",
        "data": { ... },
        "timestamp": "2025-01-15T10:30:00Z"
    }

    Server → Client (Pong):
    {
        "type": "pong",
        "timestamp": "2025-01-15T10:30:00Z"
    }
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())

    # Accept connection
    await connection_manager.connect(websocket, client_id)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "client_id": client_id,
        "message": "Connected to Meta-Orchestrator Switchboard",
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
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
                conn = connection_manager.active_connections.get(client_id)
                await websocket.send_json({
                    "type": "subscription.success",
                    "active_subscriptions": list(conn.subscriptions) if conn else [],
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif action == "unsubscribe":
                # Unsubscribe from event types
                event_types = data.get("event_types", [])
                for event_type in event_types:
                    connection_manager.unsubscribe(client_id, event_type)

                # Send confirmation
                conn = connection_manager.active_connections.get(client_id)
                await websocket.send_json({
                    "type": "subscription.updated",
                    "active_subscriptions": list(conn.subscriptions) if conn else [],
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif action == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        # Client disconnected
        connection_manager.disconnect(client_id)
    except Exception as e:
        # Error occurred, disconnect client
        print(f"WebSocket error for client {client_id}: {e}")
        connection_manager.disconnect(client_id)
```

---

### 3. Event Integration with REST API (Week 6 - Day 3-5)

#### Update: `backend/app/api/tasks.py`

Add event broadcasting after database operations:

```python
from app.websocket import connection_manager
from app.websocket.events import EventType

@router.post("", response_model=TaskResponse, ...)
async def create_task(request: TaskCreateRequest, repo: TaskRepository = Depends(...)):
    # ... existing code ...
    task_model = await repo.create_task(task)
    task = repo.to_domain(task_model)

    # 🆕 Broadcast event
    await connection_manager.broadcast(
        EventType.TASK_CREATED,
        {"task": task_to_response(task).dict()}
    )

    return task_to_response(task)

@router.put("/{task_id}/start", ...)
async def start_task(task_id: str, ...):
    # ... existing code ...
    task.start()
    task_model = await repo.update(...)

    # 🆕 Broadcast event
    await connection_manager.broadcast(
        EventType.TASK_STARTED,
        {"task": task_to_response(task).dict()}
    )

    return task_to_response(task)

# Similar for complete, fail, delete...
```

#### Update: `backend/app/api/connections.py`

```python
@router.put("/{connection_id}/establish", ...)
async def establish_connection(connection_id: str, ...):
    # ... existing code ...
    connection.establish(socket_from, socket_to)
    conn_model = await repo.update(...)

    # 🆕 Broadcast event
    await connection_manager.broadcast(
        EventType.CONNECTION_ESTABLISHED,
        {"connection": connection_to_response(connection).dict()}
    )

    return connection_to_response(connection)
```

#### Update: `backend/app/api/graphs.py`

```python
@router.post("/{graph_id}/execute", ...)
async def execute_graph(graph_id: str, ...):
    # ... existing code ...
    execution.start()
    exec_model = await exec_repo.create_execution(execution)

    # 🆕 Broadcast event
    await connection_manager.broadcast(
        EventType.EXECUTION_STARTED,
        {"execution": execution_to_response(execution).dict()}
    )

    return execution_to_response(execution)
```

---

### 4. WebSocket Test Client (Week 7)

#### File: `backend/tests/test_websocket_client.py`

```python
"""WebSocket client for testing real-time events"""

import asyncio
import json
from websockets import connect

async def test_websocket():
    uri = "ws://localhost:8000/ws/events"

    async with connect(uri) as websocket:
        # Receive welcome message
        welcome = await websocket.recv()
        print(f"Connected: {welcome}")

        # Subscribe to task events
        await websocket.send(json.dumps({
            "action": "subscribe",
            "event_types": ["task.*", "execution.*"]
        }))

        # Receive subscription confirmation
        confirmation = await websocket.recv()
        print(f"Subscribed: {confirmation}")

        # Listen for events
        print("\n🎧 Listening for events...\n")
        while True:
            message = await websocket.recv()
            event = json.loads(message)
            print(f"📨 Event: {event['type']}")
            print(f"   Data: {json.dumps(event.get('data', {}), indent=2)}")
            print()

if __name__ == "__main__":
    asyncio.run(test_websocket())
```

---

## 📊 Event Types Reference

### Task Events

| Event | Trigger | Data |
|-------|---------|------|
| `task.created` | POST /tasks | Full task object |
| `task.started` | PUT /tasks/{id}/start | Full task object |
| `task.completed` | PUT /tasks/{id}/complete | Full task object with result |
| `task.failed` | PUT /tasks/{id}/fail | Full task object with error |
| `task.deleted` | DELETE /tasks/{id} | Task ID only |

### Connection Events

| Event | Trigger | Data |
|-------|---------|------|
| `connection.created` | POST /connections | Full connection object |
| `connection.established` | PUT /connections/{id}/establish | Connection with socket numbers |
| `connection.disconnected` | PUT /connections/{id}/disconnect | Connection object |
| `connection.deleted` | DELETE /connections/{id} | Connection ID only |

### Graph & Execution Events

| Event | Trigger | Data |
|-------|---------|------|
| `graph.created` | POST /graphs | Full graph object |
| `graph.executed` | POST /graphs/{id}/execute | Execution object |
| `graph.deleted` | DELETE /graphs/{id} | Graph ID |
| `execution.started` | Execution start | Execution object |
| `execution.progress` | Progress update (future) | Progress percentage |
| `execution.completed` | Execution complete | Final execution object |
| `execution.failed` | Execution failed | Execution with error |

### Agent Events

| Event | Trigger | Data |
|-------|---------|------|
| `agent.created` | POST /agents | Full agent object |
| `agent.status_changed` | PUT /agents/{id} (status change) | Agent object |
| `agent.deleted` | DELETE /agents/{id} | Agent ID |

---

## 🧪 Testing Strategy

### Manual Testing

1. **Connection Test**
   ```bash
   # Terminal 1: Start server
   python backend/app/main.py

   # Terminal 2: Connect WebSocket client
   python backend/tests/test_websocket_client.py

   # Terminal 3: Trigger events via REST API
   curl -X POST http://localhost:8000/api/tasks \
     -H "Content-Type: application/json" \
     -d '{"description": "Test task", "task_type": "test"}'

   # Terminal 2 should show: task.created event
   ```

2. **Subscription Test**
   - Subscribe to `task.*` → should receive all task events
   - Subscribe to `task.created` → should receive only create events
   - Unsubscribe → should stop receiving events

3. **Multiple Clients**
   - Connect 2+ clients
   - Each subscribes to different event types
   - Verify each receives only subscribed events

### Automated Testing

```python
# backend/tests/test_websocket_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_connection():
    with TestClient(app).websocket_connect("/ws/events") as websocket:
        # Should receive welcome message
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert "client_id" in data

def test_websocket_subscription():
    with TestClient(app).websocket_connect("/ws/events") as websocket:
        websocket.receive_json()  # Welcome

        # Subscribe to task events
        websocket.send_json({
            "action": "subscribe",
            "event_types": ["task.*"]
        })

        # Should receive confirmation
        data = websocket.receive_json()
        assert data["type"] == "subscription.success"
        assert "task.*" in data["active_subscriptions"]
```

---

## 🚀 Deployment Considerations

### Single-Server Deployment (MVP)

- In-memory ConnectionManager works fine
- No external dependencies required
- All clients connect to same server instance

### Multi-Server Deployment (Future)

For horizontal scaling, use Redis pub/sub:

```python
# backend/app/websocket/redis_broadcaster.py

import redis.asyncio as redis
from app.core.config import settings

class RedisEventBroadcaster:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.pubsub = self.redis.pubsub()

    async def broadcast(self, event_type: str, data: dict):
        # Publish to Redis channel
        await self.redis.publish(
            "switchboard:events",
            json.dumps({"type": event_type, "data": data})
        )

    async def subscribe(self):
        # Subscribe to Redis channel
        await self.pubsub.subscribe("switchboard:events")
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                event = json.loads(message["data"])
                # Broadcast to local WebSocket connections
                await connection_manager.broadcast_local(
                    event["type"],
                    event["data"]
                )
```

---

## 📈 Performance Metrics

### Target Metrics

- **Connection Capacity**: 100+ concurrent WebSocket connections
- **Event Latency**: < 100ms from API call to client receive
- **Memory per Connection**: < 1 MB
- **CPU Usage**: < 5% with 50 active connections

### Monitoring

```python
# Add to websocket endpoint
@router.get("/ws/stats")
async def get_websocket_stats():
    return {
        "active_connections": connection_manager.get_connection_count(),
        "total_subscriptions": sum(
            len(conn.subscriptions)
            for conn in connection_manager.active_connections.values()
        )
    }
```

---

## 🎯 Success Criteria

Phase 4 is complete when:

- ✅ WebSocket endpoint `/ws/events` accepts connections
- ✅ Clients can subscribe/unsubscribe to event types
- ✅ All REST API operations broadcast events
- ✅ Multiple clients receive events in real-time (< 100ms)
- ✅ Disconnected clients are cleaned up properly
- ✅ Test client demonstrates full workflow
- ✅ Documentation updated with WebSocket usage

---

## 📝 Next Steps After Phase 4

**Phase 5: Frontend Integration**
- React frontend connects to WebSocket
- Real-time dashboard updates
- Task/connection/execution status displays
- No polling required

---

**Meta-Orchestrator Switchboard**
*Phase 4: WebSocket Real-time Updates*
**Status**: 🔄 In Progress
**Target Completion**: Week 8

