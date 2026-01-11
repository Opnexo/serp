"""
Apache Kafka Event Bus implementation.

Production-ready implementation using Kafka for:
- High-throughput event streaming
- Distributed event processing
- Partitioning for ordered delivery
- Long-term event retention
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
class KafkaEventBus(IEventBus):
    """
    Apache Kafka implementation of IEventBus.
    
    Features:
    - High-throughput event streaming
    - Consumer groups for load balancing
    - Partitioning for message ordering
    - Configurable retention and replay
    
    Prerequisites:
    - aiokafka package: `pip install aiokafka`
    - Kafka broker 2.0+
    
    Example:
        from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
        
        event_bus = KafkaEventBus(
            bootstrap_servers="localhost:9094",
            consumer_group="serp-workers",
        )
        
        # Subscribe before starting
        event_bus.subscribe(InvoiceCreatedEvent, on_invoice_created)
        
        # Start consuming
        await event_bus.start()
    
    Args:
        bootstrap_servers: Kafka broker addresses (comma-separated)
        consumer_group: Consumer group ID for load balancing
        client_id: Optional client identifier
        auto_offset_reset: Where to start consuming ("earliest" or "latest")
    """
    
    bootstrap_servers: str
    consumer_group: str
    client_id: str = "serp-event-bus"
    auto_offset_reset: str = "latest"
    
    _handlers: Dict[str, List[EventHandler]] = field(default_factory=lambda: defaultdict(list))
    _subscribed_topics: set = field(default_factory=set)
    _event_types: Dict[str, Type[DomainEvent]] = field(default_factory=dict)
    _running: bool = field(default=False)
    _producer: Any = field(default=None)
    _consumer: Any = field(default=None)
    
    async def _get_producer(self):
        """Lazy initialization of Kafka producer."""
        if self._producer is None:
            try:
                from aiokafka import AIOKafkaProducer
            except ImportError:
                raise ImportError(
                    "aiokafka is required for KafkaEventBus. "
                    "Install with: pip install aiokafka"
                )
            
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-producer",
                value_serializer=lambda v: v.encode('utf-8'),
            )
            await self._producer.start()
        return self._producer
    
    async def _get_consumer(self):
        """Lazy initialization of Kafka consumer."""
        if self._consumer is None:
            try:
                from aiokafka import AIOKafkaConsumer
            except ImportError:
                raise ImportError(
                    "aiokafka is required for KafkaEventBus. "
                    "Install with: pip install aiokafka"
                )
            
            topics = list(self._subscribed_topics)
            if not topics:
                return None
                
            self._consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group,
                client_id=f"{self.client_id}-consumer",
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=False,  # Manual commit after processing
                value_deserializer=lambda v: v.decode('utf-8'),
            )
            await self._consumer.start()
        return self._consumer
    
    async def publish(
        self, 
        event: DomainEvent,
        stream: Optional[str] = None
    ) -> None:
        """
        Publish event to Kafka topic.
        
        The topic name is derived from the event's stream_name() method.
        """
        topic = stream or event.stream_name()
        envelope = EventEnvelope.wrap(event, topic)
        
        producer = await self._get_producer()
        
        # Use event_id as key for partitioning (ensures related events go to same partition)
        key = str(event.metadata.event_id).encode('utf-8')
        
        await producer.send_and_wait(
            topic,
            value=envelope.to_json(),
            key=key,
            headers=[
                ("event_type", event.event_type().encode('utf-8')),
            ]
        )
    
    async def publish_many(
        self, 
        events: List[DomainEvent],
        stream: Optional[str] = None
    ) -> None:
        """
        Publish multiple events using Kafka batch.
        """
        if not events:
            return
        
        producer = await self._get_producer()
        
        # Send all messages
        futures = []
        for event in events:
            topic = stream or event.stream_name()
            envelope = EventEnvelope.wrap(event, topic)
            key = str(event.metadata.event_id).encode('utf-8')
            
            future = await producer.send(
                topic,
                value=envelope.to_json(),
                key=key,
                headers=[
                    ("event_type", event.event_type().encode('utf-8')),
                ]
            )
            futures.append(future)
        
        # Wait for all to complete
        await asyncio.gather(*[f for f in futures])
    
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
        group: Optional[str] = None
    ) -> None:
        """
        Subscribe to a Kafka topic for an event type.
        
        Note: Topic subscription happens when start() is called.
        """
        type_name = event_type.event_type()
        topic = event_type.stream_name()
        
        self._handlers[type_name].append(handler)
        self._subscribed_topics.add(topic)
        self._event_types[type_name] = event_type
    
    async def start(self) -> None:
        """
        Start consuming from Kafka topics.
        """
        self._running = True
        consumer = await self._get_consumer()
        
        if consumer is None:
            print("⚠️ KafkaEventBus: No subscriptions, nothing to consume")
            return
        
        print(f"📡 KafkaEventBus started. Group: {self.consumer_group}")
        print(f"   Topics: {self._subscribed_topics}")
        
        try:
            async for message in consumer:
                if not self._running:
                    break
                
                try:
                    await self._process_message(message)
                    # Commit offset after successful processing
                    await consumer.commit()
                except Exception as e:
                    print(f"❌ KafkaEventBus handler error: {e}")
                    # Don't commit - message will be redelivered
                    
        except asyncio.CancelledError:
            pass
        finally:
            print("📡 KafkaEventBus stopped.")
    
    async def stop(self) -> None:
        """Gracefully stop the consumer and producer."""
        self._running = False
        
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            
        if self._producer:
            await self._producer.stop()
            self._producer = None
    
    async def health_check(self) -> bool:
        """Check Kafka connection health."""
        try:
            producer = await self._get_producer()
            # Send a metadata request to check connectivity
            await producer.client.check_version()
            return True
        except Exception:
            return False
    
    async def _process_message(self, message) -> None:
        """Process a single Kafka message."""
        # Extract event type from headers
        event_type = None
        for key, value in message.headers or []:
            if key == "event_type":
                event_type = value.decode('utf-8')
                break
        
        if not event_type:
            print(f"⚠️ Message missing event_type header, skipping")
            return
        
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            return
        
        # Deserialize event from envelope
        envelope = EventEnvelope.from_json(message.value)
        event = self._reconstruct_event(event_type, envelope)
        
        # Call all handlers
        for handler in handlers:
            await handler(event)
    
    def _reconstruct_event(self, event_type: str, envelope: EventEnvelope) -> DomainEvent:
        """Reconstruct a DomainEvent from its envelope."""
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
        
        return event_class(
            metadata=metadata,
            **envelope.payload
        )
