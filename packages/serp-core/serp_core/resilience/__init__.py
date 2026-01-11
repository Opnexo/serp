"""
SERP Resilience Patterns

This module provides resilience patterns for cross-module communication:
- Circuit Breaker: Prevents cascade failures when a module is unhealthy
- Retry: Automatic retry with exponential backoff
- Timeout: Configurable timeouts for external calls
- Module Client: High-level client combining all patterns

Usage:
    from serp_core.resilience import CircuitBreaker, CircuitBreakerRegistry

    # Create a circuit breaker for CRM module
    breaker = CircuitBreaker(name="crm-api")

    # Use as decorator
    @breaker
    async def call_crm_service():
        return await http_client.get("/api/crm/partners")

    # Or use context manager
    async with breaker:
        result = await call_external_api()

    # Or use ModuleClient for full resilience
    from serp_core.resilience import ModuleClient

    crm = ModuleClient(module_name="crm", base_url="http://localhost:8000/api/crm")
    partners = await crm.get("/partners")
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerRegistry,
    CircuitBreakerStats,
    CircuitOpenError,
    CircuitState,
    get_circuit_breaker_registry,
)
from .module_client import ModuleClient, ModuleClientConfig
from .retry import RetryPolicy, retry_with_backoff
from .timeout import TimeoutError, timeout_context, with_timeout

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitBreakerRegistry",
    "CircuitBreakerStats",
    "CircuitOpenError",
    "CircuitState",
    "get_circuit_breaker_registry",
    # Retry
    "RetryPolicy",
    "retry_with_backoff",
    # Timeout
    "TimeoutError",
    "timeout_context",
    "with_timeout",
    # Module Client
    "ModuleClient",
    "ModuleClientConfig",
]
