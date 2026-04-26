from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...types import normalize_typed_err

ANCHOR = _ev.ERR_CLASSIFY


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    err = getattr(ctx, "error", None)
    if err is None:
        return
    typed = normalize_typed_err(err, ctx=ctx)
    setattr(ctx, "typed_error", typed)
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        temp["typed_err"] = typed


__all__ = ["ANCHOR", "run"]
