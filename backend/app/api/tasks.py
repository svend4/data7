"""
Task API Endpoints
CRUD operations for tasks with database persistence
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.domain.entities import Task
from app.domain.value_objects import TaskStatus
from app.schemas.task import (
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    TaskStartRequest,
    TaskCompleteRequest,
    TaskFailRequest,
)
from app.infrastructure.repositories import TaskRepository
from app.core.dependencies import get_task_repository

router = APIRouter(prefix="/tasks", tags=["tasks"])


def task_to_response(task: Task) -> TaskResponse:
    """Convert domain Task to API response"""
    return TaskResponse(
        id=task.id,
        description=task.description,
        task_type=task.task_type,
        status=task.status.value,
        priority=task.priority,
        assigned_agent_id=task.assigned_agent_id,
        result=task.result,
        error=task.error,
        metadata=task.metadata,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        duration_seconds=task.duration_seconds,
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="Create a new task in the system"
)
async def create_task(
    request: TaskCreateRequest,
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskResponse:
    """Create a new task"""
    # Create domain entity
    task = Task(
        description=request.description,
        task_type=request.task_type,
        priority=request.priority,
        metadata=request.metadata,
    )

    # Assign to agent if specified
    if request.assigned_agent_id:
        task.assign_to(request.assigned_agent_id)

    # Save to database
    try:
        task_model = await repo.create_task(task)
        task = repo.to_domain(task_model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

    return task_to_response(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List Tasks",
    description="Get all tasks with optional filtering"
)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    assigned_agent_id: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskListResponse:
    """List all tasks with optional filters"""
    try:
        # Convert status string to enum if provided
        status_enum = TaskStatus(status_filter) if status_filter else None

        # Get tasks with filters
        task_models = await repo.get_with_filters(
            status=status_enum,
            agent_id=assigned_agent_id,
            task_type=task_type,
            skip=0,
            limit=100
        )

        tasks = [repo.to_domain(model) for model in task_models]
        task_responses = [task_to_response(task) for task in tasks]

        return TaskListResponse(tasks=task_responses, total=len(task_responses))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value: {status_filter}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get Task",
    description="Get task by ID"
)
async def get_task(
    task_id: str,
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskResponse:
    """Get task by ID"""
    try:
        task_model = await repo.get_by_id(task_id)
        if not task_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        task = repo.to_domain(task_model)
        return task_to_response(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )


@router.put(
    "/{task_id}/start",
    response_model=TaskResponse,
    summary="Start Task",
    description="Start task execution"
)
async def start_task(
    task_id: str,
    request: TaskStartRequest,
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskResponse:
    """Start task execution"""
    try:
        # Get task
        task_model = await repo.get_by_id(task_id)
        if not task_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Convert to domain entity
        task = repo.to_domain(task_model)

        # Start task (domain logic)
        try:
            task.start()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Update in database
        task_model = await repo.update(
            task_id,
            status=task.status.value,
            started_at=task.started_at
        )

        task = repo.to_domain(task_model)
        return task_to_response(task)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start task: {str(e)}"
        )


@router.put(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete Task",
    description="Mark task as completed with result"
)
async def complete_task(
    task_id: str,
    request: TaskCompleteRequest,
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskResponse:
    """Complete task with result"""
    try:
        # Get task
        task_model = await repo.get_by_id(task_id)
        if not task_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Convert to domain entity
        task = repo.to_domain(task_model)

        # Complete task (domain logic)
        try:
            task.complete(request.result)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Update in database
        task_model = await repo.update(
            task_id,
            status=task.status.value,
            result=task.result,
            completed_at=task.completed_at
        )

        task = repo.to_domain(task_model)
        return task_to_response(task)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.put(
    "/{task_id}/fail",
    response_model=TaskResponse,
    summary="Fail Task",
    description="Mark task as failed with error message"
)
async def fail_task(
    task_id: str,
    request: TaskFailRequest,
    repo: TaskRepository = Depends(get_task_repository)
) -> TaskResponse:
    """Mark task as failed"""
    try:
        # Get task
        task_model = await repo.get_by_id(task_id)
        if not task_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Convert to domain entity
        task = repo.to_domain(task_model)

        # Fail task (domain logic)
        try:
            task.fail(request.error)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Update in database
        task_model = await repo.update(
            task_id,
            status=task.status.value,
            error=task.error,
            completed_at=task.completed_at
        )

        task = repo.to_domain(task_model)
        return task_to_response(task)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark task as failed: {str(e)}"
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Remove task from system"
)
async def delete_task(
    task_id: str,
    repo: TaskRepository = Depends(get_task_repository)
):
    """Delete task"""
    try:
        # Check if task exists
        exists = await repo.exists(task_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Delete from database
        await repo.delete(task_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=Dict,
    summary="Task Statistics",
    description="Get aggregate statistics for all tasks"
)
async def get_task_stats(
    repo: TaskRepository = Depends(get_task_repository)
) -> Dict[str, Any]:
    """Get task statistics"""
    try:
        stats = await repo.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
