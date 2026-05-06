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
    ctx.temp["batch_parameter_sets"] = [
        admission.intent.get("payload_ref") for admission in group.admissions
    ]
    if "batch_statement" not in ctx.temp:
        ctx.temp["batch_statement"] = getattr(ctx, "batch_statement", None)
    if "batch_statements" not in ctx.temp:
        ctx.temp["batch_statements"] = getattr(ctx, "batch_statements", None)


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
