from __future__ import annotations

from typing import Any

from ... import events as _ev
from tigrbl_atoms.atoms.sys._db import _resolve_db_handle

ANCHOR = _ev.ERR_ROLLBACK


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    err = getattr(ctx, "error", None)
    if err is not None and getattr(ctx, "error_ctx", None) is None:
        try:
            from ...types import build_error_ctx

            build_error_ctx(
                ctx,
                err,
                failed_phase=getattr(ctx, "phase", None),
                rollback_required=True,
            )
        except Exception:
            pass
    db = _resolve_db_handle(ctx)
    if db is None:
        return

    rollback = getattr(db, "rollback", None)
    if callable(rollback):
        rv = rollback()
        if hasattr(rv, "__await__"):
            await rv

    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        release = temp.pop("__sys_db_release__", None)
        if callable(release):
            release()


__all__ = ["ANCHOR", "run"]
