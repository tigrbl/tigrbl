from __future__ import annotations

import json
from collections import deque
from types import SimpleNamespace

import pytest

from tigrbl_runtime.channel.websocket import RuntimeWebSocket
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import _Ctx
from tigrbl_kernel.models import HotOpPlan, PackedKernel
from tigrbl_atoms.atoms.dispatch.binding_parse import _run as run_binding_parse
from tigrbl_atoms.atoms.dispatch.input_normalize import _run as run_input_normalize
from tigrbl_atoms.atoms.ingress.input_prepare import _run as run_input_prepare


def test_packed_executor_primes_exact_rest_route_before_ingress_probe() -> None:
    executor = PackedPlanExecutor()
    ctx = _Ctx.ensure(request=None, db=None, seed={})
    env = SimpleNamespace(
        scope={"type": "http", "method": "POST", "path": "/widgets", "scheme": "http"}
    )
    packed = PackedKernel(
        proto_to_id={"http.rest": 0},
        selector_to_id={"POST /widgets": 0},
        rest_exact_route_to_program={("POST", "/widgets"): 7},
    )

    program_id = executor._prime_exact_route_program(ctx, env, packed)

    assert program_id == 7
    assert ctx.temp["program_id"] == 7
    assert ctx.temp["dispatch"]["binding_protocol"] == "http.rest"
    assert ctx.temp["dispatch"]["binding_selector"] == "POST /widgets"
    assert ctx.temp["route"]["program_id"] == 7


def test_ingress_and_dispatch_reuse_cached_json_parse(monkeypatch) -> None:
    loads_calls: list[bytes] = []
    original_loads = json.loads

    def _counting_loads(payload: str | bytes | bytearray):
        if isinstance(payload, str):
            loads_calls.append(payload.encode("utf-8"))
        else:
            loads_calls.append(bytes(payload))
        return original_loads(payload)

    monkeypatch.setattr(json, "loads", _counting_loads)

    body = b'{"name":"Ada"}'
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "body": body,
            "headers": {"content-type": "application/json"},
            "temp": {"dispatch": {"binding_protocol": "http.rest"}},
        },
    )

    run_input_prepare(None, ctx)
    run_binding_parse(None, ctx)

    assert len(loads_calls) == 1
    assert ctx.temp["hot"]["parsed_json"] == {"name": "Ada"}
    assert ctx.temp["dispatch"]["parsed_payload"] == {"name": "Ada"}


def test_input_prepare_primes_request_json_cache() -> None:
    request = SimpleNamespace(_json_cache=None, _json_loaded=False, body=None)
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "body": b'{"name":"Ada"}',
            "headers": {"content-type": "application/json"},
            "request": request,
            "temp": {},
        },
    )

    run_input_prepare(None, ctx)

    assert request._json_loaded is True
    assert request._json_cache == {"name": "Ada"}


def test_rest_binding_and_normalize_reuse_body_only_json_mapping() -> None:
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "body": b'{"name":"Ada"}',
            "headers": {"content-type": "application/json"},
            "temp": {"dispatch": {"binding_protocol": "http.rest"}},
        },
    )

    run_input_prepare(None, ctx)
    run_binding_parse(None, ctx)
    run_input_normalize(None, ctx)

    parsed = ctx.temp["hot"]["parsed_json"]
    assert ctx.temp["dispatch"]["parsed_payload"] is parsed
    assert ctx.temp["dispatch"]["normalized_input"] is parsed
    assert ctx.payload is parsed


@pytest.mark.asyncio
async def test_runtime_websocket_receive_uses_fifo_queue() -> None:
    channel = SimpleNamespace(
        path="/ws",
        path_params={},
        state={
            "receive_queue": deque(
                [
                    {"type": "websocket.receive", "text": "first"},
                    {"type": "websocket.receive", "text": "second"},
                ]
            )
        },
        send=None,
        receive=None,
    )
    websocket = RuntimeWebSocket(channel)

    first = await websocket.receive_text()
    second = await websocket.receive_text()

    assert first == "first"
    assert second == "second"


@pytest.mark.asyncio
async def test_packed_executor_uses_compiled_linear_direct_runner() -> None:
    executor = PackedPlanExecutor()
    calls: list[str] = []

    def _direct_run(ctx):
        calls.append("direct")
        ctx.result = {"ok": True}
        return ctx

    def _wrapped_step(_ctx):
        raise AssertionError("wrapped step should not run when direct runner is selected")

    setattr(_wrapped_step, "__tigrbl_direct_run", _direct_run)
    setattr(_wrapped_step, "__tigrbl_use_two_args", False)
    setattr(_wrapped_step, "__tigrbl_has_direct_dep", False)

    hot_op_plan = HotOpPlan(
        program_id=0,
        alias="Widget.create",
        target="create",
        ordered_segment_ids=(0,),
        remaining_segment_ids=(),
        program_hot_runner_id=1,
    )
    packed = PackedKernel(
        phase_names=("HANDLER",),
        segment_catalog_offsets=(0,),
        segment_catalog_lengths=(1,),
        segment_catalog_atom_ids=(0,),
        segment_catalog_phase_ids=(0,),
        segment_catalog_executor_kinds=("sync.extractable",),
        segment_offsets=(0,),
        segment_lengths=(1,),
        segment_step_ids=(0,),
        segment_phases=("HANDLER",),
        segment_executor_kinds=("sync.extractable",),
        program_segment_ref_offsets=(0,),
        program_segment_ref_lengths=(1,),
        program_segment_refs=(0,),
        program_hot_runner_ids=(1,),
        atom_catalog_async_flags=(False,),
        step_async_flags=(False,),
        step_table=(_wrapped_step,),
        hot_op_plans=(hot_op_plan,),
    )
    ctx = _Ctx.ensure(request=None, db=None, seed={})

    await executor._resolve_program_runner(packed, 0, hot_op_plan)(ctx)

    assert calls == ["direct"]
    assert ctx.phase == "HANDLER"
    assert ctx.result == {"ok": True}
