from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


@pytest.mark.asyncio
async def test_emit_complete_fires_only_after_transport_acknowledges_send() -> None:
    emit_with_fence = _require("tigrbl_runtime.protocol.completion_fence", "emit_with_fence")
    trace: list[str] = []

    async def send(_message: object) -> str:
        trace.append("send-called")
        return "ack"

    result = await emit_with_fence(
        {"subevent": "message.emit", "payload": b"ready"},
        send=send,
        trace=trace.append,
    )

    assert trace == ["send-called", "message.emit_complete"]
    assert result["completion_fence"] == "POST_EMIT"


@pytest.mark.asyncio
@pytest.mark.parametrize("send_result", ("queued", "scheduled", "buffered"))
async def test_queued_or_scheduled_send_is_not_emit_complete(send_result: str) -> None:
    emit_with_fence = _require("tigrbl_runtime.protocol.completion_fence", "emit_with_fence")
    trace: list[str] = []

    async def send(_message: object) -> str:
        return send_result

    result = await emit_with_fence(
        {"subevent": "message.emit", "payload": b"ready"},
        send=send,
        trace=trace.append,
    )

    assert "message.emit_complete" not in trace
    assert result["completed"] is False


@pytest.mark.asyncio
async def test_failed_send_routes_to_error_without_emit_complete() -> None:
    emit_with_fence = _require("tigrbl_runtime.protocol.completion_fence", "emit_with_fence")
    trace: list[str] = []

    async def send(_message: object) -> str:
        raise RuntimeError("transport failed")

    result = await emit_with_fence(
        {"subevent": "message.emit", "payload": b"ready"},
        send=send,
        trace=trace.append,
    )

    assert "message.emit_complete" not in trace
    assert result["error_ctx"]["subevent"] == "message.emit"

