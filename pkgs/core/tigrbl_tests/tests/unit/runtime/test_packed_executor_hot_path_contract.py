from __future__ import annotations

import json
from collections import deque
from types import SimpleNamespace

import pytest

from tigrbl_runtime.channel.websocket import RuntimeWebSocket
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import _Ctx
from tigrbl_kernel.models import PackedKernel
from tigrbl_atoms.atoms.dispatch.binding_parse import _run as run_binding_parse
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

    def _counting_loads(payload: str):
        loads_calls.append(payload.encode("utf-8"))
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
