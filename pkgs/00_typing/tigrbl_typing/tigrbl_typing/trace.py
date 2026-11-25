"""Backend-neutral identity diagnostics shared by the execution and operation layers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import logging
import math
from typing import Any

TraceSink = Callable[[str, str, Mapping[str, Any]], None]

_FIELDS = (
    "connection_id",
    "transport_session_id",
    "session_id",
    "correlation_id",
    "opening_request_id",
    "request_id",
    "http_stream_id",
    "stream_id",
    "stream_correlation_id",
    "datagram_id",
    "subscription_id",
    "attachment_generation",
    "lease_id",
    "invocation_id",
    "attempt_id",
    "rpc_id",
    "rpc_item_index",
    "trace_id",
    "span_id",
    "parent_span_id",
    "engine_session_id",
    "transaction_id",
    "publication_id",
    "delivery_id",
    "attempt_number",
    "callback_event",
    "source_op",
    "duration_ms",
    "failure_class",
    "origin_invocation_id",
    "origin_transaction_id",
    "origin_correlation_id",
    "outcome",
    "status",
    "path",
)
_LOG = logging.getLogger(__name__)


def trace_fields(fields: Mapping[str, Any]) -> dict[str, Any]:
    """Select scalar identity metadata without carrying request or event payloads."""
    values = {}
    for key in _FIELDS:
        value = fields.get(key)
        if (
            isinstance(value, (str, int))
            or isinstance(value, float)
            and math.isfinite(value)
        ):
            values[key] = value
    return values


def emit_trace(
    sink: TraceSink | None, kind: str, transport: str, fields: Mapping[str, Any]
) -> None:
    """Emit a detached record without letting diagnostics interrupt application work."""
    if sink is None:
        return
    try:
        sink(kind, transport, trace_fields(fields))
    except Exception:
        _LOG.warning("Trace sink rejected a diagnostic event")


def transport_name(scope_type: str) -> str:
    return {
        "http": "HTTP",
        "websocket": "WebSocket",
        "webtransport": "WebTransport",
    }.get(scope_type, scope_type)
