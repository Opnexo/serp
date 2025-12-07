"""
Tests for domain entities
"""

from dataclasses import dataclass

from serp_core.domain import Entity


@dataclass
class TestCustomer(Entity):
    name: str
    email: str


def test_entity_has_id():
    """Test that entities have IDs"""
    customer = TestCustomer(name="John Doe", email="john@example.com")
    assert customer.id is not None


def test_entity_equality():
    """Test entity equality based on ID"""
    customer1 = TestCustomer(name="John Doe", email="john@example.com")
    customer2 = TestCustomer(name="Jane Doe", email="jane@example.com")
    customer2.id = customer1.id  # Same ID

    assert customer1 == customer2


def test_entity_inequality():
    """Test entity inequality with different IDs"""
    customer1 = TestCustomer(name="John Doe", email="john@example.com")
    customer2 = TestCustomer(name="John Doe", email="john@example.com")

    assert customer1 != customer2


def test_entity_mark_updated():
    """Test marking entity as updated"""
    customer = TestCustomer(name="John Doe", email="john@example.com")
    original_updated_at = customer.updated_at

    import time

    time.sleep(0.01)  # Small delay to ensure time difference

    customer._mark_updated()
    assert customer.updated_at > original_updated_at
