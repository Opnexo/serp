"""
Test configuration for serp-core
"""

import pytest


@pytest.fixture
def sample_entity():
    """Sample entity for testing"""
    from dataclasses import dataclass

    from serp_core.domain import Entity

    @dataclass
    class TestEntity(Entity):
        name: str

    return TestEntity(name="Test")


@pytest.fixture
def sample_value_object():
    """Sample value object for testing"""
    from dataclasses import dataclass

    from serp_core.domain import ValueObject

    @dataclass(frozen=True)
    class TestValueObject(ValueObject):
        value: str

    return TestValueObject(value="test")
