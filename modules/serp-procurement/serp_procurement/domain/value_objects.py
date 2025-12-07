"""Value objects for Procurement domain."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PurchaseOrderState(str, Enum):
    """Purchase Order states."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    RECEIVED = "RECEIVED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"


class RFQState(str, Enum):
    """Request for Quotation states."""

    DRAFT = "DRAFT"
    SENT = "SENT"
    QUOTED = "QUOTED"
    ACCEPTED = "ACCEPTED"
    CANCELLED = "CANCELLED"


class ReceiptStatus(str, Enum):
    """Goods receipt status."""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"


class QualityStatus(str, Enum):
    """Quality control status."""

    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    WAIVED = "WAIVED"


class DeliveryTerms(str, Enum):
    """Incoterms for delivery."""

    EXW = "EXW"  # Ex Works
    FCA = "FCA"  # Free Carrier
    CPT = "CPT"  # Carriage Paid To
    CIP = "CIP"  # Carriage and Insurance Paid To
    DAP = "DAP"  # Delivered at Place
    DPU = "DPU"  # Delivered at Place Unloaded
    DDP = "DDP"  # Delivered Duty Paid
    FAS = "FAS"  # Free Alongside Ship
    FOB = "FOB"  # Free on Board
    CFR = "CFR"  # Cost and Freight
    CIF = "CIF"  # Cost, Insurance and Freight


@dataclass(frozen=True)
class PurchaseOrderNumber:
    """Purchase Order number value object."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Purchase order number cannot be empty")
        if len(self.value) > 50:
            raise ValueError("Purchase order number too long")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RFQNumber:
    """RFQ number value object."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("RFQ number cannot be empty")
        if len(self.value) > 50:
            raise ValueError("RFQ number too long")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class GRNNumber:
    """Goods Receipt Note number value object."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("GRN number cannot be empty")
        if len(self.value) > 50:
            raise ValueError("GRN number too long")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PaymentTerms:
    """Payment terms value object."""

    code: str
    days: int
    description: str | None = None

    def __post_init__(self):
        if not self.code:
            raise ValueError("Payment terms code cannot be empty")
        if self.days < 0:
            raise ValueError("Payment days cannot be negative")

    @classmethod
    def net_30(cls) -> "PaymentTerms":
        """Standard NET30 terms."""
        return cls(code="NET30", days=30, description="Payment due in 30 days")

    @classmethod
    def net_60(cls) -> "PaymentTerms":
        """Standard NET60 terms."""
        return cls(code="NET60", days=60, description="Payment due in 60 days")

    @classmethod
    def immediate(cls) -> "PaymentTerms":
        """Immediate payment."""
        return cls(code="IMMEDIATE", days=0, description="Payment on delivery")

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True)
class QuantityTracking:
    """Track ordered vs received quantities."""

    ordered_quantity: Decimal
    received_quantity: Decimal

    def __post_init__(self):
        if self.ordered_quantity < Decimal("0"):
            raise ValueError("Ordered quantity cannot be negative")
        if self.received_quantity < Decimal("0"):
            raise ValueError("Received quantity cannot be negative")
        if self.received_quantity > self.ordered_quantity:
            raise ValueError("Received quantity cannot exceed ordered quantity")

    @property
    def pending_quantity(self) -> Decimal:
        """Quantity still to be received."""
        return self.ordered_quantity - self.received_quantity

    @property
    def is_fully_received(self) -> bool:
        """Check if all quantity received."""
        return self.received_quantity == self.ordered_quantity

    @property
    def is_partially_received(self) -> bool:
        """Check if partially received."""
        return (
            self.received_quantity > Decimal("0")
            and self.received_quantity < self.ordered_quantity
        )

    @property
    def receipt_percentage(self) -> Decimal:
        """Percentage of quantity received."""
        if self.ordered_quantity == Decimal("0"):
            return Decimal("100")
        return (self.received_quantity / self.ordered_quantity) * Decimal("100")

    def receive(self, quantity: Decimal) -> "QuantityTracking":
        """Create new tracking with received quantity added."""
        new_received = self.received_quantity + quantity
        if new_received > self.ordered_quantity:
            raise ValueError("Cannot receive more than ordered quantity")
        return QuantityTracking(
            ordered_quantity=self.ordered_quantity,
            received_quantity=new_received,
        )
