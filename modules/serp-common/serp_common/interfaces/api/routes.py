"""
API routes for serp-common module.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from serp_common.application.dto import (
    AddressCreateDTO,
    AddressDTO,
    AddressListDTO,
    AddressUpdateDTO,
)
from serp_common.application.services import AddressService
from serp_common.domain.repositories import IAddressRepository
from serp_common.infrastructure.persistence.repositories import InMemoryAddressRepository

router = APIRouter(prefix="/api/common", tags=["Common"])

# Repository singleton (in production, use DI from serp-shell)
_address_repo: Optional[IAddressRepository] = None


def get_address_repository() -> IAddressRepository:
    """Get address repository instance."""
    global _address_repo
    if _address_repo is None:
        _address_repo = InMemoryAddressRepository()
    return _address_repo


def get_address_service(
    repo: IAddressRepository = Depends(get_address_repository),
) -> AddressService:
    """Get address service instance."""
    return AddressService(repo)


@router.post(
    "/addresses",
    response_model=AddressDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
    description="Create a new address in the common module.",
)
async def create_address(
    dto: AddressCreateDTO,
    service: AddressService = Depends(get_address_service),
) -> AddressDTO:
    """Create a new address."""
    return await service.create_address(dto)


@router.get(
    "/addresses",
    response_model=AddressListDTO,
    summary="List addresses",
    description="List addresses with optional filters and pagination.",
)
async def list_addresses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    owner_type: Optional[str] = Query(None, description="Filter by owner type"),
    owner_id: Optional[str] = Query(None, description="Filter by owner ID"),
    address_type: Optional[str] = Query(
        None,
        description="Filter by address type",
        pattern="^(BILLING|SHIPPING|OFFICE|HOME|OTHER)$",
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: AddressService = Depends(get_address_service),
) -> AddressListDTO:
    """List addresses with pagination and filters."""
    return await service.list_addresses(
        skip=skip,
        limit=limit,
        owner_type=owner_type,
        owner_id=owner_id,
        address_type=address_type,
        is_active=is_active,
    )


@router.get(
    "/addresses/{address_id}",
    response_model=AddressDTO,
    summary="Get address by ID",
    description="Get a single address by its ID.",
)
async def get_address(
    address_id: str,
    service: AddressService = Depends(get_address_service),
) -> AddressDTO:
    """Get an address by ID."""
    address = await service.get_address(address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID '{address_id}' not found",
        )
    return address


@router.put(
    "/addresses/{address_id}",
    response_model=AddressDTO,
    summary="Update address",
    description="Update an existing address.",
)
async def update_address(
    address_id: str,
    dto: AddressUpdateDTO,
    service: AddressService = Depends(get_address_service),
) -> AddressDTO:
    """Update an address."""
    address = await service.update_address(address_id, dto)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID '{address_id}' not found",
        )
    return address


@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete address",
    description="Delete an address by ID.",
)
async def delete_address(
    address_id: str,
    service: AddressService = Depends(get_address_service),
) -> None:
    """Delete an address."""
    deleted = await service.delete_address(address_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID '{address_id}' not found",
        )


@router.get(
    "/addresses/owner/{owner_type}/{owner_id}",
    response_model=list[AddressDTO],
    summary="Get addresses for owner",
    description="Get all addresses belonging to a specific owner.",
)
async def get_addresses_for_owner(
    owner_type: str,
    owner_id: str,
    service: AddressService = Depends(get_address_service),
) -> list[AddressDTO]:
    """Get all addresses for an owner."""
    return await service.get_addresses_for_owner(owner_type, owner_id)


@router.get(
    "/addresses/owner/{owner_type}/{owner_id}/primary",
    response_model=AddressDTO,
    summary="Get primary address for owner",
    description="Get the primary address for a specific owner.",
)
async def get_primary_address(
    owner_type: str,
    owner_id: str,
    service: AddressService = Depends(get_address_service),
) -> AddressDTO:
    """Get the primary address for an owner."""
    address = await service.get_primary_address(owner_type, owner_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No primary address found for {owner_type}/{owner_id}",
        )
    return address
