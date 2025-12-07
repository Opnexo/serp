"""
In-memory repository implementations for testing.
"""

from typing import Optional

from serp_common.domain.entities import AddressEntity, AddressType
from serp_common.domain.repositories import IAddressRepository


class InMemoryAddressRepository(IAddressRepository):
    """In-memory implementation of IAddressRepository for testing."""

    def __init__(self):
        self._addresses: dict[str, AddressEntity] = {}

    async def get_by_id(self, address_id: str) -> Optional[AddressEntity]:
        """Get an address by ID."""
        return self._addresses.get(address_id)

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
        addresses = list(self._addresses.values())

        # Apply filters
        if owner_type is not None:
            addresses = [a for a in addresses if a.owner_type == owner_type]
        if owner_id is not None:
            addresses = [a for a in addresses if a.owner_id == owner_id]
        if address_type is not None:
            addresses = [a for a in addresses if a.address_type == address_type]
        if is_active is not None:
            addresses = [a for a in addresses if a.is_active == is_active]

        # Sort by created_at descending
        addresses.sort(key=lambda a: a.created_at, reverse=True)

        # Apply pagination
        return addresses[skip : skip + limit]

    async def count(
        self,
        owner_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        address_type: Optional[AddressType] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count addresses with optional filters."""
        addresses = list(self._addresses.values())

        if owner_type is not None:
            addresses = [a for a in addresses if a.owner_type == owner_type]
        if owner_id is not None:
            addresses = [a for a in addresses if a.owner_id == owner_id]
        if address_type is not None:
            addresses = [a for a in addresses if a.address_type == address_type]
        if is_active is not None:
            addresses = [a for a in addresses if a.is_active == is_active]

        return len(addresses)

    async def save(self, address: AddressEntity) -> AddressEntity:
        """Save an address."""
        self._addresses[address.id] = address
        return address

    async def delete(self, address_id: str) -> bool:
        """Delete an address by ID."""
        if address_id in self._addresses:
            del self._addresses[address_id]
            return True
        return False

    async def get_primary_for_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> Optional[AddressEntity]:
        """Get the primary address for an owner."""
        for address in self._addresses.values():
            if (
                address.owner_type == owner_type
                and address.owner_id == owner_id
                and address.is_primary
            ):
                return address
        return None

    async def list_by_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> list[AddressEntity]:
        """List all addresses for an owner."""
        return [
            a
            for a in self._addresses.values()
            if a.owner_type == owner_type and a.owner_id == owner_id
        ]

    def clear(self) -> None:
        """Clear all addresses (for testing)."""
        self._addresses.clear()
