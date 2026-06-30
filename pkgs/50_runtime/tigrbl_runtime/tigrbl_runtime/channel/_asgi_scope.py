from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import parse_qs

from tigrbl_kernel.channel_taxonomy import (
    channel_family as _channel_family,
    channel_kind as _channel_kind,
    channel_subevents as _subevents,
    normalize_exchange,
)
from tigrbl_typing.channel import OpChannel


def _headers(scope: Mapping[str, Any]) -> dict[str, str]:
    pairs = scope.get("headers", ())
    out: dict[str, str] = {}
    for key, value in pairs or ():
        try:
            out[bytes(key).decode("latin-1").lower()] = bytes(value).decode("latin-1")
        except Exception:
            continue
    return out


def _query(scope: Mapping[str, Any]) -> dict[str, list[str]]:
    raw = scope.get("query_string", b"")
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)):
        return {}
    return {
        key: [str(item) for item in values]
        for key, values in parse_qs(
            bytes(raw).decode("utf-8"), keep_blank_values=True
        ).items()
    }


def _scheme(scope: Mapping[str, Any]) -> str:
    return str(scope.get("scheme") or "").lower()


def build_asgi_channel(
    env: Any,
    *,
    exchange: str = "request_response",
    protocol: str | None = None,
    framing: str | None = None,
) -> OpChannel:
    exchange = normalize_exchange(exchange)
    scope = getattr(env, "scope", {}) or {}
    scope_type = str(scope.get("type") or "http")
    path = str(scope.get("path") or "/")
    method = scope.get("method")
    protocol_name = protocol or _scheme(scope) or scope_type
    selector = path
    if scope_type == "http" and isinstance(method, str):
        selector = f"{method.upper()} {path}"
    return OpChannel(
        kind=_channel_kind(scope_type, exchange),
        family=_channel_family(scope_type, exchange),
        exchange=exchange,
        protocol=protocol_name,
        path=path,
        method=str(method).upper() if isinstance(method, str) else None,
        selector=selector,
        framing=framing,
        subevents=_subevents(scope_type, exchange),
        headers=_headers(scope),
        query=_query(scope),
        path_params=scope.get("path_params", {}) or {},
        send=getattr(env, "send", None),
        receive=getattr(env, "receive", None),
    )
