from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Encoded
from ...types import Atom, Ctx, EncodedCtx

ANCHOR = _ev.BATCH_EGRESS_SHAPE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    admission = ctx.temp.get("batch_admission")
    group = ctx.temp.get("batch_group")
    if admission is None or group is None or admission.result_index is None:
        return
    try:
        result = group.result_slots[admission.result_index]
    except IndexError:
        result = None
    ctx.result = result
    ctx.temp["fanout_payload"] = {
        "admission_id": admission.admission_id,
        "correlation_id": admission.intent.get("correlation_id"),
        "result": result,
    }


class AtomImpl(Atom[Encoded, Encoded, Exception]):
    name = "fanout.shape"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
