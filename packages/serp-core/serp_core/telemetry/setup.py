"""
Telemetry setup and initialization.

Handles OpenTelemetry provider setup, exporter configuration,
and global tracer/meter access.
"""

import logging
from typing import Optional

from .config import ExporterType, TelemetryConfig

logger = logging.getLogger(__name__)

# Global state
_telemetry_config: Optional[TelemetryConfig] = None
_initialized: bool = False

# Try to import OpenTelemetry - it's optional
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.baggage.propagation import W3CBaggagePropagator

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None
    metrics = None


class NoOpTracer:
    """No-op tracer when OpenTelemetry is not available."""

    def start_span(self, name, *args, **kwargs):
        return NoOpSpan()

    def start_as_current_span(self, name, *args, **kwargs):
        return NoOpSpan()


class NoOpSpan:
    """No-op span when OpenTelemetry is not available."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key, value):
        pass

    def set_status(self, status):
        pass

    def record_exception(self, exception):
        pass

    def add_event(self, name, attributes=None):
        pass

    def end(self):
        pass


class NoOpMeter:
    """No-op meter when OpenTelemetry is not available."""

    def create_counter(self, name, *args, **kwargs):
        return NoOpInstrument()

    def create_histogram(self, name, *args, **kwargs):
        return NoOpInstrument()

    def create_up_down_counter(self, name, *args, **kwargs):
        return NoOpInstrument()

    def create_gauge(self, name, *args, **kwargs):
        return NoOpInstrument()


class NoOpInstrument:
    """No-op instrument when OpenTelemetry is not available."""

    def add(self, value, attributes=None):
        pass

    def record(self, value, attributes=None):
        pass

    def set(self, value, attributes=None):
        pass


def init_telemetry(
    config: Optional[TelemetryConfig] = None,
    service_name: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
) -> bool:
    """
    Initialize OpenTelemetry for the application.

    Args:
        config: Full telemetry configuration
        service_name: Service name (shortcut, creates default config)
        otlp_endpoint: OTLP endpoint (shortcut, enables OTLP exporter)

    Returns:
        True if telemetry was initialized, False if disabled or unavailable

    Example:
        # Using config object
        init_telemetry(TelemetryConfig.production("serp-shell", "http://otel:4317"))

        # Using shortcuts
        init_telemetry(service_name="serp-shell", otlp_endpoint="http://otel:4317")

        # Development mode (console output)
        init_telemetry(service_name="serp-shell")
    """
    global _telemetry_config, _initialized

    if _initialized:
        logger.warning("Telemetry already initialized")
        return is_telemetry_enabled()

    # Build config from parameters if not provided
    if config is None:
        if otlp_endpoint:
            config = TelemetryConfig(
                service_name=service_name or "serp",
                trace_exporter=ExporterType.OTLP,
                metrics_exporter=ExporterType.OTLP,
                otlp_endpoint=otlp_endpoint,
            )
        elif service_name:
            config = TelemetryConfig.development(service_name)
        else:
            config = TelemetryConfig.from_env()

    _telemetry_config = config

    if not config.enabled:
        logger.info("Telemetry is disabled")
        _initialized = True
        return False

    if not OTEL_AVAILABLE:
        logger.warning(
            "OpenTelemetry packages not installed. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk"
        )
        _initialized = True
        return False

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: config.service_name,
        SERVICE_VERSION: config.service_version,
        "deployment.environment": config.environment,
        **config.resource_attributes,
    })

    # Setup trace provider
    _setup_trace_provider(config, resource)

    # Setup metrics provider
    _setup_metrics_provider(config, resource)

    # Setup propagators
    _setup_propagators(config)

    _initialized = True
    logger.info(
        f"Telemetry initialized for {config.service_name} "
        f"(exporter: {config.trace_exporter.value})"
    )

    return True


def _setup_trace_provider(config: TelemetryConfig, resource: "Resource") -> None:
    """Setup the trace provider with appropriate exporter."""
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

    # Create sampler
    sampler = TraceIdRatioBased(config.sample_rate)

    # Create provider
    provider = TracerProvider(resource=resource, sampler=sampler)

    # Add exporter
    if config.trace_exporter == ExporterType.CONSOLE:
        exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(exporter))

    elif config.trace_exporter == ExporterType.OTLP:
        if config.otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter,
                )
                exporter = OTLPSpanExporter(
                    endpoint=config.otlp_endpoint,
                    headers=config.otlp_headers or None,
                )
                provider.add_span_processor(BatchSpanProcessor(exporter))
            except ImportError:
                logger.warning(
                    "OTLP exporter not available. "
                    "Install with: pip install opentelemetry-exporter-otlp"
                )
                # Fall back to console
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    elif config.trace_exporter == ExporterType.JAEGER:
        if config.jaeger_endpoint:
            try:
                from opentelemetry.exporter.jaeger.thrift import JaegerExporter
                exporter = JaegerExporter(
                    collector_endpoint=config.jaeger_endpoint,
                )
                provider.add_span_processor(BatchSpanProcessor(exporter))
            except ImportError:
                logger.warning(
                    "Jaeger exporter not available. "
                    "Install with: pip install opentelemetry-exporter-jaeger"
                )

    # Set as global provider
    trace.set_tracer_provider(provider)


def _setup_metrics_provider(config: TelemetryConfig, resource: "Resource") -> None:
    """Setup the metrics provider with appropriate exporter."""
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import (
        ConsoleMetricExporter,
        PeriodicExportingMetricReader,
    )

    readers = []

    if config.metrics_exporter == ExporterType.CONSOLE:
        reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60000,  # Export every 60 seconds
        )
        readers.append(reader)

    elif config.metrics_exporter == ExporterType.OTLP:
        if config.otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                    OTLPMetricExporter,
                )
                reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(
                        endpoint=config.otlp_endpoint,
                        headers=config.otlp_headers or None,
                    ),
                )
                readers.append(reader)
            except ImportError:
                logger.warning("OTLP metrics exporter not available")

    # Create provider
    provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(provider)


def _setup_propagators(config: TelemetryConfig) -> None:
    """Setup context propagators."""
    propagators = []

    if "tracecontext" in config.propagators:
        propagators.append(TraceContextTextMapPropagator())

    if "baggage" in config.propagators:
        propagators.append(W3CBaggagePropagator())

    if propagators:
        set_global_textmap(CompositePropagator(propagators))


def shutdown_telemetry() -> None:
    """Shutdown telemetry providers gracefully."""
    global _initialized

    if not _initialized or not OTEL_AVAILABLE:
        return

    # Flush and shutdown trace provider
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()

    # Flush and shutdown metrics provider
    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, "shutdown"):
        meter_provider.shutdown()

    _initialized = False
    logger.info("Telemetry shutdown complete")


def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled and initialized."""
    return (
        _initialized
        and _telemetry_config is not None
        and _telemetry_config.enabled
        and OTEL_AVAILABLE
    )


def get_tracer(name: str, version: str = "1.0.0") -> "trace.Tracer":
    """
    Get a tracer for the specified module/component.

    Args:
        name: Module or component name (e.g., "serp-crm", "partner-service")
        version: Version of the module

    Returns:
        Tracer instance (or NoOpTracer if telemetry is disabled)

    Example:
        tracer = get_tracer("serp-crm")
        with tracer.start_as_current_span("create_partner") as span:
            span.set_attribute("partner.name", name)
            # ... operation
    """
    if not is_telemetry_enabled():
        return NoOpTracer()

    return trace.get_tracer(name, version)


def get_meter(name: str, version: str = "1.0.0") -> "metrics.Meter":
    """
    Get a meter for the specified module/component.

    Args:
        name: Module or component name
        version: Version of the module

    Returns:
        Meter instance (or NoOpMeter if telemetry is disabled)

    Example:
        meter = get_meter("serp-crm")
        request_counter = meter.create_counter(
            "crm.requests",
            description="Number of CRM requests"
        )
        request_counter.add(1, {"method": "POST", "endpoint": "/partners"})
    """
    if not is_telemetry_enabled():
        return NoOpMeter()

    return metrics.get_meter(name, version)


def get_config() -> Optional[TelemetryConfig]:
    """Get the current telemetry configuration."""
    return _telemetry_config
