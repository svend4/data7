"""
Graph API Endpoints
Manage communication graphs and execution
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, status

from app.domain.entities import CommunicationGraph, GraphExecution, Connection
from app.schemas.graph import (
    GraphCreateRequest,
    GraphResponse,
    GraphListResponse,
    GraphEdgeResponse,
    ExecutionStartRequest,
    ExecutionResponse,
)

# In-memory storage for MVP
# TODO: Replace with database in Phase 1
graphs_db: Dict[str, CommunicationGraph] = {}
executions_db: Dict[str, GraphExecution] = {}

router = APIRouter(prefix="/graphs", tags=["graphs"])


def graph_to_response(graph: CommunicationGraph) -> GraphResponse:
    """Convert domain Graph to API response"""
    edge_responses = [
        GraphEdgeResponse(
            id=edge.id,
            from_agent_id=edge.from_agent_id,
            to_agent_id=edge.to_agent_id,
            status=edge.status.value,
            bandwidth=edge.bandwidth,
        )
        for edge in graph.edges
    ]

    return GraphResponse(
        id=graph.id,
        root_task_id=graph.root_task_id,
        nodes=graph.nodes,
        edges=edge_responses,
        execution_plan=graph.execution_plan,
        metadata=graph.metadata,
        created_at=graph.created_at,
    )


def execution_to_response(execution: GraphExecution) -> ExecutionResponse:
    """Convert domain GraphExecution to API response"""
    return ExecutionResponse(
        id=execution.id,
        graph_id=execution.graph_id,
        status=execution.status.value,
        current_step=execution.current_step,
        completed_tasks=execution.completed_tasks,
        failed_tasks=execution.failed_tasks,
        active_connections=execution.active_connections,
        results=execution.results,
        progress=execution.progress,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
    )


@router.post(
    "",
    response_model=GraphResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Graph",
    description="Create a communication graph for multi-agent coordination"
)
async def create_graph(request: GraphCreateRequest) -> GraphResponse:
    """Create a new communication graph"""
    # Create domain entity
    graph = CommunicationGraph(
        root_task_id=request.root_task_id,
        nodes=request.nodes.copy(),
        execution_plan=request.execution_plan.copy(),
        metadata=request.metadata,
    )

    # Add edges (connections)
    for edge_req in request.edges:
        connection = Connection(
            from_agent_id=edge_req.from_agent_id,
            to_agent_id=edge_req.to_agent_id,
            bandwidth=edge_req.bandwidth,
        )
        graph.add_edge(connection)

    # Store in database
    graphs_db[graph.id] = graph

    return graph_to_response(graph)


@router.get(
    "",
    response_model=GraphListResponse,
    summary="List Graphs",
    description="Get all communication graphs"
)
async def list_graphs() -> GraphListResponse:
    """List all graphs"""
    graphs = [graph_to_response(graph) for graph in graphs_db.values()]
    return GraphListResponse(graphs=graphs, total=len(graphs))


@router.get(
    "/{graph_id}",
    response_model=GraphResponse,
    summary="Get Graph",
    description="Get graph by ID"
)
async def get_graph(graph_id: str) -> GraphResponse:
    """Get graph by ID"""
    graph = graphs_db.get(graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph {graph_id} not found"
        )
    return graph_to_response(graph)


@router.post(
    "/{graph_id}/execute",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Graph",
    description="Start execution of a communication graph"
)
async def execute_graph(
    graph_id: str,
    request: ExecutionStartRequest
) -> ExecutionResponse:
    """Start graph execution"""
    graph = graphs_db.get(graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph {graph_id} not found"
        )

    # Create execution
    execution = GraphExecution(graph_id=graph_id)
    execution.start()

    # Store in database
    executions_db[execution.id] = execution

    # In production, this would trigger async execution
    # For MVP, we just return the execution object
    # TODO: Implement actual graph execution logic in Phase 2

    return execution_to_response(execution)


@router.get(
    "/{graph_id}/executions",
    response_model=list[ExecutionResponse],
    summary="List Graph Executions",
    description="Get all executions for a graph"
)
async def list_graph_executions(graph_id: str) -> list[ExecutionResponse]:
    """List all executions for a graph"""
    graph = graphs_db.get(graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph {graph_id} not found"
        )

    executions = [
        execution_to_response(exec)
        for exec in executions_db.values()
        if exec.graph_id == graph_id
    ]

    return executions


@router.delete(
    "/{graph_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Graph",
    description="Remove graph from system"
)
async def delete_graph(graph_id: str):
    """Delete graph"""
    if graph_id not in graphs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph {graph_id} not found"
        )
    del graphs_db[graph_id]


# Execution endpoints
executions_router = APIRouter(prefix="/executions", tags=["executions"])


@executions_router.get(
    "/{execution_id}",
    response_model=ExecutionResponse,
    summary="Get Execution",
    description="Get execution status by ID"
)
async def get_execution(execution_id: str) -> ExecutionResponse:
    """Get execution by ID"""
    execution = executions_db.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )
    return execution_to_response(execution)


@executions_router.put(
    "/{execution_id}/cancel",
    response_model=ExecutionResponse,
    summary="Cancel Execution",
    description="Cancel a running execution"
)
async def cancel_execution(execution_id: str) -> ExecutionResponse:
    """Cancel execution"""
    execution = executions_db.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    # Cancel execution
    execution.fail()

    return execution_to_response(execution)


# Register both routers
routers = [router, executions_router]
