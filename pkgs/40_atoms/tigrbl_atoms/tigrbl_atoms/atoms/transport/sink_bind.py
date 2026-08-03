from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.BATCH_TRANSPORT_SINK_BIND


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    transport = _ensure_temp(ctx).setdefault("transport", {})
    transport["sink"] = getattr(ctx, "transport_sink", None)
    transport["sink_index"] = getattr(ctx, "transport_sink_index", 0)
    transport["sink_family"] = getattr(ctx, "transport_sink_family", None)
    transport["correlation_id"] = getattr(ctx, "correlation_id", None)

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    send = getattr(raw, "send", None) if raw is not None else None
    if not isinstance(scope, dict) or not callable(send):
        return
    scope_type = str(scope.get("type") or "")
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
    if session_id is not None:
        realtime["session_id"] = str(session_id)
    owner = scope.get("app")
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
