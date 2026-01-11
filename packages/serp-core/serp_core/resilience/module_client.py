"""
Resilient Module Client for cross-module communication.

Provides a high-level client for making calls to other SERP modules
with built-in resilience patterns (circuit breaker, retry, timeout).

Example:
    # Create client for CRM module
    crm_client = ModuleClient(
        module_name="crm",
        base_url="http://localhost:8000/api/crm",
    )

    # Make resilient call
    partners = await crm_client.call(
        "get_partners",
        method="GET",
        path="/partners",
    )
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TypeVar

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitOpenError,
    get_circuit_breaker_registry,
)
from .retry import RetryPolicy
from .timeout import TimeoutError, with_timeout

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ModuleClientConfig:
    """Configuration for a module client."""
    # Timeout settings
    default_timeout: float = 30.0

    # Circuit breaker settings
    circuit_failure_threshold: int = 5
    circuit_success_threshold: int = 3
    circuit_recovery_timeout: float = 30.0
    circuit_failure_window: float = 60.0

    # Retry settings
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    retry_jitter: float = 0.1

    # Exceptions that should not trigger circuit breaker
    excluded_exceptions: tuple = field(default_factory=tuple)

    # Exceptions that should trigger retry
    retryable_exceptions: tuple = field(
        default_factory=lambda: (ConnectionError, TimeoutError)
    )


@dataclass
class ModuleClient:
    """
    Resilient client for cross-module communication.

    Combines circuit breaker, retry, and timeout patterns for
    making reliable calls to other SERP modules.

    Args:
        module_name: Name of the target module
        base_url: Base URL for the module's API
        config: Client configuration (uses defaults if not provided)
        http_client: Optional HTTP client to use (for testing)

    Example:
        # Create client
        crm_client = ModuleClient(
            module_name="crm",
            base_url="http://localhost:8000/api/crm",
        )

        # Call with all resilience patterns
        try:
            result = await crm_client.call(
                "get_partner",
                method="GET",
                path="/partners/123",
            )
        except CircuitOpenError:
            # CRM module is having issues
            return cached_data or default_value
    """
    module_name: str
    base_url: str
    config: ModuleClientConfig = field(default_factory=ModuleClientConfig)
    http_client: Any = field(default=None)  # Optional httpx.AsyncClient or similar

    _circuit_breaker: CircuitBreaker = field(init=False)
    _retry_policy: RetryPolicy = field(init=False)

    def __post_init__(self) -> None:
        """Initialize resilience components."""
        # Get or create circuit breaker
        registry = get_circuit_breaker_registry()
        self._circuit_breaker = registry.get_or_create(
            name=f"{self.module_name}-api",
            failure_threshold=self.config.circuit_failure_threshold,
            success_threshold=self.config.circuit_success_threshold,
            recovery_timeout=self.config.circuit_recovery_timeout,
            failure_window=self.config.circuit_failure_window,
            excluded_exceptions=self.config.excluded_exceptions,
        )

        # Create retry policy
        self._retry_policy = RetryPolicy(
            max_retries=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            max_delay=self.config.retry_max_delay,
            jitter=self.config.retry_jitter,
            retryable_exceptions=self.config.retryable_exceptions,
        )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Access the circuit breaker for this client."""
        return self._circuit_breaker

    @property
    def is_available(self) -> bool:
        """Check if the module is available (circuit not open)."""
        return not self._circuit_breaker.is_open

    async def call(
        self,
        operation: str,
        method: str = "GET",
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        skip_retry: bool = False,
        skip_circuit_breaker: bool = False,
    ) -> Any:
        """
        Make a resilient call to the module.

        Args:
            operation: Name of the operation (for logging)
            method: HTTP method
            path: URL path (appended to base_url)
            params: Query parameters
            json: JSON body
            headers: Additional headers
            timeout: Override default timeout
            skip_retry: Disable retry for this call
            skip_circuit_breaker: Disable circuit breaker for this call

        Returns:
            Response data

        Raises:
            CircuitOpenError: If circuit is open
            TimeoutError: If call times out
            Exception: If all retries fail
        """
        actual_timeout = timeout or self.config.default_timeout
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        async def _make_request() -> Any:
            """Inner function that makes the actual HTTP request."""
            if self.http_client is None:
                # For production, use httpx or similar
                raise NotImplementedError(
                    "HTTP client not configured. "
                    "Set http_client in ModuleClient constructor."
                )

            response = await self.http_client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                timeout=actual_timeout,
            )
            response.raise_for_status()
            return response.json()

        async def _with_timeout() -> Any:
            """Apply timeout to the request."""
            return await with_timeout(
                actual_timeout,
                _make_request,
                operation_name=f"{self.module_name}.{operation}",
            )()

        async def _with_retry() -> Any:
            """Apply retry logic."""
            if skip_retry:
                return await _with_timeout()
            return await self._retry_policy.execute(_with_timeout)

        async def _with_circuit_breaker() -> Any:
            """Apply circuit breaker."""
            if skip_circuit_breaker:
                return await _with_retry()
            async with self._circuit_breaker:
                return await _with_retry()

        logger.debug(
            f"Calling {self.module_name}.{operation}: {method} {url}"
        )

        try:
            return await _with_circuit_breaker()
        except CircuitOpenError:
            logger.warning(
                f"Circuit open for {self.module_name}, "
                f"operation {operation} blocked"
            )
            raise
        except Exception as e:
            logger.error(
                f"Call to {self.module_name}.{operation} failed: {e}"
            )
            raise

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Convenience method for GET requests."""
        return await self.call(
            operation=f"GET {path}",
            method="GET",
            path=path,
            params=params,
            **kwargs,
        )

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Convenience method for POST requests."""
        return await self.call(
            operation=f"POST {path}",
            method="POST",
            path=path,
            json=json,
            **kwargs,
        )

    async def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Convenience method for PUT requests."""
        return await self.call(
            operation=f"PUT {path}",
            method="PUT",
            path=path,
            json=json,
            **kwargs,
        )

    async def delete(
        self,
        path: str,
        **kwargs,
    ) -> Any:
        """Convenience method for DELETE requests."""
        return await self.call(
            operation=f"DELETE {path}",
            method="DELETE",
            path=path,
            **kwargs,
        )

    def get_status(self) -> Dict[str, Any]:
        """Get client status including circuit breaker state."""
        return {
            "module_name": self.module_name,
            "base_url": self.base_url,
            "is_available": self.is_available,
            "circuit_breaker": self._circuit_breaker.get_status(),
        }
