from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_kernel.models import PackedKernel
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import HotCtx, _Ctx


@pytest.mark.asyncio
async def test_websocket_fast_runner_accepts_before_waiting_for_payload() -> None:
    sent: list[dict[str, object]] = []
    receive_calls = 0

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    async def receive() -> dict[str, object]:
        nonlocal receive_calls
        receive_calls += 1
        if receive_calls == 1:
            return {"type": "websocket.connect"}
        assert sent and sent[0]["type"] == "websocket.accept"
        return {"type": "websocket.receive", "text": "hello"}

    async def endpoint(ws) -> None:
        text = await ws.receive_text()
        await ws.send_text(f"ws:{text}")
        await ws.close(code=1000)

    executor = PackedPlanExecutor()
    packed = PackedKernel()
    runner = executor._resolve_program_websocket_unary_text_runner(
        packed,
        0,
        SimpleNamespace(websocket_direct_endpoint=endpoint),
    )
    ctx = _Ctx()
    ctx.temp = {
        "hot_ctx": HotCtx(
            scope_type="websocket",
            path="/ws/echo",
            raw_receive=receive,
            raw_send=send,
        )
    }

    await runner(ctx)

    assert [message["type"] for message in sent] == [
        "websocket.accept",
        "websocket.send",
        "websocket.close",
    ]


@pytest.mark.asyncio
async def test_websocket_fast_runner_does_not_hang_when_client_disconnects_before_payload() -> None:
    sent: list[dict[str, object]] = []
    receive_calls = 0

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    async def receive() -> dict[str, object]:
        nonlocal receive_calls
        receive_calls += 1
        if receive_calls == 1:
            return {"type": "websocket.connect"}
        return {"type": "websocket.disconnect", "code": 1001}

    async def endpoint(ws) -> None:
        try:
            await ws.receive_text()
        except RuntimeError:
            await ws.close(code=1001)

    executor = PackedPlanExecutor()
    packed = PackedKernel()
    runner = executor._resolve_program_websocket_unary_text_runner(
        packed,
        0,
        SimpleNamespace(websocket_direct_endpoint=endpoint),
    )
    ctx = _Ctx()
    ctx.temp = {
        "hot_ctx": HotCtx(
            scope_type="websocket",
            path="/ws/echo",
            raw_receive=receive,
            raw_send=send,
        )
    }

    await runner(ctx)

    assert sent == [{"type": "websocket.accept"}]
