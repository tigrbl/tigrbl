from __future__ import annotations

import pytest

from tigrbl_kernel.cross_transport import (
    canonical_operation_id,
    compile_equivalence_manifest,
)


def test_canonical_op_id_stable_across_rest_jsonrpc_ws() -> None:
    manifest = compile_equivalence_manifest(
        "Widget.create",
        (
            {"kind": "http.rest", "path": "/widgets", "methods": ("POST",)},
            {"kind": "http.jsonrpc", "rpc_method": "Widget.create"},
            {"kind": "ws", "path": "/socket", "framing": "jsonrpc", "subprotocols": ("jsonrpc",)},
        ),
    )

    assert manifest["op_id"] == "Widget.create"


def test_custom_op_requires_canonical_op_id() -> None:
    assert canonical_operation_id("Widget.custom_reindex") == "Widget.custom_reindex"
    with pytest.raises(ValueError, match="canonical operation id"):
        canonical_operation_id("custom_reindex")


def test_openapi_openrpc_runtime_op_id_parity() -> None:
    openapi_op_id = "Widget.read"
    openrpc_method = "Widget.read"
    runtime = compile_equivalence_manifest(
        "Widget.read",
        (
            {"kind": "http.rest", "path": "/widgets/{id}", "methods": ("GET",)},
            {"kind": "http.jsonrpc", "rpc_method": openrpc_method},
        ),
    )

    assert runtime["op_id"] == openapi_op_id == openrpc_method


def test_transport_selector_aliases_resolve_to_op_id() -> None:
    selector_aliases = {
        "GET /widgets/{id}": "Widget.read",
        "rpc:Widget.read": "Widget.read",
        "ws:Widget.read": "Widget.read",
    }

    assert {canonical_operation_id(value) for value in selector_aliases.values()} == {
        "Widget.read"
    }
