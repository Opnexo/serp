"""
Unit of Work pattern for transaction management
"""

from abc import ABC, abstractmethod
from typing import Any


class UnitOfWork(ABC):
    """
    Unit of Work pattern for managing transactions.

    The UoW:
    - Groups operations into a transaction
    - Ensures atomicity (all or nothing)
    - Manages repository lifecycle
    - Commits or rolls back changes

    Example:
        class SQLAlchemyUnitOfWork(UnitOfWork):
            def __init__(self, session_factory: Callable):
                self.session_factory = session_factory
                self.session = None

            async def __aenter__(self):
                self.session = self.session_factory()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    await self.rollback()
                await self.session.close()

            async def commit(self) -> None:
                await self.session.commit()

            async def rollback(self) -> None:
                await self.session.rollback()

        # Usage:
        async with uow:
            customer = await customer_repository.find_by_id(customer_id)
            customer.change_email(new_email)
            await customer_repository.save(customer)
            await uow.commit()
    """

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Enter the context manager"""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit the context manager"""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction"""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction"""
        raise NotImplementedError
