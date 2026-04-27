from __future__ import annotations

from typing import Any

import pytest

from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_concrete._concrete._router import Router as TigrblRouter


async def _run_websocket(app: Any, path: str, inbound: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []
    pending = list(inbound)

    async def receive() -> dict[str, Any]:
        return pending.pop(0) if pending else {"type": "websocket.disconnect", "code": 1000}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(
        {"type": "websocket", "path": path, "query_string": b"", "headers": []},
        receive,
        send,
    )
    return sent


@pytest.mark.asyncio
async def test_websocket_route_accepts_text_and_closes_with_explicit_code() -> None:
    app = TigrblApp(title="WebSocket Contract")

    @app.websocket("/ws/echo")
    async def echo(ws):
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"echo:{text}")
        await ws.close(code=1001)

    sent = await _run_websocket(app, "/ws/echo", [{"type": "websocket.receive", "text": "hello"}])

    assert sent[0]["type"] == "websocket.accept"
    assert sent[1] == {"type": "websocket.send", "text": "echo:hello"}
    assert sent[2]["type"] == "websocket.close"
    assert sent[2]["code"] == 1001


def test_websocket_route_registration_records_prefixed_runtime_binding_metadata() -> None:
    app = TigrblApp(title="WebSocket Binding Contract")
    router = TigrblRouter()

    @router.websocket("/events", framing="jsonrpc", summary="Event socket")
    async def events(ws):
        await ws.accept()
        await ws.close()

    app.include_router(router, prefix="/tenant")
    route = next(item for item in app.websocket_routes if item.path_template == "/tenant/events")
    system_model = app.tables["__tigrbl_route_ops__"]
    op_spec = next(
        item
        for item in tuple(getattr(getattr(system_model, "ops", None), "all", ()) or ())
        if getattr(item, "alias", None) == "events"
    )
    binding = op_spec.bindings[0]

    assert route.name == "events"
    assert route.summary == "Event socket"
    assert binding.path == "/tenant/events"
    assert binding.proto == "ws"
    assert binding.exchange == "bidirectional_stream"
    assert binding.framing == "jsonrpc"


@pytest.mark.asyncio
async def test_unmatched_websocket_path_closes_without_accepting() -> None:
    app = TigrblApp(title="WebSocket Reject Contract")

    @app.websocket("/ws/known")
    async def known(ws):
        await ws.accept()
        await ws.close()

    sent = await _run_websocket(app, "/ws/missing", [])

    assert sent
    assert sent[0]["type"] == "websocket.close"
    assert all(message["type"] != "websocket.accept" for message in sent)
