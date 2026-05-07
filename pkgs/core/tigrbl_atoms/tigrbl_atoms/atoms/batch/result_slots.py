from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Operated
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.BATCH_RESULT_SLOTS


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_resident_handled"):
        return
    group = ctx.temp.get("batch_group")
    if group is None:
        return
    if ctx.temp.get("batch_execution_kind") == "scalar_fallback":
        group.result_slots = [None for _ in group.admissions]
        return
    raw = ctx.temp.get("batch_raw_results")
    slots = list(raw if isinstance(raw, (list, tuple)) else [raw])
    if len(slots) < len(group.admissions):
        slots.extend([None] * (len(group.admissions) - len(slots)))
    group.result_slots = slots


hot_run = _run


class AtomImpl(Atom[Operated, Operated, Exception]):
    name = "batch.result_slots"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
