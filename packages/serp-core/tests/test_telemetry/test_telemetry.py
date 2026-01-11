"""Tests for telemetry module.

These tests verify the telemetry module works correctly both
with and without OpenTelemetry installed.
"""

import pytest

from serp_core.telemetry import (
    ExporterType,
    TelemetryConfig,
    get_meter,
    get_tracer,
    init_telemetry,
    is_telemetry_enabled,
    trace_operation,
)
from serp_core.telemetry.setup import OTEL_AVAILABLE, NoOpMeter, NoOpTracer


class TestTelemetryConfig:
    """Test TelemetryConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TelemetryConfig()

        assert config.service_name == "serp"
        assert config.service_version == "1.0.0"
        assert config.environment == "development"
        assert config.enabled is True
        assert config.trace_exporter == ExporterType.CONSOLE
        assert config.sample_rate == 1.0

    def test_disabled_config(self):
        """Test disabled configuration."""
        config = TelemetryConfig.disabled()

        assert config.enabled is False
        assert config.trace_exporter == ExporterType.NONE

    def test_development_config(self):
        """Test development configuration."""
        config = TelemetryConfig.development("my-service")

        assert config.service_name == "my-service"
        assert config.environment == "development"
        assert config.trace_exporter == ExporterType.CONSOLE
        assert config.console_pretty is True

    def test_production_config(self):
        """Test production configuration."""
        config = TelemetryConfig.production(
            service_name="prod-service",
            otlp_endpoint="http://otel:4317",
            sample_rate=0.1,
        )

        assert config.service_name == "prod-service"
        assert config.environment == "production"
        assert config.trace_exporter == ExporterType.OTLP
        assert config.otlp_endpoint == "http://otel:4317"
        assert config.sample_rate == 0.1

    def test_custom_resource_attributes(self):
        """Test custom resource attributes."""
        config = TelemetryConfig(
            resource_attributes={
                "service.namespace": "erp",
                "deployment.region": "us-east-1",
            }
        )

        assert config.resource_attributes["service.namespace"] == "erp"
        assert config.resource_attributes["deployment.region"] == "us-east-1"


class TestExporterType:
    """Test ExporterType enum."""

    def test_exporter_values(self):
        """Test exporter type values."""
        assert ExporterType.CONSOLE.value == "console"
        assert ExporterType.OTLP.value == "otlp"
        assert ExporterType.JAEGER.value == "jaeger"
        assert ExporterType.ZIPKIN.value == "zipkin"
        assert ExporterType.NONE.value == "none"


class TestNoOpImplementations:
    """Test no-op implementations when telemetry is disabled."""

    def test_noop_tracer(self):
        """Test NoOpTracer doesn't raise errors."""
        tracer = NoOpTracer()

        span = tracer.start_span("test")
        assert span is not None

        # Context manager should work
        with tracer.start_as_current_span("test") as span:
            span.set_attribute("key", "value")
            span.add_event("event")
            span.set_status(None)
            span.record_exception(Exception("test"))
            span.end()

    def test_noop_meter(self):
        """Test NoOpMeter doesn't raise errors."""
        meter = NoOpMeter()

        counter = meter.create_counter("test.counter")
        counter.add(1, {"key": "value"})

        histogram = meter.create_histogram("test.histogram")
        histogram.record(100.5, {"key": "value"})

        gauge = meter.create_gauge("test.gauge")
        gauge.set(42, {"key": "value"})


class TestGetTracerAndMeter:
    """Test get_tracer and get_meter functions."""

    def test_get_tracer_returns_noop_when_disabled(self):
        """Test that get_tracer returns NoOpTracer when telemetry is disabled."""
        # Initialize with disabled config
        init_telemetry(TelemetryConfig.disabled())

        tracer = get_tracer("test-module")

        # Should return NoOpTracer when disabled
        assert isinstance(tracer, NoOpTracer)

    def test_get_meter_returns_noop_when_disabled(self):
        """Test that get_meter returns NoOpMeter when telemetry is disabled."""
        # Initialize with disabled config
        init_telemetry(TelemetryConfig.disabled())

        meter = get_meter("test-module")

        # Should return NoOpMeter when disabled
        assert isinstance(meter, NoOpMeter)


@pytest.mark.asyncio
class TestTraceOperationDecorator:
    """Test trace_operation decorator."""

    async def test_decorator_works_without_otel(self):
        """Test decorator works when OpenTelemetry is not available/disabled."""
        # Ensure telemetry is disabled
        init_telemetry(TelemetryConfig.disabled())

        @trace_operation()
        async def my_operation(value: int) -> int:
            return value * 2

        result = await my_operation(21)
        assert result == 42

    async def test_decorator_with_custom_name(self):
        """Test decorator with custom span name."""
        init_telemetry(TelemetryConfig.disabled())

        @trace_operation("custom_operation_name")
        async def my_operation():
            return "result"

        result = await my_operation()
        assert result == "result"

    async def test_decorator_with_attributes(self):
        """Test decorator with static attributes."""
        init_telemetry(TelemetryConfig.disabled())

        @trace_operation(attributes={"operation.type": "test"})
        async def my_operation():
            return "result"

        result = await my_operation()
        assert result == "result"

    async def test_decorator_handles_exceptions(self):
        """Test decorator properly propagates exceptions."""
        init_telemetry(TelemetryConfig.disabled())

        @trace_operation()
        async def failing_operation():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await failing_operation()

    def test_sync_decorator(self):
        """Test decorator works with sync functions."""
        init_telemetry(TelemetryConfig.disabled())

        @trace_operation()
        def sync_operation(x: int) -> int:
            return x + 1

        result = sync_operation(5)
        assert result == 6


class TestTelemetryWithOTel:
    """Tests that require OpenTelemetry to be installed."""

    @pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
    def test_init_with_console_exporter(self):
        """Test initialization with console exporter."""
        config = TelemetryConfig.development("test-service")
        result = init_telemetry(config)

        # Should return True if OTEL is available
        assert result is True
        assert is_telemetry_enabled()

    @pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
    def test_tracer_creates_spans(self):
        """Test that tracer creates actual spans."""
        init_telemetry(TelemetryConfig.development("test-service"))

        tracer = get_tracer("test-module")

        # Should not be NoOpTracer
        assert not isinstance(tracer, NoOpTracer)

        # Should be able to create spans
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test.key", "test_value")
            # Span should have context
            context = span.get_span_context()
            assert context is not None
            assert context.is_valid


class TestContextPropagation:
    """Test trace context propagation utilities."""

    def test_get_trace_context_empty_when_disabled(self):
        """Test get_trace_context returns empty dict when disabled."""
        from serp_core.telemetry.context import get_trace_context

        init_telemetry(TelemetryConfig.disabled())

        context = get_trace_context()
        assert context == {}

    def test_get_current_trace_id_none_when_disabled(self):
        """Test get_current_trace_id returns None when disabled."""
        from serp_core.telemetry.context import get_current_trace_id

        init_telemetry(TelemetryConfig.disabled())

        trace_id = get_current_trace_id()
        assert trace_id is None

    def test_inject_trace_context_noop_when_disabled(self):
        """Test inject_trace_context is no-op when disabled."""
        from serp_core.telemetry.context import inject_trace_context

        init_telemetry(TelemetryConfig.disabled())

        headers = {"existing": "header"}
        inject_trace_context(headers)

        # Should not have added any trace headers
        assert headers == {"existing": "header"}

    def test_get_trace_info_empty_when_disabled(self):
        """Test get_trace_info returns empty info when disabled."""
        from serp_core.telemetry.context import get_trace_info

        init_telemetry(TelemetryConfig.disabled())

        info = get_trace_info()

        assert info["trace_id"] is None
        assert info["span_id"] is None
        assert info["parent_span_id"] is None
