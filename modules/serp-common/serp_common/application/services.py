"""
Application services for serp-common module.

Services orchestrate domain logic and handle use cases.
"""

from typing import Optional

from serp_common.application.dto import (
    AddressCreateDTO,
    AddressDTO,
    AddressListDTO,
    AddressUpdateDTO,
)
from serp_common.domain.entities import AddressEntity, AddressType
from serp_common.domain.repositories import IAddressRepository


class AddressService:
    """Service for managing addresses."""

    def __init__(self, address_repository: IAddressRepository):
        self._repository = address_repository

    async def create_address(self, dto: AddressCreateDTO) -> AddressDTO:
        """Create a new address."""
        # If this should be primary, unset other primaries for the owner
        if dto.is_primary and dto.owner_type and dto.owner_id:
            await self._unset_primary_for_owner(dto.owner_type, dto.owner_id)

        address = AddressEntity(
            label=dto.label,
            street=dto.street,
            city=dto.city,
            country=dto.country,
            state=dto.state,
            postal_code=dto.postal_code,
            address_type=AddressType(dto.address_type),
            owner_type=dto.owner_type,
            owner_id=dto.owner_id,
            is_primary=dto.is_primary,
            notes=dto.notes,
        )

        address = await self._repository.save(address)
        return self._to_dto(address)

    async def get_address(self, address_id: str) -> Optional[AddressDTO]:
        """Get an address by ID."""
        address = await self._repository.get_by_id(address_id)
        return self._to_dto(address) if address else None

    async def update_address(
        self,
        address_id: str,
        dto: AddressUpdateDTO,
    ) -> Optional[AddressDTO]:
        """Update an address."""
        address = await self._repository.get_by_id(address_id)
        if not address:
            return None

        # If setting as primary, unset other primaries for the owner
        if dto.is_primary and address.owner_type and address.owner_id:
            await self._unset_primary_for_owner(
                address.owner_type,
                address.owner_id,
                exclude_id=address_id,
            )

        address.update(
            label=dto.label,
            street=dto.street,
            city=dto.city,
            country=dto.country,
            state=dto.state,
            postal_code=dto.postal_code,
            address_type=AddressType(dto.address_type) if dto.address_type else None,
            is_primary=dto.is_primary,
            notes=dto.notes,
        )

        address = await self._repository.save(address)
        return self._to_dto(address)

    async def delete_address(self, address_id: str) -> bool:
        """Delete an address."""
        return await self._repository.delete(address_id)

    async def list_addresses(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        address_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> AddressListDTO:
        """List addresses with pagination and filters."""
        addr_type = AddressType(address_type) if address_type else None

        addresses = await self._repository.list_all(
            skip=skip,
            limit=limit,
            owner_type=owner_type,
            owner_id=owner_id,
            address_type=addr_type,
            is_active=is_active,
        )

        total = await self._repository.count(
            owner_type=owner_type,
            owner_id=owner_id,
            address_type=addr_type,
            is_active=is_active,
        )

        return AddressListDTO(
            items=[self._to_dto(a) for a in addresses],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_addresses_for_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> list[AddressDTO]:
        """Get all addresses for an owner."""
        addresses = await self._repository.list_by_owner(owner_type, owner_id)
        return [self._to_dto(a) for a in addresses]

    async def get_primary_address(
        self,
        owner_type: str,
        owner_id: str,
    ) -> Optional[AddressDTO]:
        """Get the primary address for an owner."""
        address = await self._repository.get_primary_for_owner(owner_type, owner_id)
        return self._to_dto(address) if address else None

    async def _unset_primary_for_owner(
        self,
        owner_type: str,
        owner_id: str,
        exclude_id: Optional[str] = None,
    ) -> None:
        """Unset primary flag for all addresses of an owner."""
        addresses = await self._repository.list_by_owner(owner_type, owner_id)
        for address in addresses:
            if address.is_primary and address.id != exclude_id:
                address.is_primary = False
                await self._repository.save(address)

    def _to_dto(self, address: AddressEntity) -> AddressDTO:
        """Convert entity to DTO."""
        return AddressDTO(
            id=address.id,
            label=address.label,
            street=address.street,
            city=address.city,
            country=address.country,
            state=address.state,
            postal_code=address.postal_code,
            address_type=address.address_type.value,
            owner_type=address.owner_type,
            owner_id=address.owner_id,
            is_primary=address.is_primary,
            is_active=address.is_active,
            notes=address.notes,
            single_line=address.single_line,
            created_at=address.created_at,
            updated_at=address.updated_at,
        )
