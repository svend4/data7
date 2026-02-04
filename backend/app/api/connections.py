"""
Connection API Endpoints
Manage connections between agents
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.domain.entities import Connection
from app.domain.value_objects import ConnectionStatus
from app.schemas.connection import ConnectionCreateRequest, ConnectionResponse

# In-memory storage for MVP
# TODO: Replace with database in Phase 1
connections_db: Dict[str, Connection] = {}

# Simple socket allocation (1-100)
# In production, this would be managed by SwitchboardService
allocated_sockets: set = set()

router = APIRouter(prefix="/connections", tags=["connections"])


def connection_to_response(conn: Connection) -> ConnectionResponse:
    """Convert domain Connection to API response"""
    return ConnectionResponse(
        id=conn.id,
        from_agent_id=conn.from_agent_id,
        to_agent_id=conn.to_agent_id,
        status=conn.status.value,
        socket_from=conn.socket_from,
        socket_to=conn.socket_to,
        bandwidth=conn.bandwidth,
        latency_ms=conn.latency_ms,
        metadata=conn.metadata,
        established_at=conn.established_at,
        closed_at=conn.closed_at,
    )


def allocate_socket() -> Optional[int]:
    """Allocate next available socket (1-100)"""
    for socket_num in range(1, 101):
        if socket_num not in allocated_sockets:
            allocated_sockets.add(socket_num)
            return socket_num
    return None


def free_socket(socket_num: int) -> None:
    """Free a socket"""
    if socket_num in allocated_sockets:
        allocated_sockets.remove(socket_num)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Connection",
    description="Create a connection between two agents"
)
async def create_connection(request: ConnectionCreateRequest) -> ConnectionResponse:
    """Create a new connection"""
    # Validate agent IDs are different
    if request.from_agent_id == request.to_agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot connect agent to itself"
        )

    # Check if agents exist (in production, verify against agents_db)
    # For MVP, we skip this check

    # Create domain entity
    connection = Connection(
        from_agent_id=request.from_agent_id,
        to_agent_id=request.to_agent_id,
        bandwidth=request.bandwidth,
        metadata=request.metadata,
    )

    # Store in database
    connections_db[connection.id] = connection

    return connection_to_response(connection)


@router.get(
    "",
    response_model=List[ConnectionResponse],
    summary="List Connections",
    description="Get all connections with optional filtering"
)
async def list_connections(
    status_filter: Optional[str] = Query(None, alias="status"),
    agent_id: Optional[str] = Query(None),
) -> List[ConnectionResponse]:
    """List all connections with optional filters"""
    connections = list(connections_db.values())

    # Apply filters
    if status_filter:
        connections = [c for c in connections if c.status.value == status_filter]
    if agent_id:
        connections = [
            c for c in connections
            if c.from_agent_id == agent_id or c.to_agent_id == agent_id
        ]

    return [connection_to_response(conn) for conn in connections]


@router.get(
    "/{connection_id}",
    response_model=ConnectionResponse,
    summary="Get Connection",
    description="Get connection by ID"
)
async def get_connection(connection_id: str) -> ConnectionResponse:
    """Get connection by ID"""
    connection = connections_db.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found"
        )
    return connection_to_response(connection)


@router.put(
    "/{connection_id}/establish",
    response_model=ConnectionResponse,
    summary="Establish Connection",
    description="Establish connection and allocate sockets"
)
async def establish_connection(connection_id: str) -> ConnectionResponse:
    """Establish connection and allocate sockets"""
    connection = connections_db.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found"
        )

    # Allocate sockets
    socket_from = allocate_socket()
    socket_to = allocate_socket()

    if socket_from is None or socket_to is None:
        # Free any allocated socket
        if socket_from:
            free_socket(socket_from)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available sockets on switchboard"
        )

    try:
        connection.establish(socket_from, socket_to)
    except ValueError as e:
        # Free sockets on error
        free_socket(socket_from)
        free_socket(socket_to)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return connection_to_response(connection)


@router.put(
    "/{connection_id}/disconnect",
    response_model=ConnectionResponse,
    summary="Disconnect Connection",
    description="Disconnect connection and free sockets"
)
async def disconnect_connection(connection_id: str) -> ConnectionResponse:
    """Disconnect connection and free sockets"""
    connection = connections_db.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found"
        )

    # Free sockets
    if connection.socket_from:
        free_socket(connection.socket_from)
    if connection.socket_to:
        free_socket(connection.socket_to)

    try:
        connection.disconnect()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return connection_to_response(connection)


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Connection",
    description="Remove connection from system"
)
async def delete_connection(connection_id: str):
    """Delete connection"""
    connection = connections_db.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found"
        )

    # Free sockets if allocated
    if connection.socket_from:
        free_socket(connection.socket_from)
    if connection.socket_to:
        free_socket(connection.socket_to)

    del connections_db[connection_id]


@router.get(
    "/stats/summary",
    response_model=Dict,
    summary="Connection Statistics",
    description="Get aggregate statistics for all connections"
)
async def get_connection_stats() -> Dict:
    """Get connection statistics"""
    connections = list(connections_db.values())
    total = len(connections)

    if total == 0:
        return {
            "total_connections": 0,
            "connected": 0,
            "disconnected": 0,
            "transmitting": 0,
            "available_sockets": 100,
            "avg_bandwidth": 0.0,
            "avg_latency_ms": 0.0,
        }

    connected = sum(1 for c in connections if c.status == ConnectionStatus.CONNECTED)
    disconnected = sum(1 for c in connections if c.status == ConnectionStatus.DISCONNECTED)
    transmitting = sum(1 for c in connections if c.status == ConnectionStatus.TRANSMITTING)

    avg_bandwidth = sum(c.bandwidth for c in connections) / total
    avg_latency = sum(c.latency_ms for c in connections) / total

    return {
        "total_connections": total,
        "connected": connected,
        "disconnected": disconnected,
        "transmitting": transmitting,
        "available_sockets": 100 - len(allocated_sockets),
        "avg_bandwidth": round(avg_bandwidth, 3),
        "avg_latency_ms": round(avg_latency, 2),
    }
