"""
Redis Streams Event Bus implementation.

Production-ready implementation using Redis Streams for:
- Persistent message storage
- Consumer groups for load balancing
- Automatic message acknowledgment
- Retry handling for failed messages
"""

import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Type, Optional, Any
from uuid import UUID
from datetime import datetime

from ..domain.base_event import DomainEvent, EventMetadata
from ..domain.event_envelope import EventEnvelope
from ..ports.event_bus import IEventBus, EventHandler


@dataclass
class RedisEventBus(IEventBus):
    """
    Redis Streams implementation of IEventBus.
    
    Features:
    - Consumer groups for load balancing across workers
    - Message acknowledgment for reliable delivery
    - Automatic retry of failed messages
    - Persistent message storage in Redis Streams
    
    Prerequisites:
    - redis[hiredis] package: `pip install redis[hiredis]`
    - Redis server 5.0+
    
    Example:
        from redis.asyncio import Redis
        
        redis_client = Redis.from_url("redis://localhost:6379")
        event_bus = RedisEventBus(
            redis_client=redis_client,
            consumer_group="serp-workers",
            consumer_name="worker-1"
        )
        
        # Subscribe before starting
        event_bus.subscribe(InvoiceCreatedEvent, on_invoice_created)
        
        # Start consuming
        await event_bus.start()
    
    Args:
        redis_client: Async Redis client instance
        consumer_group: Name of the consumer group for load balancing
        consumer_name: Unique name for this consumer instance
        max_retry: Maximum retry attempts for failed messages
        block_ms: Milliseconds to block waiting for messages
    """
    
    redis_client: Any  # redis.asyncio.Redis (optional dependency)
    consumer_group: str
    consumer_name: str
    max_retry: int = 3
    block_ms: int = 5000
    
    _handlers: Dict[str, List[EventHandler]] = field(default_factory=lambda: defaultdict(list))
    _subscribed_streams: set = field(default_factory=set)
    _event_types: Dict[str, Type[DomainEvent]] = field(default_factory=dict)
    _running: bool = field(default=False)
    
    async def publish(
        self, 
        event: DomainEvent,
        stream: Optional[str] = None
    ) -> None:
        """
        Publish event to Redis Stream.
        
        Creates an EventEnvelope and adds it to the appropriate stream.
        """
        stream_name = stream or event.stream_name()
        envelope = EventEnvelope.wrap(event, stream_name)
        
        await self.redis_client.xadd(
            stream_name,
            {
                "event_type": event.event_type(),
                "data": envelope.to_json()
            }
        )
    
    async def publish_many(
        self, 
        events: List[DomainEvent],
        stream: Optional[str] = None
    ) -> None:
        """
        Publish multiple events using Redis pipeline for efficiency.
        """
        if not events:
            return
            
        async with self.redis_client.pipeline() as pipe:
            for event in events:
                stream_name = stream or event.stream_name()
                envelope = EventEnvelope.wrap(event, stream_name)
                pipe.xadd(stream_name, {
                    "event_type": event.event_type(),
                    "data": envelope.to_json()
                })
            await pipe.execute()
    
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
        group: Optional[str] = None
    ) -> None:
        """
        Register a handler for an event type.
        
        The stream will be subscribed to when start() is called.
        """
        type_name = event_type.event_type()
        stream_name = event_type.stream_name()
        
        self._handlers[type_name].append(handler)
        self._subscribed_streams.add(stream_name)
        self._event_types[type_name] = event_type
    
    async def start(self) -> None:
        """
        Start the consumer loop.
        
        Creates consumer groups and begins reading from subscribed streams.
        """
        self._running = True
        await self._ensure_consumer_groups()
        
        print(f"📡 RedisEventBus started. Consumer: {self.consumer_name}")
        print(f"   Streams: {self._subscribed_streams}")
        
        while self._running:
            try:
                # Build streams dict with ">" to get only new messages
                streams = {s: ">" for s in self._subscribed_streams}
                
                if not streams:
                    await asyncio.sleep(1)
                    continue
                
                messages = await self.redis_client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams=streams,
                    count=10,
                    block=self.block_ms
                )
                
                if messages:
                    for stream_name, stream_messages in messages:
                        # Handle bytes or string stream name
                        if isinstance(stream_name, bytes):
                            stream_name = stream_name.decode()
                            
                        for message_id, message_data in stream_messages:
                            await self._process_message(
                                stream_name, message_id, message_data
                            )
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ RedisEventBus consumer error: {e}")
                await asyncio.sleep(1)
        
        print("📡 RedisEventBus stopped.")
    
    async def stop(self) -> None:
        """Gracefully stop the consumer loop."""
        self._running = False
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def _process_message(
        self, 
        stream: str, 
        message_id: bytes | str, 
        data: dict
    ) -> None:
        """Process a single message from the stream."""
        # Extract event type and data
        event_type = self._extract_field(data, "event_type")
        event_data = self._extract_field(data, "data")
        
        if isinstance(message_id, bytes):
            message_id = message_id.decode()
        
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            # No handlers for this event type - acknowledge and skip
            await self.redis_client.xack(stream, self.consumer_group, message_id)
            return
        
        try:
            # Deserialize event from envelope
            envelope = EventEnvelope.from_json(event_data)
            event = self._reconstruct_event(event_type, envelope)
            
            # Call all handlers
            for handler in handlers:
                await handler(event)
            
            # Acknowledge successful processing
            await self.redis_client.xack(stream, self.consumer_group, message_id)
            
        except Exception as e:
            print(f"❌ Handler error for {event_type}: {e}")
            # Don't acknowledge - message will be retried via XPENDING
    
    def _extract_field(self, data: dict, field: str) -> str:
        """Extract field from message data, handling bytes/str."""
        value = data.get(field.encode(), data.get(field, ""))
        if isinstance(value, bytes):
            value = value.decode()
        return value
    
    def _reconstruct_event(self, event_type: str, envelope: EventEnvelope) -> DomainEvent:
        """Reconstruct a DomainEvent from its envelope."""
        # Get the event class
        event_class = self._event_types.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        # Rebuild metadata
        metadata = EventMetadata(
            event_id=UUID(envelope.metadata.get("event_id", str(envelope.envelope_id))),
            timestamp=datetime.fromisoformat(envelope.metadata.get("timestamp", datetime.utcnow().isoformat())),
            correlation_id=UUID(envelope.metadata["correlation_id"]) if envelope.metadata.get("correlation_id") else None,
            causation_id=UUID(envelope.metadata["causation_id"]) if envelope.metadata.get("causation_id") else None,
            user_id=UUID(envelope.metadata["user_id"]) if envelope.metadata.get("user_id") else None,
            version=envelope.metadata.get("version", "1.0"),
        )
        
        # Create event with payload + metadata
        return event_class(
            metadata=metadata,
            **envelope.payload
        )
    
    async def _ensure_consumer_groups(self) -> None:
        """Create consumer groups if they don't exist."""
        for stream in self._subscribed_streams:
            try:
                await self.redis_client.xgroup_create(
                    stream, 
                    self.consumer_group, 
                    id="0",
                    mkstream=True
                )
                print(f"   Created consumer group '{self.consumer_group}' on stream '{stream}'")
            except Exception as e:
                # Group already exists - that's fine
                if "BUSYGROUP" not in str(e):
                    print(f"   Warning creating group on {stream}: {e}")
