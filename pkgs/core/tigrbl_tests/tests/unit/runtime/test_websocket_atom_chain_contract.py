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


def test_websocket_chain_compiles_connect_accept_receive_send_and_close() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.websocket", "compile_websocket_chain")

    chain = compile_chain({"path": "/socket", "scheme": "wss"})
    anchors = tuple(chain["anchors"])

    assert anchors.index("transport.accept") < anchors.index("framing.decode")
    assert anchors.index("framing.decode") < anchors.index("CALL_HANDLER")
    assert anchors.index("CALL_HANDLER") < anchors.index("transport.emit")
    assert anchors.index("transport.emit") < anchors.index("transport.close")
    assert chain["scope_metadata"]["secure"] is True


@pytest.mark.asyncio
async def test_websocket_runtime_processes_message_loop_and_clean_close() -> None:
    run_ws = _require("tigrbl_runtime.protocol.websocket", "run_websocket_chain")

    result = await run_ws(
        {
            "scope": {"type": "websocket", "scheme": "ws", "path": "/socket"},
            "messages": [{"type": "websocket.receive", "text": "ping"}, {"type": "websocket.disconnect"}],
        }
    )

    assert result["accepted"] is True
    assert result["received"] == ["ping"]
    assert result["closed"] is True
    assert result["close_code"] == 1000


@pytest.mark.asyncio
async def test_websocket_handler_failure_closes_with_typed_error_metadata() -> None:
    run_ws = _require("tigrbl_runtime.protocol.websocket", "run_websocket_chain")

    async def handler(_message: object) -> object:
        raise RuntimeError("bad message")

    result = await run_ws(
        {
            "scope": {"type": "websocket", "scheme": "wss", "path": "/socket"},
            "messages": [{"type": "websocket.receive", "text": "bad"}],
            "handler": handler,
        }
    )

    assert result["closed"] is True
    assert result["close_code"] in {1003, 1011}
    assert result["error_ctx"]["binding"] in {"websocket", "wss"}
    assert result["error_ctx"]["subevent"] == "message.received"
