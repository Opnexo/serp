"""
Telemetry decorators.

Provides convenient decorators for tracing operations.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from .setup import get_tracer, is_telemetry_enabled, OTEL_AVAILABLE

if OTEL_AVAILABLE:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def trace_operation(
    name: Optional[str] = None,
    module: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
    set_status_on_exception: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to trace a function or method.

    Creates a span for the decorated function, automatically recording
    execution time, exceptions, and custom attributes.

    Args:
        name: Span name (defaults to function name)
        module: Module name for the tracer (defaults to function's module)
        attributes: Static attributes to add to the span
        record_exception: Whether to record exceptions in the span
        set_status_on_exception: Whether to set ERROR status on exception

    Example:
        @trace_operation()
        async def create_partner(data: PartnerCreate) -> Partner:
            return await repo.save(Partner(**data))

        @trace_operation("process_payment", module="payments")
        async def process(payment_id: str):
            # ...

        @trace_operation(attributes={"operation.type": "write"})
        async def save_document(doc):
            # ...
    """
    def decorator(func: F) -> F:
        # Determine span name
        span_name = name or func.__name__

        # Determine module name
        tracer_name = module or func.__module__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_telemetry_enabled():
                return await func(*args, **kwargs)

            tracer = get_tracer(tracer_name)

            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function arguments as attributes (sanitized)
                _add_argument_attributes(span, func, args, kwargs)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                    if set_status_on_exception:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_telemetry_enabled():
                return func(*args, **kwargs)

            tracer = get_tracer(tracer_name)

            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function arguments as attributes
                _add_argument_attributes(span, func, args, kwargs)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                    if set_status_on_exception:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _add_argument_attributes(span: Any, func: Callable, args: tuple, kwargs: dict) -> None:
    """
    Add function arguments as span attributes.

    Only adds simple types (str, int, float, bool) to avoid
    serialization issues and sensitive data exposure.
    """
    import inspect

    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # Add positional args
        for i, (param_name, value) in enumerate(zip(params, args)):
            if param_name == "self":
                continue
            _safe_set_attribute(span, f"arg.{param_name}", value)

        # Add keyword args
        for key, value in kwargs.items():
            _safe_set_attribute(span, f"arg.{key}", value)

    except Exception:
        # Don't fail if we can't inspect arguments
        pass


def _safe_set_attribute(span: Any, key: str, value: Any) -> None:
    """
    Safely set a span attribute, converting to safe types.

    Only sets attributes for simple, serializable types.
    """
    # Skip None values
    if value is None:
        return

    # Only set simple types
    if isinstance(value, (str, int, float, bool)):
        # Truncate long strings
        if isinstance(value, str) and len(value) > 256:
            value = value[:256] + "..."
        span.set_attribute(key, value)

    elif isinstance(value, (list, tuple)) and len(value) <= 10:
        # Convert simple sequences
        if all(isinstance(v, (str, int, float, bool)) for v in value):
            span.set_attribute(key, list(value))


class SpanContext:
    """
    Context manager for creating spans with additional features.

    Provides a more fluent API for span creation with automatic
    timing and status handling.

    Example:
        async with SpanContext("process_order", module="orders") as span:
            span.set_attribute("order.id", order_id)
            span.add_event("validation_started")
            await validate(order)
            span.add_event("validation_complete")
            await process(order)
    """

    def __init__(
        self,
        name: str,
        module: str = "serp",
        attributes: Optional[Dict[str, Any]] = None,
        parent_context: Any = None,
    ):
        self.name = name
        self.module = module
        self.attributes = attributes or {}
        self.parent_context = parent_context
        self._span = None

    def __enter__(self):
        if not is_telemetry_enabled():
            return NoOpSpanWrapper()

        tracer = get_tracer(self.module)
        self._span = tracer.start_span(
            self.name,
            context=self.parent_context,
        )

        for key, value in self.attributes.items():
            self._span.set_attribute(key, value)

        return SpanWrapper(self._span)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span is None:
            return False

        if exc_type is not None:
            self._span.record_exception(exc_val)
            self._span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self._span.set_status(Status(StatusCode.OK))

        self._span.end()
        return False

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)


class SpanWrapper:
    """Wrapper around span with convenience methods."""

    def __init__(self, span: Any):
        self._span = span

    def set_attribute(self, key: str, value: Any) -> "SpanWrapper":
        """Set an attribute on the span."""
        _safe_set_attribute(self._span, key, value)
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "SpanWrapper":
        """Add an event to the span."""
        self._span.add_event(name, attributes=attributes)
        return self

    def set_ok(self) -> "SpanWrapper":
        """Set the span status to OK."""
        self._span.set_status(Status(StatusCode.OK))
        return self

    def set_error(self, message: str) -> "SpanWrapper":
        """Set the span status to ERROR."""
        self._span.set_status(Status(StatusCode.ERROR, message))
        return self


class NoOpSpanWrapper:
    """No-op span wrapper when telemetry is disabled."""

    def set_attribute(self, key: str, value: Any) -> "NoOpSpanWrapper":
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "NoOpSpanWrapper":
        return self

    def set_ok(self) -> "NoOpSpanWrapper":
        return self

    def set_error(self, message: str) -> "NoOpSpanWrapper":
        return self
