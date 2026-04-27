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


def test_sse_chain_declares_session_message_stream_and_completion_subevents() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.sse", "compile_sse_chain")

    chain = compile_chain({"path": "/events", "heartbeat_seconds": 15})
    subevents = tuple(chain["subevents"])

    assert subevents[:2] == ("session.open", "stream.start")
    assert "message.emit" in subevents
    assert "heartbeat.emit" in subevents
    assert subevents[-2:] == ("stream.end", "session.close")
    assert chain["completion_fence"] == "POST_EMIT"


def test_sse_chain_orders_heartbeat_without_draining_message_stream() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.sse", "compile_sse_chain")

    chain = compile_chain({"path": "/events", "heartbeat_seconds": 15})

    assert chain["heartbeat"]["subevent"] == "heartbeat.emit"
    assert chain["heartbeat"]["producer"] == "timer"
    assert chain["heartbeat"]["drains_message_producer"] is False


def test_sse_chain_declares_error_branch_and_disconnect_finalization() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.sse", "compile_sse_chain")

    chain = compile_chain({"path": "/events", "heartbeat_seconds": 15})

    assert "disconnect" in chain["break_conditions"]
    assert chain["err_target"] in {"transport.close", "stream.end", "session.close"}
    assert chain["error_ctx"]["binding"] == "http.sse"
    assert chain["error_ctx"]["family"] in {"event_stream", "stream"}


@pytest.mark.asyncio
async def test_sse_lazy_runtime_does_not_prebuffer_iterator() -> None:
    run_sse = _require("tigrbl_runtime.protocol.sse", "run_sse_chain")
    produced: list[int] = []

    async def events():
        for idx in range(1000):
            produced.append(idx)
            yield {"event": "item", "data": str(idx)}

    sent: list[dict[str, object]] = []
    result = await run_sse({"producer": events(), "send": sent.append, "stop_after": 2})

    assert produced == [0, 1]
    assert len([message for message in sent if message["type"] == "http.response.body"]) == 2
    assert result["lazy"] is True


@pytest.mark.asyncio
async def test_sse_lazy_runtime_accepts_sync_iterators() -> None:
    run_sse = _require("tigrbl_runtime.protocol.sse", "run_sse_chain")

    sent: list[dict[str, object]] = []
    result = await run_sse(
        {
            "producer": iter(({"event": "item", "data": "1"}, {"event": "item", "data": "2"})),
            "send": sent.append,
        }
    )

    assert result["lazy"] is True
    assert [message["type"] for message in sent].count("http.response.body") == 2


@pytest.mark.asyncio
async def test_sse_lazy_runtime_rejects_invalid_event_before_emit() -> None:
    run_sse = _require("tigrbl_runtime.protocol.sse", "run_sse_chain")

    async def events():
        yield {"data": object()}

    sent: list[dict[str, object]] = []

    with pytest.raises(TypeError, match="SSE|event|data|serial"):
        await run_sse({"producer": events(), "send": sent.append})

    assert sent == []


@pytest.mark.asyncio
async def test_sse_disconnect_cancels_iterator_and_emits_session_close() -> None:
    run_sse = _require("tigrbl_runtime.protocol.sse", "run_sse_chain")
    finalized: list[str] = []

    async def events():
        try:
            yield {"event": "item", "data": "1"}
            yield {"event": "item", "data": "2"}
        finally:
            finalized.append("done")

    result = await run_sse({"producer": events(), "disconnect_after": 1})

    assert result["exit_reason"] == "disconnect"
    assert result["subevents"][-1] == "session.close"
    assert finalized == ["done"]


@pytest.mark.asyncio
async def test_sse_normal_exhaustion_emits_stream_end_and_session_close() -> None:
    run_sse = _require("tigrbl_runtime.protocol.sse", "run_sse_chain")

    async def events():
        yield {"event": "item", "data": "1"}

    result = await run_sse({"producer": events()})

    assert result["exit_reason"] == "producer.exhausted"
    assert result["subevents"][-2:] == ["stream.end", "session.close"]
    assert result["completion_fence"] == "POST_EMIT"
