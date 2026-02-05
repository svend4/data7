"""
Graph API Endpoints
Manage communication graphs and execution with database persistence
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import Dict, List
from fastapi import APIRouter, HTTPException, status, Depends

from app.domain.entities import CommunicationGraph, GraphExecution, Connection
from app.schemas.graph import (
    GraphCreateRequest,
    GraphResponse,
    GraphListResponse,
    GraphEdgeResponse,
    ExecutionStartRequest,
    ExecutionResponse,
)
from app.infrastructure.repositories import GraphRepository, ExecutionRepository
from app.core.dependencies import get_graph_repository, get_execution_repository

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
async def create_graph(
    request: GraphCreateRequest,
    repo: GraphRepository = Depends(get_graph_repository)
) -> GraphResponse:
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

    # Save to database
    try:
        graph_model = await repo.create_graph(graph)
        graph = repo.to_domain(graph_model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create graph: {str(e)}"
        )

    return graph_to_response(graph)


@router.get(
    "",
    response_model=GraphListResponse,
    summary="List Graphs",
    description="Get all communication graphs"
)
async def list_graphs(
    repo: GraphRepository = Depends(get_graph_repository)
) -> GraphListResponse:
    """List all graphs"""
    try:
        graph_models = await repo.get_all_with_edges()
        graphs = [repo.to_domain(model) for model in graph_models]
        graph_responses = [graph_to_response(graph) for graph in graphs]
        return GraphListResponse(graphs=graph_responses, total=len(graph_responses))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list graphs: {str(e)}"
        )


@router.get(
    "/{graph_id}",
    response_model=GraphResponse,
    summary="Get Graph",
    description="Get graph by ID"
)
async def get_graph(
    graph_id: str,
    repo: GraphRepository = Depends(get_graph_repository)
) -> GraphResponse:
    """Get graph by ID"""
    try:
        graph_model = await repo.get_with_edges(graph_id)
        if not graph_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Graph {graph_id} not found"
            )
        graph = repo.to_domain(graph_model)
        return graph_to_response(graph)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph: {str(e)}"
        )


@router.post(
    "/{graph_id}/execute",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Graph",
    description="Start execution of a communication graph"
)
async def execute_graph(
    graph_id: str,
    request: ExecutionStartRequest,
    graph_repo: GraphRepository = Depends(get_graph_repository),
    exec_repo: ExecutionRepository = Depends(get_execution_repository)
) -> ExecutionResponse:
    """Start graph execution"""
    try:
        # Check if graph exists
        graph_model = await graph_repo.get_with_edges(graph_id)
        if not graph_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Graph {graph_id} not found"
            )

        # Create execution
        execution = GraphExecution(graph_id=graph_id)
        execution.start()

        # Save to database
        exec_model = await exec_repo.create_execution(execution)
        execution = exec_repo.to_domain(exec_model)

        # In production, this would trigger async execution
        # For MVP, we just return the execution object
        # TODO: Implement actual graph execution logic in Phase 4

        return execution_to_response(execution)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute graph: {str(e)}"
        )


@router.get(
    "/{graph_id}/executions",
    response_model=List[ExecutionResponse],
    summary="List Graph Executions",
    description="Get all executions for a graph"
)
async def list_graph_executions(
    graph_id: str,
    graph_repo: GraphRepository = Depends(get_graph_repository),
    exec_repo: ExecutionRepository = Depends(get_execution_repository)
) -> List[ExecutionResponse]:
    """List all executions for a graph"""
    try:
        # Check if graph exists
        graph_exists = await graph_repo.exists(graph_id)
        if not graph_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Graph {graph_id} not found"
            )

        # Get executions
        exec_models = await exec_repo.get_by_graph(graph_id)
        executions = [exec_repo.to_domain(model) for model in exec_models]
        return [execution_to_response(exec) for exec in executions]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )


@router.delete(
    "/{graph_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Graph",
    description="Remove graph from system"
)
async def delete_graph(
    graph_id: str,
    repo: GraphRepository = Depends(get_graph_repository)
):
    """Delete graph"""
    try:
        # Check if graph exists
        exists = await repo.exists(graph_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Graph {graph_id} not found"
            )

        # Delete from database (cascades to edges and executions)
        await repo.delete(graph_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete graph: {str(e)}"
        )


# Execution endpoints
executions_router = APIRouter(prefix="/executions", tags=["executions"])


@executions_router.get(
    "/{execution_id}",
    response_model=ExecutionResponse,
    summary="Get Execution",
    description="Get execution status by ID"
)
async def get_execution(
    execution_id: str,
    repo: ExecutionRepository = Depends(get_execution_repository)
) -> ExecutionResponse:
    """Get execution by ID"""
    try:
        exec_model = await repo.get_by_id(execution_id)
        if not exec_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found"
            )
        execution = repo.to_domain(exec_model)
        return execution_to_response(execution)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )


@executions_router.put(
    "/{execution_id}/cancel",
    response_model=ExecutionResponse,
    summary="Cancel Execution",
    description="Cancel a running execution"
)
async def cancel_execution(
    execution_id: str,
    repo: ExecutionRepository = Depends(get_execution_repository)
) -> ExecutionResponse:
    """Cancel execution"""
    try:
        # Get execution
        exec_model = await repo.get_by_id(execution_id)
        if not exec_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found"
            )

        # Convert to domain entity
        execution = repo.to_domain(exec_model)

        # Cancel execution (domain logic)
        execution.fail()

        # Update in database
        exec_model = await repo.update(
            execution_id,
            status=execution.status.value,
            completed_at=execution.completed_at
        )

        execution = repo.to_domain(exec_model)
        return execution_to_response(execution)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel execution: {str(e)}"
        )
