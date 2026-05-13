from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded, Executing
from ...types import Atom, Ctx, ExecutingCtx

ANCHOR = _ev.BATCH_TX_BEGIN


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_group") is not None:
        ctx.temp["batch_tx_begin"] = True


class AtomImpl(Atom[Guarded, Executing, Exception]):
    name = "batch.tx_begin"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
