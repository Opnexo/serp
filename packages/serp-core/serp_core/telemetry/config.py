"""
Telemetry configuration.

Defines configuration options for OpenTelemetry setup.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ExporterType(str, Enum):
    """Supported telemetry exporters."""
    CONSOLE = "console"
    OTLP = "otlp"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    NONE = "none"


@dataclass
class TelemetryConfig:
    """
    Configuration for SERP telemetry.

    Attributes:
        service_name: Name of this service (e.g., "serp-shell", "serp-crm")
        service_version: Version of this service
        environment: Deployment environment (dev, staging, prod)
        enabled: Whether telemetry is enabled
        trace_exporter: Exporter for traces
        metrics_exporter: Exporter for metrics
        otlp_endpoint: OTLP collector endpoint (for OTLP exporter)
        otlp_headers: Headers for OTLP requests (e.g., auth tokens)
        jaeger_endpoint: Jaeger collector endpoint
        zipkin_endpoint: Zipkin collector endpoint
        sample_rate: Trace sampling rate (0.0 to 1.0)
        resource_attributes: Additional resource attributes
        propagators: Context propagators to use
        console_pretty: Pretty print console output
    """
    service_name: str = "serp"
    service_version: str = "1.0.0"
    environment: str = "development"
    enabled: bool = True

    # Exporters
    trace_exporter: ExporterType = ExporterType.CONSOLE
    metrics_exporter: ExporterType = ExporterType.CONSOLE

    # OTLP configuration
    otlp_endpoint: Optional[str] = None
    otlp_headers: Dict[str, str] = field(default_factory=dict)

    # Alternative exporters
    jaeger_endpoint: Optional[str] = None
    zipkin_endpoint: Optional[str] = None

    # Sampling
    sample_rate: float = 1.0  # 100% sampling by default

    # Resource attributes
    resource_attributes: Dict[str, str] = field(default_factory=dict)

    # Propagators (W3C TraceContext, B3, etc.)
    propagators: List[str] = field(
        default_factory=lambda: ["tracecontext", "baggage"]
    )

    # Console exporter options
    console_pretty: bool = True

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        """
        Create configuration from environment variables.

        Environment variables:
            OTEL_SERVICE_NAME: Service name
            OTEL_SERVICE_VERSION: Service version
            SERP_ENVIRONMENT: Environment name
            OTEL_ENABLED: Enable/disable telemetry (true/false)
            OTEL_EXPORTER_TYPE: Exporter type (console, otlp, jaeger, zipkin)
            OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint
            OTEL_TRACES_SAMPLER_ARG: Sample rate
        """
        import os

        enabled_str = os.getenv("OTEL_ENABLED", "true").lower()
        enabled = enabled_str in ("true", "1", "yes")

        exporter_str = os.getenv("OTEL_EXPORTER_TYPE", "console").lower()
        try:
            trace_exporter = ExporterType(exporter_str)
        except ValueError:
            trace_exporter = ExporterType.CONSOLE

        sample_rate_str = os.getenv("OTEL_TRACES_SAMPLER_ARG", "1.0")
        try:
            sample_rate = float(sample_rate_str)
        except ValueError:
            sample_rate = 1.0

        return cls(
            service_name=os.getenv("OTEL_SERVICE_NAME", "serp"),
            service_version=os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
            environment=os.getenv("SERP_ENVIRONMENT", "development"),
            enabled=enabled,
            trace_exporter=trace_exporter,
            metrics_exporter=trace_exporter,  # Use same exporter for metrics
            otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            jaeger_endpoint=os.getenv("OTEL_EXPORTER_JAEGER_ENDPOINT"),
            zipkin_endpoint=os.getenv("OTEL_EXPORTER_ZIPKIN_ENDPOINT"),
            sample_rate=sample_rate,
        )

    @classmethod
    def disabled(cls) -> "TelemetryConfig":
        """Create a disabled telemetry configuration."""
        return cls(enabled=False, trace_exporter=ExporterType.NONE)

    @classmethod
    def development(cls, service_name: str = "serp") -> "TelemetryConfig":
        """Create a development configuration with console output."""
        return cls(
            service_name=service_name,
            environment="development",
            trace_exporter=ExporterType.CONSOLE,
            metrics_exporter=ExporterType.CONSOLE,
            console_pretty=True,
        )

    @classmethod
    def production(
        cls,
        service_name: str,
        otlp_endpoint: str,
        sample_rate: float = 0.1,
    ) -> "TelemetryConfig":
        """Create a production configuration with OTLP exporter."""
        return cls(
            service_name=service_name,
            environment="production",
            trace_exporter=ExporterType.OTLP,
            metrics_exporter=ExporterType.OTLP,
            otlp_endpoint=otlp_endpoint,
            sample_rate=sample_rate,
        )
