"""
Event envelope for serialization and transport.

The EventEnvelope wraps a DomainEvent with routing information
for transmission over the event bus.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import json
import re

from .base_event import DomainEvent, EventMetadata


@dataclass
class EventEnvelope:
    """
    Wrapper for domain events that includes routing and serialization info.

    The envelope adds transport-layer information while keeping
    the domain event clean of infrastructure concerns.

    Attributes:
        event_type: The versioned event type (e.g., "invoicing.invoice.created.v1")
        base_event_type: The unversioned event type (e.g., "invoicing.invoice.created")
        schema_version: The schema version number
        stream: The target stream/topic name
        payload: The serialized event data
        metadata: Event metadata for tracing
        created_at: When the envelope was created
        envelope_id: Unique ID for this envelope (different from event_id)
    """
    event_type: str
    base_event_type: str
    schema_version: int
    stream: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    envelope_id: UUID = field(default_factory=uuid4)

    @classmethod
    def wrap(cls, event: DomainEvent, stream: Optional[str] = None) -> "EventEnvelope":
        """
        Wrap a domain event in an envelope for transport.

        Args:
            event: The domain event to wrap
            stream: Optional stream override (defaults to event's stream_name())

        Returns:
            EventEnvelope ready for serialization
        """
        from dataclasses import asdict

        # Serialize event payload (excluding metadata which goes in envelope)
        event_dict = asdict(event)
        metadata_dict = event_dict.pop('metadata', {})

        # Convert UUIDs and datetimes to strings
        payload = cls._serialize_values(event_dict)
        metadata = cls._serialize_values(metadata_dict)

        return cls(
            event_type=event.event_type(),
            base_event_type=event.base_event_type(),
            schema_version=event.VERSION,
            stream=stream or event.stream_name(),
            payload=payload,
            metadata=metadata,
        )

    def to_json(self) -> str:
        """Serialize envelope to JSON string."""
        data = {
            "envelope_id": str(self.envelope_id),
            "event_type": self.event_type,
            "base_event_type": self.base_event_type,
            "schema_version": self.schema_version,
            "stream": self.stream,
            "payload": self.payload,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "EventEnvelope":
        """Deserialize envelope from JSON string."""
        data = json.loads(json_str)

        # Handle legacy envelopes without version info
        schema_version = data.get("schema_version", 1)
        base_event_type = data.get("base_event_type")

        if base_event_type is None:
            # Extract from versioned event_type if not present
            base_event_type = cls._extract_base_event_type(data["event_type"])

        return cls(
            envelope_id=UUID(data["envelope_id"]),
            event_type=data["event_type"],
            base_event_type=base_event_type,
            schema_version=schema_version,
            stream=data["stream"],
            payload=data["payload"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    @staticmethod
    def _extract_base_event_type(event_type: str) -> str:
        """
        Extract base event type from versioned event type.

        E.g., "crm.partner.created.v1" -> "crm.partner.created"
        """
        # Remove version suffix if present
        match = re.match(r"(.+)\.v\d+$", event_type)
        if match:
            return match.group(1)
        return event_type

    @staticmethod
    def _extract_version(event_type: str) -> int:
        """
        Extract version number from versioned event type.

        E.g., "crm.partner.created.v2" -> 2
        """
        match = re.search(r"\.v(\d+)$", event_type)
        if match:
            return int(match.group(1))
        return 1

    @staticmethod
    def _serialize_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert non-JSON-serializable values to strings."""
        result = {}
        for key, value in data.items():
            if isinstance(value, UUID):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = EventEnvelope._serialize_values(value)
            else:
                result[key] = value
        return result
