"""
SERP Event-Driven Architecture

This module provides the event bus infrastructure for inter-module communication.

Structure:
- domain/: Base event classes (DomainEvent, EventMetadata)
- ports/: Interfaces (IEventBus, IEventPublisher, IEventSubscriber)
- adapters/: Technology implementations (Redis, Kafka, InMemory)

Event Versioning:
- Events include schema version: event_type = "crm.partner.created.v1"
- Use EventMigrationRegistry to handle version upgrades
- Handlers can subscribe to specific versions or use migrations

Usage:
    from serp_core.events import IEventBus, DomainEvent, EventMetadata
    from serp_core.events import EventMigrationRegistry, get_event_migration_registry
    from serp_core.events.adapters import RedisEventBus, InMemoryEventBus
"""

from .domain.base_event import (
    DomainEvent,
    EventMetadata,
    EventMigrationFunc,
    EventMigrationRegistry,
    compare_versions,
    get_event_migration_registry,
    parse_version,
)
from .domain.event_envelope import EventEnvelope
from .ports.event_bus import IEventBus
from .ports.event_publisher import IEventPublisher
from .ports.event_subscriber import IEventSubscriber

__all__ = [
    # Domain
    "DomainEvent",
    "EventMetadata",
    "EventEnvelope",
    # Versioning
    "EventMigrationRegistry",
    "EventMigrationFunc",
    "get_event_migration_registry",
    "parse_version",
    "compare_versions",
    # Ports
    "IEventBus",
    "IEventPublisher",
    "IEventSubscriber",
]
