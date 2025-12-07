"""
Value objects for Sales module.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from serp_core.domain.value_objects import ValueObject


class QuoteNumber(ValueObject):
    """Quote number value object."""

    def __init__(self, value: str):
        if not value:
            raise ValueError("Quote number cannot be empty")
        self.value = value

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def generate(year: int, sequence: int, prefix: str = "QT") -> "QuoteNumber":
        """Generate a quote number."""
        return QuoteNumber(f"{prefix}-{year}-{sequence:04d}")


class OrderNumber(ValueObject):
    """Sales order number value object."""

    def __init__(self, value: str):
        if not value:
            raise ValueError("Order number cannot be empty")
        self.value = value

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def generate(year: int, sequence: int, prefix: str = "SO") -> "OrderNumber":
        """Generate an order number."""
        return OrderNumber(f"{prefix}-{year}-{sequence:04d}")


class QuoteStatus(str, Enum):
    """Quote status enumeration."""

    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderStatus(str, Enum):
    """Sales order status enumeration."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Discount(ValueObject):
    """Discount value object."""

    percent: Decimal

    def __post_init__(self):
        if self.percent < Decimal("0") or self.percent > Decimal("100"):
            raise ValueError("Discount percent must be between 0 and 100")

    def apply(self, amount: Decimal) -> Decimal:
        """Apply discount to an amount."""
        return amount * (Decimal("100") - self.percent) / Decimal("100")


@dataclass(frozen=True)
class TaxRate(ValueObject):
    """Tax rate value object."""

    rate: Decimal

    def __post_init__(self):
        if self.rate < Decimal("0") or self.rate > Decimal("1"):
            raise ValueError("Tax rate must be between 0 and 1")

    def apply(self, amount: Decimal) -> Decimal:
        """Apply tax to an amount."""
        return amount * self.rate


@dataclass(frozen=True)
class ShippingInfo(ValueObject):
    """Shipping information value object."""

    carrier: str
    tracking_number: str | None = None
    shipping_method: str | None = None

    def __post_init__(self):
        if not self.carrier:
            raise ValueError("Carrier is required")
