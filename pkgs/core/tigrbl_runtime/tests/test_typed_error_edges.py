from __future__ import annotations

import pytest

from tigrbl_runtime.executors.invoke import _invoke
from tigrbl_runtime.executors.types import _Ctx


class _Db:
    def __init__(self) -> None:
        self.rolled_back = False

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.mark.asyncio
async def test_invoke_builds_error_ctx_for_raised_phase_exception() -> None:
    ctx = _Ctx()
    db = _Db()
    seen = []

    async def boom(_ctx):
        raise RuntimeError("phase exploded")

    async def on_error(_ctx):
        seen.append(_ctx.temp["error_ctx"])

    with pytest.raises(Exception):
        await _invoke(
            request=None,
            db=db,
            phases={
                "PRE_HANDLER": [boom],
                "ON_PRE_HANDLER_ERROR": [on_error],
            },
            ctx=ctx,
        )

    assert db.rolled_back is True
    assert seen
    assert seen[0].failed_phase == "PRE_HANDLER"
    assert seen[0].rollback_required is True
    assert seen[0].err_target.kind == "rollback"
    assert ctx.error_phase == "ON_PRE_HANDLER_ERROR"
