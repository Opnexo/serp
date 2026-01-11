"""
Event Subscriber Interface - Read-only access to the event bus.

Use this interface for components that only need to subscribe to events,
not publish them. Enables better dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import Type, Optional

from ..domain.base_event import DomainEvent
from .event_bus import EventHandler


class IEventSubscriber(ABC):
    """
    Read-only interface for components that only subscribe to events.
    
    This is a narrower interface than IEventBus, following the
    Interface Segregation Principle. Primarily used by the event worker
    and for testing.
    
    Example:
        class NotificationWorker:
            def __init__(self, subscriber: IEventSubscriber):
                self._subscriber = subscriber
                self._setup_handlers()
            
            def _setup_handlers(self):
                self._subscriber.subscribe(
                    OrderSubmittedEvent,
                    self.on_order_submitted
                )
    """
    
    @abstractmethod
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
        group: Optional[str] = None
    ) -> None:
        """
        Subscribe to an event type with a handler function.
        
        Args:
            event_type: The event class to listen for
            handler: Async callback function that receives the event
            group: Consumer group name for load balancing
        """
        ...
    
    @abstractmethod
    async def start(self) -> None:
        """Start listening for events."""
        ...
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop listening for events."""
        ...
