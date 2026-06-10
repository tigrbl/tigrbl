from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    DocsPayloadSpec,
    DocsProjectionSpec,
    DocsUixSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    OpSpec,
    PathSpec,
    SseBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.docs_spec import validate_docs_tree
from tigrbl_core._spec.table_spec import TableSpec
from tigrbl import RestJsonRpcTable


def _op(alias: str, *bindings: object, tags: tuple[str, ...] = ()) -> OpSpec:
    return OpSpec(
        alias=alias,
        target="custom",
        bindings=tuple(bindings),
        tags=tags,
    )


def _projection_paths() -> tuple[PathSpec, ...]:
    return (
        PathSpec(
            path="/items",
            kind="resource",
            ops=(
                _op(
                    "list",
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/items",
                    ),
                    tags=("public",),
                ),
            ),
        ),
        PathSpec(
            path="/rpc",
            kind="jsonrpc",
            ops=(
                _op(
                    "create",
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="Item.create",
                        endpoint="/rpc",
                    ),
                    tags=("rpc",),
                ),
            ),
        ),
        PathSpec(
            path="/items/tail",
            kind="stream",
            ops=(
                _op(
                    "tail",
                    HttpStreamBindingSpec(
                        proto="https.stream",
                        path="/items/tail",
                        framing="ndjson",
                    ),
                    tags=("stream",),
                ),
            ),
        ),
        PathSpec(
            path="/events",
            kind="sse",
            ops=(
                _op(
                    "events",
                    SseBindingSpec(proto="http.sse", path="/events"),
                    tags=("stream",),
                ),
            ),
        ),
        PathSpec(
            path="/ws/rpc",
            kind="ws-jsonrpc",
            ops=(
                _op(
                    "socket_rpc",
                    WsBindingSpec(
                        proto="ws",
                        path="/ws/rpc",
                        framing="jsonrpc",
                        subprotocols=("jsonrpc",),
                    ),
                    tags=("socket",),
                ),
            ),
        ),
        PathSpec(
            path="/wss/rpc",
            kind="wss-jsonrpc",
            ops=(
                _op(
                    "secure_socket_rpc",
                    WsBindingSpec(
                        proto="wss",
                        path="/wss/rpc",
                        framing="jsonrpc",
                        subprotocols=("jsonrpc",),
                    ),
                    tags=("socket", "secure"),
                ),
            ),
        ),
    )


def test_docs_projection_filters_by_protocol_kind_framing_and_subprotocol() -> None:
    projection = DocsProjectionSpec(
        name="websocket-jsonrpc",
        include_protocols=("wss",),
        include_path_kinds=("wss-jsonrpc",),
        include_framings=("jsonrpc",),
        include_subprotocols=("jsonrpc",),
    )

    selected = projection.select(_projection_paths())

    assert [item.path for item in selected] == ["/wss/rpc"]
    assert selected[0].protocols == ("wss",)
    assert selected[0].framings == ("jsonrpc",)
    assert selected[0].subprotocols == ("jsonrpc",)


def test_docs_projection_matrix_is_deterministic() -> None:
    projection = DocsProjectionSpec(
        name="transport-matrix",
        include_path_kinds=(
            "resource",
            "jsonrpc",
            "stream",
            "sse",
            "ws-jsonrpc",
            "wss-jsonrpc",
        ),
    )

    selected = projection.select(_projection_paths())

    assert [(item.path, item.op, item.path_kind) for item in selected] == [
        ("/items", "list", "resource"),
        ("/rpc", "create", "jsonrpc"),
        ("/items/tail", "tail", "stream"),
        ("/events", "events", "sse"),
        ("/ws/rpc", "socket_rpc", "ws-jsonrpc"),
        ("/wss/rpc", "secure_socket_rpc", "wss-jsonrpc"),
    ]


def test_docs_projection_impossible_combination_selects_nothing() -> None:
    projection = DocsProjectionSpec(
        name="impossible",
        include_protocols=("http.rest",),
        include_path_kinds=("ws-jsonrpc",),
        include_framings=("jsonrpc",),
    )

    assert projection.select(_projection_paths()) == ()


def test_docs_projection_respects_excludes_and_rpc_method_filters() -> None:
    projection = DocsProjectionSpec(
        name="rpc-only",
        include_protocols=("http.jsonrpc",),
        exclude_paths=("/private/rpc",),
        rpc_methods=("Item.create",),
    )

    selected = projection.select(_projection_paths())

    assert len(selected) == 1
    assert selected[0].path == "/rpc"
    assert selected[0].rpc_methods == ("Item.create",)


def test_docs_projection_selects_rest_and_openrpc_surfaces_for_dual_table_profile() -> None:
    profile_op = TableSpec.collect(RestJsonRpcTable).ops[0]
    rest_binding, jsonrpc_binding = profile_op.bindings
    paths = (
        PathSpec(
            path="/create",
            kind="resource",
            ops=(
                OpSpec(
                    alias=profile_op.alias,
                    target=profile_op.target,
                    bindings=(rest_binding,),
                ),
            ),
        ),
        PathSpec(
            path="/rpc",
            kind="jsonrpc",
            ops=(
                OpSpec(
                    alias=profile_op.alias,
                    target=profile_op.target,
                    bindings=(jsonrpc_binding,),
                ),
            ),
        ),
    )

    openapi = DocsPayloadSpec(
        kind="openapi",
        projection=DocsProjectionSpec(
            name="rest-surface",
            include_protocols=("http.rest",),
            include_path_kinds=("resource",),
        ),
    )
    openrpc = DocsPayloadSpec(
        kind="openrpc",
        projection=DocsProjectionSpec(
            name="rpc-surface",
            include_protocols=("http.jsonrpc",),
            include_path_kinds=("jsonrpc",),
            rpc_methods=("RestJsonRpcTable.create",),
        ),
    )

    rest_selected = openapi.projection.select(paths)
    rpc_selected = openrpc.projection.select(paths)

    assert [(item.path, item.op, item.protocols) for item in rest_selected] == [
        ("/create", "create", ("http.rest",)),
    ]
    assert [
        (item.path, item.op, item.protocols, item.rpc_methods)
        for item in rpc_selected
    ] == [
        (
            "/rpc",
            "create",
            ("http.jsonrpc",),
            ("RestJsonRpcTable.create",),
        ),
    ]


def test_docs_paths_remain_separate_from_runtime_projection() -> None:
    payload = PathSpec(
        path="/openapi.json",
        kind="docs-payload",
        docs_payload=DocsPayloadSpec(
            kind="openapi",
            projection=DocsProjectionSpec(
                name="public-http",
                include_protocols=("http.rest",),
            ),
        ),
    )
    uix = PathSpec(
        path="/docs",
        kind="docs-uix",
        docs_uix=DocsUixSpec(kind="swagger", payload_path="/openapi.json"),
    )

    validate_docs_tree((payload, uix))


def test_docs_payload_projection_rejects_incidental_runtime_selection() -> None:
    payload = PathSpec(
        path="/openrpc.json",
        kind="docs-payload",
        docs_payload=DocsPayloadSpec(
            kind="openrpc",
            projection=DocsProjectionSpec(
                name="rpc",
                include_protocols=("http.jsonrpc",),
            ),
        ),
    )

    with pytest.raises(ValueError, match="incidental docs path exposure"):
        payload.docs_payload.projection.select = lambda _paths: (object(),)  # type: ignore[method-assign]
        validate_docs_tree((payload,))
