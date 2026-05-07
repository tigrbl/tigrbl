from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Executing
from ...types import Atom, Ctx, ExecutingCtx

ANCHOR = _ev.BATCH_PREPARE_EXECUTE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    group = ctx.temp.get("batch_group")
    if group is None:
        return
    if ctx.temp.get("batch_execution_kind") == "scalar_fallback":
        group.fallback = True
        group.fallback_reason = str(ctx.temp.get("batch_fallback_reason") or "")
        return

    explicit_stmt = ctx.temp.get("batch_statement", getattr(ctx, "batch_statement", None))
    explicit_statements = ctx.temp.get(
        "batch_statements", getattr(ctx, "batch_statements", None)
    )
    parameter_sets = [
        admission.intent.get("payload_ref") for admission in group.admissions
    ]
    if explicit_stmt is not None:
        ctx.temp["batch_execution_kind"] = "executemany"
        ctx.temp["batch_statement"] = explicit_stmt
        ctx.temp["batch_parameter_sets"] = parameter_sets
        return
    if explicit_statements is not None:
        ctx.temp["batch_execution_kind"] = "executeloop"
        ctx.temp["batch_statements"] = explicit_statements
        return

    statements = [admission.intent.get("statement") for admission in group.admissions]
    if any(statement is None for statement in statements):
        ctx.temp["batch_execution_kind"] = "unsupported"
        ctx.temp["batch_unsupported_reason"] = "missing_statement"
        return

    first = statements[0] if statements else None
    if statements and all(statement == first for statement in statements):
        ctx.temp["batch_execution_kind"] = "executemany"
        ctx.temp["batch_statement"] = first
        ctx.temp["batch_parameter_sets"] = parameter_sets
        return

    ctx.temp["batch_execution_kind"] = "executeloop"
    ctx.temp["batch_statements"] = list(zip(statements, parameter_sets))


class AtomImpl(Atom[Executing, Executing, Exception]):
    name = "batch.prepare_execute"
    anchor = ANCHOR

    async def __call__(
        self, obj: object | None, ctx: Ctx[Executing]
    ) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
