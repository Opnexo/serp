"""
Retry utilities with exponential backoff.

Provides configurable retry logic for transient failures.

Example:
    # Using decorator
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def call_external_api():
        return await http.get("/api/data")

    # Using RetryPolicy
    policy = RetryPolicy(max_retries=5, base_delay=0.5)
    result = await policy.execute(risky_operation)
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Optional, Set, Type, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (0 = no retries)
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Add random jitter to delays (0.0-1.0)
        retryable_exceptions: Exception types that should trigger retry
        non_retryable_exceptions: Exception types that should NOT be retried

    Example:
        policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            exponential_base=2.0,
            jitter=0.1,
        )

        async def call_api():
            return await http.get("/api")

        result = await policy.execute(call_api)
    """
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: float = 0.1
    retryable_exceptions: tuple = field(
        default_factory=lambda: (Exception,)
    )
    non_retryable_exceptions: tuple = field(default_factory=tuple)

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given retry attempt.

        Args:
            attempt: The retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.base_delay * (self.exponential_base ** attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter
        if self.jitter > 0:
            jitter_range = delay * self.jitter
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if an exception should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        # Check non-retryable exceptions first
        if self.non_retryable_exceptions:
            if isinstance(exception, self.non_retryable_exceptions):
                return False

        # Check retryable exceptions
        return isinstance(exception, self.retryable_exceptions)

    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: The function to execute (sync or async)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The function result

        Raises:
            The last exception if all retries fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if not self.should_retry(e, attempt):
                    logger.warning(
                        f"Non-retryable exception on attempt {attempt + 1}: {e}"
                    )
                    raise

                delay = self.calculate_delay(attempt)
                logger.info(
                    f"Retry attempt {attempt + 1}/{self.max_retries} "
                    f"after {delay:.2f}s due to: {e}"
                )
                await asyncio.sleep(delay)

        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry state")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: float = 0.1,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for adding retry logic to functions.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Random jitter factor (0.0-1.0)
        retryable_exceptions: Exceptions that trigger retry
        non_retryable_exceptions: Exceptions that don't trigger retry

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        async def fetch_data():
            return await http_client.get("/api/data")

        @retry_with_backoff(
            max_retries=5,
            retryable_exceptions=(ConnectionError, TimeoutError),
        )
        async def connect_to_service():
            return await service.connect()
    """
    policy = RetryPolicy(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        non_retryable_exceptions=non_retryable_exceptions,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                return await policy.execute(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                # For sync functions, we need to run in event loop
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(
                    policy.execute(func, *args, **kwargs)
                )
            return sync_wrapper

    return decorator
