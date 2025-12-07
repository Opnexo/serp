"""
PostgreSQL repository implementations.
"""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from serp_common.domain.entities import AddressEntity, AddressType
from serp_common.domain.repositories import IAddressRepository
from serp_common.infrastructure.persistence.mappers import AddressMapper
from serp_common.infrastructure.persistence.models import AddressModel


class PostgresAddressRepository(IAddressRepository):
    """PostgreSQL implementation of IAddressRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, address_id: str) -> Optional[AddressEntity]:
        """Get an address by ID."""
        result = await self._session.execute(
            select(AddressModel).where(AddressModel.id == address_id)
        )
        model = result.scalar_one_or_none()
        return AddressMapper.to_entity(model) if model else None

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
        query = select(AddressModel)

        # Apply filters
        if owner_type is not None:
            query = query.where(AddressModel.owner_type == owner_type)
        if owner_id is not None:
            query = query.where(AddressModel.owner_id == owner_id)
        if address_type is not None:
            query = query.where(AddressModel.address_type == address_type.value)
        if is_active is not None:
            query = query.where(AddressModel.is_active == is_active)

        # Order and paginate
        query = query.order_by(AddressModel.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [AddressMapper.to_entity(m) for m in models]

    async def count(
        self,
        owner_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        address_type: Optional[AddressType] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count addresses with optional filters."""
        query = select(func.count(AddressModel.id))

        if owner_type is not None:
            query = query.where(AddressModel.owner_type == owner_type)
        if owner_id is not None:
            query = query.where(AddressModel.owner_id == owner_id)
        if address_type is not None:
            query = query.where(AddressModel.address_type == address_type.value)
        if is_active is not None:
            query = query.where(AddressModel.is_active == is_active)

        result = await self._session.execute(query)
        return result.scalar() or 0

    async def save(self, address: AddressEntity) -> AddressEntity:
        """Save an address (create or update)."""
        # Check if exists
        result = await self._session.execute(
            select(AddressModel).where(AddressModel.id == address.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            AddressMapper.update_model(existing, address)
            await self._session.flush()
        else:
            # Create new
            model = AddressMapper.to_model(address)
            self._session.add(model)
            await self._session.flush()

        return address

    async def delete(self, address_id: str) -> bool:
        """Delete an address by ID."""
        result = await self._session.execute(
            select(AddressModel).where(AddressModel.id == address_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True

        return False

    async def get_primary_for_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> Optional[AddressEntity]:
        """Get the primary address for an owner."""
        result = await self._session.execute(
            select(AddressModel)
            .where(AddressModel.owner_type == owner_type)
            .where(AddressModel.owner_id == owner_id)
            .where(AddressModel.is_primary == True)  # noqa: E712
        )
        model = result.scalar_one_or_none()
        return AddressMapper.to_entity(model) if model else None

    async def list_by_owner(
        self,
        owner_type: str,
        owner_id: str,
    ) -> list[AddressEntity]:
        """List all addresses for an owner."""
        result = await self._session.execute(
            select(AddressModel)
            .where(AddressModel.owner_type == owner_type)
            .where(AddressModel.owner_id == owner_id)
            .order_by(AddressModel.is_primary.desc(), AddressModel.created_at.desc())
        )
        models = result.scalars().all()
        return [AddressMapper.to_entity(m) for m in models]
