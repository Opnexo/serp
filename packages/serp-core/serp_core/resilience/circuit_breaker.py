"""
Circuit Breaker Pattern Implementation

The Circuit Breaker prevents cascade failures by detecting when a service
is failing and temporarily blocking requests to it.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests are blocked
- HALF_OPEN: Testing if service recovered, limited requests allowed

Transitions:
- CLOSED -> OPEN: After failure_threshold failures within failure_window
- OPEN -> HALF_OPEN: After recovery_timeout seconds
- HALF_OPEN -> CLOSED: After success_threshold consecutive successes
- HALF_OPEN -> OPEN: On any failure

Example:
    breaker = CircuitBreaker(
        name="crm-service",
        failure_threshold=5,      # Open after 5 failures
        success_threshold=3,      # Close after 3 successes
        recovery_timeout=30.0,    # Wait 30s before half-open
        failure_window=60.0,      # Count failures in 60s window
    )

    @breaker
    async def call_crm():
        return await http_client.get("/api/crm/partners")
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""
    pass


class CircuitOpenError(CircuitBreakerError):
    """Raised when circuit is open and request is blocked."""

    def __init__(
        self,
        name: str,
        remaining_time: float,
        message: Optional[str] = None,
    ):
        self.name = name
        self.remaining_time = remaining_time
        super().__init__(
            message or f"Circuit '{name}' is open. Retry in {remaining_time:.1f}s"
        )


@dataclass
class CircuitBreakerStats:
    """Statistics for a circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "success_rate": (
                self.successful_calls / self.total_calls
                if self.total_calls > 0 else 0.0
            ),
            "last_failure_time": (
                self.last_failure_time.isoformat()
                if self.last_failure_time else None
            ),
            "last_success_time": (
                self.last_success_time.isoformat()
                if self.last_success_time else None
            ),
        }


@dataclass
class CircuitBreaker:
    """
    Circuit Breaker implementation for resilient cross-module calls.

    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected immediately
    - HALF_OPEN: Testing recovery, limited requests allowed

    Args:
        name: Identifier for this circuit breaker (e.g., "crm-api")
        failure_threshold: Number of failures before opening circuit
        success_threshold: Consecutive successes needed to close from half-open
        recovery_timeout: Seconds to wait before transitioning to half-open
        failure_window: Time window (seconds) for counting failures
        excluded_exceptions: Exception types that should NOT count as failures

    Example:
        breaker = CircuitBreaker(name="payment-gateway")

        # As decorator
        @breaker
        async def process_payment(amount):
            return await gateway.charge(amount)

        # As context manager
        async with breaker:
            result = await external_call()

        # Manual control
        try:
            breaker.before_call()
            result = await risky_operation()
            breaker.on_success()
        except Exception as e:
            breaker.on_failure(e)
            raise
    """
    name: str
    failure_threshold: int = 5
    success_threshold: int = 3
    recovery_timeout: float = 30.0
    failure_window: float = 60.0
    excluded_exceptions: tuple = field(default_factory=tuple)

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_times: List[float] = field(default_factory=list, init=False)
    _consecutive_successes: int = field(default=0, init=False)
    _opened_at: Optional[float] = field(default=None, init=False)
    _stats: CircuitBreakerStats = field(
        default_factory=CircuitBreakerStats, init=False
    )
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, handling automatic transitions."""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._opened_at is not None:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self._stats

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state

        # Record state change
        self._stats.state_changes.append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Keep only last 100 state changes
        if len(self._stats.state_changes) > 100:
            self._stats.state_changes = self._stats.state_changes[-100:]

        logger.info(
            f"Circuit '{self.name}' transitioned from {old_state.value} "
            f"to {new_state.value}"
        )

        # Reset state-specific counters
        if new_state == CircuitState.HALF_OPEN:
            self._consecutive_successes = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_times.clear()
            self._opened_at = None

    def _count_recent_failures(self) -> int:
        """Count failures within the failure window."""
        now = time.monotonic()
        cutoff = now - self.failure_window
        self._failure_times = [t for t in self._failure_times if t > cutoff]
        return len(self._failure_times)

    def _remaining_recovery_time(self) -> float:
        """Get remaining time until recovery attempt."""
        if self._opened_at is None:
            return 0.0
        elapsed = time.monotonic() - self._opened_at
        remaining = self.recovery_timeout - elapsed
        return max(0.0, remaining)

    def before_call(self) -> None:
        """
        Check circuit state before making a call.

        Raises:
            CircuitOpenError: If circuit is open
        """
        current_state = self.state  # This triggers auto-transition

        if current_state == CircuitState.OPEN:
            self._stats.rejected_calls += 1
            raise CircuitOpenError(
                name=self.name,
                remaining_time=self._remaining_recovery_time(),
            )

    def on_success(self) -> None:
        """Record a successful call."""
        self._stats.total_calls += 1
        self._stats.successful_calls += 1
        self._stats.last_success_time = datetime.now(timezone.utc)

        if self._state == CircuitState.HALF_OPEN:
            self._consecutive_successes += 1
            if self._consecutive_successes >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def on_failure(self, exception: Optional[Exception] = None) -> None:
        """
        Record a failed call.

        Args:
            exception: The exception that occurred (if any)
        """
        # Check if this exception type should be excluded
        if exception is not None and self.excluded_exceptions:
            if isinstance(exception, self.excluded_exceptions):
                # Treat as success for circuit breaker purposes
                self.on_success()
                return

        self._stats.total_calls += 1
        self._stats.failed_calls += 1
        self._stats.last_failure_time = datetime.now(timezone.utc)

        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open state reopens the circuit
            self._opened_at = time.monotonic()
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            # Record failure time
            self._failure_times.append(time.monotonic())

            # Check if we've exceeded threshold
            if self._count_recent_failures() >= self.failure_threshold:
                self._opened_at = time.monotonic()
                self._transition_to(CircuitState.OPEN)

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self._transition_to(CircuitState.CLOSED)
        self._failure_times.clear()
        self._consecutive_successes = 0
        self._opened_at = None

    def force_open(self) -> None:
        """Manually force the circuit to open state."""
        self._opened_at = time.monotonic()
        self._transition_to(CircuitState.OPEN)

    async def __aenter__(self) -> "CircuitBreaker":
        """Async context manager entry."""
        async with self._lock:
            self.before_call()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit."""
        async with self._lock:
            if exc_type is None:
                self.on_success()
            else:
                self.on_failure(exc_val)
        return False  # Don't suppress exception

    def __call__(
        self, func: Callable[..., T]
    ) -> Callable[..., T]:
        """
        Use circuit breaker as a decorator.

        Example:
            @circuit_breaker
            async def call_external_api():
                return await http.get("/api/data")
        """
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                async with self:
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                self.before_call()
                try:
                    result = func(*args, **kwargs)
                    self.on_success()
                    return result
                except Exception as e:
                    self.on_failure(e)
                    raise
            return sync_wrapper

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "recovery_timeout": self.recovery_timeout,
            "recent_failures": self._count_recent_failures(),
            "consecutive_successes": self._consecutive_successes,
            "remaining_recovery_time": (
                self._remaining_recovery_time()
                if self._state == CircuitState.OPEN else None
            ),
            "stats": self._stats.to_dict(),
        }


class CircuitBreakerRegistry:
    """
    Registry for managing circuit breakers across modules.

    Provides centralized management and monitoring of all circuit breakers
    in the system.

    Example:
        registry = CircuitBreakerRegistry()

        # Get or create a circuit breaker
        crm_breaker = registry.get_or_create(
            "crm-api",
            failure_threshold=5,
            recovery_timeout=30.0,
        )

        # Get all statuses for monitoring
        statuses = registry.get_all_statuses()
    """

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    def register(self, breaker: CircuitBreaker) -> None:
        """Register a circuit breaker."""
        self._breakers[breaker.name] = breaker

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        return self._breakers.get(name)

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        recovery_timeout: float = 30.0,
        failure_window: float = 60.0,
        excluded_exceptions: tuple = (),
    ) -> CircuitBreaker:
        """
        Get existing or create new circuit breaker.

        Args:
            name: Unique identifier for the circuit breaker
            **kwargs: Arguments passed to CircuitBreaker constructor

        Returns:
            The circuit breaker instance
        """
        if name not in self._breakers:
            breaker = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                recovery_timeout=recovery_timeout,
                failure_window=failure_window,
                excluded_exceptions=excluded_exceptions,
            )
            self._breakers[name] = breaker
        return self._breakers[name]

    def remove(self, name: str) -> bool:
        """Remove a circuit breaker from the registry."""
        if name in self._breakers:
            del self._breakers[name]
            return True
        return False

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {
            name: breaker.get_status()
            for name, breaker in self._breakers.items()
        }

    def get_open_circuits(self) -> List[str]:
        """Get names of all open circuits."""
        return [
            name for name, breaker in self._breakers.items()
            if breaker.is_open
        ]

    def reset_all(self) -> None:
        """Reset all circuit breakers to closed state."""
        for breaker in self._breakers.values():
            breaker.reset()

    def clear(self) -> None:
        """Remove all circuit breakers."""
        self._breakers.clear()


# Global registry instance
_circuit_breaker_registry = CircuitBreakerRegistry()


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return _circuit_breaker_registry
