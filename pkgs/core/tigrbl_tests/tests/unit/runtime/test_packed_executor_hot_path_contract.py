from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from types import SimpleNamespace

import pytest

from tigrbl_kernel import build_kernel_plan
from tigrbl_runtime.channel.websocket import RuntimeWebSocket
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx
from tigrbl_kernel.models import HotOpPlan, PackedKernel
from tigrbl_atoms.atoms.dispatch.binding_parse import _run as run_binding_parse
from tigrbl_atoms.atoms.dispatch.input_normalize import _run as run_input_normalize
from tigrbl_atoms.atoms.ingress.input_prepare import _run as run_input_prepare
from tigrbl_typing.status.exceptions import HTTPException
from tests.perf.helper_websocket_apps import create_tigrbl_websocket_transport_app


def test_packed_executor_primes_exact_rest_route_before_ingress_probe() -> None:
    executor = PackedPlanExecutor()
    ctx = _Ctx.ensure(request=None, db=None, seed={})
    env = SimpleNamespace(
        scope={"type": "http", "method": "POST", "path": "/widgets", "scheme": "http"}
    )
    packed = PackedKernel(
        proto_to_id={"http.rest": 0},
        selector_to_id={"POST /widgets": 0},
        hot_block_view={
            "exact_method_ids": (PackedPlanExecutor._http_method_id("POST"),),
            "exact_path_hashes": (PackedPlanExecutor._stable_name_hash64("/widgets"),),
            "exact_program_ids": (7,),
        },
    )

    program_id = executor._prime_exact_route_program(ctx, env, packed)

    assert program_id == 7
    assert ctx.temp["program_id"] == 7
    assert dict.__contains__(ctx.temp, "dispatch") is False
    assert dict.__contains__(ctx.temp, "route") is False
    hot = ctx.temp["hot_ctx"]
    assert hot.dispatch_binding_protocol == "http.rest"
    assert hot.dispatch_binding_selector == "POST /widgets"
    assert hot.route_program_id == 7
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


def test_websocket_transport_route_compiles_to_fast_runner() -> None:
    app = create_tigrbl_websocket_transport_app(Path("dummy.sqlite3"))
    packed = build_kernel_plan(app).packed
    assert packed is not None

    hot_op_plan = packed.hot_op_plans[0]

    assert hot_op_plan.program_hot_runner_id == 3
    assert hot_op_plan.websocket_path == "/ws/echo"
    assert hot_op_plan.websocket_protocol == "ws"
    assert hot_op_plan.websocket_framing == "text"
    assert callable(hot_op_plan.websocket_direct_endpoint)


def test_packed_executor_skips_channel_prelude_for_exact_websocket_fast_runner() -> None:
    app = create_tigrbl_websocket_transport_app(Path("dummy.sqlite3"))
    plan = build_kernel_plan(app)
    packed = plan.packed
    assert packed is not None

    executor = PackedPlanExecutor()
    ctx = _Ctx.ensure(request=None, db=None, seed={"temp": {}})
    env = SimpleNamespace(
        scope={"type": "websocket", "scheme": "ws", "path": "/ws/echo"}
    )

    assert (
        executor.should_skip_channel_prelude(
            runtime=SimpleNamespace(),
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed,
        )
        is True
    )
    assert ctx.temp["program_id"] == 0


@pytest.mark.asyncio
async def test_packed_executor_websocket_fast_runner_accepts_receives_sends_and_closes() -> None:
    app = create_tigrbl_websocket_transport_app(Path("dummy.sqlite3"))
    packed = build_kernel_plan(app).packed
    assert packed is not None
    hot_op_plan = packed.hot_op_plans[0]

    received = deque(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": "hello"},
        ]
    )
    sent: list[dict[str, object]] = []

    async def _receive() -> dict[str, object]:
        return received.popleft() if received else {"type": "websocket.disconnect", "code": 1000}

    async def _send(message: dict[str, object]) -> None:
        sent.append(dict(message))

    executor = PackedPlanExecutor()
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="websocket",
                    path="/ws/echo",
                    protocol="ws",
                    selector="/ws/echo",
                    raw_receive=_receive,
                    raw_send=_send,
                    path_params={},
                )
            }
        },
    )

    await executor._resolve_program_runner(packed, 0, hot_op_plan)(ctx)

    assert ctx.phase == "HANDLER"
    assert ctx.result == "hello"
    assert dict.__contains__(ctx.temp, "route") is False
    assert dict.__contains__(ctx.temp, "dispatch") is False
    assert dict.__contains__(ctx.temp, "egress") is False
    assert sent == [
        {"type": "websocket.accept"},
        {"type": "websocket.send", "text": "hello"},
        {"type": "websocket.close", "code": 1000},
    ]


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

    def _wrapped_phase_db(_ctx):
        raise AssertionError("compiled param runner should skip SYS_PHASE_DB_BIND")

    def _wrapped_validate(_ctx):
        raise AssertionError("compiled param runner should inline validate_in")

    def _wrapped_assemble(_ctx):
        raise AssertionError("compiled param runner should inline resolve.assemble")

    def _wrapped_handler(_ctx):
        return _handler_direct(_ctx)

    for step, direct in (
        (_wrapped_skip, _skipped_direct),
        (_wrapped_phase_db, _skipped_direct),
        (_wrapped_validate, _skipped_direct),
        (_wrapped_assemble, _skipped_direct),
        (_wrapped_handler, _handler_direct),
    ):
        setattr(step, "__tigrbl_direct_run", direct)
        setattr(step, "__tigrbl_use_two_args", False)
        setattr(step, "__tigrbl_has_direct_dep", False)
        setattr(step, "__tigrbl_direct_is_async", False)
    setattr(_wrapped_skip, "__tigrbl_skip_in_compiled_param", True)
    setattr(_wrapped_phase_db, "__tigrbl_skip_in_compiled_param", True)
    setattr(_wrapped_validate, "__tigrbl_skip_in_compiled_param", True)
    setattr(_wrapped_assemble, "__tigrbl_skip_in_compiled_param", True)

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
        atom_catalog_opcode_ids=(0, 1, 2, 3, 4),
        atom_opcode_keys=(
            "step.skip",
            "step.phase_db",
            "step.validate",
            "step.assemble",
            "handler.create",
        ),
        atom_catalog_async_flags=(False, False, False, False, False),
        phase_names=("PRE_HANDLER",),
        segment_catalog_offsets=(0,),
        segment_catalog_lengths=(5,),
        segment_catalog_atom_ids=(0, 1, 2, 3, 4),
        segment_catalog_phase_ids=(0,),
        segment_catalog_executor_kinds=("sync.extractable",),
        segment_offsets=(0,),
        segment_lengths=(5,),
        segment_step_ids=(0, 1, 2, 3, 4),
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
            _wrapped_phase_db,
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
    hot = temp["hot_ctx"]

    assert calls == ["handler"]
    assert ctx.phase == "PRE_HANDLER"
    assert ctx.result == {"ok": True}
    assert hot.body_hashed_items is None
    assert hot.query_hashed_spans is None
    assert hot.header_hashed_pairs is None
    assert dict.__contains__(temp, "route") is False
    assert dict.__contains__(temp, "dispatch") is False
    assert dict.__contains__(temp, "in_values") is False
    assert dict.__contains__(temp, "assembled_values") is False
    route = temp["route"]
    dispatch = temp["dispatch"]
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
async def test_packed_executor_compiled_param_runner_specializes_jsonrpc_body_only_params() -> None:
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

    body = b'{"jsonrpc":"2.0","method":"Widget.create","params":{"name":"Ada"},"id":7}'
    hot_op_plan = HotOpPlan(
        program_id=0,
        alias="Widget.create",
        target="create",
        ordered_segment_ids=(0,),
        remaining_segment_ids=(),
        program_hot_runner_id=2,
        param_shape_id=0,
        transport_kind_id=2,
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
        program_transport_kind_ids=(2,),
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
            "body": body,
            "temp": {
                "hot_ctx": HotCtx(
                    scope_type="http",
                    method="POST",
                    path="/rpc",
                    protocol="http.jsonrpc",
                    selector="Widget.create",
                    raw_scope={
                        "type": "http",
                        "method": "POST",
                        "path": "/rpc",
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
    hot = temp["hot_ctx"]

    assert calls == ["handler"]
    assert dict.__contains__(temp, "jsonrpc_request_id") is False
    assert temp["jsonrpc_request_id"] == 7
    assert temp["dispatch"]["rpc_method"] == "Widget.create"
    assert temp["route"]["rpc_envelope"]["id"] == 7
    assert hot.body_hashed_items is None
    assert hot.query_hashed_spans is None
    assert hot.header_hashed_pairs is None
    assert dict(temp["in_values"]) == {"name": "Ada"}
    assert temp["assembled_values"] == {"name": "Ada"}
    assert ctx.result == {"ok": True}


def test_hot_namespace_lazy_publication_and_write_through_syncs_hot_ctx() -> None:
    hot = HotCtx(
        scope_type="http",
        method="POST",
        path="/widgets",
        protocol="http.rest",
        selector="POST /widgets",
        route_protocol="http.rest",
        route_selector="POST /widgets",
        dispatch_binding_protocol="http.rest",
        dispatch_binding_selector="POST /widgets",
    )
    ctx = _Ctx.ensure(request=None, db=None, seed={"temp": {"hot_ctx": hot}})
    temp = ctx.temp

    assert dict.__contains__(temp, "route") is False
    assert dict.__contains__(temp, "dispatch") is False
    assert dict.__contains__(temp, "egress") is False

    route = temp["route"]
    dispatch = temp["dispatch"]
    egress = temp["egress"]

    route["short_circuit"] = True
    route["method_not_allowed"] = True
    route["path_params"] = {"item_id": "7"}
    dispatch["binding_protocol"] = "http.jsonrpc"
    dispatch["binding_selector"] = "Widget.create"
    dispatch["rpc"] = {"jsonrpc": "2.0", "method": "Widget.create", "id": 7}
    egress["transport_response"] = {"status_code": 202}
    temp["jsonrpc_request_id"] = 7

    assert hot.route_short_circuit is True
    assert hot.route_method_not_allowed is True
    assert hot.route_path_params == {"item_id": "7"}
    assert hot.dispatch_binding_protocol == "http.jsonrpc"
    assert hot.dispatch_binding_selector == "Widget.create"
    assert hot.dispatch_rpc_method == "Widget.create"
    assert hot.dispatch_jsonrpc_request_id == 7
    assert hot.egress_transport_response == {"status_code": 202}


@pytest.mark.asyncio
async def test_execute_packed_uses_hot_method_not_allowed_without_route_dict(monkeypatch) -> None:
    executor = PackedPlanExecutor()
    sent: list[tuple[int, dict[str, object]]] = []

    async def _send_json(_env, status, payload, headers=None):
        del headers
        sent.append((status, dict(payload)))

    async def _send_transport_response(_env, _ctx):
        raise AssertionError("transport response should not send for method_not_allowed")

    async def _probe(*_args, **_kwargs):
        return -1

    monkeypatch.setattr(
        executor, "_resolve_transport_senders", lambda: (_send_json, _send_transport_response)
    )
    monkeypatch.setattr(executor, "_require_program_id_from_ctx", lambda _ctx: -1)
    monkeypatch.setattr(executor, "_prime_exact_route_program", lambda *_args: -1)
    monkeypatch.setattr(executor, "_prime_exact_websocket_program", lambda *_args: -1)
    monkeypatch.setattr(executor, "_probe_ingress_for_program", _probe)

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
                    route_method_not_allowed=True,
                )
            }
        },
    )
    env = SimpleNamespace(scope={"type": "http", "method": "POST", "path": "/widgets"})

    await executor._execute_packed(env, ctx, SimpleNamespace(opmeta=()), PackedKernel())

    assert dict.__contains__(ctx.temp, "route") is False
    assert sent == [(405, {"detail": "Method Not Allowed"})]


@pytest.mark.asyncio
async def test_execute_packed_uses_hot_short_circuit_transport_without_namespace_dicts(
    monkeypatch,
) -> None:
    executor = PackedPlanExecutor()
    sent: list[str] = []

    async def _send_json(_env, _status, _payload, headers=None):
        del headers
        raise AssertionError("short circuit should not go through JSON send")

    async def _send_transport_response(_env, _ctx):
        sent.append("transport")

    async def _runner(_ctx):
        return None

    monkeypatch.setattr(
        executor, "_resolve_transport_senders", lambda: (_send_json, _send_transport_response)
    )
    monkeypatch.setattr(executor, "_require_program_id_from_ctx", lambda _ctx: 0)
    monkeypatch.setattr(executor, "_resolve_program_hot_runner_id", lambda *_args: 0)
    monkeypatch.setattr(executor, "_resolve_program_runner", lambda *_args: _runner)
    monkeypatch.setattr(executor, "_resolve_db_acquire", lambda *_args: (lambda _ctx: (None, None)))
    monkeypatch.setattr(executor, "_resolve_error_segments", lambda *_args: {})

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
                    route_short_circuit=True,
                    egress_transport_response={"status_code": 202},
                )
            }
        },
    )
    env = SimpleNamespace(scope={"type": "http", "method": "POST", "path": "/widgets"})
    plan = SimpleNamespace(opmeta=[SimpleNamespace(model=None, alias="widgets.create", target="create")])

    await executor._execute_packed(env, ctx, plan, PackedKernel())

    assert dict.__contains__(ctx.temp, "route") is False
    assert dict.__contains__(ctx.temp, "egress") is False
    assert sent == ["transport"]


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


@pytest.mark.asyncio
async def test_packed_executor_compiled_param_runner_rejects_sync_step_returning_awaitable() -> None:
    executor = PackedPlanExecutor()

    async def _late_value():
        return None

    def _bad_sync_direct(_ctx):
        return _late_value()

    setattr(_bad_sync_direct, "__tigrbl_direct_is_async", False)

    def _wrapped_handler(_ctx):
        return _bad_sync_direct(_ctx)

    setattr(_wrapped_handler, "__tigrbl_direct_run", _bad_sync_direct)
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
        param_shape_id=-1,
        transport_kind_id=1,
    )
    packed = PackedKernel(
        atom_catalog_opcode_ids=(0,),
        atom_opcode_keys=("handler.create",),
        atom_catalog_async_flags=(False,),
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
        program_hot_runner_ids=(2,),
        program_param_shape_ids=(-1,),
        program_transport_kind_ids=(1,),
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
            }
        },
    )

    with pytest.raises(RuntimeError, match="sync compiled step returned awaitable"):
        await executor._resolve_program_runner(packed, 0, hot_op_plan)(ctx)
