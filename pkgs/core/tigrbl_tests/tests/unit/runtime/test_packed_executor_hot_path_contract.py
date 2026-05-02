from __future__ import annotations

import json
from collections import deque
from types import SimpleNamespace

import pytest

from tigrbl_runtime.channel.websocket import RuntimeWebSocket
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx
from tigrbl_kernel.models import HotOpPlan, PackedKernel
from tigrbl_atoms.atoms.dispatch.binding_parse import _run as run_binding_parse
from tigrbl_atoms.atoms.dispatch.input_normalize import _run as run_input_normalize
from tigrbl_atoms.atoms.ingress.input_prepare import _run as run_input_prepare
from tigrbl_typing.status.exceptions import HTTPException


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


@pytest.mark.asyncio
async def test_packed_executor_compiled_param_runner_decodes_body_without_running_dispatch_atoms() -> None:
    executor = PackedPlanExecutor()
    calls: list[str] = []

    def _skipped_direct(_ctx):
        raise AssertionError("compiled param runner should skip ingress/dispatch/build atoms")

    def _handler_direct(ctx):
        calls.append("handler")
        ctx.result = {"ok": True}
        return ctx

    def _wrapped_skip(_ctx):
        raise AssertionError("wrapped skip step should not run")

    def _wrapped_validate(_ctx):
        raise AssertionError("compiled param runner should inline validate_in")

    def _wrapped_assemble(_ctx):
        raise AssertionError("compiled param runner should inline resolve.assemble")

    def _wrapped_handler(_ctx):
        return _handler_direct(_ctx)

    for step, direct in (
        (_wrapped_skip, _skipped_direct),
        (_wrapped_validate, _skipped_direct),
        (_wrapped_assemble, _skipped_direct),
        (_wrapped_handler, _handler_direct),
    ):
        setattr(step, "__tigrbl_direct_run", direct)
        setattr(step, "__tigrbl_use_two_args", False)
        setattr(step, "__tigrbl_has_direct_dep", False)
        setattr(step, "__tigrbl_direct_is_async", False)

    body = b'{"name":"Ada"}'
    hot_op_plan = HotOpPlan(
        program_id=0,
        alias="Widget.create",
        target="create",
        ordered_segment_ids=(0,),
        remaining_segment_ids=(),
        program_hot_runner_id=2,
        param_shape_id=0,
        transport_kind_id=1,
    )
    packed = PackedKernel(
        atom_catalog_opcode_ids=(0, 1, 2, 3),
        atom_opcode_keys=(
            "ingress.transport_extract",
            "wire.validate_in",
            "resolve.assemble",
            "handler.create",
        ),
        atom_catalog_async_flags=(False, False, False, False),
        phase_names=("PRE_HANDLER",),
        segment_catalog_offsets=(0,),
        segment_catalog_lengths=(4,),
        segment_catalog_atom_ids=(0, 1, 2, 3),
        segment_catalog_phase_ids=(0,),
        segment_catalog_executor_kinds=("sync.extractable",),
        segment_offsets=(0,),
        segment_lengths=(4,),
        segment_step_ids=(0, 1, 2, 3),
        segment_phases=("PRE_HANDLER",),
        segment_executor_kinds=("sync.extractable",),
        program_segment_ref_offsets=(0,),
        program_segment_ref_lengths=(1,),
        program_segment_refs=(0,),
        program_hot_runner_ids=(2,),
        program_param_shape_ids=(0,),
        program_transport_kind_ids=(1,),
        param_shape_offsets=(0,),
        param_shape_lengths=(1,),
        param_shape_source_masks=(1,),
        param_shape_slot_ids=(0,),
        param_shape_decoder_ids=(1,),
        param_shape_required_flags=(1,),
        param_shape_header_required_flags=(0,),
        param_shape_nullable_flags=(0,),
        param_shape_max_lengths=(0,),
        param_shape_lookup_hashes=(PackedPlanExecutor._stable_name_hash64("name"),),
        param_shape_header_hashes=(0,),
        step_table=(
            _wrapped_skip,
            _wrapped_validate,
            _wrapped_assemble,
            _wrapped_handler,
        ),
        hot_op_plans=(hot_op_plan,),
    )
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "body": body,
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="http",
                    method="POST",
                    path="/widgets",
                    protocol="http.rest",
                    selector="POST /widgets",
                    raw_scope={
                        "type": "http",
                        "method": "POST",
                        "path": "/widgets",
                        "headers": ((b"content-type", b"application/json"),),
                        "query_string": b"",
                    },
                    raw_headers=((b"content-type", b"application/json"),),
                )
            },
        },
    )
    ctx.opview = SimpleNamespace(
        schema_in=SimpleNamespace(fields=("name",), by_field={"name": {"required": True}})
    )

    await executor._resolve_program_runner(packed, 0, hot_op_plan)(ctx)

    temp = ctx.temp
    route = temp["route"]
    dispatch = temp["dispatch"]

    assert calls == ["handler"]
    assert ctx.phase == "PRE_HANDLER"
    assert ctx.result == {"ok": True}
    assert dict.__contains__(temp, "in_values") is False
    assert dict.__contains__(temp, "assembled_values") is False
    assert dict.__contains__(dispatch, "normalized_input") is False
    assert dict.__contains__(dispatch, "parsed_payload") is False
    assert dict.__contains__(route, "payload") is False

    assert dict(temp["in_values"]) == {"name": "Ada"}
    assert temp["in_present"] == ("name",)
    assert dict(ctx.payload) == {"name": "Ada"}
    assert dict(dispatch["normalized_input"]) == {"name": "Ada"}
    assert dict(dispatch["parsed_payload"]) == {"name": "Ada"}
    assert dict(route["payload"]) == {"name": "Ada"}
    assert temp["assembled_values"] == {"name": "Ada"}
    assert temp["virtual_in"] == {}


@pytest.mark.asyncio
async def test_packed_executor_compiled_param_runner_publishes_validation_errors_lazily() -> None:
    executor = PackedPlanExecutor()
    calls: list[str] = []

    def _handler_direct(ctx):
        calls.append("handler")
        ctx.result = {"ok": True}
        return ctx

    def _wrapped_handler(_ctx):
        return _handler_direct(_ctx)

    setattr(_wrapped_handler, "__tigrbl_direct_run", _handler_direct)
    setattr(_wrapped_handler, "__tigrbl_use_two_args", False)
    setattr(_wrapped_handler, "__tigrbl_has_direct_dep", False)
    setattr(_wrapped_handler, "__tigrbl_direct_is_async", False)

    hot_op_plan = HotOpPlan(
        program_id=0,
        alias="Widget.create",
        target="create",
        ordered_segment_ids=(0,),
        remaining_segment_ids=(),
        program_hot_runner_id=2,
        param_shape_id=0,
        transport_kind_id=1,
    )
    packed = PackedKernel(
        atom_catalog_opcode_ids=(0,),
        atom_opcode_keys=("handler.create",),
        atom_catalog_async_flags=(False,),
        phase_names=("PRE_HANDLER",),
        segment_catalog_offsets=(0,),
        segment_catalog_lengths=(1,),
        segment_catalog_atom_ids=(0,),
        segment_catalog_phase_ids=(0,),
        segment_catalog_executor_kinds=("sync.extractable",),
        segment_offsets=(0,),
        segment_lengths=(1,),
        segment_step_ids=(0,),
        segment_phases=("PRE_HANDLER",),
        segment_executor_kinds=("sync.extractable",),
        program_segment_ref_offsets=(0,),
        program_segment_ref_lengths=(1,),
        program_segment_refs=(0,),
        program_hot_runner_ids=(2,),
        program_param_shape_ids=(0,),
        program_transport_kind_ids=(1,),
        param_shape_offsets=(0,),
        param_shape_lengths=(1,),
        param_shape_source_masks=(1,),
        param_shape_slot_ids=(0,),
        param_shape_decoder_ids=(1,),
        param_shape_required_flags=(1,),
        param_shape_header_required_flags=(0,),
        param_shape_nullable_flags=(0,),
        param_shape_max_lengths=(0,),
        param_shape_lookup_hashes=(PackedPlanExecutor._stable_name_hash64("name"),),
        param_shape_header_hashes=(0,),
        step_table=(_wrapped_handler,),
        hot_op_plans=(hot_op_plan,),
    )
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="http",
                    method="POST",
                    path="/widgets",
                    protocol="http.rest",
                    selector="POST /widgets",
                )
            },
        },
    )
    ctx.opview = SimpleNamespace(
        schema_in=SimpleNamespace(fields=("name",), by_field={"name": {"required": True}})
    )

    with pytest.raises(HTTPException) as excinfo:
        await executor._resolve_program_runner(packed, 0, hot_op_plan)(ctx)

    assert excinfo.value.status_code == 422
    assert calls == []
    assert dict.__contains__(ctx.temp, "in_errors") is False
    assert ctx.temp["in_invalid"] is True
    assert ctx.temp["in_errors"] == [
        {
            "field": "name",
            "code": "required",
            "message": "Field is required but was not provided.",
        }
    ]
