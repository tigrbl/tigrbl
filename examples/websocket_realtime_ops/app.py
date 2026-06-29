from __future__ import annotations

import sys
from pathlib import Path

from tigrbl import TigrblApp
from tigrbl_core._spec import (
    AppSpec,
    JsonRpcFramingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
    WsBindingSpec,
)

EXAMPLE_DIR = str(Path(__file__).resolve().parent)
if EXAMPLE_DIR not in sys.path:
    sys.path.insert(0, EXAMPLE_DIR)


WEBSOCKET_PATH = "/ws/realtime"
WEBSOCKET_BINDING = WsBindingSpec(
    proto="ws",
    path=WEBSOCKET_PATH,
    framing=JsonRpcFramingSpec(),
)


async def subscribe_thread(ctx: dict) -> dict:
    payload = dict(ctx.get("payload") or {})
    return {
        "subscribed": True,
        "channel": payload.get("channel", "thread:alpha"),
        "cursor": payload.get("cursor"),
    }


async def publish_thread(ctx: dict) -> dict:
    payload = dict(ctx.get("payload") or {})
    return {
        "published": True,
        "channel": payload.get("channel", "thread:alpha"),
        "event": payload.get("event", {}),
    }


async def create_message(ctx: dict) -> dict:
    payload = dict(ctx.get("payload") or {})
    return {
        "id": payload.get("id", "msg-1"),
        "thread_id": payload.get("thread_id", "thread:alpha"),
        "body": payload.get("body", ""),
        "published": False,
    }


THREAD_TABLE = TableSpec(
    name="Thread",
    resource="threads",
    model_ref="models:Thread",
    ops=(
        OpSpec(
            alias="subscribe",
            target="subscribe",
            handler=subscribe_thread,
            bindings=(WEBSOCKET_BINDING,),
            exchange="bidirectional_stream",
            tx_scope="none",
            extra={
                "semantics": "register session-scoped interest and return a JSON-RPC ack",
            },
        ),
        OpSpec(
            alias="publish",
            target="publish",
            handler=publish_thread,
            bindings=(WEBSOCKET_BINDING,),
            exchange="bidirectional_stream",
            tx_scope="none",
            extra={
                "semantics": "publish an event to matching subscribers through explicit fanout",
            },
        ),
    ),
)
MESSAGE_TABLE = TableSpec(
    name="Message",
    resource="messages",
    model_ref="models:Message",
    ops=(
        OpSpec(
            alias="create",
            target="create",
            handler=create_message,
            bindings=(WEBSOCKET_BINDING,),
            exchange="bidirectional_stream",
            tx_scope="none",
            extra={
                "publish_effect": "none",
                "semantics": (
                    "create a message without publishing unless a publish effect is declared"
                ),
            },
        ),
    ),
)

REALTIME_PATH = PathSpec(
    path=WEBSOCKET_PATH,
    kind="ws-jsonrpc",
    tables=(THREAD_TABLE, MESSAGE_TABLE),
)
REALTIME_ROUTER = RouterSpec(
    name="realtime",
    paths=(REALTIME_PATH,),
)
APP_SPEC = AppSpec(
    title="Tigrbl WebSocket Realtime JSON-RPC Framework Demo",
    version="0.3.0",
    routers=(REALTIME_ROUTER,),
)
REALTIME_OPS = REALTIME_PATH.iter_ops()


def build_app() -> TigrblApp:
    return TigrblApp.from_spec(APP_SPEC)


app = build_app()
