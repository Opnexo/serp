"""
Tests for Partner entity and value objects.
"""

from decimal import Decimal

import pytest

from serp_crm.domain.entities import Partner, PartnerType
from serp_crm.domain.value_objects import Address, Email, Money, PhoneNumber


def test_create_partner():
    """Test creating a partner."""
    partner = Partner(
        name="Acme Corp",
        partner_type=PartnerType.COMPANY,
        is_customer=True,
        email=Email("contact@acme.com"),
    )

    assert partner.name == "Acme Corp"
    assert partner.partner_type == PartnerType.COMPANY
    assert partner.is_customer is True
    assert partner.is_supplier is False
    assert partner.is_active is True


def test_partner_name_validation():
    """Test partner name validation."""
    with pytest.raises(ValueError, match="at least 2 characters"):
        Partner(
            name="A",
            partner_type=PartnerType.INDIVIDUAL,
        )


def test_email_validation():
    """Test email validation."""
    # Valid email
    email = Email("test@example.com")
    assert str(email) == "test@example.com"

    # Invalid email
    with pytest.raises(ValueError, match="Invalid email"):
        Email("not-an-email")


def test_phone_validation():
    """Test phone number validation."""
    # Valid phone
    phone = PhoneNumber("+1-555-123-4567")
    assert phone.value  # Should be cleaned

    # Invalid phone
    with pytest.raises(ValueError, match="Invalid phone"):
        PhoneNumber("123")


def test_address_creation():
    """Test address creation."""
    address = Address(
        street="123 Main St",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
    )

    assert "New York" in str(address)
    assert address.country == "USA"


def test_money_operations():
    """Test money value object."""
    m1 = Money(Decimal("100.00"), "USD")
    m2 = Money(Decimal("50.00"), "USD")

    # Addition
    m3 = m1 + m2
    assert m3.amount == Decimal("150.00")
    assert m3.currency == "USD"

    # Subtraction
    m4 = m1 - m2
    assert m4.amount == Decimal("50.00")

    # Different currencies should fail
    m5 = Money(Decimal("100.00"), "EUR")
    with pytest.raises(ValueError, match="different currencies"):
        _ = m1 + m5


def test_partner_activation():
    """Test partner activation/deactivation."""
    partner = Partner(
        name="Test Partner",
        partner_type=PartnerType.COMPANY,
        is_active=False,
    )

    # Activate
    partner.activate()
    assert partner.is_active is True

    # Deactivate
    partner.deactivate()
    assert partner.is_active is False


def test_partner_tags():
    """Test partner tag management."""
    partner = Partner(
        name="Test Partner",
        partner_type=PartnerType.COMPANY,
    )

    # Add tags
    partner.add_tag("VIP")
    partner.add_tag("Enterprise")
    assert "VIP" in partner.tags
    assert "Enterprise" in partner.tags

    # Remove tag
    partner.remove_tag("VIP")
    assert "VIP" not in partner.tags
    assert "Enterprise" in partner.tags


def test_partner_to_dict():
    """Test partner serialization."""
    partner = Partner(
        name="Test Partner",
        partner_type=PartnerType.COMPANY,
        is_customer=True,
        email=Email("test@example.com"),
    )

    data = partner.to_dict()
    assert data["name"] == "Test Partner"
    assert data["partner_type"] == "COMPANY"
    assert data["is_customer"] is True
    assert data["email"] == "test@example.com"
