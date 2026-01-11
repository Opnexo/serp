"""
Timeout utilities for async operations.

Provides configurable timeouts for external calls.

Example:
    # Using decorator
    @with_timeout(5.0)
    async def call_external_api():
        return await http.get("/api/data")

    # Using context manager
    async with timeout_context(5.0):
        result = await slow_operation()

    # Using function wrapper
    result = await with_timeout(5.0, slow_operation)
"""

import asyncio
from functools import wraps
from typing import Callable, Optional, TypeVar, Union

T = TypeVar("T")


class TimeoutError(Exception):
    """Raised when an operation times out."""

    def __init__(
        self,
        timeout: float,
        operation: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self.timeout = timeout
        self.operation = operation
        super().__init__(
            message or f"Operation '{operation or 'unknown'}' timed out after {timeout}s"
        )


def with_timeout(
    timeout: float,
    func: Optional[Callable[..., T]] = None,
    operation_name: Optional[str] = None,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """
    Add timeout to an async function.

    Can be used as:
    1. Decorator: @with_timeout(5.0)
    2. Function wrapper: await with_timeout(5.0, slow_func, arg1, arg2)

    Args:
        timeout: Timeout in seconds
        func: Optional function to wrap (for function wrapper usage)
        operation_name: Name for error messages

    Example as decorator:
        @with_timeout(5.0)
        async def fetch_data():
            return await http.get("/api/data")

    Example as wrapper:
        result = await with_timeout(5.0, fetch_data)
    """
    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        name = operation_name or f.__name__

        @wraps(f)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    f(*args, **kwargs),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                raise TimeoutError(timeout=timeout, operation=name)

        return wrapper

    if func is not None:
        # Used as function wrapper
        return decorator(func)

    # Used as decorator
    return decorator


class timeout_context:
    """
    Async context manager for timeout.

    Example:
        async with timeout_context(5.0, "database_query"):
            result = await db.query("SELECT * FROM users")
    """

    def __init__(
        self,
        timeout: float,
        operation_name: Optional[str] = None,
    ):
        self.timeout = timeout
        self.operation_name = operation_name
        self._task: Optional[asyncio.Task] = None

    async def __aenter__(self) -> "timeout_context":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is asyncio.TimeoutError:
            raise TimeoutError(
                timeout=self.timeout,
                operation=self.operation_name,
            )
        return False
