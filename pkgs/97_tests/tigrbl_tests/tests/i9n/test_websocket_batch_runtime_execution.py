from __future__ import annotations

from tigrbl_atoms.atoms.batch import _scheduler
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture
from tigrbl_kernel.models import BatchOpPlan, HotOpPlan
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx


def test_websocket_runtime_seeds_packed_batch_policy_for_message_admission() -> None:
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="websocket",
                    path="/ws/items",
                    protocol="ws",
                    selector="/ws/items",
                )
            }
        },
    )
    ctx.op = "send_message"
    ctx.model = object
    ctx.transport_unit_kind = "websocket.message"
    ctx.transport_unit = {"type": "websocket.receive", "text": "hello"}
    ctx.payload_ref = {"text": "hello"}
    ctx.correlation_id = "ws-1"
    ctx.transport_sink = object()
    ctx.transport_sink_family = "websocket"

    PackedPlanExecutor._seed_batch_policy_from_hot_plan(
        ctx,
        HotOpPlan(
            batch=BatchOpPlan(
                enabled=True,
                max_queue_depth=32,
                overflow_policy="reject",
            )
        ),
    )
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)

    policy = _scheduler.policy_from_ctx(ctx)

    assert policy.enabled is True
    assert policy.max_queue_depth == 32
    assert policy.overflow_policy == "reject"
    assert ctx.temp["transport"]["unit_kind"] == "websocket.message"
    assert ctx.temp["intent"]["batch_policy"]["max_queue_depth"] == 32
