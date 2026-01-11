"""
SERP Telemetry - OpenTelemetry Integration

Provides distributed tracing, metrics, and logging correlation
across SERP modules.

Features:
- Automatic trace context propagation between modules
- Span creation for service operations
- Metrics collection (requests, latency, errors)
- Log correlation with trace IDs
- Configurable exporters (OTLP, Jaeger, Zipkin, Console)
- FastAPI middleware for automatic request tracing

Usage:
    from serp_core.telemetry import (
        init_telemetry,
        get_tracer,
        get_meter,
        trace_operation,
        TelemetryMiddleware,
    )

    # Initialize telemetry (typically in app startup)
    init_telemetry(
        service_name="serp-shell",
        otlp_endpoint="http://localhost:4317",
    )

    # Add middleware to FastAPI app
    app.add_middleware(TelemetryMiddleware, service_name="serp-shell")

    # Get a tracer for your module
    tracer = get_tracer("serp-crm")

    # Trace an operation
    @trace_operation("create_partner")
    async def create_partner(data):
        return await repo.save(partner)

    # Manual span creation
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        result = await process(order)
"""

from .config import ExporterType, TelemetryConfig
from .context import (
    extract_trace_context,
    get_current_span,
    get_current_span_id,
    get_current_trace_id,
    get_trace_context,
    get_trace_info,
    inject_trace_context,
)
from .decorators import SpanContext, trace_operation
from .middleware import TelemetryMiddleware, add_telemetry_middleware
from .setup import (
    get_meter,
    get_tracer,
    init_telemetry,
    is_telemetry_enabled,
    shutdown_telemetry,
)

__all__ = [
    # Setup
    "init_telemetry",
    "shutdown_telemetry",
    "is_telemetry_enabled",
    "get_tracer",
    "get_meter",
    # Config
    "TelemetryConfig",
    "ExporterType",
    # Context
    "get_current_span",
    "get_current_span_id",
    "get_current_trace_id",
    "get_trace_context",
    "get_trace_info",
    "inject_trace_context",
    "extract_trace_context",
    # Decorators
    "trace_operation",
    "SpanContext",
    # Middleware
    "TelemetryMiddleware",
    "add_telemetry_middleware",
]
