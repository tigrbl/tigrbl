from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Resolved, Operated
from ...types import Atom, Ctx, OperatedCtx
from ..sys import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_group") is None:
        return
    db = _ctx.db(ctx)
    stmt = ctx.temp.get("batch_statement")
    parameter_sets = ctx.temp.get("batch_parameter_sets")
    statements = ctx.temp.get("batch_statements")
    if stmt is not None and parameter_sets is not None and hasattr(db, "executemany"):
        result = await _maybe_await(db.executemany(stmt, parameter_sets))
        ctx.temp["batch_raw_results"] = result
        ctx.result = result
        return
    if statements is not None and hasattr(db, "executeloop"):
        result = await _maybe_await(db.executeloop(statements))
        ctx.temp["batch_raw_results"] = result
        ctx.result = result
        return
    raise NotImplementedError("batch execution requires executemany or executeloop")


class AtomImpl(Atom[Resolved, Operated, Exception]):
    name = "batch.execute"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
