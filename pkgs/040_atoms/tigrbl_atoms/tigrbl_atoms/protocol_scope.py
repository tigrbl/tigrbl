from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AsgiScopeKind(str, Enum):
    HTTP = "http"
    WEBSOCKET = "websocket"
    WEBTRANSPORT = "webtransport"
    LIFESPAN = "lifespan"


@dataclass(frozen=True, slots=True)
class AsgiScope:
    kind: AsgiScopeKind


_SCOPE_PROJECTION = "_tigrbl_asgi_scope"


def _read_scope_type(scope: Mapping[str, Any]) -> Any:
    return scope.get("type")


def _cached_scope(scope: Mapping[str, Any]) -> AsgiScope | None:
    projection = scope.get(_SCOPE_PROJECTION)
    return projection if isinstance(projection, AsgiScope) else None


def project_asgi_scope(scope: Mapping[str, Any]) -> AsgiScope:
    projection = _cached_scope(scope)
    if projection is not None:
        return projection
    raw_type = _read_scope_type(scope)
    if not isinstance(raw_type, str):
        raise ValueError("ASGI scope type is required")
    try:
        kind = AsgiScopeKind(raw_type)
    except ValueError:
        raise ValueError(f"unsupported ASGI scope type: {raw_type}") from None
    projection = AsgiScope(kind)
    if isinstance(scope, dict):
        scope[_SCOPE_PROJECTION] = projection
    return projection


def scope_type(scope: Mapping[str, Any], default: str = "") -> str:
    projection = _cached_scope(scope)
    if projection is not None:
        return projection.kind.value
    # Some operation executors also accept internal contexts with no ASGI scope.
    try:
        return project_asgi_scope(scope).kind.value
    except ValueError:
        return default


def _headers(scope: dict[str, Any]) -> tuple[tuple[bytes, bytes], ...]:
    return tuple((bytes(k).lower(), bytes(v)) for k, v in scope.get("headers", ()))


def _secure(scope: dict[str, Any]) -> bool:
    return scope.get("scheme") in {"https", "wss"} or "tls" in scope.get("extensions", {})


def validate_scope(scope: dict[str, Any]) -> dict[str, Any]:
    projection = _cached_scope(scope)
    scope_type = projection.kind.value if projection is not None else _read_scope_type(scope)
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


__all__ = ["AsgiScope", "AsgiScopeKind", "project_asgi_scope", "scope_type", "validate_scope"]
