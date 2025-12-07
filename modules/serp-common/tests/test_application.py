"""Tests for application layer."""

import pytest
from serp_common.application.services import AddressService
from serp_common.application.dto import AddressCreateDTO, AddressUpdateDTO
from serp_common.infrastructure.persistence.repositories import InMemoryAddressRepository


@pytest.fixture
def repository():
    """Create a fresh repository for each test."""
    return InMemoryAddressRepository()


@pytest.fixture
def service(repository):
    """Create a service with the repository."""
    return AddressService(repository)


class TestAddressService:
    """Tests for AddressService."""

    @pytest.mark.asyncio
    async def test_create_address(self, service):
        """Test creating an address."""
        dto = AddressCreateDTO(
            label="Main Office",
            street="123 Main St",
            city="New York",
            country="US",
        )

        result = await service.create_address(dto)

        assert result.label == "Main Office"
        assert result.street == "123 Main St"
        assert result.city == "New York"
        assert result.country == "US"
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_get_address(self, service):
        """Test getting an address by ID."""
        # Create an address
        dto = AddressCreateDTO(
            label="Test",
            street="123 Main St",
            city="New York",
            country="US",
        )
        created = await service.create_address(dto)

        # Get it back
        result = await service.get_address(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.label == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_address(self, service):
        """Test getting a non-existent address."""
        result = await service.get_address("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_address(self, service):
        """Test updating an address."""
        # Create an address
        create_dto = AddressCreateDTO(
            label="Original",
            street="123 Main St",
            city="New York",
            country="US",
        )
        created = await service.create_address(create_dto)

        # Update it
        update_dto = AddressUpdateDTO(
            label="Updated",
            street="456 Oak Ave",
        )
        result = await service.update_address(created.id, update_dto)

        assert result is not None
        assert result.label == "Updated"
        assert result.street == "456 Oak Ave"
        assert result.city == "New York"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_address(self, service):
        """Test deleting an address."""
        # Create an address
        dto = AddressCreateDTO(
            label="Test",
            street="123 Main St",
            city="New York",
            country="US",
        )
        created = await service.create_address(dto)

        # Delete it
        deleted = await service.delete_address(created.id)
        assert deleted is True

        # Verify it's gone
        result = await service.get_address(created.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_list_addresses(self, service):
        """Test listing addresses."""
        # Create some addresses
        for i in range(3):
            dto = AddressCreateDTO(
                label=f"Address {i}",
                street=f"{i} Main St",
                city="New York",
                country="US",
            )
            await service.create_address(dto)

        # List them
        result = await service.list_addresses()

        assert result.total == 3
        assert len(result.items) == 3

    @pytest.mark.asyncio
    async def test_list_addresses_with_pagination(self, service):
        """Test listing addresses with pagination."""
        # Create 5 addresses
        for i in range(5):
            dto = AddressCreateDTO(
                label=f"Address {i}",
                street=f"{i} Main St",
                city="New York",
                country="US",
            )
            await service.create_address(dto)

        # Get first page
        result = await service.list_addresses(skip=0, limit=2)

        assert result.total == 5
        assert len(result.items) == 2
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_primary_address_handling(self, service):
        """Test that setting a new primary unsets the old one."""
        # Create first address as primary
        dto1 = AddressCreateDTO(
            label="First",
            street="123 Main St",
            city="New York",
            country="US",
            owner_type="partner",
            owner_id="partner-1",
            is_primary=True,
        )
        addr1 = await service.create_address(dto1)
        assert addr1.is_primary is True

        # Create second address as primary for same owner
        dto2 = AddressCreateDTO(
            label="Second",
            street="456 Oak Ave",
            city="New York",
            country="US",
            owner_type="partner",
            owner_id="partner-1",
            is_primary=True,
        )
        addr2 = await service.create_address(dto2)

        # First should no longer be primary
        addr1_updated = await service.get_address(addr1.id)
        assert addr1_updated is not None
        assert addr1_updated.is_primary is False
        assert addr2.is_primary is True
