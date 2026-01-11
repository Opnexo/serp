"""
Event Publisher Interface - Write-only access to the event bus.

Use this interface when a module only needs to publish events,
not subscribe to them. Enables better dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..domain.base_event import DomainEvent


class IEventPublisher(ABC):
    """
    Write-only interface for modules that only publish events.
    
    This is a narrower interface than IEventBus, following the
    Interface Segregation Principle. Use when a service only needs
    to publish, not subscribe.
    
    Example:
        class OrderService:
            def __init__(self, event_publisher: IEventPublisher):
                self._publisher = event_publisher
            
            async def submit_order(self, order_id: UUID):
                # ... business logic ...
                await self._publisher.publish(
                    OrderSubmittedEvent(order_id=order_id)
                )
    """
    
    @abstractmethod
    async def publish(
        self, 
        event: DomainEvent,
        stream: Optional[str] = None
    ) -> None:
        """
        Publish a single domain event.
        
        Args:
            event: The domain event to publish
            stream: Optional stream/topic override
        """
        ...
    
    @abstractmethod
    async def publish_many(
        self, 
        events: List[DomainEvent],
        stream: Optional[str] = None
    ) -> None:
        """
        Publish multiple domain events.
        
        Args:
            events: List of domain events to publish
            stream: Optional stream/topic override
        """
        ...
