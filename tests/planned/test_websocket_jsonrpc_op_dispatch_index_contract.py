from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest
from tigrbl_core._spec.binding_spec import HttpJsonRpcBindingSpec, WsBindingSpec


EXAMPLE_PATH = Path("examples/websocket_realtime_ops/app.py")


def _load_demo_module():
    example_dir = str(EXAMPLE_PATH.resolve().parent)
    if example_dir not in sys.path:
        sys.path.insert(0, example_dir)
    spec = importlib.util.spec_from_file_location(
        "planned_websocket_realtime_ops_app",
        EXAMPLE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_websocket_jsonrpc_appspec_lowering_contract() -> None:
    demo = _load_demo_module()

    app = demo.build_app()
    router = app.routers["realtime"]

    assert demo.REALTIME_PATH.kind == "ws-jsonrpc"
    assert getattr(router, "_jsonrpc_endpoint_mounts", {}) == {}
    assert {route.path_template for route in app.websocket_routes} == {
        demo.WEBSOCKET_PATH
    }

    for model_name, alias in (
        ("Thread", "subscribe"),
        ("Thread", "publish"),
        ("Message", "create"),
    ):
        model = app.tables[model_name]
        op = {spec.alias: spec for spec in model.ops.all}[alias]
        assert op.tx_scope == "none"
        assert any(
            isinstance(binding, WsBindingSpec)
            and binding.path == demo.WEBSOCKET_PATH
            for binding in op.bindings
        )
        assert any(
            isinstance(binding, HttpJsonRpcBindingSpec)
            and binding.rpc_method == f"{model_name}.{alias}"
            for binding in op.bindings
        )


@pytest.mark.asyncio
async def test_websocket_jsonrpc_dispatch_uses_framework_runtime_contract() -> None:
    demo = _load_demo_module()

    app = demo.build_app()
    sent: list[dict] = []
    inbound = [
        {"type": "websocket.connect"},
        {
            "type": "websocket.receive",
            "text": json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "Message.create",
                    "params": {
                        "id": "msg-42",
                        "thread_id": "thread:alpha",
                        "body": "hello",
                    },
                    "id": 42,
                }
            ),
        },
        {"type": "websocket.disconnect", "code": 1000},
    ]

    async def receive() -> dict:
        return inbound.pop(0)

    async def send(message: dict) -> None:
        sent.append(message)

    await app(
        {
            "type": "websocket",
            "scheme": "ws",
            "path": demo.WEBSOCKET_PATH,
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert sent[0] == {"type": "websocket.accept", "subprotocol": "jsonrpc"}
    assert json.loads(sent[1]["text"]) == {
        "jsonrpc": "2.0",
        "result": {
            "id": "msg-42",
            "thread_id": "thread:alpha",
            "body": "hello",
            "published": False,
        },
        "id": 42,
    }


def test_websocket_jsonrpc_example_has_no_custom_kernel_contract() -> None:
    source = Path("examples/websocket_realtime_ops/app.py").read_text()

    assert "compile_websocket_jsonrpc_dispatch_index" not in source
    assert "compile_websocket_chain" not in source
    assert "websocket_realtime_kernel_chain" not in source
