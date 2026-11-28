from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Operated
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.BATCH_PRECOMMIT_VALIDATE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_resident_handled"):
        return
    group = ctx.temp.get("batch_group")
    if group is None:
        return
    if getattr(group, "fallback", False):
        return
    if group.result_slots and len(group.result_slots) != len(group.admissions):
        raise RuntimeError("batch result slot count does not match admissions")


class AtomImpl(Atom[Operated, Operated, Exception]):
    name = "batch.precommit_validate"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
