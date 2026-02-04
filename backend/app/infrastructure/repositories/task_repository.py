"""
Task Repository
Database operations for tasks
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import TaskModel
from app.infrastructure.repositories.base import BaseRepository
from app.domain.entities import Task
from app.domain.value_objects import TaskStatus


class TaskRepository(BaseRepository[TaskModel]):
    """Repository for Task operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(TaskModel, session)

    async def create_task(self, task: Task) -> TaskModel:
        """
        Create task

        Args:
            task: Domain Task entity

        Returns:
            Created TaskModel
        """
        task_model = TaskModel(
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
        )

        self.session.add(task_model)
        await self.session.flush()
        await self.session.refresh(task_model)

        return task_model

    async def get_by_status(self, status: TaskStatus) -> List[TaskModel]:
        """Get tasks by status"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.status == status.value)
        )
        return list(result.scalars().all())

    async def get_by_agent(self, agent_id: str) -> List[TaskModel]:
        """Get tasks assigned to an agent"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.assigned_agent_id == agent_id)
        )
        return list(result.scalars().all())

    async def get_by_type(self, task_type: str) -> List[TaskModel]:
        """Get tasks by type"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.task_type == task_type)
        )
        return list(result.scalars().all())

    async def get_with_filters(
        self,
        status: Optional[TaskStatus] = None,
        agent_id: Optional[str] = None,
        task_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskModel]:
        """Get tasks with multiple filters"""
        query = select(TaskModel)

        if status:
            query = query.where(TaskModel.status == status.value)
        if agent_id:
            query = query.where(TaskModel.assigned_agent_id == agent_id)
        if task_type:
            query = query.where(TaskModel.task_type == task_type)

        query = query.order_by(TaskModel.priority.desc(), TaskModel.created_at).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        # Count by status
        total_query = select(func.count()).select_from(TaskModel)
        pending_query = total_query.where(TaskModel.status == TaskStatus.PENDING.value)
        queued_query = total_query.where(TaskModel.status == TaskStatus.QUEUED.value)
        running_query = total_query.where(TaskModel.status == TaskStatus.RUNNING.value)
        completed_query = total_query.where(TaskModel.status == TaskStatus.COMPLETED.value)
        failed_query = total_query.where(TaskModel.status == TaskStatus.FAILED.value)

        total_result = await self.session.execute(total_query)
        pending_result = await self.session.execute(pending_query)
        queued_result = await self.session.execute(queued_query)
        running_result = await self.session.execute(running_query)
        completed_result = await self.session.execute(completed_query)
        failed_result = await self.session.execute(failed_query)

        total = total_result.scalar_one()
        pending = pending_result.scalar_one()
        queued = queued_result.scalar_one()
        running = running_result.scalar_one()
        completed = completed_result.scalar_one()
        failed = failed_result.scalar_one()

        # Calculate average duration for completed tasks
        avg_duration = 0.0
        if completed > 0:
            # Calculate duration in SQL
            duration_query = select(
                func.avg(
                    func.extract('epoch', TaskModel.completed_at) -
                    func.extract('epoch', TaskModel.started_at)
                )
            ).where(
                TaskModel.status == TaskStatus.COMPLETED.value,
                TaskModel.started_at.isnot(None),
                TaskModel.completed_at.isnot(None)
            )
            duration_result = await self.session.execute(duration_query)
            avg_duration = float(duration_result.scalar_one() or 0.0)

        # Calculate success rate
        finished = completed + failed
        success_rate = completed / finished if finished > 0 else 0.0

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

    def to_domain(self, model: TaskModel) -> Task:
        """Convert SQLAlchemy model to domain entity"""
        task = Task(
            description=model.description,
            task_type=model.task_type,
            id=model.id,
            status=TaskStatus(model.status),
            priority=model.priority,
            assigned_agent_id=model.assigned_agent_id,
            result=model.result,
            error=model.error,
            metadata=model.metadata,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

        return task
