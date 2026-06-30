from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded
from ...types import Atom, Ctx, GuardedCtx
from . import _scheduler
from .scheduler import get_resident_scheduler

ANCHOR = _ev.BATCH_AWAIT_SEAL


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if not _scheduler.enabled(ctx):
        return
    ctx.temp["batch_group"] = _scheduler.await_seal(ctx)


async def hot_run(obj: object | None, ctx: Any) -> None:
    resident = get_resident_scheduler(ctx)
    if resident is not None and _scheduler.enabled(ctx):
        await resident.await_result(ctx)
        return
    _run(obj, ctx)


class AtomImpl(Atom[Guarded, Guarded, Exception]):
    name = "batch.await_seal"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Guarded]:
        resident = get_resident_scheduler(ctx)
        if resident is not None and _scheduler.enabled(ctx):
            await resident.await_result(ctx)
            return ctx.promote(GuardedCtx)
        _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
