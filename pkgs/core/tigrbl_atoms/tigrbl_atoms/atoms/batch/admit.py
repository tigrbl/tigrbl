from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded
from ...types import Atom, Ctx, GuardedCtx
from . import _scheduler

ANCHOR = _ev.DEP_EXTRA


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if not _scheduler.enabled(ctx):
        return
    _scheduler.admit(ctx)


class AtomImpl(Atom[Guarded, Guarded, Exception]):
    name = "batch.admit"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Guarded]:
        _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
