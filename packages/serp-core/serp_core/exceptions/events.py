"""
Event-related exceptions for SERP event-driven architecture.
"""


class EventError(Exception):
    """Base exception for all event-related errors."""
    pass


class EventPublishError(EventError):
    """Raised when event publishing fails."""
    
    def __init__(self, event_type: str, message: str):
        self.event_type = event_type
        super().__init__(f"Failed to publish {event_type}: {message}")


class EventDeserializationError(EventError):
    """Raised when event deserialization fails."""
    
    def __init__(self, event_type: str, message: str):
        self.event_type = event_type
        super().__init__(f"Failed to deserialize {event_type}: {message}")


class EventHandlerError(EventError):
    """Raised when an event handler fails."""
    
    def __init__(self, event_type: str, handler_name: str, cause: Exception):
        self.event_type = event_type
        self.handler_name = handler_name
        self.cause = cause
        super().__init__(
            f"Handler '{handler_name}' failed for {event_type}: {cause}"
        )


class EventBusConnectionError(EventError):
    """Raised when connection to event bus backend fails."""
    
    def __init__(self, backend: str, message: str):
        self.backend = backend
        super().__init__(f"Event bus connection error ({backend}): {message}")


class UnknownEventTypeError(EventError):
    """Raised when an unknown event type is received."""
    
    def __init__(self, event_type: str):
        self.event_type = event_type
        super().__init__(f"Unknown event type: {event_type}")


class EventSubscriptionError(EventError):
    """Raised when event subscription fails."""
    
    def __init__(self, event_type: str, message: str):
        self.event_type = event_type
        super().__init__(f"Failed to subscribe to {event_type}: {message}")
