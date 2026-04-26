from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...types import build_error_ctx

ANCHOR = _ev.ERR_CTX_BUILD


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    err = getattr(ctx, "error", None)
    if err is None:
        return
    existing = getattr(ctx, "error_ctx", None)
    if existing is not None:
        return
    build_error_ctx(ctx, err, failed_phase=getattr(ctx, "phase", None))


__all__ = ["ANCHOR", "run"]
