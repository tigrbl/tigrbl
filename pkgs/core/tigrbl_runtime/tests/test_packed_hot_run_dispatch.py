from __future__ import annotations

import pytest

from tigrbl_kernel.models import PackedKernel
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import _Ctx


@pytest.mark.asyncio
async def test_generic_segment_runner_prefers_direct_hot_run_over_wrapper() -> None:
    calls: list[str] = []

    def wrapper(ctx):
        calls.append("wrapper")
        ctx.wrapper_called = True

    def direct(_obj, ctx):
        calls.append("direct")
        ctx.direct_called = True

    setattr(wrapper, "__tigrbl_direct_run", direct)
    setattr(wrapper, "__tigrbl_use_two_args", True)
    setattr(wrapper, "__tigrbl_has_direct_dep", False)
    setattr(wrapper, "__tigrbl_direct_is_async", False)

    packed = PackedKernel(
        step_table=(wrapper,),
        segment_catalog_offsets=(0,),
        segment_catalog_lengths=(1,),
        segment_catalog_atom_ids=(0,),
        segment_catalog_executor_kinds=("mixed",),
        atom_catalog_async_flags=(False,),
        segment_phases=("PRE_TX_BEGIN",),
    )
    executor = PackedPlanExecutor()
    ctx = _Ctx()

    await executor._resolve_segment_runners(packed)[0](ctx)

    assert calls == ["direct"]
    assert ctx.direct_called is True
    assert ctx.wrapper_called is None
