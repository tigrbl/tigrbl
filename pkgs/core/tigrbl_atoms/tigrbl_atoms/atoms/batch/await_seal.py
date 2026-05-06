from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded
from ...types import Atom, Ctx, GuardedCtx
from . import _scheduler

ANCHOR = _ev.BATCH_AWAIT_SEAL


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if not _scheduler.enabled(ctx):
        return
    ctx.temp["batch_group"] = _scheduler.await_seal(ctx)


class AtomImpl(Atom[Guarded, Guarded, Exception]):
    name = "batch.await_seal"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Guarded]:
        _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
