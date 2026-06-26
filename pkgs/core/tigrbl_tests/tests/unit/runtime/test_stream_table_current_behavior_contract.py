from __future__ import annotations

import json
from typing import Any

import pytest

from tigrbl import StreamTable, TigrblApp, resolver as _resolver
from tigrbl._spec import TableSpec
from tigrbl.factories.engine import mem
from tigrbl.types import Column, String


async def _collect_asgi_messages(
    app: Any,
    path: str,
) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )
    return sent


@pytest.mark.asyncio
async def test_stream_table_materialized_routes_emit_json_chunks() -> None:
    class ProbeStreamTable(StreamTable):
        __tablename__ = "stream_table_current_behavior_probe"
        __allow_unmapped__ = True

        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    try:
        declared = {
            op.alias: tuple(type(binding).__name__ for binding in op.bindings)
            for op in TableSpec.collect(ProbeStreamTable).ops
        }
        assert declared == {
            "tail": ("HttpStreamBindingSpec",),
            "download": ("HttpStreamBindingSpec",),
        }

        app.include_table(ProbeStreamTable)
        app.initialize()

        route_messages = await _collect_asgi_messages(app, "/probestreamtable")
        body_messages = [
            message
            for message in route_messages
            if message["type"] == "http.response.body"
        ]

        assert len(body_messages) == 2
        assert body_messages[0]["more_body"] is True
        assert body_messages[1] == {
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        }
        assert json.loads(body_messages[0]["body"]) == {
            "downloaded": True,
            "name": "blob",
            "checkpoint": None,
        }

        materialized = {
            op.alias: tuple(type(binding).__name__ for binding in op.bindings)
            for op in app.core.ProbeStreamTable._model.ops.all
        }
        assert materialized == {
            "tail": ("HttpStreamBindingSpec",),
            "download": ("HttpStreamBindingSpec",),
        }
    finally:
        _resolver.set_default(None)


@pytest.mark.asyncio
async def test_http_stream_jsonrpc_framing_emits_jsonrpc_chunk_envelopes() -> None:
    from tigrbl import HttpStreamBindingSpec, OpSpec, TableBase
    from tigrbl_core._spec import JsonRpcFramingSpec

    class ProbeJsonRpcStream(TableBase):
        __tablename__ = "stream_table_jsonrpc_framing_probe"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(
                alias="tail",
                target="tail",
                bindings=(
                    HttpStreamBindingSpec(
                        proto="http.stream",
                        path="/tail",
                        framing=JsonRpcFramingSpec(),
                    ),
                ),
            ),
        )

        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    try:
        app.include_table(ProbeJsonRpcStream)
        app.initialize()

        route_messages = await _collect_asgi_messages(app, "/tail")
        body_messages = [
            message
            for message in route_messages
            if message["type"] == "http.response.body"
        ]

        assert len(body_messages) == 2
        assert body_messages[0]["more_body"] is True
        envelope = json.loads(body_messages[0]["body"])
        assert envelope == {
            "jsonrpc": "2.0",
            "method": "ProbeJsonRpcStream.tail.chunk",
            "params": {
                "index": 0,
                "data": {"stream": "default", "limit": 50, "tailed": True},
            },
        }
        assert body_messages[1]["more_body"] is False
    finally:
        _resolver.set_default(None)
