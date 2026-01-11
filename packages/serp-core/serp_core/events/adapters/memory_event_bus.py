"""
In-Memory Event Bus implementation for testing and development.

This adapter provides synchronous in-process event dispatch without
any external dependencies. Perfect for unit tests and local development.

Supports version-aware event handling:
- Subscribe to specific version: subscribe(OrderCreatedEventV2, handler)
- Subscribe to all versions: subscribe_all_versions("orders.order.created", handler)
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Type, Optional, Awaitable

from ..domain.base_event import DomainEvent, get_event_migration_registry
from ..ports.event_bus import IEventBus, EventHandler


@dataclass
class InMemoryEventBus(IEventBus):
    """
    In-memory implementation of IEventBus for testing.

    Features:
    - Synchronous event dispatch (immediate delivery)
    - No persistence (events lost on restart)
    - No consumer groups (all handlers receive all events)
    - Version-aware subscriptions (specific version or all versions)
    - Perfect for unit testing and development

    Example:
        event_bus = InMemoryEventBus()

        # Subscribe to specific version
        async def on_order_created_v1(event: OrderCreatedEvent):
            print(f"Order {event.order_id} created (v1)")

        event_bus.subscribe(OrderCreatedEvent, on_order_created_v1)

        # Subscribe to all versions (receives any version)
        async def on_any_order_created(event: DomainEvent, payload: dict):
            print(f"Order created (v{payload['schema_version']})")

        event_bus.subscribe_all_versions("orders.order.created", on_any_order_created)

        # Publish
        await event_bus.publish(OrderCreatedEvent(order_id=uuid4()))

        # For testing - access published events
        assert len(event_bus.published_events) == 1
    """

    # Handlers for specific versioned event types
    _handlers: Dict[str, List[EventHandler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    # Handlers for all versions of a base event type
    _base_type_handlers: Dict[str, List[Callable[[DomainEvent, Dict[str, Any]], Awaitable[None]]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    _published_events: List[DomainEvent] = field(default_factory=list)
    _running: bool = field(default=False)

    @property
    def published_events(self) -> List[DomainEvent]:
        """Access published events for testing assertions."""
        return self._published_events.copy()

    def clear(self) -> None:
        """Clear all published events and handlers (for test cleanup)."""
        self._published_events.clear()
        self._handlers.clear()
        self._base_type_handlers.clear()

    async def publish(
        self,
        event: DomainEvent,
        stream: Optional[str] = None
    ) -> None:
        """
        Publish event and immediately dispatch to handlers.

        Dispatches to:
        1. Handlers registered for the exact versioned event type
        2. Handlers registered for all versions of the base event type

        Unlike Redis/Kafka, dispatch is synchronous - handlers are
        awaited before returning.
        """
        self._published_events.append(event)

        versioned_type = event.event_type()
        base_type = event.base_event_type()

        # Dispatch to version-specific handlers
        handlers = self._handlers.get(versioned_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Handler error for {versioned_type}: {e}")

        # Dispatch to base-type handlers (all versions)
        base_handlers = self._base_type_handlers.get(base_type, [])
        if base_handlers:
            from dataclasses import asdict
            payload = asdict(event)
            payload["schema_version"] = event.VERSION

            for handler in base_handlers:
                try:
                    await handler(event, payload)
                except Exception as e:
                    print(f"Handler error for {base_type} (all versions): {e}")

    async def publish_many(
        self,
        events: List[DomainEvent],
        stream: Optional[str] = None
    ) -> None:
        """Publish multiple events sequentially."""
        for event in events:
            await self.publish(event, stream)

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
        group: Optional[str] = None  # Ignored in memory implementation
    ) -> None:
        """
        Register a handler for a specific event type and version.

        The handler will only receive events matching the exact version
        of the subscribed event type.
        """
        type_name = event_type.event_type()
        self._handlers[type_name].append(handler)

    def subscribe_all_versions(
        self,
        base_event_type: str,
        handler: Callable[[DomainEvent, Dict[str, Any]], Awaitable[None]],
        migrate_to_version: Optional[int] = None,
    ) -> None:
        """
        Subscribe to all versions of an event type.

        The handler receives both the event object and the raw payload dict.
        This allows handling events regardless of their schema version.

        Args:
            base_event_type: Base event type without version (e.g., "crm.partner.created")
            handler: Async function that receives (event, payload_dict)
            migrate_to_version: If set, attempts to migrate payload to this version

        Example:
            async def on_partner_created(event: DomainEvent, payload: dict):
                partner_id = payload.get("partner_id")
                version = payload.get("schema_version", 1)
                print(f"Partner created (v{version}): {partner_id}")

            bus.subscribe_all_versions("crm.partner.created", on_partner_created)
        """
        if migrate_to_version is not None:
            # Wrap handler to perform migration
            original_handler = handler

            async def migrating_handler(event: DomainEvent, payload: Dict[str, Any]) -> None:
                current_version = event.VERSION
                if current_version < migrate_to_version:
                    registry = get_event_migration_registry()
                    if registry.can_migrate(base_event_type, current_version, migrate_to_version):
                        payload = registry.migrate(
                            base_event_type,
                            payload,
                            current_version,
                            migrate_to_version,
                        )
                        payload["schema_version"] = migrate_to_version
                await original_handler(event, payload)

            self._base_type_handlers[base_event_type].append(migrating_handler)
        else:
            self._base_type_handlers[base_event_type].append(handler)

    async def start(self) -> None:
        """
        Start the event bus.

        In-memory implementation has nothing to start since
        dispatch is synchronous.
        """
        self._running = True
        print("InMemoryEventBus started")

    async def stop(self) -> None:
        """Stop the event bus."""
        self._running = False
        print("InMemoryEventBus stopped")

    async def health_check(self) -> bool:
        """Always healthy - no external dependencies."""
        return True

    def get_handler_count(self, event_type: Type[DomainEvent]) -> int:
        """Get number of handlers for a specific versioned event type (for testing)."""
        return len(self._handlers.get(event_type.event_type(), []))

    def get_base_handler_count(self, base_event_type: str) -> int:
        """Get number of handlers for all versions of an event type (for testing)."""
        return len(self._base_type_handlers.get(base_event_type, []))
