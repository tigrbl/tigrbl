from __future__ import annotations

from enum import Enum
from typing import Any, Mapping


class ClientTopology(str, Enum):
    SINGLE_CLIENT_SINGLE_SESSION = "single_client_single_session"
    SINGLE_CLIENT_MULTI_SESSION = "single_client_multi_session"
    SEQUENTIAL_CLIENTS = "sequential_clients"
    BOUNDED_INTERLEAVED_CLIENTS = "bounded_interleaved_clients"
    CONCURRENT_CLIENTS = "concurrent_clients"
    CHURN_CLIENTS = "churn_clients"


class SessionScope(str, Enum):
    REQUEST_SCOPED = "request_scoped"
    STREAM_SCOPED = "stream_scoped"
    CONNECTION_SCOPED = "connection_scoped"
    TRANSPORT_SESSION_SCOPED = "transport_session_scoped"


class BehaviorGroup(str, Enum):
    LIFECYCLE = "lifecycle"
    IDENTITY = "identity"
    ISOLATION = "isolation"
    ORDERING = "ordering"
    PRESSURE = "pressure"
    FAULT = "fault"
    CLEANUP = "cleanup"


class CoverageDisposition(str, Enum):
    COVERED = "covered"
    REQUIRED = "required"
    PLANNED = "planned"
    NOT_APPLICABLE = "not_applicable"
    FAIL_CLOSED = "fail_closed"


CLIENT_TOPOLOGY_VALUES = frozenset(item.value for item in ClientTopology)
SESSION_SCOPE_VALUES = frozenset(item.value for item in SessionScope)
BEHAVIOR_GROUP_VALUES = frozenset(item.value for item in BehaviorGroup)
DISPOSITION_VALUES = frozenset(item.value for item in CoverageDisposition)

GOVERNED_IDENTIFIER_FIELDS = frozenset(
    {
        "client_id",
        "session_id",
        "stream_id",
        "datagram_id",
    }
)
GOVERNED_OPTIONAL_FIELDS = frozenset({"subevent", "error_kind"})
INTERNAL_ONLY_FIELDS = frozenset({"lane"})

REQUIRED_MATRIX_AXES = frozenset(
    {
        "transport_scenario",
        "client_topology",
        "session_scope",
        "lifecycle_behavior",
        "isolation_property",
        "pressure_mode",
        "fault_mode",
        "disposition",
    }
)

NON_SESSION_TRANSPORT_SCENARIOS = frozenset(
    {
        "docs payload",
        "docs uix",
        "static files",
        "nested app mount",
    }
)

TRANSPORT_SCENARIO_SESSION_SCOPES: dict[str, SessionScope] = {
    "http rest": SessionScope.REQUEST_SCOPED,
    "https rest": SessionScope.REQUEST_SCOPED,
    "http json-rpc": SessionScope.REQUEST_SCOPED,
    "https json-rpc": SessionScope.REQUEST_SCOPED,
    "http jsonrpc": SessionScope.REQUEST_SCOPED,
    "https jsonrpc": SessionScope.REQUEST_SCOPED,
    "http.rest": SessionScope.REQUEST_SCOPED,
    "https.rest": SessionScope.REQUEST_SCOPED,
    "http.jsonrpc": SessionScope.REQUEST_SCOPED,
    "https.jsonrpc": SessionScope.REQUEST_SCOPED,
    "http stream": SessionScope.STREAM_SCOPED,
    "https stream": SessionScope.STREAM_SCOPED,
    "http.stream": SessionScope.STREAM_SCOPED,
    "https.stream": SessionScope.STREAM_SCOPED,
    "http sse": SessionScope.STREAM_SCOPED,
    "https sse": SessionScope.STREAM_SCOPED,
    "http.sse": SessionScope.STREAM_SCOPED,
    "https.sse": SessionScope.STREAM_SCOPED,
    "ws text": SessionScope.CONNECTION_SCOPED,
    "wss text": SessionScope.CONNECTION_SCOPED,
    "ws binary": SessionScope.CONNECTION_SCOPED,
    "wss binary": SessionScope.CONNECTION_SCOPED,
    "ws json-rpc": SessionScope.CONNECTION_SCOPED,
    "wss json-rpc": SessionScope.CONNECTION_SCOPED,
    "ws jsonrpc": SessionScope.CONNECTION_SCOPED,
    "wss jsonrpc": SessionScope.CONNECTION_SCOPED,
    "ws ndjson": SessionScope.CONNECTION_SCOPED,
    "wss ndjson": SessionScope.CONNECTION_SCOPED,
    "ws": SessionScope.CONNECTION_SCOPED,
    "wss": SessionScope.CONNECTION_SCOPED,
    "webtransport": SessionScope.TRANSPORT_SESSION_SCOPED,
    "message bus": SessionScope.CONNECTION_SCOPED,
    "datagram": SessionScope.TRANSPORT_SESSION_SCOPED,
}


def _normalize_token(value: object) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def classify_transport_session_scope(
    transport_scenario: object,
) -> SessionScope | None:
    """Return the default session-scope classification for a transport row."""

    key = _normalize_token(transport_scenario)
    if key in NON_SESSION_TRANSPORT_SCENARIOS:
        return None
    if key in TRANSPORT_SCENARIO_SESSION_SCOPES:
        return TRANSPORT_SCENARIO_SESSION_SCOPES[key]
    dotted = key.replace(" ", ".")
    if dotted in TRANSPORT_SCENARIO_SESSION_SCOPES:
        return TRANSPORT_SCENARIO_SESSION_SCOPES[dotted]
    raise ValueError(f"unknown transport scenario: {transport_scenario!r}")


def validate_no_internal_lane(record: Mapping[str, Any]) -> None:
    if INTERNAL_ONLY_FIELDS.intersection(record):
        raise ValueError("lane is runtime-internal and not a governed proof field")


def validate_governed_identifier_fields(record: Mapping[str, Any]) -> None:
    validate_no_internal_lane(record)
    for field in ("stream_id", "datagram_id"):
        if field in record and record[field] is None:
            raise ValueError(f"{field} must be omitted or populated")


def validate_matrix_row(row: Mapping[str, Any]) -> None:
    validate_governed_identifier_fields(row)

    missing = sorted(REQUIRED_MATRIX_AXES.difference(row))
    if missing:
        raise ValueError(f"client-session matrix row missing axes: {missing}")

    topology = _enum_value(row["client_topology"])
    if topology not in CLIENT_TOPOLOGY_VALUES:
        raise ValueError(f"unknown client topology: {topology!r}")

    scope = _enum_value(row["session_scope"])
    if scope not in SESSION_SCOPE_VALUES:
        raise ValueError(f"unknown session scope: {scope!r}")

    disposition = _enum_value(row["disposition"])
    if disposition not in DISPOSITION_VALUES:
        raise ValueError(f"unknown disposition: {disposition!r}")

    for axis in ("lifecycle_behavior", "isolation_property", "pressure_mode", "fault_mode"):
        axis_value = _enum_value(row[axis])
        if axis_value not in DISPOSITION_VALUES:
            raise ValueError(f"{axis} must be a coverage disposition: {axis_value!r}")


def build_matrix_row(
    *,
    transport_scenario: str,
    client_topology: ClientTopology | str,
    session_scope: SessionScope | str | None = None,
    disposition: CoverageDisposition | str = CoverageDisposition.REQUIRED,
    lifecycle_behavior: CoverageDisposition | str = CoverageDisposition.REQUIRED,
    isolation_property: CoverageDisposition | str = CoverageDisposition.REQUIRED,
    pressure_mode: CoverageDisposition | str = CoverageDisposition.REQUIRED,
    fault_mode: CoverageDisposition | str = CoverageDisposition.REQUIRED,
    **identifiers: Any,
) -> dict[str, Any]:
    resolved_scope = session_scope or classify_transport_session_scope(transport_scenario)
    if resolved_scope is None:
        raise ValueError("non-session transport rows need explicit not_applicable handling")

    row: dict[str, Any] = {
        "transport_scenario": transport_scenario,
        "client_topology": _enum_value(client_topology),
        "session_scope": _enum_value(resolved_scope),
        "lifecycle_behavior": _enum_value(lifecycle_behavior),
        "isolation_property": _enum_value(isolation_property),
        "pressure_mode": _enum_value(pressure_mode),
        "fault_mode": _enum_value(fault_mode),
        "disposition": _enum_value(disposition),
    }
    row.update(identifiers)
    validate_matrix_row(row)
    return row


__all__ = [
    "BEHAVIOR_GROUP_VALUES",
    "CLIENT_TOPOLOGY_VALUES",
    "DISPOSITION_VALUES",
    "GOVERNED_IDENTIFIER_FIELDS",
    "GOVERNED_OPTIONAL_FIELDS",
    "INTERNAL_ONLY_FIELDS",
    "NON_SESSION_TRANSPORT_SCENARIOS",
    "REQUIRED_MATRIX_AXES",
    "SESSION_SCOPE_VALUES",
    "TRANSPORT_SCENARIO_SESSION_SCOPES",
    "BehaviorGroup",
    "ClientTopology",
    "CoverageDisposition",
    "SessionScope",
    "build_matrix_row",
    "classify_transport_session_scope",
    "validate_governed_identifier_fields",
    "validate_matrix_row",
    "validate_no_internal_lane",
]
