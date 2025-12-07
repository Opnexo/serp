"""
Domain entities for serp-common module.

AddressEntity is a persisted address that can be referenced by other modules.
Unlike the Address value object (immutable, embedded), AddressEntity has:
- Its own identity (id)
- Can be updated independently
- Can be shared across entities (e.g., a Partner's billing address)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from serp_core.domain import AggregateRoot

from serp_common.domain.value_objects import Address


class AddressType(str, Enum):
    """Types of addresses."""

    BILLING = "BILLING"
    SHIPPING = "SHIPPING"
    OFFICE = "OFFICE"
    HOME = "HOME"
    OTHER = "OTHER"


@dataclass
class AddressEntity(AggregateRoot):
    """
    A persisted address entity.

    This wraps the Address value object with identity and metadata,
    allowing it to be stored and referenced independently.
    """

    # Required fields
    label: str = ""
    street: str = ""
    city: str = ""
    country: str = ""

    # Optional fields
    state: str | None = None
    postal_code: str | None = None
    address_type: AddressType = AddressType.OTHER

    # Reference fields (for linking to owning entity)
    owner_type: str | None = None  # e.g., "partner", "contact"
    owner_id: str | None = None

    # Metadata
    is_primary: bool = False
    is_active: bool = True
    notes: str | None = None

    # Audit fields
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate address after initialization."""
        if not self.street:
            raise ValueError("Street is required")
        if not self.city:
            raise ValueError("City is required")
        if not self.country:
            raise ValueError("Country is required")
        if not self.label:
            self.label = f"{self.address_type.value} Address"

    def to_value_object(self) -> Address:
        """Convert to immutable Address value object."""
        return Address(
            street=self.street,
            city=self.city,
            country=self.country,
            state=self.state,
            postal_code=self.postal_code,
        )

    @classmethod
    def from_value_object(
        cls,
        address: Address,
        label: str = "",
        address_type: AddressType = AddressType.OTHER,
        owner_type: str | None = None,
        owner_id: str | None = None,
    ) -> "AddressEntity":
        """Create entity from Address value object."""
        return cls(
            label=label,
            street=address.street,
            city=address.city,
            country=address.country,
            state=address.state,
            postal_code=address.postal_code,
            address_type=address_type,
            owner_type=owner_type,
            owner_id=owner_id,
        )

    def update(
        self,
        label: str | None = None,
        street: str | None = None,
        city: str | None = None,
        country: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        address_type: AddressType | None = None,
        is_primary: bool | None = None,
        notes: str | None = None,
    ) -> None:
        """Update address fields."""
        if label is not None:
            self.label = label
        if street is not None:
            self.street = street
        if city is not None:
            self.city = city
        if country is not None:
            self.country = country
        if state is not None:
            self.state = state
        if postal_code is not None:
            self.postal_code = postal_code
        if address_type is not None:
            self.address_type = address_type
        if is_primary is not None:
            self.is_primary = is_primary
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Mark address as inactive."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Mark address as active."""
        self.is_active = True
        self.updated_at = datetime.now()

    def set_as_primary(self) -> None:
        """Set this address as the primary address."""
        self.is_primary = True
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "address_type": self.address_type.value,
            "owner_type": self.owner_type,
            "owner_id": self.owner_id,
            "is_primary": self.is_primary,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @property
    def single_line(self) -> str:
        """Format as single line string."""
        return self.to_value_object().single_line

    @property
    def multi_line(self) -> str:
        """Format as multi-line string."""
        return self.to_value_object().multi_line
