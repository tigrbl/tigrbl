from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

pytest.importorskip("tigrbl")

from tigrbl_core._spec import (
    HttpJsonRpcProtocolBindingSpec,
    HttpRestProtocolBindingSpec,
    JsonFramingSpec,
    JsonRpcFramingSpec,
    OpSpec,
    WebSocketProtocolBindingSpec,
    WebTransportProtocolBindingSpec,
)
from tigrbl_kernel._compile import _compile_plan
from tigrbl_kernel.models import KernelPlan, OpKey
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


@dataclass
class AppFixture:
    tables: tuple[type, ...]


class CompilerFixture:
    def __init__(self) -> None:
        self.packed_marker: object = object()

    def _build_ingress(self, app: Any) -> dict[str, list[Any]]:
        return {"INGRESS": [lambda *_: app]}

    def _build_egress(self, app: Any) -> dict[str, list[Any]]:
        return {"EGRESS": [lambda *_: app]}

    def _build_op(self, model: type, alias: str) -> dict[str, list[Any]]:
        def _step(*_: Any) -> tuple[type, str]:
            return model, alias

        return {"HANDLER": [_step]}

    def _pack_kernel_plan(self, semantic: KernelPlan) -> object:
        return self.packed_marker


class WidgetProtocolTable:
    ops = (
        OpSpec(
            alias="create",
            target="create",
            bindings=(
                HttpRestProtocolBindingSpec(
                    path="/widgets",
                    methods=("POST",),
                    framing=JsonFramingSpec(),
                ),
                HttpJsonRpcProtocolBindingSpec(
                    path="/rpc",
                    method="Widget.create",
                    framing=JsonRpcFramingSpec(),
                ),
                WebSocketProtocolBindingSpec(
                    path="/ws/widgets",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="read",
            target="read",
            bindings=(
                HttpRestProtocolBindingSpec(
                    path="/widgets/{id}",
                    methods=("GET",),
                    framing=JsonFramingSpec(),
                ),
                HttpJsonRpcProtocolBindingSpec(
                    path="/rpc",
                    method="Widget.read",
                    framing=JsonRpcFramingSpec(),
                ),
                WebSocketProtocolBindingSpec(
                    path="/ws/widgets",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="subscribe",
            target="subscribe",
            bindings=(
                WebTransportProtocolBindingSpec(
                    path="/wt/widgets",
                    control_stream={
                        "kind": "bidi_stream",
                        "opens": "first",
                        "purpose": "session_control",
                        "framing": JsonRpcFramingSpec(),
                    },
                    streams=(
                        {
                            "name": "commands",
                            "kind": "bidi_stream",
                            "purpose": "jsonrpc_commands",
                            "framing": JsonRpcFramingSpec(),
                        },
                        {
                            "name": "events",
                            "kind": "unidi_server_stream",
                            "purpose": "subscription_events",
                            "framing": JsonRpcFramingSpec(),
                        },
                        {
                            "name": "uploads",
                            "kind": "unidi_client_stream",
                            "purpose": "client_upload_commands",
                            "framing": JsonRpcFramingSpec(),
                        },
                    ),
                    datagrams=(
                        {
                            "name": "acks",
                            "purpose": "low_latency_jsonrpc_ack",
                            "framing": JsonRpcFramingSpec(),
                        },
                    ),
                ),
            ),
        ),
    )


def test_multiple_ops_compile_to_distinct_http_rest_routes() -> None:
    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetProtocolTable,)))

    rest_index = plan.proto_indices["http.rest"]

    assert plan.opkey_to_meta[OpKey("http.rest", "POST /widgets")] == 0
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets/{id}")] == 1
    assert rest_index["exact"]["POST /widgets"] == 0
    assert rest_index["templated"][0]["selector"] == "GET /widgets/{id}"
    assert rest_index["templated"][0]["names"] == ("id",)


def test_multiple_ops_compile_to_jsonrpc_methods_on_same_path() -> None:
    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetProtocolTable,)))

    jsonrpc = plan.proto_indices["http.jsonrpc"]["endpoints"]["/rpc"]

    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "/rpc:Widget.create")] == 0
    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "/rpc:Widget.read")] == 1
    assert jsonrpc["Widget.create"]["path"] == "/rpc"
    assert jsonrpc["Widget.create"]["method"] == "Widget.create"
    assert jsonrpc["Widget.create"]["meta_index"] == 0
    assert jsonrpc["Widget.read"]["meta_index"] == 1


def test_websocket_jsonrpc_route_derives_subprotocol_from_framing() -> None:
    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetProtocolTable,)))

    metadata = plan.proto_indices["ws"]["exact_metadata"]["/ws/widgets"]

    assert metadata["framing"] == "jsonrpc"
    assert metadata["websocket_subprotocol"] == "jsonrpc"
    assert "subprotocols" not in metadata
    assert "required_subprotocol" not in metadata


def test_webtransport_route_preserves_session_lane_catalog() -> None:
    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetProtocolTable,)))

    wt_index = plan.proto_indices["webtransport"]
    metadata = wt_index["exact_metadata"]["/wt/widgets"]

    assert wt_index["exact"]["/wt/widgets"] == 2
    assert metadata["control_stream"]["kind"] == "bidi_stream"
    assert metadata["control_stream"]["opens"] == "first"
    assert metadata["control_stream"]["framing"] == "jsonrpc"
    assert tuple(row["name"] for row in metadata["streams"]) == (
        "commands",
        "events",
        "uploads",
    )
    assert {row["framing"] for row in metadata["streams"]} == {"jsonrpc"}
    assert metadata["datagrams"][0]["name"] == "acks"
    assert metadata["datagrams"][0]["framing"] == "jsonrpc"
    assert "inner_framing_spec" not in metadata


def test_protocol_plan_compiles_websocket_and_webtransport_derived_fields() -> None:
    ws_plan = compile_binding_protocol_plan(
        "Widget.create",
        {
            "kind": "ws",
            "path": "/ws/widgets",
            "framing": JsonRpcFramingSpec(),
        },
    )
    wt_plan = compile_binding_protocol_plan(
        "Widget.subscribe",
        {
            "kind": "webtransport",
            "path": "/wt/widgets",
            "control_stream": {
                "kind": "bidi_stream",
                "opens": "first",
                "framing": JsonRpcFramingSpec(),
            },
            "streams": (
                {
                    "name": "events",
                    "kind": "unidi_server_stream",
                    "framing": JsonRpcFramingSpec(),
                },
            ),
            "datagrams": (
                {
                    "name": "acks",
                    "framing": JsonRpcFramingSpec(),
                },
            ),
        },
    )

    assert ws_plan["websocket_subprotocol"] == "jsonrpc"
    assert "required_subprotocol" not in ws_plan
    assert ws_plan["event_key_inputs"]["websocket_subprotocol"] == "jsonrpc"

    catalog = wt_plan["lane_catalog"]
    assert catalog["control_stream"]["framing"] == "jsonrpc"
    assert catalog["streams"][0]["framing"] == "jsonrpc"
    assert catalog["datagrams"][0]["framing"] == "jsonrpc"
    assert "inner_framing_spec" not in wt_plan
