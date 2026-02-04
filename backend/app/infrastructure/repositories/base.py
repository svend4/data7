"""
Base Repository Pattern
Generic repository for CRUD operations
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository for database operations

    Provides basic CRUD operations for any SQLAlchemy model
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record

        Args:
            **kwargs: Model fields

        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get record by ID

        Args:
            id: Primary key value

        Returns:
            Model instance or None if not found
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get all records with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by

        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)

        if order_by:
            query = query.order_by(getattr(self.model, order_by))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_filter(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get records by filter criteria

        Args:
            filters: Dict of field_name: value pairs
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        query = select(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID

        Args:
            id: Primary key value
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        # Get existing record
        instance = await self.get_by_id(id)
        if not instance:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: Any) -> bool:
        """
        Delete record by ID

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records

        Args:
            filters: Optional filter criteria

        Returns:
            Number of records
        """
        query = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists(self, id: Any) -> bool:
        """
        Check if record exists

        Args:
            id: Primary key value

        Returns:
            True if exists, False otherwise
        """
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        count = result.scalar_one()
        return count > 0
