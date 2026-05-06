from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Failed
from ...types import Atom, Ctx, FailedCtx

ANCHOR = _ev.ERR_TRANSPORT_SHAPE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    admission = ctx.temp.get("batch_admission")
    if admission is None:
        return
    ctx.result = {
        "admission_id": admission.admission_id,
        "error": getattr(ctx, "error", None),
    }


class AtomImpl(Atom[Failed, Failed, Exception]):
    name = "batch.error_project"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Failed]) -> Ctx[Failed]:
        _run(obj, ctx)
        return ctx.promote(FailedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
