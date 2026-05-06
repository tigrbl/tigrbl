from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Failed
from ...types import Atom, Ctx, FailedCtx

ANCHOR = _ev.ERR_CTX_BUILD


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    admission = ctx.temp.get("batch_admission")
    if admission is not None:
        ctx.temp.setdefault("batch_rejections", []).append(admission.admission_id)


class AtomImpl(Atom[Failed, Failed, Exception]):
    name = "batch.reject_admission"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Failed]) -> Ctx[Failed]:
        _run(obj, ctx)
        return ctx.promote(FailedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
