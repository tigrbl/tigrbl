from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT__
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
        def _step(*_: Any) -> tuple[type, str]:
            return model, alias

        return {"HANDLER": [_step]}

    def _pack_kernel_plan(self, semantic: KernelPlan) -> object:
        return object()


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


def test_kernelplan_owns_transport_lookup_and_matching() -> None:
    plan = _compile_plan(CompilerFixture(), AppFixture(tables=(WidgetTable,)))

    assert isinstance(plan, KernelPlan)
    assert plan.opkey_to_meta[OpKey("http.rest", "GET /widgets")] == 0
    assert (
        plan.opkey_to_meta[
            OpKey("http.jsonrpc", f"{__JSONRPC_DEFAULT_ENDPOINT__}:widgets.lookup")
        ]
        == 1
    )

    assert plan.proto_indices["http.rest"]["exact"]["GET /widgets"] == 0
    endpoint_index = plan.proto_indices["http.jsonrpc"]["endpoints"][
        __JSONRPC_DEFAULT_ENDPOINT__
    ]
    assert endpoint_index["widgets.lookup"] == {
        "meta_index": 1,
        "selector": f"{__JSONRPC_DEFAULT_ENDPOINT__}:widgets.lookup",
        "rpc_method": "widgets.lookup",
        "endpoint": __JSONRPC_DEFAULT_ENDPOINT__,
    }
