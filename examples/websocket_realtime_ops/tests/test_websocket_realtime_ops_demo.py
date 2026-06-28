from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest


EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _load_example_module():
    spec = importlib.util.spec_from_file_location(
        "websocket_realtime_ops_app",
        EXAMPLE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _WebSocketClient:
    def __init__(self, app: Any, path: str) -> None:
        self.sent: list[dict[str, object]] = []
        self._inbound: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._message_event = asyncio.Event()

        async def receive() -> dict[str, object]:
            return await self._inbound.get()

        async def send(message: dict[str, object]) -> None:
            self.sent.append(message)
            self._message_event.set()

        self._task = asyncio.create_task(
            app(
                {
                    "type": "websocket",
                    "scheme": "ws",
                    "path": path,
                    "query_string": b"",
                    "headers": [],
                },
                receive,
                send,
            )
        )

    async def receive_text(self, text: str) -> None:
        await self._inbound.put({"type": "websocket.receive", "text": text})

    async def disconnect(self) -> None:
        await self._inbound.put({"type": "websocket.disconnect", "code": 1000})
        await asyncio.wait_for(self._task, timeout=1.0)

    async def wait_for(self, op: str) -> dict[str, object]:
        while True:
            for message in self.sent:
                if message.get("type") != "websocket.send":
                    continue
                payload = json.loads(str(message.get("text") or "{}"))
                if payload.get("op") == op:
                    return payload
            self._message_event.clear()
            await asyncio.wait_for(self._message_event.wait(), timeout=1.0)


def test_websocket_realtime_ops_demo_registers_websocket_route() -> None:
    module = _load_example_module()
    app = module.build_app()

    paths = {route.path_template: route for route in app.websocket_routes}

    assert "/ws/realtime" in paths
    assert paths["/ws/realtime"].protocol == "ws"
    assert paths["/ws/realtime"].framing == "text"


@pytest.mark.asyncio
async def test_websocket_realtime_ops_demo_observes_subscribe_and_publish() -> None:
    module = _load_example_module()
    app = module.build_app()

    subscriber = _WebSocketClient(app, "/ws/realtime")
    publisher = _WebSocketClient(app, "/ws/realtime")
    try:
        await subscriber.receive_text(
            json.dumps(
                {
                    "op": "subscribe",
                    "payload": {"channel": "thread:alpha", "cursor": "msg-0"},
                },
                separators=(",", ":"),
            )
        )
        subscribe_result = await subscriber.wait_for("subscribe.result")

        assert subscribe_result == {
            "op": "subscribe.result",
            "result": {
                "subscribed": True,
                "channel": "thread:alpha",
                "cursor": "msg-0",
            },
        }

        await publisher.receive_text(
            json.dumps(
                {
                    "op": "publish",
                    "payload": {
                        "channel": "thread:alpha",
                        "event": {"message_id": "msg-1", "body": "hello"},
                    },
                },
                separators=(",", ":"),
            )
        )
        publish_result = await publisher.wait_for("publish.result")
        published_event = await subscriber.wait_for("publish.event")

        expected_publish_result = {
            "op": "publish.result",
            "result": {
                "published": True,
                "channel": "thread:alpha",
                "event": {"message_id": "msg-1", "body": "hello"},
            },
        }
        assert publish_result == expected_publish_result
        assert published_event == {
            "op": "publish.event",
            "result": expected_publish_result["result"],
        }
    finally:
        await subscriber.disconnect()
        await publisher.disconnect()
