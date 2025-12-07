"""
Domain events for event-driven architecture
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """
    Base class for domain events.

    Domain events:
    - Represent something that happened in the domain
    - Are immutable (frozen dataclass)
    - Have a timestamp
    - Use past tense naming (CustomerCreated, OrderSubmitted)

    Example:
        @dataclass(frozen=True)
        class CustomerCreated(DomainEvent):
            customer_id: UUID
            email: str
            name: str

        @dataclass(frozen=True)
        class OrderSubmitted(DomainEvent):
            order_id: UUID
            customer_id: UUID
            total_amount: Decimal

        # In an aggregate:
        class Customer(AggregateRoot):
            def create(self, name: str, email: str) -> 'Customer':
                customer = Customer(name=name, email=email)
                customer._add_domain_event(
                    CustomerCreated(
                        customer_id=customer.id,
                        email=email,
                        name=name
                    )
                )
                return customer
    """

    event_id: UUID = field(default_factory=uuid4, init=False)
    occurred_at: datetime = field(default_factory=datetime.utcnow, init=False)


class DomainEventHandler(ABC):
    """
    Base class for domain event handlers.

    Event handlers:
    - Subscribe to specific event types
    - Perform side effects (send emails, update read models, etc.)
    - Should be idempotent when possible

    Example:
        class CustomerCreatedHandler(DomainEventHandler):
            def __init__(self, email_service: EmailService):
                self.email_service = email_service

            async def handle(self, event: CustomerCreated) -> None:
                await self.email_service.send_welcome_email(
                    to=event.email,
                    name=event.name
                )

        class OrderSubmittedHandler(DomainEventHandler):
            def __init__(self, inventory_service: InventoryService):
                self.inventory_service = inventory_service

            async def handle(self, event: OrderSubmitted) -> None:
                await self.inventory_service.reserve_items(event.order_id)
    """

    async def handle(self, event: DomainEvent) -> None:
        """
        Handle a domain event.

        Args:
            event: The domain event to handle
        """
        raise NotImplementedError


class EventBus:
    """
    Simple in-memory event bus for domain events.

    This is a basic implementation. In production, you might use:
    - RabbitMQ, Kafka, or AWS SNS/SQS for distributed systems
    - Outbox pattern for transactional consistency
    - Event sourcing for full event history
    """

    def __init__(self) -> None:
        self._handlers: Dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type[DomainEvent], handler: Callable) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: The handler function or method
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: The event to publish
        """
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events.

        Args:
            events: List of events to publish
        """
        for event in events:
            await self.publish(event)
