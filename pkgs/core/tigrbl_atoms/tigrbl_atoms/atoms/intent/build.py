from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_INPUT_PREPARE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    transport = temp.get("transport", {})
    temp["intent"] = {
        "op": getattr(ctx, "op", None),
        "model": getattr(ctx, "model", None),
        "payload_ref": transport.get("payload_ref"),
        "sink_family": transport.get("sink_family"),
        "sink_index": transport.get("sink_index", 0),
        "correlation_id": transport.get("correlation_id"),
        "batch_policy": getattr(ctx, "batch_policy", None) or {},
    }


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "intent.build"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
