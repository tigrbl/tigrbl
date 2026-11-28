"""Backend-neutral identity diagnostics shared by the execution and operation layers."""

from __future__ import annotations

import logging
import math
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from typing import Any

TraceSink = Callable[[str, str, Mapping[str, Any]], None]
AtomTiming = tuple[str, str, int, int, str, str | None, str | None]

TRACE_ID_FIELDS = (
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
    "lease_id",
    "invocation_id",
    "attempt_id",
    "rpc_id",
    "engine_session_id",
    "transaction_id",
    "flush_id",
    "publication_id",
    "delivery_id",
    "origin_invocation_id",
    "origin_correlation_id",
    "attachment_generation",
)

TRACE_EXECUTION_FIELDS = (
    "op_model",
    "op_alias",
    "hook_name",
    "hook_phase",
    "atom_label",
    "atom_phase",
    "source_started_at",
    "source_ended_at",
    "timing_boundary",
    "clock_domain",
)

_FIELDS = (
    *TRACE_ID_FIELDS,
    *TRACE_EXECUTION_FIELDS,
    "rpc_item_index",
    "trace_id",
    "span_id",
    "parent_span_id",
    "attempt_number",
    "callback_event",
    "source_op",
    "duration_ms",
    "failure_class",
    "origin_transaction_id",
    "outcome",
    "status",
    "path",
    "atom_ordinal",
    "atom_trace_dropped",
    "measured_duration_ms",
)
_LOG = logging.getLogger(__name__)


def atom_timing_fields(
    anchor: datetime, ordinal: int, sample: AtomTiming
) -> dict[str, Any]:
    label, phase, offset_ns, duration_ns, outcome, engine_session_id, transaction_id = (
        sample
    )
    start = anchor + timedelta(microseconds=offset_ns / 1000)
    end = anchor + timedelta(microseconds=(offset_ns + duration_ns) / 1000)
    return {
        "atom_label": label,
        "atom_phase": phase,
        "atom_ordinal": ordinal,
        "source_started_at": start.isoformat(),
        "source_ended_at": end.isoformat(),
        "measured_duration_ms": duration_ns / 1_000_000,
        "timing_boundary": "atom_monotonic",
        "clock_domain": "server_monotonic",
        "outcome": outcome,
        "engine_session_id": engine_session_id,
        "transaction_id": transaction_id,
    }


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
