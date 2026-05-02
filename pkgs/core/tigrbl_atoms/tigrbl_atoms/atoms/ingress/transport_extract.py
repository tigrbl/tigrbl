from __future__ import annotations

from typing import Any

from tigrbl_typing.gw.raw import GwRouteEnvelope

from ... import events as _ev
from ..._request import Request
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_TRANSPORT_EXTRACT
async def _read_http_body(ctx: Any) -> object | None:
    temp = _ensure_temp(ctx)
    hot = temp.setdefault("hot", {})
    if isinstance(hot, dict):
        cached_body = hot.get("body_bytes")
        if isinstance(cached_body, bytes):
            return cached_body

    body = getattr(ctx, "body", None)
    if body is not None:
        if isinstance(hot, dict):
            if isinstance(body, memoryview):
                hot["body_bytes"] = body.tobytes()
                hot["body_view"] = memoryview(hot["body_bytes"])
            elif isinstance(body, bytearray):
                hot["body_bytes"] = bytes(body)
                hot["body_view"] = memoryview(hot["body_bytes"])
            elif isinstance(body, bytes):
                hot["body_bytes"] = body
                hot["body_view"] = memoryview(body)
        return body

    raw = getattr(ctx, "raw", None)
    receive = getattr(raw, "receive", None) if raw is not None else None
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not (
        callable(receive) and isinstance(scope, dict) and scope.get("type") == "http"
    ):
        return None

    message = await receive()
    if not isinstance(message, dict) or message.get("type") != "http.request":
        return None
    first_chunk = message.get("body", b"")
    body_bytes = (
        bytes(first_chunk) if isinstance(first_chunk, (bytes, bytearray)) else b""
    )
    if bool(message.get("more_body", False)):
        chunks: list[bytes] = [body_bytes]
        while True:
            message = await receive()
            if not isinstance(message, dict) or message.get("type") != "http.request":
                break
            chunk = message.get("body", b"")
            if isinstance(chunk, (bytes, bytearray)):
                chunks.append(bytes(chunk))
            if not bool(message.get("more_body", False)):
                break
        body_bytes = b"".join(chunks)
    if isinstance(hot, dict):
        hot["body_bytes"] = body_bytes
        hot["body_view"] = memoryview(body_bytes)
    return body_bytes


async def _run(obj: object | None, ctx: Any) -> None:
    del obj

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    request = getattr(ctx, "request", None)
    if request is None:
        request = Request(scope, app=getattr(ctx, "app", None))
        setattr(ctx, "request", request)
    method = str(getattr(request, "method", scope.get("method", "")) or "").upper()
    path = str(getattr(request, "path", scope.get("path", "/")) or "/")
    temp = _ensure_temp(ctx)
    hot = temp.setdefault("hot", {})
    headers = getattr(request, "headers", {})
    query = getattr(request, "query", {})
    if isinstance(hot, dict):
        hot["raw_query_string"] = scope.get("query_string", b"")

    body = await _read_http_body(ctx)
    if body is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        body = getattr(gw_raw, "body", None) if gw_raw is not None else None

    if isinstance(body, bytearray):
        body = bytes(body)
    if isinstance(body, memoryview):
        body = body.tobytes()
    if isinstance(body, str):
        body = body.encode("utf-8")
    if body is not None:
        if isinstance(hot, dict):
            hot["body_bytes"] = body
            hot["body_view"] = memoryview(body)
        setattr(request, "body", body)
        if hasattr(request, "_json_loaded"):
            setattr(request, "_json_loaded", False)
        if hasattr(request, "_json_cache"):
            setattr(request, "_json_cache", None)
        if hasattr(request, "_form_loaded"):
            setattr(request, "_form_loaded", False)
        if hasattr(request, "_form_cache"):
            setattr(request, "_form_cache", None)

    transport = "ws" if scope.get("type") == "websocket" else "http"
    scheme = str(scope.get("scheme", "http")).lower()

    gw_raw = GwRouteEnvelope(
        transport=transport,
        scheme="wss"
        if scheme in {"wss", "https"} and transport == "ws"
        else (
            "https" if scheme == "https" else ("ws" if transport == "ws" else "http")
        ),
        kind="unknown",
        method=method if transport == "http" else None,
        path=path,
        headers=headers,
        query=query,
        body=body if transport == "http" else None,
        ws_event=getattr(ctx, "raw_event", None) if transport == "ws" else None,
        rpc=None,
    )
    setattr(ctx, "gw_raw", gw_raw)

    ingress = temp.setdefault("ingress", {})
    ingress.update(
        {
            "transport": transport,
            "scheme": gw_raw.scheme,
            "method": method,
            "path": path,
            "headers": headers,
            "query": query,
            "body": body,
            "request": request,
        }
    )
    setattr(ctx, "method", method)
    setattr(ctx, "path", path)
    setattr(ctx, "headers", headers)
    setattr(ctx, "query", query)
    if body is not None:
        setattr(ctx, "body", body)


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "ingress.transport_extract"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        await _run(obj, ctx)
        return ctx


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
