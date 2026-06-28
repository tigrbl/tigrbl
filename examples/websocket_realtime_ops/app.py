from __future__ import annotations

import json
from typing import Any

from tigrbl import TigrblApp
from tigrbl_core._spec import TextFramingSpec
from tigrbl_ops_realtime import publish as realtime_publish
from tigrbl_ops_realtime import subscribe as realtime_subscribe


_REALTIME_PROTOCOL_CLOSE_CODE = 1003


def _subscribers(app: TigrblApp) -> dict[str, set[Any]]:
    subscribers = getattr(app, "_websocket_realtime_subscribers", None)
    if not isinstance(subscribers, dict):
        subscribers = {}
        setattr(app, "_websocket_realtime_subscribers", subscribers)
    return subscribers


async def _send_json(ws: Any, payload: dict[str, Any]) -> None:
    await ws.send_text(json.dumps(payload, separators=(",", ":")))


async def _broadcast(
    app: TigrblApp,
    *,
    channel: str,
    payload: dict[str, Any],
) -> None:
    for subscriber in tuple(_subscribers(app).get(channel, set())):
        if getattr(subscriber, "closed", False):
            continue
        await _send_json(subscriber, payload)


def build_app() -> TigrblApp:
    app = TigrblApp(
        title="Tigrbl WebSocket Realtime Ops Demo",
        version="0.1.0",
        mount_system=False,
    )

    @app.websocket(
        "/ws/realtime",
        proto="ws",
        framing=TextFramingSpec(),
        summary="Observe realtime subscribe and publish ops",
    )
    async def realtime_socket(ws) -> None:
        await ws.accept()
        subscribed_channels: set[str] = set()
        try:
            while True:
                try:
                    text = await ws.receive_text()
                except RuntimeError:
                    break
                try:
                    message = json.loads(text or "")
                except Exception:
                    await ws.close(code=_REALTIME_PROTOCOL_CLOSE_CODE)
                    break
                if not isinstance(message, dict):
                    await ws.close(code=_REALTIME_PROTOCOL_CLOSE_CODE)
                    break
                op = str(message.get("op") or message.get("method") or "")
                payload = message.get("payload") or message.get("params") or {}
                if not isinstance(payload, dict):
                    await ws.close(code=_REALTIME_PROTOCOL_CLOSE_CODE)
                    break
                if op == "subscribe":
                    result = await realtime_subscribe(payload)
                    channel = str(result["channel"])
                    _subscribers(app).setdefault(channel, set()).add(ws)
                    subscribed_channels.add(channel)
                    await _send_json(ws, {"op": "subscribe.result", "result": result})
                    continue
                if op == "publish":
                    result = await realtime_publish(payload)
                    channel = str(result["channel"])
                    await _send_json(ws, {"op": "publish.result", "result": result})
                    await _broadcast(
                        app,
                        channel=channel,
                        payload={"op": "publish.event", "result": result},
                    )
                    continue
                await ws.close(code=_REALTIME_PROTOCOL_CLOSE_CODE)
                break
        finally:
            subscribers = _subscribers(app)
            for channel in subscribed_channels:
                channel_subscribers = subscribers.get(channel)
                if channel_subscribers is not None:
                    channel_subscribers.discard(ws)
                    if not channel_subscribers:
                        subscribers.pop(channel, None)

    return app


app = build_app()
