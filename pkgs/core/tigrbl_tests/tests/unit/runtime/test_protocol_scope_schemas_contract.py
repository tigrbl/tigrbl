from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def _field(value: object, name: str) -> object:
    if isinstance(value, dict):
        return value[name]
    return getattr(value, name)


def test_http_and_websocket_scopes_normalize_protocol_metadata() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    http = validate_scope(
        {
            "type": "http",
            "http_version": "2",
            "method": "GET",
            "path": "/items",
            "headers": [(b"host", b"example.test")],
        }
    )
    ws = validate_scope(
        {
            "type": "websocket",
            "scheme": "wss",
            "path": "/socket",
            "headers": [(b"host", b"example.test")],
            "extensions": {"tls": {"version": "TLSv1.3", "cipher": "TLS_AES_128_GCM_SHA256"}},
        }
    )

    assert _field(http, "scope_type") == "http"
    assert _field(http, "http_version") == "2"
    assert _field(ws, "scope_type") == "websocket"
    assert _field(ws, "secure") is True
    assert _field(ws, "tls")["version"] == "TLSv1.3"


def test_webtransport_and_lifespan_scopes_validate_extensions() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    transport = validate_scope(
        {
            "type": "webtransport",
            "path": "/transport",
            "extensions": {"quic": {"alpn": "h3", "stream_id": "7"}},
        }
    )
    lifespan = validate_scope({"type": "lifespan", "asgi": {"version": "3.0"}})

    assert _field(transport, "scope_type") == "webtransport"
    assert _field(transport, "quic")["alpn"] == "h3"
    assert _field(lifespan, "scope_type") == "lifespan"


def test_message_and_datagram_scopes_normalize_runtime_metadata() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    message = validate_scope(
        {
            "type": "message",
            "topic": "inventory.changed",
            "headers": [(b"x-event-id", b"evt-1")],
        }
    )
    datagram = validate_scope(
        {
            "type": "datagram",
            "endpoint": "events",
            "peer": ("127.0.0.1", 9999),
            "payload_type": "bytes",
        }
    )

    assert _field(message, "scope_type") == "message"
    assert _field(message, "family") == "message"
    assert _field(message, "topic") == "inventory.changed"
    assert _field(datagram, "scope_type") == "datagram"
    assert _field(datagram, "family") == "datagram"
    assert _field(datagram, "peer") == ("127.0.0.1", 9999)


def test_http_scope_normalizes_headers_to_lowercase_byte_pairs() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    scope = validate_scope(
        {
            "type": "http",
            "method": "POST",
            "path": "/items",
            "headers": [(b"Content-Type", b"application/json"), (b"X-Trace", b"abc")],
        }
    )

    assert _field(scope, "headers") == (
        (b"content-type", b"application/json"),
        (b"x-trace", b"abc"),
    )


def test_secure_scope_derives_tls_metadata_from_scheme_and_extensions() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    scope = validate_scope(
        {
            "type": "http",
            "scheme": "https",
            "method": "GET",
            "path": "/secure",
            "extensions": {"tls": {"version": "TLSv1.3"}},
        }
    )

    assert _field(scope, "secure") is True
    assert _field(scope, "tls")["version"] == "TLSv1.3"


def test_invalid_protocol_scope_fails_closed_before_dispatch() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    with pytest.raises(ValueError, match="scope|protocol|type|required"):
        validate_scope({"type": "websocket", "scheme": "wss"})


@pytest.mark.parametrize(
    "bad_scope",
    (
        {"type": "http", "method": "GET"},
        {"type": "webtransport", "path": "/wt", "extensions": {"quic": "h3"}},
        {"type": "message"},
        {"type": "datagram", "endpoint": "events", "peer": "127.0.0.1:9999"},
    ),
)
def test_invalid_protocol_scope_extensions_fail_closed(bad_scope: dict[str, object]) -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    with pytest.raises(ValueError, match="scope|protocol|extension|required|peer"):
        validate_scope(bad_scope)
