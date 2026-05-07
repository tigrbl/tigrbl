from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Operated
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.BATCH_COMMIT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_resident_handled"):
        ctx.temp["batch_commit"] = True
        return
    if ctx.temp.get("batch_group") is not None:
        ctx.temp["batch_commit"] = True


hot_run = _run


class AtomImpl(Atom[Operated, Operated, Exception]):
    name = "batch.commit"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
