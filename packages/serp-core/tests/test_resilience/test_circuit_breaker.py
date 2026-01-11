"""Tests for circuit breaker pattern."""

import asyncio
import time

import pytest

from serp_core.resilience import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitOpenError,
    CircuitState,
    get_circuit_breaker_registry,
)


class TestCircuitState:
    """Test circuit breaker states."""

    def test_state_values(self):
        """Verify state enum values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreaker:
    """Test CircuitBreaker class."""

    def test_initial_state_is_closed(self):
        """Test that breaker starts in closed state."""
        breaker = CircuitBreaker(name="test")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open

    def test_success_keeps_closed(self):
        """Test that successes keep circuit closed."""
        breaker = CircuitBreaker(name="test")

        for _ in range(10):
            breaker.on_success()

        assert breaker.is_closed
        assert breaker.stats.successful_calls == 10

    def test_opens_after_threshold_failures(self):
        """Test that circuit opens after failure threshold."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=3,
            failure_window=60.0,
        )

        # First 2 failures - still closed
        for _ in range(2):
            breaker.on_failure()
        assert breaker.is_closed

        # 3rd failure - opens
        breaker.on_failure()
        assert breaker.is_open

    def test_open_rejects_calls(self):
        """Test that open circuit rejects calls."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=60.0,
        )

        breaker.on_failure()
        assert breaker.is_open

        with pytest.raises(CircuitOpenError) as exc_info:
            breaker.before_call()

        assert exc_info.value.name == "test"
        assert exc_info.value.remaining_time > 0

    def test_transitions_to_half_open(self):
        """Test transition from open to half-open after timeout."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=0.1,  # Very short for testing
        )

        breaker.on_failure()
        assert breaker.is_open

        # Wait for recovery timeout
        time.sleep(0.15)

        # Accessing state should trigger transition
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.is_half_open

    def test_half_open_closes_on_success(self):
        """Test that half-open circuit closes on success threshold."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            success_threshold=2,
            recovery_timeout=0.01,
        )

        # Open circuit
        breaker.on_failure()
        assert breaker.is_open

        # Wait for half-open
        time.sleep(0.02)
        assert breaker.is_half_open

        # First success
        breaker.on_success()
        assert breaker.is_half_open

        # Second success - should close
        breaker.on_success()
        assert breaker.is_closed

    def test_half_open_reopens_on_failure(self):
        """Test that any failure in half-open reopens circuit."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=0.01,
        )

        # Open circuit
        breaker.on_failure()
        time.sleep(0.02)
        assert breaker.is_half_open

        # Failure reopens
        breaker.on_failure()
        assert breaker.is_open

    def test_failure_window(self):
        """Test that old failures are ignored outside window."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=3,
            failure_window=0.1,  # Very short window
        )

        # 2 failures
        breaker.on_failure()
        breaker.on_failure()

        # Wait for window to expire
        time.sleep(0.15)

        # This failure should be the only one in window
        breaker.on_failure()
        assert breaker.is_closed  # Only 1 failure in window

        # Two more failures should open
        breaker.on_failure()
        breaker.on_failure()
        assert breaker.is_open

    def test_excluded_exceptions(self):
        """Test that excluded exceptions don't count as failures."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            excluded_exceptions=(ValueError,),
        )

        # ValueError should not count as failure
        breaker.on_failure(ValueError("expected"))
        assert breaker.is_closed
        assert breaker.stats.successful_calls == 1

        # Other exception should count
        breaker.on_failure(RuntimeError("unexpected"))
        assert breaker.is_open

    def test_reset(self):
        """Test manual reset."""
        breaker = CircuitBreaker(name="test", failure_threshold=1)

        breaker.on_failure()
        assert breaker.is_open

        breaker.reset()
        assert breaker.is_closed

    def test_force_open(self):
        """Test manual force open."""
        breaker = CircuitBreaker(name="test")

        assert breaker.is_closed
        breaker.force_open()
        assert breaker.is_open

    def test_get_status(self):
        """Test status report."""
        breaker = CircuitBreaker(
            name="test-status",
            failure_threshold=5,
            recovery_timeout=30.0,
        )

        breaker.on_success()
        breaker.on_failure()

        status = breaker.get_status()

        assert status["name"] == "test-status"
        assert status["state"] == "closed"
        assert status["failure_threshold"] == 5
        assert status["stats"]["total_calls"] == 2
        assert status["stats"]["successful_calls"] == 1
        assert status["stats"]["failed_calls"] == 1


@pytest.mark.asyncio
class TestCircuitBreakerAsync:
    """Test circuit breaker async functionality."""

    async def test_context_manager_success(self):
        """Test using circuit breaker as context manager."""
        breaker = CircuitBreaker(name="test-async")
        result = None

        async with breaker:
            result = "success"

        assert result == "success"
        assert breaker.stats.successful_calls == 1

    async def test_context_manager_failure(self):
        """Test context manager records failures."""
        breaker = CircuitBreaker(name="test-async", failure_threshold=5)

        with pytest.raises(ValueError):
            async with breaker:
                raise ValueError("test error")

        assert breaker.stats.failed_calls == 1

    async def test_decorator_success(self):
        """Test using circuit breaker as decorator."""
        breaker = CircuitBreaker(name="test-decorator")

        @breaker
        async def successful_operation():
            return "result"

        result = await successful_operation()

        assert result == "result"
        assert breaker.stats.successful_calls == 1

    async def test_decorator_failure(self):
        """Test decorator records failures."""
        breaker = CircuitBreaker(name="test-decorator", failure_threshold=5)

        @breaker
        async def failing_operation():
            raise RuntimeError("failure")

        with pytest.raises(RuntimeError):
            await failing_operation()

        assert breaker.stats.failed_calls == 1

    async def test_decorator_blocks_when_open(self):
        """Test that decorator blocks when circuit is open."""
        breaker = CircuitBreaker(
            name="test-decorator",
            failure_threshold=1,
            recovery_timeout=60.0,
        )

        @breaker
        async def operation():
            return "result"

        # Fail to open circuit
        breaker.on_failure()
        assert breaker.is_open

        # Should raise CircuitOpenError
        with pytest.raises(CircuitOpenError):
            await operation()


class TestCircuitBreakerRegistry:
    """Test circuit breaker registry."""

    def test_register_and_get(self):
        """Test registering and retrieving breakers."""
        registry = CircuitBreakerRegistry()
        breaker = CircuitBreaker(name="test")

        registry.register(breaker)

        assert registry.get("test") is breaker
        assert registry.get("nonexistent") is None

    def test_get_or_create(self):
        """Test get_or_create creates new breaker if needed."""
        registry = CircuitBreakerRegistry()

        breaker1 = registry.get_or_create("service-a", failure_threshold=3)
        breaker2 = registry.get_or_create("service-a", failure_threshold=10)

        # Should return same instance
        assert breaker1 is breaker2
        assert breaker1.failure_threshold == 3

    def test_remove(self):
        """Test removing breakers."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("test")

        assert registry.remove("test")
        assert registry.get("test") is None
        assert not registry.remove("nonexistent")

    def test_get_all_statuses(self):
        """Test getting all statuses."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("service-a")
        registry.get_or_create("service-b")

        statuses = registry.get_all_statuses()

        assert "service-a" in statuses
        assert "service-b" in statuses
        assert statuses["service-a"]["state"] == "closed"

    def test_get_open_circuits(self):
        """Test getting open circuits."""
        registry = CircuitBreakerRegistry()
        breaker_a = registry.get_or_create("service-a", failure_threshold=1)
        registry.get_or_create("service-b", failure_threshold=1)

        # Open one circuit
        breaker_a.on_failure()

        open_circuits = registry.get_open_circuits()
        assert "service-a" in open_circuits
        assert "service-b" not in open_circuits

    def test_reset_all(self):
        """Test resetting all breakers."""
        registry = CircuitBreakerRegistry()
        breaker_a = registry.get_or_create("service-a", failure_threshold=1)
        breaker_b = registry.get_or_create("service-b", failure_threshold=1)

        breaker_a.on_failure()
        breaker_b.on_failure()

        assert breaker_a.is_open
        assert breaker_b.is_open

        registry.reset_all()

        assert breaker_a.is_closed
        assert breaker_b.is_closed

    def test_clear(self):
        """Test clearing registry."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("service-a")
        registry.get_or_create("service-b")

        registry.clear()

        assert registry.get("service-a") is None
        assert registry.get("service-b") is None

    def test_global_registry(self):
        """Test global registry singleton."""
        reg1 = get_circuit_breaker_registry()
        reg2 = get_circuit_breaker_registry()

        assert reg1 is reg2
