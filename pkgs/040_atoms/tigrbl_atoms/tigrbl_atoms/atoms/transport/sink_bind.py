from __future__ import annotations

from tigrbl_atoms.protocol_scope import scope_type as projected_scope_type

from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp
from ..ingress.identity import webtransport_lane_identity

ANCHOR = _ev.BATCH_TRANSPORT_SINK_BIND


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    transport = _ensure_temp(ctx).setdefault("transport", {})
    transport["sink"] = getattr(ctx, "transport_sink", None)
    transport["sink_index"] = getattr(ctx, "transport_sink_index", 0)
    transport["sink_family"] = getattr(ctx, "transport_sink_family", None)
    identity = _ensure_temp(ctx).get("identity") or {}
    transport["identity"] = dict(identity)
    transport["correlation_id"] = identity.get("correlation_id") or getattr(ctx, "correlation_id", None)

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    send = getattr(raw, "send", None) if raw is not None else None
    if not isinstance(scope, dict) or not callable(send):
        return
    scope_type = projected_scope_type(scope)
    if scope_type not in {"websocket", "webtransport"}:
        return
    session_id = None
    message = getattr(ctx, "channel_message", None)
    if isinstance(message, dict):
        session_id = message.get("session_id")
    if session_id is None:
        extensions = scope.get("extensions")
        if isinstance(extensions, dict):
            extension = extensions.get(scope_type)
            if isinstance(extension, dict):
                session_id = extension.get("session_id")
    realtime = _ensure_temp(ctx).setdefault("realtime", {})
    realtime["sink"] = send
    realtime["transport"] = scope_type
    session_id = identity.get("transport_session_id") or session_id
    if session_id is not None:
        realtime["session_id"] = str(session_id)
    if scope_type == "webtransport" and identity:
        def identity_for_stream(stream_id: str) -> dict:
            lane = webtransport_lane_identity(scope, {"stream_id": stream_id}, identity)
            return {"stream_correlation_id": lane["stream_correlation_id"]}

        realtime["identity_for_stream"] = identity_for_stream
    owner = scope.get("app") or getattr(ctx, "app", None)
    broker = getattr(owner, "__realtime_broker__", None)
    if broker is not None:
        realtime["broker"] = broker


hot_run = _run


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "transport.sink_bind"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
