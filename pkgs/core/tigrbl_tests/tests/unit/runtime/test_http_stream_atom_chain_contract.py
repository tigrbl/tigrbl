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


def test_http_stream_chain_compiles_iterator_chunk_emit_and_completion_fence() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.http_stream", "compile_http_stream_chain")

    chain = compile_chain({"path": "/stream", "method": "GET", "producer": "iterator"})
    anchors = tuple(chain["anchors"])

    assert "dispatch.exchange.select" in anchors
    assert "iterator.producer.start" in anchors
    assert "transport.emit" in anchors
    assert "transport.emit_complete" in anchors
    assert anchors.index("transport.emit") < anchors.index("transport.emit_complete")


def test_http_stream_chain_declares_disconnect_and_error_edges() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.http_stream", "compile_http_stream_chain")

    chain = compile_chain({"path": "/stream", "method": "GET", "producer": "async_iterator"})

    assert chain["exchange"] == "server_stream"
    assert chain["family"] == "stream"
    assert "disconnect" in chain["break_conditions"]
    assert chain["err_target"] in {"ON_HANDLER_ERROR", "transport.close", "POST_EMIT"}


def test_http_stream_chain_rejects_unknown_producer_kind() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.http_stream", "compile_http_stream_chain")

    with pytest.raises(ValueError, match="producer|iterator|stream"):
        compile_chain({"path": "/stream", "method": "GET", "producer": "buffer_all"})


@pytest.mark.asyncio
async def test_http_stream_runtime_emits_start_chunks_and_final_completion() -> None:
    run_chain = _require("tigrbl_runtime.protocol.http_stream", "run_http_stream_chain")

    async def chunks():
        yield b"a"
        yield b"b"

    sent: list[dict[str, object]] = []
    result = await run_chain({"producer": chunks(), "send": sent.append})

    assert [message["type"] for message in sent] == [
        "http.response.start",
        "http.response.body",
        "http.response.body",
        "http.response.body",
    ]
    assert sent[-1]["more_body"] is False
    assert result["completion_fence"] == "POST_EMIT"


@pytest.mark.asyncio
async def test_http_stream_runtime_supports_sync_iterators_without_buffering() -> None:
    run_chain = _require("tigrbl_runtime.protocol.http_stream", "run_http_stream_chain")

    sent: list[dict[str, object]] = []
    result = await run_chain({"producer": iter((b"a", b"b", b"c")), "send": sent.append})

    body_messages = [message for message in sent if message["type"] == "http.response.body"]
    assert [message["body"] for message in body_messages[:-1]] == [b"a", b"b", b"c"]
    assert body_messages[-1]["body"] == b""
    assert body_messages[-1]["more_body"] is False
    assert result["chunks_emitted"] == 3


@pytest.mark.asyncio
async def test_http_stream_runtime_rejects_invalid_chunk_before_emit() -> None:
    run_chain = _require("tigrbl_runtime.protocol.http_stream", "run_http_stream_chain")

    async def chunks():
        yield {"not": "bytes"}

    sent: list[dict[str, object]] = []

    with pytest.raises(TypeError, match="chunk|bytes|str"):
        await run_chain({"producer": chunks(), "send": sent.append})

    assert [message["type"] for message in sent] == ["http.response.start"]


@pytest.mark.asyncio
async def test_http_stream_disconnect_cancels_producer_and_finalizes() -> None:
    run_chain = _require("tigrbl_runtime.protocol.http_stream", "run_http_stream_chain")
    finalized: list[str] = []

    async def chunks():
        try:
            yield b"a"
            yield b"b"
        finally:
            finalized.append("done")

    result = await run_chain({"producer": chunks(), "disconnect_after": 1})

    assert result["exit_reason"] == "disconnect"
    assert finalized == ["done"]
