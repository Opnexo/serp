"""
Base domain event classes for SERP event-driven architecture.

All module events MUST inherit from DomainEvent.

Event Versioning Strategy:
- Each event class declares its schema version (default: 1)
- Event types include version suffix: {module}.{aggregate}.{action}.v{version}
- Handlers can subscribe to specific versions or all versions
- Event migrations transform old versions to new ones
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type
from uuid import UUID, uuid4
import re


def parse_version(version: str) -> Tuple[int, int]:
    """
    Parse version string to tuple for comparison.

    Supports formats: "1", "1.0", "1.0.0" (patch ignored)

    Returns:
        Tuple of (major, minor)
    """
    parts = version.split(".")
    major = int(parts[0]) if len(parts) > 0 else 1
    minor = int(parts[1]) if len(parts) > 1 else 0
    return (major, minor)


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.

    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    parsed1 = parse_version(v1)
    parsed2 = parse_version(v2)

    if parsed1 < parsed2:
        return -1
    elif parsed1 > parsed2:
        return 1
    return 0


@dataclass(frozen=True)
class EventMetadata:
    """
    Metadata attached to every domain event.

    Provides traceability and correlation across the system.

    Attributes:
        event_id: Unique identifier for this event instance
        timestamp: When the event occurred
        correlation_id: Links related events in a flow (e.g., all events from one request)
        causation_id: The event that caused this one (for event chains)
        user_id: Who triggered the action that caused this event
        schema_version: Event schema version (populated from event class)
    """
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    schema_version: str = "1"


@dataclass(kw_only=True)
class DomainEvent(ABC):
    """
    Base class for all domain events in SERP.

    All module events MUST inherit from this class.
    Events are immutable records of something that happened.

    Schema Versioning:
    - Set VERSION class variable to declare schema version (default: 1)
    - event_type() now returns versioned type: "crm.partner.created.v1"
    - base_event_type() returns unversioned type: "crm.partner.created"
    - Use VERSION_HISTORY to document breaking changes

    Naming Convention:
    - Past tense (InvoiceCreated, not CreateInvoice)
    - Descriptive of the business action

    Note: Uses kw_only=True to allow child classes to have required fields
    while this base class has metadata with a default value.

    Example:
        @dataclass(kw_only=True)
        class CustomerCreatedEvent(DomainEvent):
            VERSION: ClassVar[int] = 1
            VERSION_HISTORY: ClassVar[Dict[int, str]] = {
                1: "Initial version with customer_id, email, name",
            }

            customer_id: UUID
            email: str
            name: str

            @classmethod
            def base_event_type(cls) -> str:
                return "users.customer.created"

        # v2 with breaking change (added required field)
        @dataclass(kw_only=True)
        class CustomerCreatedEventV2(DomainEvent):
            VERSION: ClassVar[int] = 2
            VERSION_HISTORY: ClassVar[Dict[int, str]] = {
                1: "Initial version with customer_id, email, name",
                2: "Added phone_number as required field",
            }

            customer_id: UUID
            email: str
            name: str
            phone_number: str  # New required field

            @classmethod
            def base_event_type(cls) -> str:
                return "users.customer.created"
    """
    # Class-level version - override in subclasses for breaking changes
    VERSION: ClassVar[int] = 1

    # Version history for documentation (optional but recommended)
    VERSION_HISTORY: ClassVar[Dict[int, str]] = {
        1: "Base version",
    }

    metadata: EventMetadata = field(default_factory=EventMetadata)

    def __post_init__(self) -> None:
        """Ensure metadata has correct schema version from class."""
        if self.metadata.schema_version != str(self.VERSION):
            # Update metadata with correct version
            new_metadata = EventMetadata(
                event_id=self.metadata.event_id,
                timestamp=self.metadata.timestamp,
                correlation_id=self.metadata.correlation_id,
                causation_id=self.metadata.causation_id,
                user_id=self.metadata.user_id,
                schema_version=str(self.VERSION),
            )
            object.__setattr__(self, 'metadata', new_metadata)

    @classmethod
    def base_event_type(cls) -> str:
        """
        Returns the base event type identifier WITHOUT version.

        Convention: {module}.{aggregate}.{action}
        Example: "invoicing.invoice.created"

        Override in subclasses for custom naming.
        Default converts CamelCase class name to dot.notation.
        """
        name = cls.__name__
        # Remove 'Event' suffix if present
        if name.endswith('Event'):
            name = name[:-5]
        # Remove version suffix (V1, V2, etc.)
        name = re.sub(r'V\d+$', '', name)
        # Convert CamelCase to dot.notation
        return re.sub(r'(?<!^)(?=[A-Z])', '.', name).lower()

    @classmethod
    def event_type(cls) -> str:
        """
        Returns the versioned event type identifier.

        Format: {module}.{aggregate}.{action}.v{version}
        Example: "invoicing.invoice.created.v1"

        This includes the version for proper routing and handling.
        """
        return f"{cls.base_event_type()}.v{cls.VERSION}"

    @classmethod
    def stream_name(cls) -> str:
        """
        Returns the stream/topic name for routing.

        Default: First part of event_type (module name) + "-events".
        Override for custom routing strategies.

        Example: "invoicing.invoice.created.v1" -> "invoicing-events"
        """
        return cls.base_event_type().split('.')[0] + "-events"

    @classmethod
    def schema_version(cls) -> int:
        """Return the schema version of this event class."""
        return cls.VERSION

    def with_correlation(self, correlation_id: UUID) -> "DomainEvent":
        """
        Create a new event with the given correlation ID.

        Useful when publishing events within a chain of operations.
        """
        new_metadata = EventMetadata(
            event_id=self.metadata.event_id,
            timestamp=self.metadata.timestamp,
            correlation_id=correlation_id,
            causation_id=self.metadata.causation_id,
            user_id=self.metadata.user_id,
            schema_version=self.metadata.schema_version,
        )
        # Shallow copy with new metadata
        import copy
        new_event = copy.copy(self)
        object.__setattr__(new_event, 'metadata', new_metadata)
        return new_event


# Type alias for event migration functions
EventMigrationFunc = Callable[[Dict[str, Any]], Dict[str, Any]]


class EventMigrationRegistry:
    """
    Registry for event schema migrations.

    Migrations transform event payloads from older versions to newer ones,
    allowing handlers written for v2 to process v1 events.

    Example:
        registry = EventMigrationRegistry()

        # Register migration from v1 to v2
        @registry.register("crm.partner.created", 1, 2)
        def migrate_partner_created_v1_to_v2(payload: dict) -> dict:
            # Add default phone_number for v1 events
            payload["phone_number"] = payload.get("phone_number", "")
            return payload
    """

    def __init__(self) -> None:
        # Key: (base_event_type, from_version, to_version)
        self._migrations: Dict[Tuple[str, int, int], EventMigrationFunc] = {}

    def register(
        self,
        base_event_type: str,
        from_version: int,
        to_version: int,
    ) -> Callable[[EventMigrationFunc], EventMigrationFunc]:
        """
        Decorator to register a migration function.

        Args:
            base_event_type: The base event type (without version)
            from_version: Source schema version
            to_version: Target schema version
        """
        def decorator(func: EventMigrationFunc) -> EventMigrationFunc:
            key = (base_event_type, from_version, to_version)
            self._migrations[key] = func
            return func
        return decorator

    def migrate(
        self,
        base_event_type: str,
        payload: Dict[str, Any],
        from_version: int,
        to_version: int,
    ) -> Dict[str, Any]:
        """
        Migrate an event payload from one version to another.

        Applies migrations in sequence if direct migration doesn't exist.
        E.g., v1 -> v3 might apply v1 -> v2, then v2 -> v3.

        Args:
            base_event_type: The base event type
            payload: The event payload to migrate
            from_version: Current version of the payload
            to_version: Target version

        Returns:
            Migrated payload

        Raises:
            ValueError: If no migration path exists
        """
        if from_version == to_version:
            return payload

        current_version = from_version
        current_payload = payload.copy()

        while current_version < to_version:
            next_version = current_version + 1
            key = (base_event_type, current_version, next_version)

            if key not in self._migrations:
                raise ValueError(
                    f"No migration found for {base_event_type} "
                    f"from v{current_version} to v{next_version}"
                )

            current_payload = self._migrations[key](current_payload)
            current_version = next_version

        return current_payload

    def has_migration(
        self,
        base_event_type: str,
        from_version: int,
        to_version: int,
    ) -> bool:
        """Check if a direct migration exists."""
        return (base_event_type, from_version, to_version) in self._migrations

    def can_migrate(
        self,
        base_event_type: str,
        from_version: int,
        to_version: int,
    ) -> bool:
        """Check if a migration path exists (direct or chained)."""
        if from_version >= to_version:
            return from_version == to_version

        current = from_version
        while current < to_version:
            if not self.has_migration(base_event_type, current, current + 1):
                return False
            current += 1
        return True


# Global migration registry
_event_migration_registry = EventMigrationRegistry()


def get_event_migration_registry() -> EventMigrationRegistry:
    """Get the global event migration registry."""
    return _event_migration_registry
