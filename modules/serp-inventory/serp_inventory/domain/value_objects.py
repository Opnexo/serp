"""Domain value objects for inventory."""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class LocationType(str, Enum):
    """Types of stock locations."""

    STOCK = "STOCK"  # Physical storage
    TRANSIT = "TRANSIT"  # In-transit goods
    CUSTOMER = "CUSTOMER"  # Customer locations
    SUPPLIER = "SUPPLIER"  # Supplier locations
    PRODUCTION = "PRODUCTION"  # Manufacturing
    INVENTORY = "INVENTORY"  # Virtual inventory adjustment location
    SCRAP = "SCRAP"  # Scrapped/disposed items


class LocationUsage(str, Enum):
    """How location is used."""

    INTERNAL = "INTERNAL"  # Company-owned location
    EXTERNAL = "EXTERNAL"  # Third-party location
    VIEW = "VIEW"  # Virtual grouping location


class StockMoveType(str, Enum):
    """Types of stock movements."""

    RECEIPT = "RECEIPT"  # Incoming from supplier
    DELIVERY = "DELIVERY"  # Outgoing to customer
    INTERNAL = "INTERNAL"  # Between internal locations
    ADJUSTMENT = "ADJUSTMENT"  # Inventory adjustment
    PRODUCTION_IN = "PRODUCTION_IN"  # Produced goods
    PRODUCTION_OUT = "PRODUCTION_OUT"  # Consumed materials
    SCRAP = "SCRAP"  # Scrapping


class StockMoveState(str, Enum):
    """Stock movement lifecycle states."""

    DRAFT = "DRAFT"  # Planned, not confirmed
    CONFIRMED = "CONFIRMED"  # Confirmed, reserved stock
    DONE = "DONE"  # Executed, stock moved
    CANCELLED = "CANCELLED"  # Cancelled


class AdjustmentReason(str, Enum):
    """Reasons for inventory adjustments."""

    CYCLE_COUNT = "CYCLE_COUNT"
    PHYSICAL_INVENTORY = "PHYSICAL_INVENTORY"
    DAMAGE = "DAMAGE"
    LOSS = "LOSS"
    FOUND = "FOUND"
    CORRECTION = "CORRECTION"
    OTHER = "OTHER"


class AdjustmentState(str, Enum):
    """Inventory adjustment states."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class CostingMethod(str, Enum):
    """Inventory valuation methods."""

    FIFO = "FIFO"  # First In, First Out
    LIFO = "LIFO"  # Last In, First Out
    AVERAGE = "AVERAGE"  # Weighted average cost


class ReorderRoute(str, Enum):
    """How to replenish stock."""

    BUY = "BUY"  # Purchase from supplier
    MANUFACTURE = "MANUFACTURE"  # Produce internally
    TRANSFER = "TRANSFER"  # Transfer from another warehouse


class LocationCode(BaseModel):
    """Location identifier value object."""

    value: str = Field(..., min_length=3, max_length=20)

    @field_validator("value")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate location code format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Location code must be alphanumeric")
        return v.upper()

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class MovementNumber(BaseModel):
    """Stock movement number value object."""

    value: str = Field(..., pattern=r"^STK\d{8}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class AdjustmentNumber(BaseModel):
    """Adjustment number value object."""

    value: str = Field(..., pattern=r"^ADJ\d{6}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class StockQuantity(BaseModel):
    """Stock quantity with availability tracking."""

    on_hand: Decimal = Field(default=Decimal("0"), ge=0)
    reserved: Decimal = Field(default=Decimal("0"), ge=0)

    @property
    def available(self) -> Decimal:
        """Calculate available quantity."""
        return self.on_hand - self.reserved

    def reserve(self, quantity: Decimal) -> "StockQuantity":
        """Reserve quantity, returns new instance."""
        if quantity > self.available:
            raise ValueError(
                f"Cannot reserve {quantity}, only {self.available} available"
            )
        return StockQuantity(on_hand=self.on_hand, reserved=self.reserved + quantity)

    def unreserve(self, quantity: Decimal) -> "StockQuantity":
        """Unreserve quantity, returns new instance."""
        if quantity > self.reserved:
            raise ValueError(
                f"Cannot unreserve {quantity}, only {self.reserved} reserved"
            )
        return StockQuantity(on_hand=self.on_hand, reserved=self.reserved - quantity)

    def add(self, quantity: Decimal) -> "StockQuantity":
        """Add to on_hand quantity, returns new instance."""
        return StockQuantity(on_hand=self.on_hand + quantity, reserved=self.reserved)

    def remove(self, quantity: Decimal) -> "StockQuantity":
        """Remove from on_hand quantity, returns new instance."""
        if quantity > self.on_hand:
            raise ValueError(f"Cannot remove {quantity}, only {self.on_hand} on hand")
        return StockQuantity(on_hand=self.on_hand - quantity, reserved=self.reserved)

    def fulfill_reservation(self, quantity: Decimal) -> "StockQuantity":
        """Fulfill reservation by removing from both on_hand and reserved."""
        if quantity > self.reserved:
            raise ValueError(
                f"Cannot fulfill {quantity}, only {self.reserved} reserved"
            )
        if quantity > self.on_hand:
            raise ValueError(f"Cannot fulfill {quantity}, only {self.on_hand} on hand")
        return StockQuantity(
            on_hand=self.on_hand - quantity, reserved=self.reserved - quantity
        )


class LotSerialNumber(BaseModel):
    """Lot or serial number value object."""

    value: str = Field(..., min_length=1, max_length=50)

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)
