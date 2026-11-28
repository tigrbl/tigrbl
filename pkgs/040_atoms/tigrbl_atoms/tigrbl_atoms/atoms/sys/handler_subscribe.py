from __future__ import annotations

from typing import Any

import tigrbl_ops_realtime as _core

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    from tigrbl_ops_realtime.quotas import SubscriptionAdmissionError
    from tigrbl_typing.status.exceptions import HTTPException

    try:
        setattr(ctx, "result", await _core.subscribe(_ctx.payload(ctx), ctx=ctx))
    except SubscriptionAdmissionError as exc:
        headers = (
            {"Retry-After": str(max(1, __import__("math").ceil(exc.retry_after)))}
            if exc.retry_after is not None
            else None
        )
        raise HTTPException(
            status_code=exc.status_code, detail=exc.detail(), headers=headers
        ) from exc


class AtomImpl(Atom[Resolved, Operated, Exception]):
    name = "sys.handler_subscribe"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
