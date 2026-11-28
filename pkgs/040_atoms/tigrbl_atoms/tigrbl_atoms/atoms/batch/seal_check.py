from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded
from ...types import Atom, Ctx, GuardedCtx
from . import _scheduler

ANCHOR = _ev.BATCH_SEAL_CHECK


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if not _scheduler.enabled(ctx):
        return
    ctx.temp["batch_should_seal"] = _scheduler.seal_check(ctx)


hot_run = _run


class AtomImpl(Atom[Guarded, Guarded, Exception]):
    name = "batch.seal_check"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Guarded]:
        _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
