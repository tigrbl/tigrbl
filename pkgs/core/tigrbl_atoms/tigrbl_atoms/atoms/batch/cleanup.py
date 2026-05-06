from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Egressed
from ...types import Atom, Ctx, EgressedCtx
from . import _scheduler

ANCHOR = _ev.POST_RESPONSE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    _scheduler.cleanup(ctx)


class AtomImpl(Atom[Egressed, Egressed, Exception]):
    name = "batch.cleanup"
    anchor = ANCHOR

    async def __call__(
        self, obj: object | None, ctx: Ctx[Egressed]
    ) -> Ctx[Egressed]:
        _run(obj, ctx)
        return ctx.promote(EgressedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
