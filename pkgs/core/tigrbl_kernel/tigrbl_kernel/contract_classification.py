from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.binding_spec import normalize_exchange


CONTRACT_CHANNELS: tuple[str, ...] = ("receive", "send")
CONTRACT_SCOPE_TYPES: tuple[str, ...] = ("http", "websocket", "webtransport")
CONTRACT_DIRECTIONS: tuple[str, ...] = (
    "client_to_server",
    "server_to_client",
    "app_to_server",
    "server_to_app",
    "system",
)
CONTRACT_FAMILIES: tuple[str, ...] = (
    "request",
    "session",
    "message",
    "stream",
    "datagram",
)

CONTRACT_BINDING_ALIASES: dict[str, tuple[str, ...]] = {
    "rest": ("http.rest", "https.rest"),
    "jsonrpc": ("http.jsonrpc", "https.jsonrpc"),
    "http.stream": ("http.stream", "https.stream"),
    "sse": ("http.sse", "https.sse"),
    "websocket": ("ws", "wss"),
    "webtransport": ("webtransport",),
}

CONTRACT_EXCHANGE_ALIASES: dict[str, str] = {
    "unary": "request_response",
    "duplex": "bidirectional_stream",
    "client_stream": "client_stream",
    "server_stream": "server_stream",
    "fire_and_forget": "fire_and_forget",
}

CANONICAL_CONTRACT_EVENTS: tuple[str, ...] = (
    "http.request",
    "http.disconnect",
    "http.response.start",
    "http.response.body",
    "http.response.pathsend",
    "websocket.connect",
    "websocket.receive",
    "websocket.disconnect",
    "websocket.accept",
    "websocket.send",
    "websocket.close",
    "webtransport.connect",
    "webtransport.accept",
    "webtransport.stream.receive",
    "webtransport.stream.send",
    "webtransport.stream.close",
    "webtransport.stream.reset",
    "webtransport.stream.stop_sending",
    "webtransport.datagram.receive",
    "webtransport.datagram.send",
    "webtransport.disconnect",
    "webtransport.close",
    "transport.emit.complete",
    "transport.emit.failed",
)

_EVENT_SCOPE_PREFIXES: dict[str, str] = {
    "http.": "http",
    "websocket.": "websocket",
    "webtransport.": "webtransport",
    "transport.emit.": "webtransport",
}


@dataclass(frozen=True, slots=True)
class ContractClassificationProjection:
    event: str
    channel: str
    scope_type: str
    binding: str
    local_binding_kinds: tuple[str, ...]
    family: str
    contract_exchange: str
    local_exchange: str
    direction: str
    allowed_framings: tuple[str, ...]
    required_payload_fields: tuple[str, ...]


def project_contract_classification(row: dict[str, Any]) -> ContractClassificationProjection:
    if "subsurface" in row:
        raise ValueError("contract classifications must not use subsurface")

    event = _required_str(row, "event")
    channel = _required_str(row, "channel")
    scope_type = _required_str(row, "scope_type")
    binding = _required_str(row, "binding")
    family = _required_str(row, "family")
    exchange = _required_str(row, "exchange")
    direction = _required_str(row, "direction")

    if event not in CANONICAL_CONTRACT_EVENTS:
        raise ValueError(f"unsupported contract event {event!r}")
    if channel not in CONTRACT_CHANNELS:
        raise ValueError(f"unsupported contract channel {channel!r}")
    if scope_type not in CONTRACT_SCOPE_TYPES:
        raise ValueError(f"unsupported contract scope_type {scope_type!r}")
    if not _event_matches_scope(event=event, scope_type=scope_type):
        raise ValueError(f"contract event {event!r} does not match scope_type {scope_type!r}")
    if family not in CONTRACT_FAMILIES:
        raise ValueError(f"unsupported contract family {family!r}")
    if direction not in CONTRACT_DIRECTIONS:
        raise ValueError(f"unsupported contract direction {direction!r}")
    if binding not in CONTRACT_BINDING_ALIASES:
        raise ValueError(f"unsupported contract binding {binding!r}")
    if scope_type == "webtransport" and family == "message":
        raise ValueError("WebTransport message is not a native transport family")

    try:
        local_exchange = normalize_exchange(CONTRACT_EXCHANGE_ALIASES[exchange])
    except KeyError as exc:
        raise ValueError(f"unsupported contract exchange {exchange!r}") from exc

    return ContractClassificationProjection(
        event=event,
        channel=channel,
        scope_type=scope_type,
        binding=binding,
        local_binding_kinds=CONTRACT_BINDING_ALIASES[binding],
        family=family,
        contract_exchange=exchange,
        local_exchange=local_exchange,
        direction=direction,
        allowed_framings=_string_tuple(row.get("allowed_framings", ())),
        required_payload_fields=_string_tuple(row.get("required_payload_fields", ())),
    )


def is_supported_contract_classification(row: dict[str, Any]) -> bool:
    try:
        project_contract_classification(row)
    except ValueError:
        return False
    return True


def _required_str(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"contract classification requires string {key!r}")
    return value


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError("contract classification list fields must be sequences")
    result = tuple(str(item) for item in value)
    if any(not item for item in result):
        raise ValueError("contract classification list fields must not contain blanks")
    return result


def _event_matches_scope(*, event: str, scope_type: str) -> bool:
    for prefix, expected_scope_type in _EVENT_SCOPE_PREFIXES.items():
        if event.startswith(prefix):
            return scope_type == expected_scope_type
    return False


__all__ = [
    "CANONICAL_CONTRACT_EVENTS",
    "CONTRACT_BINDING_ALIASES",
    "CONTRACT_CHANNELS",
    "CONTRACT_DIRECTIONS",
    "CONTRACT_EXCHANGE_ALIASES",
    "CONTRACT_FAMILIES",
    "CONTRACT_SCOPE_TYPES",
    "ContractClassificationProjection",
    "is_supported_contract_classification",
    "project_contract_classification",
]
