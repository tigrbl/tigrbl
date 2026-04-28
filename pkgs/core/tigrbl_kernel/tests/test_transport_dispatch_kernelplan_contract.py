from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_kernel._compile import _compile_plan
from tigrbl_kernel.models import KernelPlan, OpKey


@dataclass
class AppFixture:
    tables: tuple[type, ...]


class CompilerFixture:
    def _build_ingress(self, app: Any) -> dict[str, list[Any]]:
        return {"INGRESS": [lambda *_: app]}

    def _build_egress(self, app: Any) -> dict[str, list[Any]]:
        return {"EGRESS": [lambda *_: app]}

    def _build_op(self, model: type, alias: str) -> dict[str, list[Any]]:
        return {"HANDLER": [lambda *_: (model, alias)]}

    def _pack_kernel_plan(self, semantic: KernelPlan, **_: Any) -> object:
        return object()


def test_kernelplan_owns_transport_lookup_and_matching() -> None:
    class WidgetTable:
        __tigrbl_ops__ = (
            OpSpec(
                alias="widgets.create",
                target="create",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("POST",),
                        path="/widgets",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.create",
                    ),
                ),
            ),
            OpSpec(
                alias="widgets.read",
                target="read",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/widgets/{item_id}",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.read",
                    ),
                ),
            ),
        )

    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetTable,)))

    assert plan.opkey_to_meta[OpKey("http.rest", "POST /widgets")] == 0
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets/{item_id}")] == 1
    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "default:widgets.create")] == 0
    assert plan.opkey_to_meta[OpKey("http.jsonrpc", "default:widgets.read")] == 1

    rest_index = plan.proto_indices["http.rest"]
    assert rest_index["exact"]["POST /widgets"] == 0
    assert rest_index["templated"][0]["selector"] == "GET /widgets/{item_id}"
    assert rest_index["templated"][0]["names"] == ("item_id",)

    jsonrpc_index = plan.proto_indices["http.jsonrpc"]["endpoints"]["default"]
    assert jsonrpc_index["widgets.create"]["meta_index"] == 0
    assert jsonrpc_index["widgets.read"]["selector"] == "default:widgets.read"
