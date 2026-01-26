"""
Base Repository interface for Domain-Driven Design
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from serp_core.domain.entity import Entity

TEntity = TypeVar("TEntity", bound=Entity)


class Repository(ABC, Generic[TEntity]):
    """
    Base repository interface for aggregate persistence.

    Repositories:
    - Provide collection-like interface for aggregates
    - Abstract away persistence details
    - Work with aggregate roots only
    - Use domain language in method names

    Example:
        class CustomerRepository(Repository[Customer]):
            async def find_by_email(self, email: str) -> Optional[Customer]:
                raise NotImplementedError

            async def find_active_customers(self) -> List[Customer]:
                raise NotImplementedError

        # Implementation in infrastructure layer
        class SQLAlchemyCustomerRepository(CustomerRepository):
            def __init__(self, session: AsyncSession):
                self.session = session

            async def save(self, customer: Customer) -> None:
                # SQLAlchemy implementation
                pass

            async def find_by_id(self, customer_id: UUID) -> Optional[Customer]:
                # SQLAlchemy implementation
                pass
    """

    @abstractmethod
    async def save(self, entity: TEntity) -> None:
        """
        Save (insert or update) an entity.

        Args:
            entity: The entity to save
        """
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> Optional[TEntity]:
        """
        Find an entity by its ID.

        Args:
            entity_id: The unique identifier

        Returns:
            The entity if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> List[TEntity]:
        """
        Find all entities.

        Returns:
            List of all entities
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: TEntity) -> None:
        """
        Delete an entity.

        Args:
            entity: The entity to delete
        """
        raise NotImplementedError

    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: The unique identifier

        Returns:
            True if entity exists, False otherwise
        """
        entity = await self.find_by_id(entity_id)
        return entity is not None


# Alias for interface-style naming convention
IRepository = Repository
