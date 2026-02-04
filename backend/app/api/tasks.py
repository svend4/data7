"""
Task API Endpoints
CRUD operations for tasks
Based on TECHNICAL_SPEC_PART3_API.md
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Query

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

# In-memory storage for MVP
# TODO: Replace with database in Phase 1
tasks_db: Dict[str, Task] = {}

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
async def create_task(request: TaskCreateRequest) -> TaskResponse:
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

    # Store in database
    tasks_db[task.id] = task

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
) -> TaskListResponse:
    """List all tasks with optional filters"""
    tasks = list(tasks_db.values())

    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t.status.value == status_filter]
    if assigned_agent_id:
        tasks = [t for t in tasks if t.assigned_agent_id == assigned_agent_id]
    if task_type:
        tasks = [t for t in tasks if t.task_type == task_type]

    # Sort by priority (high to low) then by created_at
    tasks.sort(key=lambda t: (-t.priority, t.created_at))

    task_responses = [task_to_response(task) for task in tasks]
    return TaskListResponse(tasks=task_responses, total=len(task_responses))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get Task",
    description="Get task by ID"
)
async def get_task(task_id: str) -> TaskResponse:
    """Get task by ID"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task_to_response(task)


@router.put(
    "/{task_id}/start",
    response_model=TaskResponse,
    summary="Start Task",
    description="Start task execution"
)
async def start_task(task_id: str, request: TaskStartRequest) -> TaskResponse:
    """Start task execution"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    try:
        task.start()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return task_to_response(task)


@router.put(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete Task",
    description="Mark task as completed with result"
)
async def complete_task(task_id: str, request: TaskCompleteRequest) -> TaskResponse:
    """Complete task with result"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    try:
        task.complete(request.result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return task_to_response(task)


@router.put(
    "/{task_id}/fail",
    response_model=TaskResponse,
    summary="Fail Task",
    description="Mark task as failed with error message"
)
async def fail_task(task_id: str, request: TaskFailRequest) -> TaskResponse:
    """Mark task as failed"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    try:
        task.fail(request.error)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return task_to_response(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Remove task from system"
)
async def delete_task(task_id: str):
    """Delete task"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    del tasks_db[task_id]


@router.get(
    "/stats/summary",
    response_model=Dict,
    summary="Task Statistics",
    description="Get aggregate statistics for all tasks"
)
async def get_task_stats() -> Dict:
    """Get task statistics"""
    tasks = list(tasks_db.values())
    total = len(tasks)

    if total == 0:
        return {
            "total_tasks": 0,
            "pending": 0,
            "queued": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "avg_duration_seconds": 0.0,
            "success_rate": 0.0,
        }

    pending = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
    queued = sum(1 for t in tasks if t.status == TaskStatus.QUEUED)
    running = sum(1 for t in tasks if t.status == TaskStatus.RUNNING)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

    # Calculate average duration for completed tasks
    completed_tasks = [t for t in tasks if t.duration_seconds is not None]
    avg_duration = (
        sum(t.duration_seconds for t in completed_tasks) / len(completed_tasks)
        if completed_tasks else 0.0
    )

    # Calculate success rate
    finished_tasks = completed + failed
    success_rate = completed / finished_tasks if finished_tasks > 0 else 0.0

    return {
        "total_tasks": total,
        "pending": pending,
        "queued": queued,
        "running": running,
        "completed": completed,
        "failed": failed,
        "avg_duration_seconds": round(avg_duration, 2),
        "success_rate": round(success_rate, 4),
    }
