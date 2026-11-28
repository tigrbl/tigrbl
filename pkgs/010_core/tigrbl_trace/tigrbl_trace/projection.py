"""Canonical timeline projection for native Tigrbl trace records."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, TypedDict

from tigrbl_typing.trace import TRACE_EXECUTION_FIELDS, TRACE_ID_FIELDS

PROTOCOLS = ("rest", "http_jsonrpc", "websocket", "webtransport")
CARRIERS = {
    "REST": "rest",
    "JSON-RPC": "http_jsonrpc",
    "WebSocket": "websocket",
    "WebTransport": "webtransport",
}
KINDS = {
    "Invocation": ("invocation.completed", "runtime"),
    "Hook": ("hook.completed", "runtime"),
    "Atom": ("atom.completed", "runtime"),
    "Transaction participant": ("db.tx.participant", "database"),
    "Subscription opened": ("broker.subscription.acknowledged", "broker"),
    "Subscription resumed": ("broker.subscription.reattached", "broker"),
    "Attachment detached": ("broker.subscription.detached", "broker"),
    "Publication": ("broker.publication.created", "broker"),
    "Delivery": ("broker.delivery.dispatched", "broker"),
    "webtransport.stream.receive": ("wt.stream.received", "runtime"),
    "webtransport.stream.send": ("wt.stream.sent", "runtime"),
    "webtransport.datagram.receive": ("wt.datagram.received", "runtime"),
    "webtransport.datagram.send": ("wt.datagram.sent", "runtime"),
    "webtransport.connect": ("wt.session.opened", "runtime"),
    "webtransport.disconnect": ("wt.session.closed", "runtime"),
}
TX_KINDS = {"begin": "begin", "committed": "commit", "rolled_back": "rollback"}
BAD_OUTCOMES = {"failed", "rejected", "rolled_back"}


class TimelineRow(TypedDict, total=False):
    sequence: int
    at: str
    kind: str
    transport: str
    source: str
    outcome: str
    correlation_id: str
    invocation_id: str
    engine_session_id: str
    transaction_id: str
    measured_duration_ms: float
    duration_ms: float
    timing_boundary: str
    clock_domain: str


@dataclass(frozen=True)
class ProjectionContext:
    invocation_carriers: Mapping[str, str]
    http_carriers: Mapping[str, str]


def projection_context(rows: Iterable[Mapping[str, Any]]) -> ProjectionContext:
    invocations = {}
    http: dict[str, set[str]] = {}
    for row in rows:
        protocol = CARRIERS.get(row.get("transport"))
        if protocol is None:
            continue
        if invocation := row.get("invocation_id"):
            invocations[invocation] = protocol
        if protocol in {"rest", "http_jsonrpc"} and (
            correlation := row.get("correlation_id")
        ):
            http.setdefault(correlation, set()).add(protocol)
    return ProjectionContext(
        invocations,
        {
            key: next(iter(protocols))
            for key, protocols in http.items()
            if len(protocols) == 1
        },
    )


def project_event(
    row: Mapping[str, Any], origins: ProjectionContext, *, unclassified: bool = False
) -> TimelineRow | None:
    kind = row["kind"]
    carrier = row["transport"]
    protocol = CARRIERS.get(carrier)
    if carrier == "HTTP":
        protocol = origins.http_carriers.get(row.get("correlation_id"))
        if protocol is None:
            protocol = "http_jsonrpc" if row.get("path") == "/rpc" else "rest"
    elif carrier == "Realtime":
        protocol = origins.invocation_carriers.get(row.get("origin_invocation_id"))
        if protocol is None and unclassified:
            protocol = "realtime"

    outcome = row.get("outcome")
    source_kind, source = KINDS.get(kind, (kind, "unknown"))
    if kind in {"Transaction", "Transaction participant"}:
        protocol = "database"
        if kind == "Transaction":
            source_kind = "db.tx." + TX_KINDS.get(outcome, "event")
            source = "database"
            if outcome == "begin":
                outcome = "open"
    elif kind in {"Scope opened", "Response"}:
        source = "app"
        if kind == "Scope opened":
            source_kind = {
                "HTTP": "http.request.received",
                "WebSocket": "ws.session.opened",
                "WebTransport": "wt.session.opened",
            }.get(carrier, kind)
        else:
            source_kind = "http.response.sent"
            status = row.get("status")
            if isinstance(status, int):
                outcome = (
                    "failed" if status >= 500 else "rejected" if status >= 400 else "ok"
                )
    elif kind == "Flush":
        protocol = source = "database"
        source_kind = "db.flush.failed" if outcome == "failed" else "db.flush.completed"

    if kind == "Delivery" and outcome in BAD_OUTCOMES:
        source_kind = "broker.delivery.rejected"
    if kind == "Atom" and outcome in BAD_OUTCOMES:
        source_kind = "atom.failed"
    if protocol == "webtransport" and outcome in {"reject", "rejected"}:
        source_kind = "wt.stream.rejected"
        outcome = "rejected"
    if protocol is None and not unclassified:
        return None

    event: TimelineRow = {
        "sequence": row["sequence"],
        "at": row["at"],
        "kind": source_kind,
        "transport": protocol or "unknown",
        "source": source,
        "outcome": outcome
        if outcome
        in {
            "ok",
            "failed",
            "rejected",
            "committed",
            "rolled_back",
            "delivered",
            "open",
            "partial",
        }
        else "unknown",
    }
    if isinstance(row.get("status"), int):
        event["http_status"] = row["status"]
    if isinstance(row.get("rpc_item_index"), int):
        event["rpc_item_index"] = row["rpc_item_index"]
    for key in TRACE_ID_FIELDS:
        value = row.get(key)
        if isinstance(value, (str, int)) and not isinstance(value, bool):
            event[key] = str(value)
    if kind in {"Invocation", "Hook", "Response", "Transaction", "Flush", "Atom"}:
        for key in TRACE_EXECUTION_FIELDS:
            if isinstance(row.get(key), str):
                event[key] = row[key]
        for key in ("atom_ordinal", "atom_trace_dropped"):
            if type(row.get(key)) is int:
                event[key] = row[key]
        duration = row.get("measured_duration_ms")
        if type(duration) in {int, float} and 0 <= duration < float("inf"):
            event["measured_duration_ms"] = duration
            event["duration_ms"] = duration
            if (
                kind == "Invocation"
                and event.get("timing_boundary") == "invocation_monotonic"
                and event.get("clock_domain")
            ):
                event["observation"] = {
                    "measure": "invocation_latency",
                    "unit": "ms",
                    "value": duration,
                    "clock_domain": event["clock_domain"],
                    "timing_boundary": event["timing_boundary"],
                    "provenance": "Tigrbl operation trace",
                }
    return event
