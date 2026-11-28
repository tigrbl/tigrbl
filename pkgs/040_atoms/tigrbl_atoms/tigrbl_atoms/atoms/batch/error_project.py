from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Failed
from ...types import Atom, Ctx, FailedCtx

ANCHOR = _ev.BATCH_ERROR_PROJECT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    admission = ctx.temp.get("batch_admission")
    if admission is None:
        return
    group = ctx.temp.get("batch_group")
    if group is not None and admission.result_index is not None:
        while len(group.error_slots) < len(group.admissions):
            group.error_slots.append(None)
        group.error_slots[admission.result_index] = getattr(ctx, "error", None)
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
