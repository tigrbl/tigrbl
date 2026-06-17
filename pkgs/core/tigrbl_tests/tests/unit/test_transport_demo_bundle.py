from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from httpx import ASGITransport, AsyncClient
import pytest


DEMO_PATH = Path(__file__).resolve().parents[5] / "examples" / "transport_demo" / "app.py"


def _load_demo_module():
    spec = importlib.util.spec_from_file_location("transport_demo_app", DEMO_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _run_websocket(
    app,
    path: str,
    inbound: list[dict[str, object]],
    *,
    headers: list[tuple[bytes, bytes]] | None = None,
) -> list[dict[str, object]]:
    sent: list[dict[str, object]] = []
    pending = list(inbound)

    async def receive() -> dict[str, object]:
        if pending:
            return pending.pop(0)
        return {"type": "websocket.disconnect", "code": 1000}

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    await app(
        {
            "type": "websocket",
            "scheme": "wss",
            "path": path,
            "query_string": b"",
            "headers": headers or [],
        },
        receive,
        send,
    )
    return sent


def test_transport_demo_negative_examples_preserve_wss_ndjson_subprotocol_contract() -> None:
    module = _load_demo_module()

    failures = module.build_fail_closed_examples()

    assert "wss_ndjson" in failures
    assert "subprotocols" in failures["wss_ndjson"].lower()
    assert "ndjson" in failures["wss_ndjson"].lower()


def test_transport_demo_registers_expected_websocket_metadata() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_test.sqlite3"))

    paths = {route.path_template: route for route in app.websocket_routes}

    assert "/ws/echo" in paths
    assert paths["/ws/echo"].protocol == "ws"
    assert paths["/ws/echo"].framing == "text"
    assert "/wss/echo" in paths
    assert paths["/wss/echo"].protocol == "wss"
    assert "/wss/jsonrpc" in paths
    assert paths["/wss/jsonrpc"].protocol == "wss"
    assert paths["/wss/jsonrpc"].framing == "jsonrpc"


@pytest.mark.asyncio
async def test_transport_demo_docs_and_matrix_surfaces_render() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_docs.sqlite3"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        matrix = await client.get("/matrix")
        openapi = await client.get("/openapi.json")
        openrpc = await client.get("/openrpc.json")

    assert matrix.status_code == 200
    matrix_payload = matrix.json()
    assert any(item["demo"] == "webtransport-session" for item in matrix_payload["demos"])
    assert "wss_ndjson" in matrix_payload["negative_examples"]

    assert openapi.status_code == 200
    openapi_payload = openapi.json()
    assert "/mtls/echo" in openapi_payload["paths"]
    assert openapi_payload["components"]["securitySchemes"]["MutualTLSAuth"]["type"] == "mutualTLS"

    assert openrpc.status_code == 200
    openrpc_payload = openrpc.json()
    method_names = {method["name"] for method in openrpc_payload["methods"]}
    assert "DemoItem.create" in method_names
    assert "DemoItem.read" in method_names


@pytest.mark.asyncio
async def test_transport_demo_wss_jsonrpc_rejects_missing_subprotocol_offer() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_ws_missing_subprotocol.sqlite3"))

    sent = await _run_websocket(
        app,
        "/wss/jsonrpc",
        [{"type": "websocket.receive", "text": '{"jsonrpc":"2.0","method":"demo.echo","id":1}'}],
    )

    assert sent == [{"type": "websocket.close", "code": 1002}]


@pytest.mark.asyncio
async def test_transport_demo_wss_jsonrpc_rejects_invalid_json_frame() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_ws_invalid_json.sqlite3"))

    sent = await _run_websocket(
        app,
        "/wss/jsonrpc",
        [{"type": "websocket.receive", "text": "not-json"}],
        headers=[(b"sec-websocket-protocol", b"jsonrpc")],
    )

    assert sent == [
        {"type": "websocket.accept", "subprotocol": "jsonrpc"},
        {"type": "websocket.close", "code": 1002},
    ]


@pytest.mark.asyncio
async def test_transport_demo_wss_jsonrpc_returns_protocol_native_error_payloads() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_ws_error_payload.sqlite3"))

    sent = await _run_websocket(
        app,
        "/wss/jsonrpc",
        [
            {
                "type": "websocket.receive",
                "text": '{"jsonrpc":"2.0","method":"demo.unknown","params":{"value":7},"id":9}',
            }
        ],
        headers=[(b"sec-websocket-protocol", b"jsonrpc")],
    )

    assert sent[0] == {"type": "websocket.accept", "subprotocol": "jsonrpc"}
    payload = json.loads(str(sent[1]["text"]))
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 9
    assert payload["error"]["code"] == -32601
    assert sent[2] == {"type": "websocket.close", "code": 1000}
