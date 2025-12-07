"""
Value objects for Products module.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from serp_core.domain.value_objects import ValueObject


class ProductType(str, Enum):
    """Product type enumeration."""

    PHYSICAL = "PHYSICAL"  # Tangible goods (trackable, shippable)
    SERVICE = "SERVICE"  # Services (time-based, non-trackable)
    DIGITAL = "DIGITAL"  # Software, downloads (deliverable, non-physical)
    BUNDLE = "BUNDLE"  # Combination of products


class UoMCategory(str, Enum):
    """Unit of measure category enumeration."""

    UNIT = "UNIT"  # Discrete items (each, piece, dozen)
    WEIGHT = "WEIGHT"  # Mass (kg, lb, ton)
    VOLUME = "VOLUME"  # Capacity (liter, gallon, m³)
    LENGTH = "LENGTH"  # Distance (meter, inch, foot)
    AREA = "AREA"  # Surface (m², ft²)
    TIME = "TIME"  # Duration (hour, day, minute)
    TEMPERATURE = "TEMPERATURE"  # Heat (celsius, fahrenheit)


class AttributeDataType(str, Enum):
    """Attribute data type enumeration."""

    TEXT = "TEXT"  # String value
    NUMERIC = "NUMERIC"  # Decimal number
    BOOLEAN = "BOOLEAN"  # True/False
    DATE = "DATE"  # Date value
    REFERENCE = "REFERENCE"  # Reference to another entity


@dataclass(frozen=True)
class ProductCode(ValueObject):
    """Product code value object."""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Product code cannot be empty")
        if len(self.value) > 50:
            raise ValueError("Product code too long (max 50 chars)")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Measurement(ValueObject):
    """Measurement with unit value object."""

    value: Decimal
    uom_id: str

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Measurement value cannot be negative")
        if not self.uom_id:
            raise ValueError("UoM is required for measurement")

    def __str__(self) -> str:
        return f"{self.value} {self.uom_id}"


@dataclass(frozen=True)
class ConversionFactor(ValueObject):
    """Unit conversion factor value object."""

    factor: Decimal

    def __post_init__(self):
        if self.factor <= 0:
            raise ValueError("Conversion factor must be positive")

    def convert(self, value: Decimal) -> Decimal:
        """Apply conversion factor to a value."""
        return value * self.factor

    def reverse_convert(self, value: Decimal) -> Decimal:
        """Apply inverse conversion."""
        return value / self.factor


@dataclass(frozen=True)
class AttributeValue(ValueObject):
    """Polymorphic attribute value."""

    data_type: AttributeDataType
    text_value: str | None = None
    numeric_value: Decimal | None = None
    boolean_value: bool | None = None
    date_value: str | None = None  # ISO format
    reference_value: str | None = None  # Entity ID
    uom_id: str | None = None  # For numeric values with units

    def __post_init__(self):
        """Validate that appropriate value is set for data type."""
        if self.data_type == AttributeDataType.TEXT and self.text_value is None:
            raise ValueError("Text value required for TEXT type")
        if self.data_type == AttributeDataType.NUMERIC and self.numeric_value is None:
            raise ValueError("Numeric value required for NUMERIC type")
        if self.data_type == AttributeDataType.BOOLEAN and self.boolean_value is None:
            raise ValueError("Boolean value required for BOOLEAN type")
        if self.data_type == AttributeDataType.DATE and self.date_value is None:
            raise ValueError("Date value required for DATE type")
        if (
            self.data_type == AttributeDataType.REFERENCE
            and self.reference_value is None
        ):
            raise ValueError("Reference value required for REFERENCE type")

    def get_value(self) -> str | Decimal | bool:
        """Get the actual value based on type."""
        if self.data_type == AttributeDataType.TEXT:
            return self.text_value or ""
        elif self.data_type == AttributeDataType.NUMERIC:
            return self.numeric_value or Decimal("0")
        elif self.data_type == AttributeDataType.BOOLEAN:
            return self.boolean_value or False
        elif self.data_type == AttributeDataType.DATE:
            return self.date_value or ""
        elif self.data_type == AttributeDataType.REFERENCE:
            return self.reference_value or ""
        return ""

    def display_value(self) -> str:
        """Get formatted display value."""
        if self.data_type == AttributeDataType.NUMERIC and self.uom_id:
            return f"{self.numeric_value} {self.uom_id}"
        return str(self.get_value())


@dataclass(frozen=True)
class Barcode(ValueObject):
    """Barcode value object."""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Barcode cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Barcode too long (max 100 chars)")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CategoryPath(ValueObject):
    """Hierarchical category path value object."""

    path: str  # e.g., "/Electronics/Computers/Laptops"

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError("Category path must start with /")

    def get_parent_path(self) -> str | None:
        """Get parent category path."""
        if self.path == "/":
            return None
        parts = self.path.rsplit("/", 1)
        return parts[0] if parts[0] else "/"

    def get_depth(self) -> int:
        """Get category depth level."""
        return self.path.count("/") - 1

    def __str__(self) -> str:
        return self.path
