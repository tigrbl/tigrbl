from __future__ import annotations

from tigrbl_atoms.atoms.batch import _scheduler
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture
from tigrbl_kernel.models import BatchOpPlan, HotOpPlan
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx


def test_jsonrpc_runtime_seeds_packed_batch_policy_for_admission() -> None:
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="http",
                    method="POST",
                    path="/rpc",
                    protocol="http.jsonrpc",
                    selector="default:Widget.create",
                )
            }
        },
    )
    ctx.op = "create"
    ctx.model = object
    ctx.transport_unit_kind = "http.jsonrpc.request"
    ctx.transport_unit = {
        "jsonrpc": "2.0",
        "method": "Widget.create",
        "params": {"name": "Ada"},
        "id": 7,
    }
    ctx.payload_ref = ctx.transport_unit
    ctx.correlation_id = "rpc-7"
    ctx.transport_sink = object()
    ctx.transport_sink_family = "http.jsonrpc"

    PackedPlanExecutor._seed_batch_policy_from_hot_plan(
        ctx,
        HotOpPlan(
            batch=BatchOpPlan(
                enabled=True,
                max_size=2,
                result_fanout="by_admission",
            )
        ),
    )
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)

    policy = _scheduler.policy_from_ctx(ctx)

    assert policy.enabled is True
    assert policy.max_size == 2
    assert ctx.temp["intent"]["batch_policy"]["result_fanout"] == "by_admission"
    assert ctx.temp["transport"]["unit_kind"] == "http.jsonrpc.request"
