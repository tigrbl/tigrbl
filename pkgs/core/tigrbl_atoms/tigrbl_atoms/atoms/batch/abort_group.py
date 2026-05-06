from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Failed
from ...types import Atom, Ctx, FailedCtx

ANCHOR = _ev.ERR_ROLLBACK


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    group = ctx.temp.get("batch_group")
    if group is not None:
        group.sealed = True
        ctx.temp["batch_aborted"] = True


class AtomImpl(Atom[Failed, Failed, Exception]):
    name = "batch.abort_group"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Failed]) -> Ctx[Failed]:
        _run(obj, ctx)
        return ctx.promote(FailedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
