from __future__ import annotations

from tigrbl_core._spec import AppSpec, HttpJsonRpcBindingSpec, OpSpec
from tigrbl_core.config.constants import (
    __JSONRPC_DEFAULT_ENDPOINT__,
    __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__,
)


def test_http_jsonrpc_binding_spec_exposes_endpoint_identity() -> None:
    default_binding = HttpJsonRpcBindingSpec(
        proto="http.jsonrpc",
        rpc_method="Widget.create",
    )
    admin_binding = HttpJsonRpcBindingSpec(
        proto="http.jsonrpc",
        rpc_method="AdminWidget.create",
        endpoint="admin",
    )

    app_spec = AppSpec.from_dict(
        {
            "title": "endpoint binding contract",
            "version": "0.1.0",
            "ops": (
                OpSpec(alias="Widget.create", target="create", bindings=(default_binding,)),
                OpSpec(
                    alias="AdminWidget.create",
                    target="create",
                    bindings=(admin_binding,),
                ),
            ),
        }
    )
    restored = AppSpec.from_dict(app_spec.to_dict())
    bindings = {
        op.alias: next(
            binding
            for binding in op.bindings
            if getattr(binding, "proto", None) == "http.jsonrpc"
        )
        for op in restored.ops
    }

    assert bindings["Widget.create"].endpoint == __JSONRPC_DEFAULT_ENDPOINT__
    assert __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__[bindings["Widget.create"].endpoint] == "/rpc"
    assert bindings["AdminWidget.create"].endpoint == "admin"
    assert bindings["AdminWidget.create"].rpc_method == "AdminWidget.create"
