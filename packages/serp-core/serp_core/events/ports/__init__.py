"""
Event bus ports (interfaces) for dependency inversion.

These interfaces define the contract for event bus implementations.
Modules interact ONLY with these interfaces, never with Redis/Kafka directly.
"""

from .event_bus import IEventBus
from .event_publisher import IEventPublisher
from .event_subscriber import IEventSubscriber

__all__ = [
    "IEventBus",
    "IEventPublisher",
    "IEventSubscriber",
]
