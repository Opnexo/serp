"""Tests for event schema versioning system."""

from dataclasses import dataclass
from typing import ClassVar, Dict
from uuid import uuid4

import pytest

from serp_core.events import (
    DomainEvent,
    EventEnvelope,
    EventMetadata,
    EventMigrationRegistry,
    compare_versions,
    get_event_migration_registry,
    parse_version,
)
from serp_core.events.adapters import InMemoryEventBus


class TestVersionParsing:
    """Test version string parsing utilities."""

    def test_parse_simple_version(self):
        """Test parsing single number version."""
        assert parse_version("1") == (1, 0)
        assert parse_version("2") == (2, 0)

    def test_parse_major_minor_version(self):
        """Test parsing major.minor version."""
        assert parse_version("1.0") == (1, 0)
        assert parse_version("1.5") == (1, 5)
        assert parse_version("2.3") == (2, 3)

    def test_parse_full_version(self):
        """Test parsing major.minor.patch (patch is ignored)."""
        assert parse_version("1.0.0") == (1, 0)
        assert parse_version("2.3.5") == (2, 3)


class TestVersionComparison:
    """Test version comparison utility."""

    def test_compare_equal_versions(self):
        """Test equal versions."""
        assert compare_versions("1", "1") == 0
        assert compare_versions("1.0", "1") == 0
        assert compare_versions("2.5", "2.5") == 0

    def test_compare_less_than(self):
        """Test v1 < v2."""
        assert compare_versions("1", "2") == -1
        assert compare_versions("1.0", "1.1") == -1
        assert compare_versions("1.9", "2.0") == -1

    def test_compare_greater_than(self):
        """Test v1 > v2."""
        assert compare_versions("2", "1") == 1
        assert compare_versions("1.5", "1.4") == 1
        assert compare_versions("3.0", "2.9") == 1


# Test event classes
@dataclass(kw_only=True)
class PartnerCreatedEventV1(DomainEvent):
    """V1 of partner created event."""
    VERSION: ClassVar[int] = 1
    VERSION_HISTORY: ClassVar[Dict[int, str]] = {
        1: "Initial version with partner_id, name, email",
    }

    partner_id: str
    name: str
    email: str

    @classmethod
    def base_event_type(cls) -> str:
        return "crm.partner.created"


@dataclass(kw_only=True)
class PartnerCreatedEventV2(DomainEvent):
    """V2 of partner created event with phone number."""
    VERSION: ClassVar[int] = 2
    VERSION_HISTORY: ClassVar[Dict[int, str]] = {
        1: "Initial version with partner_id, name, email",
        2: "Added phone_number field",
    }

    partner_id: str
    name: str
    email: str
    phone_number: str

    @classmethod
    def base_event_type(cls) -> str:
        return "crm.partner.created"


class TestDomainEventVersioning:
    """Test DomainEvent versioning features."""

    def test_event_has_version(self):
        """Test that events have VERSION class attribute."""
        assert PartnerCreatedEventV1.VERSION == 1
        assert PartnerCreatedEventV2.VERSION == 2

    def test_event_type_includes_version(self):
        """Test that event_type() includes version suffix."""
        assert PartnerCreatedEventV1.event_type() == "crm.partner.created.v1"
        assert PartnerCreatedEventV2.event_type() == "crm.partner.created.v2"

    def test_base_event_type_excludes_version(self):
        """Test that base_event_type() does not include version."""
        assert PartnerCreatedEventV1.base_event_type() == "crm.partner.created"
        assert PartnerCreatedEventV2.base_event_type() == "crm.partner.created"

    def test_schema_version_method(self):
        """Test schema_version() class method."""
        assert PartnerCreatedEventV1.schema_version() == 1
        assert PartnerCreatedEventV2.schema_version() == 2

    def test_metadata_has_schema_version(self):
        """Test that event metadata contains schema version."""
        event = PartnerCreatedEventV1(
            partner_id="p-123",
            name="Acme Corp",
            email="info@acme.com",
        )
        assert event.metadata.schema_version == "1"

    def test_metadata_version_synced_with_class(self):
        """Test that metadata version is synced from class VERSION."""
        event_v2 = PartnerCreatedEventV2(
            partner_id="p-456",
            name="Beta Inc",
            email="info@beta.com",
            phone_number="+1234567890",
        )
        assert event_v2.metadata.schema_version == "2"

    def test_stream_name_not_affected_by_version(self):
        """Test that stream_name() is consistent across versions."""
        assert PartnerCreatedEventV1.stream_name() == "crm-events"
        assert PartnerCreatedEventV2.stream_name() == "crm-events"


class TestEventEnvelopeVersioning:
    """Test EventEnvelope versioning features."""

    def test_envelope_contains_version_info(self):
        """Test that envelope includes version information."""
        event = PartnerCreatedEventV1(
            partner_id="p-123",
            name="Acme Corp",
            email="info@acme.com",
        )
        envelope = EventEnvelope.wrap(event)

        assert envelope.event_type == "crm.partner.created.v1"
        assert envelope.base_event_type == "crm.partner.created"
        assert envelope.schema_version == 1

    def test_envelope_v2_version_info(self):
        """Test envelope with v2 event."""
        event = PartnerCreatedEventV2(
            partner_id="p-456",
            name="Beta Inc",
            email="info@beta.com",
            phone_number="+1234567890",
        )
        envelope = EventEnvelope.wrap(event)

        assert envelope.event_type == "crm.partner.created.v2"
        assert envelope.base_event_type == "crm.partner.created"
        assert envelope.schema_version == 2

    def test_envelope_json_serialization(self):
        """Test that version info survives JSON round-trip."""
        event = PartnerCreatedEventV2(
            partner_id="p-789",
            name="Gamma LLC",
            email="info@gamma.com",
            phone_number="+9876543210",
        )
        envelope = EventEnvelope.wrap(event)
        json_str = envelope.to_json()
        restored = EventEnvelope.from_json(json_str)

        assert restored.event_type == "crm.partner.created.v2"
        assert restored.base_event_type == "crm.partner.created"
        assert restored.schema_version == 2

    def test_envelope_handles_legacy_without_version(self):
        """Test backward compatibility with envelopes without version."""
        # Simulate legacy JSON without base_event_type and schema_version
        legacy_json = (
            '{"envelope_id": "12345678-1234-1234-1234-123456789012", '
            '"event_type": "crm.partner.created.v1", '
            '"stream": "crm-events", '
            '"payload": {"partner_id": "p-123", "name": "Test"}, '
            '"metadata": {}, '
            '"created_at": "2024-01-01T00:00:00"}'
        )
        envelope = EventEnvelope.from_json(legacy_json)

        # Should extract base_event_type from event_type
        assert envelope.base_event_type == "crm.partner.created"
        assert envelope.schema_version == 1


class TestEventMigrationRegistry:
    """Test event migration functionality."""

    def test_register_migration(self):
        """Test registering a migration function."""
        registry = EventMigrationRegistry()

        @registry.register("test.event", 1, 2)
        def migrate_v1_to_v2(payload):
            payload["new_field"] = "default"
            return payload

        assert registry.has_migration("test.event", 1, 2)
        assert not registry.has_migration("test.event", 2, 3)

    def test_migrate_payload(self):
        """Test migrating a payload."""
        registry = EventMigrationRegistry()

        @registry.register("test.event", 1, 2)
        def migrate_v1_to_v2(payload):
            payload["phone"] = payload.get("phone", "unknown")
            return payload

        payload = {"name": "Test", "email": "test@test.com"}
        migrated = registry.migrate("test.event", payload, 1, 2)

        assert migrated["name"] == "Test"
        assert migrated["phone"] == "unknown"

    def test_migrate_chain(self):
        """Test migrating through multiple versions."""
        registry = EventMigrationRegistry()

        @registry.register("test.event", 1, 2)
        def migrate_v1_to_v2(payload):
            payload["field_v2"] = "added_in_v2"
            return payload

        @registry.register("test.event", 2, 3)
        def migrate_v2_to_v3(payload):
            payload["field_v3"] = "added_in_v3"
            return payload

        payload = {"original": "data"}
        migrated = registry.migrate("test.event", payload, 1, 3)

        assert migrated["original"] == "data"
        assert migrated["field_v2"] == "added_in_v2"
        assert migrated["field_v3"] == "added_in_v3"

    def test_migrate_same_version_no_op(self):
        """Test that same version migration is a no-op."""
        registry = EventMigrationRegistry()
        payload = {"data": "unchanged"}
        result = registry.migrate("any.event", payload, 1, 1)

        assert result == payload

    def test_migrate_missing_path_raises(self):
        """Test that missing migration path raises error."""
        registry = EventMigrationRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.migrate("unknown.event", {}, 1, 2)

        assert "No migration found" in str(exc_info.value)

    def test_can_migrate_checks_path(self):
        """Test can_migrate checks for complete path."""
        registry = EventMigrationRegistry()

        @registry.register("test.event", 1, 2)
        def migrate_v1_to_v2(payload):
            return payload

        assert registry.can_migrate("test.event", 1, 2)
        assert registry.can_migrate("test.event", 1, 1)  # Same version
        assert not registry.can_migrate("test.event", 1, 3)  # No v2->v3

    def test_global_migration_registry(self):
        """Test global registry singleton."""
        reg1 = get_event_migration_registry()
        reg2 = get_event_migration_registry()

        assert reg1 is reg2


@pytest.mark.asyncio
class TestInMemoryEventBusVersioning:
    """Test version-aware event bus functionality."""

    async def test_subscribe_to_specific_version(self):
        """Test subscribing to specific event version."""
        bus = InMemoryEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(PartnerCreatedEventV1, handler)

        # Publish v1 - should be received
        event_v1 = PartnerCreatedEventV1(
            partner_id="p-1",
            name="Test",
            email="test@test.com",
        )
        await bus.publish(event_v1)

        assert len(received) == 1
        assert received[0].partner_id == "p-1"

    async def test_version_specific_handlers_isolated(self):
        """Test that v1 handler doesn't receive v2 events."""
        bus = InMemoryEventBus()
        v1_received = []
        v2_received = []

        async def v1_handler(event):
            v1_received.append(event)

        async def v2_handler(event):
            v2_received.append(event)

        bus.subscribe(PartnerCreatedEventV1, v1_handler)
        bus.subscribe(PartnerCreatedEventV2, v2_handler)

        # Publish v2
        event_v2 = PartnerCreatedEventV2(
            partner_id="p-2",
            name="Test V2",
            email="v2@test.com",
            phone_number="+1111111111",
        )
        await bus.publish(event_v2)

        assert len(v1_received) == 0  # v1 handler should NOT receive v2
        assert len(v2_received) == 1

    async def test_subscribe_all_versions(self):
        """Test subscribing to all versions of an event."""
        bus = InMemoryEventBus()
        received = []

        async def all_versions_handler(event, payload):
            received.append((event, payload))

        bus.subscribe_all_versions("crm.partner.created", all_versions_handler)

        # Publish v1
        event_v1 = PartnerCreatedEventV1(
            partner_id="p-1",
            name="V1 Partner",
            email="v1@test.com",
        )
        await bus.publish(event_v1)

        # Publish v2
        event_v2 = PartnerCreatedEventV2(
            partner_id="p-2",
            name="V2 Partner",
            email="v2@test.com",
            phone_number="+2222222222",
        )
        await bus.publish(event_v2)

        assert len(received) == 2
        assert received[0][1]["schema_version"] == 1
        assert received[1][1]["schema_version"] == 2

    async def test_subscribe_all_versions_with_migration(self):
        """Test auto-migration when subscribing to all versions."""
        bus = InMemoryEventBus()
        registry = get_event_migration_registry()
        received_payloads = []

        # Register migration
        @registry.register("crm.partner.created", 1, 2)
        def migrate_v1_to_v2(payload):
            payload["phone_number"] = payload.get("phone_number", "N/A")
            return payload

        async def handler(event, payload):
            received_payloads.append(payload)

        bus.subscribe_all_versions(
            "crm.partner.created",
            handler,
            migrate_to_version=2,
        )

        # Publish v1 event
        event_v1 = PartnerCreatedEventV1(
            partner_id="p-migrate",
            name="Migrate Me",
            email="migrate@test.com",
        )
        await bus.publish(event_v1)

        # Handler should receive migrated payload
        assert len(received_payloads) == 1
        assert received_payloads[0]["phone_number"] == "N/A"
        assert received_payloads[0]["schema_version"] == 2

    async def test_get_base_handler_count(self):
        """Test counting base event type handlers."""
        bus = InMemoryEventBus()

        async def handler(event, payload):
            pass

        bus.subscribe_all_versions("crm.partner.created", handler)
        bus.subscribe_all_versions("crm.partner.created", handler)

        assert bus.get_base_handler_count("crm.partner.created") == 2
        assert bus.get_base_handler_count("crm.other.event") == 0
