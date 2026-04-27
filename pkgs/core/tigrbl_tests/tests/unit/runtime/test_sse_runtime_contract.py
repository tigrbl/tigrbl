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

