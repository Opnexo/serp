"""
Trace context utilities.

Provides functions for accessing and propagating trace context
across service boundaries.
"""

from typing import Any, Dict, Optional

from .setup import OTEL_AVAILABLE, is_telemetry_enabled

if OTEL_AVAILABLE:
    from opentelemetry import trace
    from opentelemetry.propagate import extract, inject
    from opentelemetry.trace import SpanContext, format_trace_id, format_span_id


def get_current_span() -> Any:
    """
    Get the current active span.

    Returns:
        Current span or None if no span is active
    """
    if not is_telemetry_enabled():
        return None

    return trace.get_current_span()


def get_current_trace_id() -> Optional[str]:
    """
    Get the current trace ID as a hex string.

    Useful for logging correlation and debugging.

    Returns:
        Trace ID as hex string, or None if no trace is active

    Example:
        trace_id = get_current_trace_id()
        logger.info(f"Processing request", extra={"trace_id": trace_id})
    """
    if not is_telemetry_enabled():
        return None

    span = trace.get_current_span()
    if span is None:
        return None

    context = span.get_span_context()
    if context is None or not context.is_valid:
        return None

    return format_trace_id(context.trace_id)


def get_current_span_id() -> Optional[str]:
    """
    Get the current span ID as a hex string.

    Returns:
        Span ID as hex string, or None if no span is active
    """
    if not is_telemetry_enabled():
        return None

    span = trace.get_current_span()
    if span is None:
        return None

    context = span.get_span_context()
    if context is None or not context.is_valid:
        return None

    return format_span_id(context.span_id)


def get_trace_context() -> Dict[str, str]:
    """
    Get trace context headers for propagation.

    Use this when making HTTP calls to other services to propagate
    the trace context.

    Returns:
        Dictionary of headers to include in outgoing requests

    Example:
        headers = get_trace_context()
        response = await http_client.get(url, headers=headers)
    """
    headers: Dict[str, str] = {}

    if not is_telemetry_enabled():
        return headers

    inject(headers)
    return headers


def inject_trace_context(carrier: Dict[str, str]) -> None:
    """
    Inject trace context into a carrier (headers dict).

    Modifies the carrier in place to add trace context headers.

    Args:
        carrier: Dictionary to inject headers into

    Example:
        headers = {"Authorization": "Bearer token"}
        inject_trace_context(headers)
        # headers now contains traceparent, tracestate, etc.
    """
    if not is_telemetry_enabled():
        return

    inject(carrier)


def extract_trace_context(carrier: Dict[str, str]) -> Any:
    """
    Extract trace context from incoming request headers.

    Use this when receiving requests to continue an existing trace.

    Args:
        carrier: Dictionary containing incoming headers

    Returns:
        Context object to use with trace.set_span_in_context()

    Example:
        # In FastAPI middleware
        ctx = extract_trace_context(dict(request.headers))
        with tracer.start_as_current_span("handle_request", context=ctx):
            # ... handle request
    """
    if not is_telemetry_enabled():
        return None

    return extract(carrier)


def get_trace_info() -> Dict[str, Optional[str]]:
    """
    Get current trace information as a dictionary.

    Useful for logging and debugging.

    Returns:
        Dictionary with trace_id, span_id, and parent_span_id
    """
    if not is_telemetry_enabled():
        return {
            "trace_id": None,
            "span_id": None,
            "parent_span_id": None,
        }

    span = trace.get_current_span()
    if span is None:
        return {
            "trace_id": None,
            "span_id": None,
            "parent_span_id": None,
        }

    context = span.get_span_context()
    if context is None or not context.is_valid:
        return {
            "trace_id": None,
            "span_id": None,
            "parent_span_id": None,
        }

    # Get parent span ID if available
    parent_span_id = None
    parent = getattr(span, "parent", None)
    if parent is not None and hasattr(parent, "span_id"):
        parent_span_id = format_span_id(parent.span_id)

    return {
        "trace_id": format_trace_id(context.trace_id),
        "span_id": format_span_id(context.span_id),
        "parent_span_id": parent_span_id,
    }
