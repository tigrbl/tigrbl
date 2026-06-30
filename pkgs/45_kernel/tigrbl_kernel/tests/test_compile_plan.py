from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

pytest.importorskip("tigrbl")

from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    JsonRpcFramingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.table_spec import TableSpec
from tigrbl import RestJsonRpcTable

from tigrbl_kernel._compile import _compile_plan
from tigrbl_kernel.models import KernelPlan, OpKey


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


class WidgetTable:
    ops = (
        OpSpec(
            alias="list_widgets",
            target="list",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/widgets",
                ),
            ),
        ),
        OpSpec(
            alias="get_widget",
            target="read",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/widgets/{widget_id}",
                ),
                WsBindingSpec(proto="ws", path="/ws/widgets/{widget_id}"),
            ),
        ),
        OpSpec(
            alias="rpc_lookup",
            target="custom",
            bindings=(
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="widgets.lookup",
                ),
            ),
        ),
    )


class RealtimeRouteMetadataTable:
    ops = (
        OpSpec(
            alias="ws_rpc",
            target="read",
            bindings=(
                WsBindingSpec(
                    proto="ws",
                    path="/ws/rpc",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="ws_rpc_item",
            target="read",
            bindings=(
                WsBindingSpec(
                    proto="ws",
                    path="/ws/rpc/{item_id}",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="wt_create",
            target="create",
            bindings=(
                WebTransportBindingSpec(
                    path="/wt/create",
                    profile="bidi_stream",
                    inner_framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
    )


def test_compile_plan_builds_indices_for_rest_ws_and_jsonrpc_bindings() -> None:
    compiler = CompilerFixture()
    app = AppFixture(tables=(WidgetTable,))

    plan = _compile_plan(compiler, app)

    assert plan.packed is compiler.packed_marker
    assert len(plan.opmeta) == 3
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets")] == 0
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets/{widget_id}")] == 1
    assert plan.opkey_to_meta[OpKey("ws", "/ws/widgets/{widget_id}")] == 1
    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "default:widgets.lookup")] == 2

    http_rest_index = plan.proto_indices["http.rest"]
    assert http_rest_index["exact"]["GET /widgets"] == 0
    templated_rest = http_rest_index["templated"][0]
    assert templated_rest["path"] == "/widgets/{widget_id}"
    assert templated_rest["names"] == ("widget_id",)

    ws_index = plan.proto_indices["ws"]
    templated_ws = ws_index["templated"][0]
    assert templated_ws["path"] == "/ws/widgets/{widget_id}"
    assert templated_ws["names"] == ("widget_id",)

    jsonrpc_index = plan.proto_indices["http.jsonrpc"]["endpoints"]["default"]
    assert jsonrpc_index["widgets.lookup"]["meta_index"] == 2
    assert jsonrpc_index["widgets.lookup"]["selector"] == "default:widgets.lookup"


def test_compile_plan_preserves_derived_websocket_route_metadata() -> None:
    compiler = CompilerFixture()
    app = AppFixture(tables=(RealtimeRouteMetadataTable,))

    plan = _compile_plan(compiler, app)

    ws_index = plan.proto_indices["ws"]
    exact_metadata = ws_index["exact_metadata"]["/ws/rpc"]
    templated_metadata = ws_index["templated"][0]

    assert ws_index["exact"]["/ws/rpc"] == 0
    assert exact_metadata["framing"] == "jsonrpc"
    assert exact_metadata["framing_spec"] == "JsonRpcFramingSpec"
    assert exact_metadata["subprotocols"] == ("jsonrpc",)
    assert templated_metadata["path"] == "/ws/rpc/{item_id}"
    assert templated_metadata["framing"] == "jsonrpc"
    assert templated_metadata["framing_spec"] == "JsonRpcFramingSpec"
    assert templated_metadata["subprotocols"] == ("jsonrpc",)


def test_compile_plan_preserves_webtransport_lane_framing_metadata() -> None:
    compiler = CompilerFixture()
    app = AppFixture(tables=(RealtimeRouteMetadataTable,))

    plan = _compile_plan(compiler, app)

    wt_index = plan.proto_indices["webtransport"]
    metadata = wt_index["exact_metadata"]["/wt/create"]

    assert wt_index["exact"]["/wt/create"] == 2
    assert metadata["framing"] == ""
    assert metadata["framing_spec"] == ""
    assert metadata["lane"] == "bidi_stream"
    assert metadata["inner_framing"] == "jsonrpc"
    assert metadata["inner_framing_spec"] == "JsonRpcFramingSpec"


def test_compile_plan_accepts_appspec_and_declared_tigrbl_ops() -> None:
    class GadgetTable:
        __tigrbl_ops__ = (
            OpSpec(
                alias="list_gadgets",
                target="list",
                bindings=(
                    HttpRestBindingSpec(
                        proto="https.rest",
                        methods=("GET",),
                        path="/gadgets",
                    ),
                ),
            ),
        )

    compiler = CompilerFixture()
    app = AppSpec(tables=(GadgetTable,))

    plan = _compile_plan(compiler, app)

    assert len(plan.opmeta) == 1
    assert plan.opmeta[0].alias == "list_gadgets"
    assert plan.opmeta[0].target == "list"
    assert plan.opkey_to_meta[OpKey("https.rest", "GET /gadgets")] == 0
    assert plan.proto_indices["https.rest"]["exact"]["GET /gadgets"] == 0


def test_compile_plan_keeps_table_profile_rest_jsonrpc_bindings_separate() -> None:
    class DualProfileTable:
        __tigrbl_ops__ = (TableSpec.collect(RestJsonRpcTable).ops[0],)

    compiler = CompilerFixture()
    app = AppFixture(tables=(DualProfileTable,))

    plan = _compile_plan(compiler, app)

    assert len(plan.opmeta) == 1
    assert plan.opmeta[0].alias == "create"
    assert plan.opmeta[0].target == "create"
    assert plan.opkey_to_meta[OpKey("http.rest", "POST /create")] == 0
    assert (
        plan.opkey_to_meta[
            OpKey("http.jsonrpc", "default:RestJsonRpcTable.create")
        ]
        == 0
    )
    assert plan.proto_indices["http.rest"]["exact"]["POST /create"] == 0
    jsonrpc = plan.proto_indices["http.jsonrpc"]["endpoints"]["default"]
    assert jsonrpc["RestJsonRpcTable.create"]["meta_index"] == 0
    assert jsonrpc["RestJsonRpcTable.create"]["selector"] == (
        "default:RestJsonRpcTable.create"
    )
