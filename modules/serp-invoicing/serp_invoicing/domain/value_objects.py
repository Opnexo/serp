"""
Value Objects for Invoicing domain.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class InvoiceStatus(str, Enum):
    """Status of an invoice."""

    DRAFT = "DRAFT"  # Being prepared
    SENT = "SENT"  # Sent to customer
    PAID = "PAID"  # Fully paid
    OVERDUE = "OVERDUE"  # Past due date and unpaid
    CANCELLED = "CANCELLED"  # Cancelled/voided


class PaymentMethod(str, Enum):
    """Payment method type."""

    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CHECK = "CHECK"
    OTHER = "OTHER"


@dataclass(frozen=True)
class InvoiceNumber:
    """Invoice number value object with auto-generation support."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Invoice number cannot be empty")
        if len(self.value) > 50:
            raise ValueError("Invoice number too long")

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def generate(year: int, sequence: int, prefix: str = "INV") -> "InvoiceNumber":
        """
        Generate an invoice number.

        Format: PREFIX-YYYY-NNNN (e.g., INV-2025-0001)
        """
        number = f"{prefix}-{year}-{sequence:04d}"
        return InvoiceNumber(number)


@dataclass(frozen=True)
class TaxRate:
    """Tax rate value object."""

    rate: Decimal  # As decimal (e.g., 0.10 for 10%)
    name: str | None = None  # Tax name (e.g., "VAT", "GST")

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Decimal):
            object.__setattr__(self, "rate", Decimal(str(self.rate)))
        if self.rate < Decimal("0") or self.rate > Decimal("1"):
            raise ValueError("Tax rate must be between 0 and 1")

    def apply(self, amount: Decimal) -> Decimal:
        """Calculate tax amount for given amount."""
        return amount * self.rate

    def __str__(self) -> str:
        percentage = self.rate * 100
        if self.name:
            return f"{self.name} ({percentage}%)"
        return f"{percentage}%"


@dataclass(frozen=True)
class PaymentReference:
    """Payment reference/transaction ID value object."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Payment reference cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Payment reference too long")

    def __str__(self) -> str:
        return self.value
