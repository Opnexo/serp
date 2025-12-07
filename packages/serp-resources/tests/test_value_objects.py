"""Tests for value objects."""

from decimal import Decimal

import pytest

from serp_resources import Address, Email, Money, PhoneNumber, TaxId


class TestEmail:
    """Tests for Email value object."""

    def test_valid_email(self) -> None:
        email = Email("user@example.com")
        assert str(email) == "user@example.com"

    def test_email_properties(self) -> None:
        email = Email("user@example.com")
        assert email.local_part == "user"
        assert email.domain == "example.com"

    def test_email_case_insensitive_equality(self) -> None:
        email1 = Email("User@Example.com")
        email2 = Email("user@example.com")
        assert email1 == email2

    def test_invalid_email_no_at(self) -> None:
        with pytest.raises(ValueError):
            Email("invalid-email")

    def test_invalid_email_empty(self) -> None:
        with pytest.raises(ValueError):
            Email("")

    def test_email_too_long(self) -> None:
        with pytest.raises(ValueError):
            Email("a" * 250 + "@example.com")


class TestPhoneNumber:
    """Tests for PhoneNumber value object."""

    def test_valid_phone(self) -> None:
        phone = PhoneNumber("+1-555-123-4567")
        assert str(phone) == "+15551234567"

    def test_phone_formatting_removed(self) -> None:
        phone = PhoneNumber("(555) 123-4567")
        assert str(phone) == "5551234567"

    def test_phone_country_code(self) -> None:
        phone = PhoneNumber("+1-555-123-4567")
        assert phone.country_code == "1"

    def test_phone_formatted(self) -> None:
        phone = PhoneNumber("5551234567")
        assert phone.formatted == "(555) 123-4567"

    def test_invalid_phone_too_short(self) -> None:
        with pytest.raises(ValueError):
            PhoneNumber("123")


class TestAddress:
    """Tests for Address value object."""

    def test_valid_address(self) -> None:
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US",
        )
        assert "123 Main St" in str(address)
        assert "New York" in str(address)

    def test_address_to_dict(self) -> None:
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US",
        )
        d = address.to_dict()
        assert d["street"] == "123 Main St"
        assert d["city"] == "New York"

    def test_address_from_dict(self) -> None:
        data = {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "US",
        }
        address = Address.from_dict(data)
        assert address.street == "123 Main St"

    def test_invalid_address_no_street(self) -> None:
        with pytest.raises(ValueError):
            Address(street="", city="New York", country="US")


class TestMoney:
    """Tests for Money value object."""

    def test_valid_money(self) -> None:
        money = Money(Decimal("99.99"), "USD")
        assert money.amount == Decimal("99.99")
        assert money.currency == "USD"

    def test_money_from_float(self) -> None:
        money = Money(99.99, "USD")
        assert money.amount == Decimal("99.99")

    def test_money_addition(self) -> None:
        m1 = Money(Decimal("10.00"), "USD")
        m2 = Money(Decimal("5.00"), "USD")
        result = m1 + m2
        assert result.amount == Decimal("15.00")

    def test_money_subtraction(self) -> None:
        m1 = Money(Decimal("10.00"), "USD")
        m2 = Money(Decimal("3.00"), "USD")
        result = m1 - m2
        assert result.amount == Decimal("7.00")

    def test_money_multiplication(self) -> None:
        money = Money(Decimal("10.00"), "USD")
        result = money * 3
        assert result.amount == Decimal("30.00")

    def test_money_division(self) -> None:
        money = Money(Decimal("10.00"), "USD")
        result = money / 2
        assert result.amount == Decimal("5.00")

    def test_money_different_currency_error(self) -> None:
        m1 = Money(Decimal("10.00"), "USD")
        m2 = Money(Decimal("5.00"), "EUR")
        with pytest.raises(ValueError):
            _ = m1 + m2

    def test_money_zero(self) -> None:
        money = Money.zero("USD")
        assert money.is_zero
        assert money.amount == Decimal("0")

    def test_invalid_currency(self) -> None:
        with pytest.raises(ValueError):
            Money(Decimal("10.00"), "INVALID")


class TestTaxId:
    """Tests for TaxId value object."""

    def test_valid_tax_id(self) -> None:
        tax_id = TaxId("123456789", "US")
        assert str(tax_id) == "US-123456789"

    def test_tax_id_country_normalized(self) -> None:
        tax_id = TaxId("123456789", "us")
        assert tax_id.country == "US"

    def test_tax_id_to_dict(self) -> None:
        tax_id = TaxId("123456789", "US")
        d = tax_id.to_dict()
        assert d["value"] == "123456789"
        assert d["country"] == "US"

    def test_invalid_tax_id_empty(self) -> None:
        with pytest.raises(ValueError):
            TaxId("", "US")

    def test_invalid_country_code(self) -> None:
        with pytest.raises(ValueError):
            TaxId("123456789", "USA")
