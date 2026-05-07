from __future__ import annotations

from tigrbl_atoms.atoms.batch import _scheduler
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture
from tigrbl_kernel.models import BatchOpPlan, HotOpPlan
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx


def test_http_stream_runtime_seeds_packed_batch_policy_for_chunk_admission() -> None:
    chunk = memoryview(b"stream-chunk-1")
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="http",
                    method="POST",
                    path="/stream",
                    protocol="http.stream",
                    selector="POST /stream",
                    body_view=chunk,
                )
            }
        },
    )
    ctx.op = "append_chunk"
    ctx.model = object
    ctx.transport_unit_kind = "http.stream.chunk"
    ctx.transport_unit = chunk
    ctx.payload_ref = chunk
    ctx.correlation_id = "stream-1"
    ctx.transport_sink = object()
    ctx.transport_sink_family = "http.stream"

    PackedPlanExecutor._seed_batch_policy_from_hot_plan(
        ctx,
        HotOpPlan(
            batch=BatchOpPlan(
                enabled=True,
                max_size=8,
                max_bytes=4096,
            )
        ),
    )
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)

    policy = _scheduler.policy_from_ctx(ctx)

    assert policy.enabled is True
    assert policy.max_size == 8
    assert policy.max_bytes == 4096
    assert ctx.temp["transport"]["payload_bytes"] == len(chunk)
    assert ctx.temp["intent"]["batch_policy"]["enabled"] is True
