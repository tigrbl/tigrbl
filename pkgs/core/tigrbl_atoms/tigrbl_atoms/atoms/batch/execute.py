from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Resolved, Operated
from ...types import Atom, Ctx, OperatedCtx
from ..sys import _oltp_context as _ctx
from . import _scheduler

ANCHOR = _ev.BATCH_EXECUTE


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_group") is None:
        return
    db = _ctx.db(ctx)
    policy = _scheduler.policy_from_ctx(ctx)
    kind = ctx.temp.get("batch_execution_kind")
    if kind == "unsupported":
        _handle_unsupported(ctx, str(ctx.temp.get("batch_unsupported_reason") or "unsupported"))
        return
    stmt = ctx.temp.get("batch_statement")
    parameter_sets = ctx.temp.get("batch_parameter_sets")
    statements = ctx.temp.get("batch_statements")
    if kind in {None, "executemany"} and stmt is not None and parameter_sets is not None and hasattr(db, "executemany"):
        result = await _maybe_await(db.executemany(stmt, parameter_sets))
        ctx.temp["batch_raw_results"] = result
        ctx.result = result
        return
    if kind in {None, "executeloop"} and statements is not None and hasattr(db, "executeloop"):
        result = await _maybe_await(db.executeloop(statements))
        ctx.temp["batch_raw_results"] = result
        ctx.result = result
        return
    unsupported = "unsupported_executemany" if kind == "executemany" else "unsupported_executeloop"
    if policy.conflict_policy == "reject":
        raise NotImplementedError(unsupported)
    _handle_unsupported(ctx, unsupported)


def _handle_unsupported(ctx: Any, reason: str) -> None:
    group = ctx.temp.get("batch_group")
    if group is not None:
        group.fallback = True
        group.fallback_reason = reason
    ctx.temp["batch_execution_kind"] = "scalar_fallback"
    ctx.temp["batch_fallback_reason"] = reason


class AtomImpl(Atom[Resolved, Operated, Exception]):
    name = "batch.execute"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
