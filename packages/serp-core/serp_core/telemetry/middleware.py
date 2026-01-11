"""
FastAPI middleware for OpenTelemetry integration.

Provides automatic request tracing for FastAPI applications.
"""

import time
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .context import extract_trace_context, get_current_trace_id
from .setup import get_meter, get_tracer, is_telemetry_enabled, OTEL_AVAILABLE

if OTEL_AVAILABLE:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode, SpanKind


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic request tracing.

    Features:
    - Creates spans for each HTTP request
    - Extracts incoming trace context from headers
    - Adds trace ID to response headers
    - Records request/response attributes
    - Tracks request metrics (count, latency)

    Example:
        from fastapi import FastAPI
        from serp_core.telemetry.middleware import TelemetryMiddleware

        app = FastAPI()
        app.add_middleware(TelemetryMiddleware, service_name="serp-shell")
    """

    def __init__(
        self,
        app,
        service_name: str = "serp",
        excluded_paths: Optional[list] = None,
        record_request_body: bool = False,
        add_trace_id_header: bool = True,
        trace_id_header_name: str = "X-Trace-ID",
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            service_name: Name of this service for tracing
            excluded_paths: Paths to exclude from tracing (e.g., ["/health"])
            record_request_body: Whether to record request body (careful with PII)
            add_trace_id_header: Add trace ID to response headers
            trace_id_header_name: Header name for trace ID
        """
        super().__init__(app)
        self.service_name = service_name
        self.excluded_paths = excluded_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        self.record_request_body = record_request_body
        self.add_trace_id_header = add_trace_id_header
        self.trace_id_header_name = trace_id_header_name

        # Get tracer and meter
        self._tracer = get_tracer(service_name)
        self._meter = get_meter(service_name)

        # Create metrics
        if is_telemetry_enabled():
            self._request_counter = self._meter.create_counter(
                "http.server.request.count",
                description="Number of HTTP requests",
                unit="1",
            )
            self._request_duration = self._meter.create_histogram(
                "http.server.request.duration",
                description="HTTP request duration",
                unit="ms",
            )
        else:
            self._request_counter = None
            self._request_duration = None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with tracing."""
        # Skip excluded paths
        if self._should_skip(request.url.path):
            return await call_next(request)

        # If telemetry is disabled, just pass through
        if not is_telemetry_enabled():
            return await call_next(request)

        # Extract trace context from incoming headers
        carrier = dict(request.headers)
        ctx = extract_trace_context(carrier)

        # Create span name
        span_name = f"{request.method} {request.url.path}"

        # Start timing
        start_time = time.perf_counter()

        # Create span
        with self._tracer.start_as_current_span(
            span_name,
            context=ctx,
            kind=SpanKind.SERVER,
        ) as span:
            # Add request attributes
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.target", request.url.path)
            span.set_attribute("http.host", request.url.hostname or "")
            span.set_attribute("http.scheme", request.url.scheme)
            span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))

            # Add client info
            if request.client:
                span.set_attribute("http.client_ip", request.client.host)

            # Add query parameters (sanitized)
            if request.query_params:
                span.set_attribute("http.query_string", str(request.query_params))

            try:
                # Process request
                response = await call_next(request)

                # Calculate duration
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Add response attributes
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.response.duration_ms", duration_ms)

                # Set span status based on HTTP status
                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                elif response.status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Record metrics
                self._record_metrics(request, response, duration_ms)

                # Add trace ID to response headers
                if self.add_trace_id_header:
                    trace_id = get_current_trace_id()
                    if trace_id:
                        response.headers[self.trace_id_header_name] = trace_id

                return response

            except Exception as e:
                # Calculate duration
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Record exception
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("http.status_code", 500)

                # Record metrics for error
                self._record_metrics(request, None, duration_ms, error=True)

                raise

    def _should_skip(self, path: str) -> bool:
        """Check if path should be skipped from tracing."""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False

    def _record_metrics(
        self,
        request: Request,
        response: Optional[Response],
        duration_ms: float,
        error: bool = False,
    ) -> None:
        """Record request metrics."""
        if self._request_counter is None:
            return

        attributes = {
            "http.method": request.method,
            "http.route": request.url.path,
            "http.status_code": response.status_code if response else 500,
            "error": error,
        }

        self._request_counter.add(1, attributes)

        if self._request_duration:
            self._request_duration.record(duration_ms, attributes)


def add_telemetry_middleware(
    app,
    service_name: str = "serp",
    excluded_paths: Optional[list] = None,
) -> None:
    """
    Convenience function to add telemetry middleware to a FastAPI app.

    Args:
        app: FastAPI application
        service_name: Name of this service
        excluded_paths: Paths to exclude from tracing
    """
    app.add_middleware(
        TelemetryMiddleware,
        service_name=service_name,
        excluded_paths=excluded_paths,
    )
