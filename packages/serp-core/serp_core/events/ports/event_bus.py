"""
Event Bus Interface - Main contract for event-driven communication.

This interface abstracts the underlying event transport technology
(Redis, Kafka, RabbitMQ, etc.) allowing modules to remain decoupled
from infrastructure concerns.
"""

from abc import ABC, abstractmethod
from typing import Callable, Type, Optional, List, Awaitable

from ..domain.base_event import DomainEvent


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class IEventBus(ABC):
    """
    Abstract Event Bus Interface.
    
    This is the main contract for event-driven communication.
    Implementations can use Redis, Kafka, RabbitMQ, etc.
    
    Modules interact ONLY with this interface, never with
    the underlying technology directly.
    
    Example usage in a service:
        class InvoiceService:
            def __init__(self, event_bus: IEventBus):
                self._event_bus = event_bus
            
            async def create_invoice(self, request):
                invoice = Invoice(...)
                await self._repository.save(invoice)
                await self._event_bus.publish(InvoiceCreatedEvent(...))
    """
    
    @abstractmethod
    async def publish(
        self, 
        event: DomainEvent,
        stream: Optional[str] = None
    ) -> None:
        """
        Publish a domain event to the event stream.
        
        Args:
            event: The domain event to publish
            stream: Optional stream/topic override (defaults to event.stream_name())
        """
        ...
    
    @abstractmethod
    async def publish_many(
        self, 
        events: List[DomainEvent],
        stream: Optional[str] = None
    ) -> None:
        """
        Publish multiple events atomically (if supported by implementation).
        
        Args:
            events: List of domain events to publish
            stream: Optional stream/topic override
        """
        ...
    
    @abstractmethod
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
        group: Optional[str] = None
    ) -> None:
        """
        Subscribe to an event type with a handler function.
        
        The handler will be called asynchronously when events of
        the specified type are received.
        
        Args:
            event_type: The event class to listen for
            handler: Async callback function that receives the event
            group: Consumer group name for load balancing (implementation-specific)
        """
        ...
    
    @abstractmethod
    async def start(self) -> None:
        """
        Start the event consumer loop.
        
        Begins listening for events on subscribed streams/topics.
        This is typically called by the worker process.
        """
        ...
    
    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully stop the event consumer.
        
        Stops accepting new events and waits for in-flight handlers to complete.
        """
        ...
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the event bus connection is healthy.
        
        Returns:
            True if connected and operational, False otherwise
        """
        ...
