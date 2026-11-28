from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.protocol_runtime import run_http_client_stream_chain
from tigrbl_core._spec.binding_spec import BytesFramingSpec, HttpStreamBindingSpec
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan
from tigrbl_runtime.channel._asgi_scope import build_asgi_channel


def test_http_stream_request_binding_projects_client_stream_runtime_metadata() -> None:
    binding = HttpStreamBindingSpec(
        proto="http.stream",
        path="/upload",
        methods=("POST",),
        exchange="client_stream",
        framing=BytesFramingSpec(),
    )
    plan = compile_binding_protocol_plan(
        "Upload.append",
        {
            "kind": "http.stream",
            "path": binding.path,
            "exchange": binding.exchange,
            "framing": binding.framing,
        },
    )
    channel = build_asgi_channel(
        SimpleNamespace(scope={"type": "http", "method": "POST", "path": "/upload"}),
        exchange=binding.exchange,
    )

    assert plan["family"] == "stream"
    assert "transport.receive" in plan["atom_anchors"]
    assert channel.kind == "stream"
    assert channel.family == "stream"
    assert channel.exchange == "client_stream"


@pytest.mark.asyncio
async def test_http_client_stream_runtime_preserves_order_and_calls_handler() -> None:
    seen: list[bytes] = []

    def handler(body: bytes) -> int:
        seen.append(body)
        return len(body)

    result = await run_http_client_stream_chain(
        {"chunks": [b"first-", "second", bytearray(b"-third")], "handler": handler}
    )

    assert result["body"] == b"first-second-third"
    assert result["result"] == len(b"first-second-third")
    assert result["chunks_received"] == 3
    assert result["subevents"] == (
        "request.body.receive",
        "stream.chunk.received",
        "stream.chunk.received",
        "stream.chunk.received",
        "stream.receive_complete",
    )
    assert seen == [b"first-second-third"]


@pytest.mark.asyncio
async def test_http_client_stream_runtime_disconnect_returns_partial_body() -> None:
    async def chunks():
        yield b"a"
        yield b"b"

    result = await run_http_client_stream_chain(
        {"chunks": chunks(), "disconnect_after": 1}
    )

    assert result["exit_reason"] == "disconnect"
    assert result["chunks_received"] == 1
    assert result["body"] == b"a"
    assert "stream.receive_complete" not in result["subevents"]
