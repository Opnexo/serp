"""
Base AggregateRoot class for Domain-Driven Design
"""

from dataclasses import dataclass, field
from typing import List

from serp_core.domain.entity import Entity
from serp_core.domain.events import DomainEvent


@dataclass
class AggregateRoot(Entity):
    """
    Base class for aggregate roots.

    Aggregate roots are entities that:
    - Serve as the entry point to an aggregate
    - Maintain consistency boundaries
    - Collect domain events
    - Control access to child entities

    Example:
        @dataclass
        class Order(AggregateRoot):
            customer_id: UUID
            items: List[OrderItem] = field(default_factory=list)
            status: OrderStatus = OrderStatus.DRAFT

            def add_item(self, product_id: UUID, quantity: int) -> None:
                item = OrderItem(product_id=product_id, quantity=quantity)
                self.items.append(item)
                self._add_domain_event(OrderItemAdded(order_id=self.id, item=item))

            def submit(self) -> None:
                if not self.items:
                    raise ValueError("Cannot submit empty order")
                self.status = OrderStatus.SUBMITTED
                self._add_domain_event(OrderSubmitted(order_id=self.id))
    """

    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events (typically after publishing)"""
        self._domain_events.clear()
