"""Domain value objects for logistics."""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class PickingStrategy(str, Enum):
    """Picking strategies."""

    WAVE = "WAVE"  # Batch orders by timeframe
    BATCH = "BATCH"  # Multiple orders at once
    ZONE = "ZONE"  # By warehouse area
    SINGLE = "SINGLE"  # One order at a time


class PickingState(str, Enum):
    """Picking operation states."""

    PENDING = "PENDING"  # Created, not assigned
    ASSIGNED = "ASSIGNED"  # Assigned to picker
    IN_PROGRESS = "IN_PROGRESS"  # Picker started
    COMPLETED = "COMPLETED"  # All items picked
    CANCELLED = "CANCELLED"  # Cancelled


class PackingState(str, Enum):
    """Packing operation states."""

    PENDING = "PENDING"  # Waiting for picking
    IN_PROGRESS = "IN_PROGRESS"  # Packing started
    COMPLETED = "COMPLETED"  # All items packed
    SHIPPED = "SHIPPED"  # Shipment created


class ShipmentState(str, Enum):
    """Shipment states."""

    DRAFT = "DRAFT"  # Created, not confirmed
    CONFIRMED = "CONFIRMED"  # Ready for pickup
    PICKED_UP = "PICKED_UP"  # Carrier collected
    IN_TRANSIT = "IN_TRANSIT"  # On the way
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"  # Final delivery
    DELIVERED = "DELIVERED"  # Successfully delivered
    DELIVERY_FAILED = "DELIVERY_FAILED"  # Delivery attempt failed
    RETURNED = "RETURNED"  # Returned to sender
    CANCELLED = "CANCELLED"  # Cancelled


class ServiceLevel(str, Enum):
    """Carrier service levels."""

    STANDARD = "STANDARD"  # Regular delivery
    EXPRESS = "EXPRESS"  # Fast delivery
    OVERNIGHT = "OVERNIGHT"  # Next day
    TWO_DAY = "TWO_DAY"  # 2-day delivery
    ECONOMY = "ECONOMY"  # Slow but cheap


class RouteState(str, Enum):
    """Delivery route states."""

    PLANNED = "PLANNED"  # Route created
    IN_PROGRESS = "IN_PROGRESS"  # Driver started
    COMPLETED = "COMPLETED"  # All stops done
    CANCELLED = "CANCELLED"  # Cancelled


class RMAState(str, Enum):
    """RMA (Return) states."""

    REQUESTED = "REQUESTED"  # Customer requested
    APPROVED = "APPROVED"  # Approved by company
    REJECTED = "REJECTED"  # Rejected
    SHIPPED = "SHIPPED"  # Customer shipped back
    RECEIVED = "RECEIVED"  # Company received
    PROCESSED = "PROCESSED"  # Refund/exchange done
    CANCELLED = "CANCELLED"  # Cancelled


class RMAAction(str, Enum):
    """RMA processing actions."""

    REFUND = "REFUND"  # Full refund
    EXCHANGE = "EXCHANGE"  # Exchange for same item
    REPLACE = "REPLACE"  # Replace with different item
    CREDIT = "CREDIT"  # Store credit
    REPAIR = "REPAIR"  # Repair and return


class PickingNumber(BaseModel):
    """Picking operation number value object."""

    value: str = Field(..., pattern=r"^PICK\d{8}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class PackingNumber(BaseModel):
    """Packing operation number value object."""

    value: str = Field(..., pattern=r"^PACK\d{8}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class ShipmentNumber(BaseModel):
    """Shipment number value object."""

    value: str = Field(..., pattern=r"^SHIP\d{8}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class RouteNumber(BaseModel):
    """Route number value object."""

    value: str = Field(..., pattern=r"^ROUTE\d{6}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class RMANumber(BaseModel):
    """RMA number value object."""

    value: str = Field(..., pattern=r"^RMA\d{8}$")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class TrackingNumber(BaseModel):
    """Carrier tracking number value object."""

    value: str = Field(..., min_length=5, max_length=50)

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)


class Address(BaseModel):
    """Shipping address value object."""

    name: str = Field(..., min_length=1, max_length=200)
    street1: str = Field(..., min_length=1, max_length=200)
    street2: str = Field(default="", max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=2)  # ISO 2-letter code
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=100)
    is_residential: bool = False

    def __str__(self) -> str:
        """String representation."""
        parts = [self.name, self.street1]
        if self.street2:
            parts.append(self.street2)
        parts.append(f"{self.city}, {self.state} {self.postal_code}")
        parts.append(self.country)
        return ", ".join(parts)


class PackageDimensions(BaseModel):
    """Package dimensions value object."""

    length_cm: Decimal = Field(..., gt=0)
    width_cm: Decimal = Field(..., gt=0)
    height_cm: Decimal = Field(..., gt=0)

    @property
    def volume_cm3(self) -> Decimal:
        """Calculate volume in cubic centimeters."""
        return self.length_cm * self.width_cm * self.height_cm

    def dimensional_weight_kg(self, divisor: int = 5000) -> Decimal:
        """Calculate dimensional weight."""
        return self.volume_cm3 / Decimal(divisor)


class Weight(BaseModel):
    """Weight value object."""

    kg: Decimal = Field(..., ge=0)

    @classmethod
    def from_grams(cls, grams: Decimal) -> "Weight":
        """Create from grams."""
        return cls(kg=grams / Decimal("1000"))

    @classmethod
    def from_pounds(cls, pounds: Decimal) -> "Weight":
        """Create from pounds."""
        return cls(kg=pounds * Decimal("0.453592"))

    @property
    def grams(self) -> Decimal:
        """Get weight in grams."""
        return self.kg * Decimal("1000")

    @property
    def pounds(self) -> Decimal:
        """Get weight in pounds."""
        return self.kg / Decimal("0.453592")

    def __add__(self, other: "Weight") -> "Weight":
        """Add weights."""
        return Weight(kg=self.kg + other.kg)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.kg} kg"
