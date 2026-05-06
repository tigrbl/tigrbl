from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Operated
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.POST_FLUSH


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    group = ctx.temp.get("batch_group")
    if group is None:
        return
    raw = ctx.temp.get("batch_raw_results")
    group.result_slots = list(raw if isinstance(raw, (list, tuple)) else [raw])


class AtomImpl(Atom[Operated, Operated, Exception]):
    name = "batch.result_slots"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
