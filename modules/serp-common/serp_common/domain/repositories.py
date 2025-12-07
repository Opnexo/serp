"""
Repository interfaces for serp-common module.

These are abstract base classes that define the contract for data access.
Implementations are in the infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import Optional

from serp_common.domain.entities import AddressEntity, AddressType


class IAddressRepository(ABC):
    """Abstract repository for AddressEntity."""

    @abstractmethod
    async def get_by_id(self, address_id: str) -> Optional[AddressEntity]:
        """Get an address by ID."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        address_type: Optional[AddressType] = None,
        is_active: Optional[bool] = None,
    ) -> list[AddressEntity]:
        """List addresses with optional filters."""
        pass

    @abstractmethod
    async def count(
        self,
        owner_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        address_type: Optional[AddressType] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count addresses with optional filters."""
        pass

    @abstractmethod
    async def save(self, address: AddressEntity) -> AddressEntity:
        """Save (create or update) an address."""
        pass

    @abstractmethod
    async def delete(self, address_id: str) -> bool:
        """Delete an address by ID."""
        pass

    @abstractmethod
    async def get_primary_for_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> Optional[AddressEntity]:
        """Get the primary address for an owner."""
        pass

    @abstractmethod
    async def list_by_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> list[AddressEntity]:
        """List all addresses for an owner."""
        pass
