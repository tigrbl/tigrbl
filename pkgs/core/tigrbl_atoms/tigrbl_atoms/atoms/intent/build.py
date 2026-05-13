from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx
from .._temp import _ensure_temp
from ..hot.slots import capture_slot_payload

ANCHOR = _ev.BATCH_INTENT_BUILD


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    transport = temp.get("transport", {})
    temp["intent"] = {
        "op": getattr(ctx, "op", None),
        "target": getattr(ctx, "target", None),
        "model": getattr(ctx, "model", None),
        "payload_ref": transport.get("payload_ref"),
        "payload_bytes": int(transport.get("payload_bytes", 0) or 0),
        "sink_family": transport.get("sink_family"),
        "sink_index": transport.get("sink_index", 0),
        "correlation_id": transport.get("correlation_id"),
        "batch_policy": getattr(ctx, "batch_policy", None) or {},
    }
    slot_payload = capture_slot_payload(ctx)
    if slot_payload is not None:
        temp["intent"]["slot_payload"] = slot_payload
        if temp["intent"]["payload_ref"] is None:
            temp["intent"]["payload_ref"] = slot_payload.as_mapping()


hot_run = _run


class AtomImpl(Atom[Bound, Bound, Exception]):
    name = "intent.build"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
