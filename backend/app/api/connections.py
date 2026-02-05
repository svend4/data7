"""
Connection API Endpoints
Manage connections between agents with database persistence
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.domain.entities import Connection
from app.domain.value_objects import ConnectionStatus
from app.schemas.connection import ConnectionCreateRequest, ConnectionResponse
from app.infrastructure.repositories import ConnectionRepository
from app.core.dependencies import get_connection_repository

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


async def allocate_socket(repo: ConnectionRepository) -> Optional[int]:
    """Allocate next available socket (1-100)"""
    allocated_sockets = await repo.get_allocated_sockets()
    for socket_num in range(1, 101):
        if socket_num not in allocated_sockets:
            return socket_num
    return None


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Connection",
    description="Create a connection between two agents"
)
async def create_connection(
    request: ConnectionCreateRequest,
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> ConnectionResponse:
    """Create a new connection"""
    # Validate agent IDs are different
    if request.from_agent_id == request.to_agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot connect agent to itself"
        )

    # Create domain entity
    connection = Connection(
        from_agent_id=request.from_agent_id,
        to_agent_id=request.to_agent_id,
        bandwidth=request.bandwidth,
        metadata=request.metadata,
    )

    # Save to database
    try:
        conn_model = await repo.create_connection(connection)
        connection = repo.to_domain(conn_model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connection: {str(e)}"
        )

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
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> List[ConnectionResponse]:
    """List all connections with optional filters"""
    try:
        # Convert status string to enum if provided
        status_enum = ConnectionStatus(status_filter) if status_filter else None

        # Get connections with filters
        conn_models = await repo.get_with_filters(
            status=status_enum,
            agent_id=agent_id,
            skip=0,
            limit=100
        )

        connections = [repo.to_domain(model) for model in conn_models]
        return [connection_to_response(conn) for conn in connections]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value: {status_filter}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list connections: {str(e)}"
        )


@router.get(
    "/{connection_id}",
    response_model=ConnectionResponse,
    summary="Get Connection",
    description="Get connection by ID"
)
async def get_connection(
    connection_id: str,
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> ConnectionResponse:
    """Get connection by ID"""
    try:
        conn_model = await repo.get_by_id(connection_id)
        if not conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection {connection_id} not found"
            )
        connection = repo.to_domain(conn_model)
        return connection_to_response(connection)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection: {str(e)}"
        )


@router.put(
    "/{connection_id}/establish",
    response_model=ConnectionResponse,
    summary="Establish Connection",
    description="Establish connection and allocate sockets"
)
async def establish_connection(
    connection_id: str,
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> ConnectionResponse:
    """Establish connection and allocate sockets"""
    try:
        # Get connection
        conn_model = await repo.get_by_id(connection_id)
        if not conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection {connection_id} not found"
            )

        # Convert to domain entity
        connection = repo.to_domain(conn_model)

        # Allocate sockets
        socket_from = await allocate_socket(repo)
        socket_to = await allocate_socket(repo)

        if socket_from is None or socket_to is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No available sockets on switchboard"
            )

        # Establish connection (domain logic)
        try:
            connection.establish(socket_from, socket_to)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Update in database
        conn_model = await repo.update(
            connection_id,
            status=connection.status.value,
            socket_from=connection.socket_from,
            socket_to=connection.socket_to,
            established_at=connection.established_at
        )

        connection = repo.to_domain(conn_model)
        return connection_to_response(connection)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to establish connection: {str(e)}"
        )


@router.put(
    "/{connection_id}/disconnect",
    response_model=ConnectionResponse,
    summary="Disconnect Connection",
    description="Disconnect connection and free sockets"
)
async def disconnect_connection(
    connection_id: str,
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> ConnectionResponse:
    """Disconnect connection and free sockets"""
    try:
        # Get connection
        conn_model = await repo.get_by_id(connection_id)
        if not conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection {connection_id} not found"
            )

        # Convert to domain entity
        connection = repo.to_domain(conn_model)

        # Disconnect (domain logic)
        try:
            connection.disconnect()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Update in database
        # Sockets will be freed when status changes to DISCONNECTED
        conn_model = await repo.update(
            connection_id,
            status=connection.status.value,
            closed_at=connection.closed_at
        )

        connection = repo.to_domain(conn_model)
        return connection_to_response(connection)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect connection: {str(e)}"
        )


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Connection",
    description="Remove connection from system"
)
async def delete_connection(
    connection_id: str,
    repo: ConnectionRepository = Depends(get_connection_repository)
):
    """Delete connection"""
    try:
        # Check if connection exists
        exists = await repo.exists(connection_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection {connection_id} not found"
            )

        # Delete from database (sockets automatically freed by query)
        await repo.delete(connection_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete connection: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=Dict,
    summary="Connection Statistics",
    description="Get aggregate statistics for all connections"
)
async def get_connection_stats(
    repo: ConnectionRepository = Depends(get_connection_repository)
) -> Dict:
    """Get connection statistics"""
    try:
        stats = await repo.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
