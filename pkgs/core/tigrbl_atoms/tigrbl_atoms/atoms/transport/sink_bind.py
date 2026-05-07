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
