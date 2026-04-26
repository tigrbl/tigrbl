from __future__ import annotations

import pytest

from tigrbl_atoms.types import BootCtx, fail
from tigrbl_kernel.helpers import _run_chain


@pytest.mark.asyncio
async def test_run_chain_turns_failed_ctx_into_typed_error_branch() -> None:
    ctx = BootCtx()

    async def step(_ctx):
        return fail(_ctx, ValueError("bad branch"))

    with pytest.raises(ValueError, match="bad branch"):
        await _run_chain(ctx, [step], phase="HANDLER")

    assert ctx.error is not None
    assert ctx.error_phase == "ON_HANDLER_ERROR"
    assert ctx.temp["typed_err"].exc_type == "ValueError"
    assert ctx.temp["error_ctx"].failed_phase == "HANDLER"
