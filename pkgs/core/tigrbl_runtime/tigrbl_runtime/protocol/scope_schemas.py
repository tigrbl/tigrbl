from __future__ import annotations

from typing import Any


def _headers(scope: dict[str, Any]) -> tuple[tuple[bytes, bytes], ...]:
    return tuple((bytes(k).lower(), bytes(v)) for k, v in scope.get("headers", ()))


def _secure(scope: dict[str, Any]) -> bool:
    return scope.get("scheme") in {"https", "wss"} or "tls" in scope.get("extensions", {})


def validate_scope(scope: dict[str, Any]) -> dict[str, Any]:
    scope_type = scope.get("type")
    if not isinstance(scope_type, str):
        raise ValueError("protocol scope type is required")
    extensions = scope.get("extensions", {})
    if extensions is None:
        extensions = {}
    if not isinstance(extensions, dict):
        raise ValueError("protocol scope extensions must be a mapping")

    if scope_type == "http":
        if "method" not in scope or "path" not in scope:
            raise ValueError("http protocol scope requires method and path")
        return {
            **scope,
            "scope_type": "http",
            "headers": _headers(scope),
            "secure": _secure(scope),
            "tls": extensions.get("tls"),
        }
    if scope_type == "websocket":
        if "path" not in scope:
            raise ValueError("websocket protocol scope requires path")
        return {
            **scope,
            "scope_type": "websocket",
            "headers": _headers(scope),
            "secure": _secure(scope),
            "tls": extensions.get("tls"),
        }
    if scope_type == "webtransport":
        quic = extensions.get("quic")
        if not isinstance(quic, dict):
            raise ValueError("webtransport protocol scope requires quic extension metadata")
        return {**scope, "scope_type": "webtransport", "quic": quic}
    if scope_type == "lifespan":
        return {**scope, "scope_type": "lifespan"}
    if scope_type == "message":
        if "topic" not in scope:
            raise ValueError("message protocol scope requires topic")
        return {**scope, "scope_type": "message", "family": "message", "headers": _headers(scope)}
    if scope_type == "datagram":
        peer = scope.get("peer")
        if not isinstance(peer, tuple):
            raise ValueError("datagram protocol scope requires peer tuple")
        return {**scope, "scope_type": "datagram", "family": "datagram"}
    raise ValueError(f"unsupported protocol scope type: {scope_type}")


__all__ = ["validate_scope"]
