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


def test_invalid_protocol_scope_fails_closed_before_dispatch() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.scope_schemas", "validate_scope")

    with pytest.raises(ValueError, match="scope|protocol|type|required"):
        validate_scope({"type": "websocket", "scheme": "wss"})

