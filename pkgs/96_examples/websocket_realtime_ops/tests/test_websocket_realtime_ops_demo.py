from __future__ import annotations

import ast
import asyncio
import json
import importlib.util
import sys
from pathlib import Path

import pytest
from tigrbl_core._spec import AppSpec, OpSpec, PathSpec, RouterSpec, TableSpec
from tigrbl_core._spec.binding_spec import HttpJsonRpcBindingSpec, WsBindingSpec


EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _load_example_module():
    example_dir = str(EXAMPLE_PATH.parent)
    if example_dir not in sys.path:
        sys.path.insert(0, example_dir)
    spec = importlib.util.spec_from_file_location(
        "websocket_realtime_ops_app",
        EXAMPLE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_websocket_realtime_ops_demo_declares_jsonrpc_websocket_route() -> None:
    module = _load_example_module()
    app = module.build_app()

    assert isinstance(module.APP_SPEC, AppSpec)
    assert isinstance(module.REALTIME_ROUTER, RouterSpec)
    assert isinstance(module.REALTIME_PATH, PathSpec)
    assert module.REALTIME_PATH.path == "/ws/realtime"
    assert module.REALTIME_PATH.kind == "ws-jsonrpc"
    assert module.WEBSOCKET_BINDING.subprotocols == ("jsonrpc",)
    assert app.title == module.APP_SPEC.title
    assert {route.path_template for route in app.websocket_routes} == {
        module.WEBSOCKET_PATH
    }


def test_websocket_realtime_ops_demo_declares_table_owned_opspecs() -> None:
    module = _load_example_module()

    assert tuple(module.REALTIME_PATH.tables) == (
        module.THREAD_TABLE,
        module.MESSAGE_TABLE,
    )
    assert all(isinstance(table, TableSpec) for table in module.REALTIME_PATH.tables)
    assert all(isinstance(op, OpSpec) for op in module.REALTIME_OPS)
    assert (
        tuple(
            (table.name, op.alias, op.target)
            for table in module.REALTIME_PATH.tables
            for op in table.ops
        )
        == (
            ("Thread", "subscribe", "subscribe"),
            ("Thread", "publish", "publish"),
            ("Message", "create", "create"),
        )
    )
    assert {
        binding.path
        for op in module.REALTIME_PATH.iter_ops()
        for binding in op.bindings
    } == {"/ws/realtime"}
    assert all(op.tx_scope == "none" for op in module.REALTIME_PATH.iter_ops())


def test_websocket_realtime_ops_demo_uses_framework_lowered_bindings() -> None:
    module = _load_example_module()
    app = module.build_app()

    thread = app.tables["Thread"]
    message = app.tables["Message"]
    thread_methods = {op.alias: op for op in thread.ops.all}
    message_methods = {op.alias: op for op in message.ops.all}

    assert app.routers["realtime"]._jsonrpc_endpoint_mounts == {}
    for model, alias in (
        (thread, "subscribe"),
        (thread, "publish"),
        (message, "create"),
    ):
        op = {spec.alias: spec for spec in model.ops.all}[alias]
        assert any(isinstance(binding, WsBindingSpec) for binding in op.bindings)
        assert any(
            isinstance(binding, HttpJsonRpcBindingSpec)
            and binding.rpc_method == f"{model.__name__}.{alias}"
            for binding in op.bindings
        )

    assert set(thread_methods) >= {"subscribe", "publish"}
    assert set(message_methods) >= {"create"}


@pytest.mark.asyncio
async def test_websocket_realtime_ops_demo_dispatches_jsonrpc_over_websocket() -> None:
    module = _load_example_module()
    app = module.build_app()
    sent = []
    inbound = [
        {"type": "websocket.connect"},
        {
            "type": "websocket.receive",
            "text": json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "Thread.subscribe",
                    "params": {"channel": "thread:alpha", "cursor": "msg-0"},
                    "id": "sub-1",
                }
            ),
        },
        {"type": "websocket.disconnect", "code": 1000},
    ]

    async def receive():
        return inbound.pop(0)

    async def send(message):
        sent.append(message)

    await app(
        {
            "type": "websocket",
            "scheme": "ws",
            "path": "/ws/realtime",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert sent[0] == {"type": "websocket.accept", "subprotocol": "jsonrpc"}
    payload = json.loads(sent[1]["text"])
    assert payload == {
        "jsonrpc": "2.0",
        "result": {
            "id": None,
            "subscribed": True,
            "channel": "thread:alpha",
            "cursor": "msg-0",
            "subscription_id": payload["result"]["subscription_id"],
            "subscriber_count": 1,
        },
        "id": "sub-1",
    }


@pytest.mark.asyncio
async def test_websocket_realtime_ops_demo_fanout_between_clients() -> None:
    module = _load_example_module()
    app = module.build_app()
    subscriber_sent: list[dict] = []
    publisher_sent: list[dict] = []
    subscriber_inbound: asyncio.Queue[dict] = asyncio.Queue()
    publisher_inbound: asyncio.Queue[dict] = asyncio.Queue()

    await subscriber_inbound.put({"type": "websocket.connect"})
    await subscriber_inbound.put(
        {
            "type": "websocket.receive",
            "text": json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "Thread.subscribe",
                    "params": {"channel": "thread:alpha"},
                    "id": "sub-1",
                }
            ),
        }
    )
    await publisher_inbound.put({"type": "websocket.connect"})
    await publisher_inbound.put(
        {
            "type": "websocket.receive",
            "text": json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "Thread.publish",
                    "params": {
                        "channel": "thread:alpha",
                        "event": {"id": "msg-2", "body": "hi"},
                    },
                    "id": "pub-1",
                }
            ),
        }
    )
    await publisher_inbound.put({"type": "websocket.disconnect", "code": 1000})

    async def receive_subscriber() -> dict:
        return await subscriber_inbound.get()

    async def receive_publisher() -> dict:
        return await publisher_inbound.get()

    async def send_subscriber(message: dict) -> None:
        subscriber_sent.append(message)

    async def send_publisher(message: dict) -> None:
        publisher_sent.append(message)

    subscriber_task = asyncio.create_task(
        app(
            {
                "type": "websocket",
                "scheme": "ws",
                "path": "/ws/realtime",
                "query_string": b"",
                "headers": [],
            },
            receive_subscriber,
            send_subscriber,
        )
    )

    for _ in range(50):
        if len(subscriber_sent) >= 2:
            break
        await asyncio.sleep(0.01)
    assert len(subscriber_sent) >= 2

    await app(
        {
            "type": "websocket",
            "scheme": "ws",
            "path": "/ws/realtime",
            "query_string": b"",
            "headers": [],
        },
        receive_publisher,
        send_publisher,
    )

    for _ in range(50):
        if len(subscriber_sent) >= 3:
            break
        await asyncio.sleep(0.01)
    await subscriber_inbound.put({"type": "websocket.disconnect", "code": 1000})
    await subscriber_task

    fanout = json.loads(subscriber_sent[2]["text"])
    assert fanout == {
        "jsonrpc": "2.0",
        "method": "Thread.publish",
        "params": {
            "channel": "thread:alpha",
            "event": {"id": "msg-2", "body": "hi"},
        },
    }
    publisher_ack = json.loads(publisher_sent[1]["text"])
    assert publisher_ack["result"]["published"] is True
    assert publisher_ack["result"]["delivered"] == 1


def test_websocket_realtime_ops_demo_has_no_app_local_protocol_loop() -> None:
    tree = ast.parse(EXAMPLE_PATH.read_text())
    forbidden_calls = {
        "accept",
        "receive",
        "receive_text",
        "send_text",
        "send_bytes",
        "close",
    }
    forbidden_names = {
        "publish_thread",
        "realtime_publish",
        "realtime_subscribe",
        "subscribe_thread",
    }
    forbidden_decorators = {"websocket"}

    assert not any(isinstance(node, (ast.For, ast.AsyncFor, ast.While)) for node in ast.walk(tree))
    assert not any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and ast.unparse(node.test).startswith("op ")
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in forbidden_calls
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Name) and node.id in forbidden_names
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in forbidden_decorators
        for node in ast.walk(tree)
    )
