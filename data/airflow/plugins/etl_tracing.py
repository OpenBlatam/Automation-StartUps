from __future__ import annotations

import logging
from typing import Dict, Any, Optional, ContextManager
from contextlib import nullcontext

_logger = logging.getLogger(__name__)

# Try to import OpenTelemetry if available
_tracing_available = False
try:
	from opentelemetry import trace
	from opentelemetry.trace import Tracer, Status, StatusCode
	_tracing_available = True
except Exception:
	_logger.debug("OpenTelemetry not available, tracing disabled")


def start_span(
	name: str,
	attributes: Optional[Dict[str, Any]] = None,
	tracer: Optional[Tracer] = None,
) -> ContextManager:
	"""
	Start a distributed tracing span with optional attributes.
	
	If OpenTelemetry is available, creates a real span. Otherwise, returns a no-op context.
	
	Args:
		name: Span name (e.g., "etl_example.extract")
		attributes: Optional dictionary of span attributes
		tracer: Optional OpenTelemetry tracer (uses global if not provided)
		
	Returns:
		Context manager that handles span lifecycle
		
	Example:
		with start_span("etl_example.transform", attributes={"rows": 1000}):
			# do work
	"""
	if not _tracing_available:
		# No-op context if tracing not available
		return nullcontext()
	
	try:
		if tracer is None:
			tracer = trace.get_tracer(__name__)
		
		span = tracer.start_as_current_span(name)
		
		# Add attributes if provided
		if attributes:
			for key, value in attributes.items():
				try:
					# Convert value to string for attributes
					if isinstance(value, (str, int, float, bool)):
						span.set_attribute(key, value)
					else:
						span.set_attribute(key, str(value))
				except Exception:
					pass
		
		return span
	except Exception as e:
		_logger.debug("Failed to start span, using no-op: %s", e)
		return nullcontext()


def set_span_attribute(key: str, value: Any) -> None:
	"""
	Set an attribute on the current span if available.
	
	Args:
		key: Attribute key
		value: Attribute value (will be converted to string if needed)
	"""
	if not _tracing_available:
		return
	
	try:
		span = trace.get_current_span()
		if span and span.is_recording():
			if isinstance(value, (str, int, float, bool)):
				span.set_attribute(key, value)
			else:
				span.set_attribute(key, str(value))
	except Exception:
		pass


def record_span_error(error: Exception, status_description: Optional[str] = None) -> None:
	"""
	Record an error on the current span if available.
	
	Args:
		error: Exception that occurred
		status_description: Optional description of the error
	"""
	if not _tracing_available:
		return
	
	try:
		span = trace.get_current_span()
		if span and span.is_recording():
			span.set_status(Status(StatusCode.ERROR, status_description or str(error)))
			span.record_exception(error)
	except Exception:
		pass
