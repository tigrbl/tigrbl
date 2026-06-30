from __future__ import annotations

from typing import Any

import tigrbl_ops_realtime as _core

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    setattr(ctx, "result", await _core.download(_ctx.payload(ctx)))


class AtomImpl(Atom[Resolved, Operated, Exception]):
    name = "sys.handler_download"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
