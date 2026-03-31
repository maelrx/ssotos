"""OpenTelemetry light integration — per D-58.

Provides:
- Trace context propagation across async boundaries
- HTTP request tracing
- Job processing spans
- Export to console/OTLP endpoint
"""
import os
from contextlib import contextmanager
from typing import Any, Generator
from uuid import uuid4
import structlog

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

logger = structlog.get_logger(__name__)

# Global tracer instance
_tracer: trace.Tracer | None = None
_propagator = TraceContextTextMapPropagator()


class NoOpSpan:
    """No-op span for when OTel is disabled."""
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def set_attribute(self, key: str, value: Any): pass
    def set_status(self, status: Any): pass
    def record_exception(self, exc: Exception): pass
    def add_event(self, name: str, attributes: dict | None = None): pass


def configure_otel(service_name: str = "knowledge-os") -> None:
    """Configure OpenTelemetry with console exporter.

    For production, replace ConsoleSpanExporter with OTLP exporter.
    """
    global _tracer

    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.1.0",
    })

    provider = TracerProvider(resource=resource)

    # Console exporter for development
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Can add OTLP exporter here for production:
    # from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    # otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    # provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)

    logger.info("opentelemetry_configured", service_name=service_name)


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance."""
    global _tracer
    if _tracer is None:
        # Lazy initialization with default service name
        configure_otel()
    return _tracer


def get_current_trace_id() -> str | None:
    """Get the current trace ID from the active span."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


@contextmanager
def create_span(
    name: str,
    attributes: dict | None = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL
) -> Generator[Span, None, None]:
    """Create a traced span with the global tracer.

    Usage:
        with create_span("process_job", {"job_id": "123"}) as span:
            # do work
            span.set_attribute("result", "success")

    If OTel is not configured, returns a no-op context.
    """
    tracer = get_tracer()
    if tracer is None:
        yield NoOpSpan()
        return

    with tracer.start_as_current_span(name, kind=kind) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def extract_trace_context(carrier: dict) -> dict:
    """Extract trace context from a carrier dict (e.g., headers).

    Returns a new carrier dict with trace context injected.
    """
    return _propagator.extract(carrier)


def inject_trace_context(carrier: dict) -> dict:
    """Inject trace context into a carrier dict (e.g., for outgoing requests)."""
    _propagator.inject(carrier)
    return carrier
