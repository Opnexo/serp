"""Tests for domain layer."""

import pytest
from serp_common.domain.entities import AddressEntity, AddressType


class TestAddressEntity:
    """Tests for AddressEntity."""

    def test_create_address(self):
        """Test creating a basic address."""
        address = AddressEntity(
            label="Main Office",
            street="123 Main St",
            city="New York",
            country="US",
        )

        assert address.label == "Main Office"
        assert address.street == "123 Main St"
        assert address.city == "New York"
        assert address.country == "US"
        assert address.is_active is True
        assert address.is_primary is False
        assert address.address_type == AddressType.OTHER

    def test_create_address_with_all_fields(self):
        """Test creating an address with all fields."""
        address = AddressEntity(
            label="Billing Address",
            street="456 Oak Ave",
            city="Los Angeles",
            state="CA",
            postal_code="90001",
            country="US",
            address_type=AddressType.BILLING,
            is_primary=True,
            notes="Main billing address",
        )

        assert address.state == "CA"
        assert address.postal_code == "90001"
        assert address.address_type == AddressType.BILLING
        assert address.is_primary is True
        assert address.notes == "Main billing address"

    def test_address_requires_street(self):
        """Test that street is required."""
        with pytest.raises(ValueError, match="Street is required"):
            AddressEntity(
                label="Test",
                street="",
                city="New York",
                country="US",
            )

    def test_address_requires_city(self):
        """Test that city is required."""
        with pytest.raises(ValueError, match="City is required"):
            AddressEntity(
                label="Test",
                street="123 Main St",
                city="",
                country="US",
            )

    def test_address_requires_country(self):
        """Test that country is required."""
        with pytest.raises(ValueError, match="Country is required"):
            AddressEntity(
                label="Test",
                street="123 Main St",
                city="New York",
                country="",
            )

    def test_update_address(self):
        """Test updating address fields."""
        address = AddressEntity(
            label="Original",
            street="123 Main St",
            city="New York",
            country="US",
        )

        original_updated = address.updated_at

        address.update(
            label="Updated Label",
            street="456 Oak Ave",
            city="Los Angeles",
        )

        assert address.label == "Updated Label"
        assert address.street == "456 Oak Ave"
        assert address.city == "Los Angeles"
        assert address.updated_at > original_updated

    def test_deactivate_address(self):
        """Test deactivating an address."""
        address = AddressEntity(
            label="Test",
            street="123 Main St",
            city="New York",
            country="US",
        )

        assert address.is_active is True
        address.deactivate()
        assert address.is_active is False

    def test_to_value_object(self):
        """Test converting to value object."""
        address = AddressEntity(
            label="Test",
            street="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US",
        )

        vo = address.to_value_object()

        assert vo.street == "123 Main St"
        assert vo.city == "New York"
        assert vo.state == "NY"
        assert vo.postal_code == "10001"
        assert vo.country == "US"

    def test_to_dict(self):
        """Test serialization to dict."""
        address = AddressEntity(
            label="Test",
            street="123 Main St",
            city="New York",
            country="US",
        )

        data = address.to_dict()

        assert data["label"] == "Test"
        assert data["street"] == "123 Main St"
        assert data["city"] == "New York"
        assert data["country"] == "US"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
