from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    AppSpec,
    DocsPayloadSpec,
    DocsProjectionSpec,
    DocsUixSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    SseBindingSpec,
    TableSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    validate_docs_tree,
)


def _op(alias: str, target: str, *bindings: object, arity: str = "collection") -> OpSpec:
    return OpSpec(
        alias=alias,
        target=target,  # type: ignore[arg-type]
        arity=arity,  # type: ignore[arg-type]
        bindings=tuple(bindings),  # type: ignore[arg-type]
    )


def _widget_rest_paths() -> tuple[PathSpec, PathSpec]:
    collection = PathSpec(
        path="/widgets",
        tables=(
            TableSpec(
                name="Widget",
                resource="widget",
                model_ref="app.models:Widget",
                ops=(
                    _op(
                        "create",
                        "create",
                        HttpRestBindingSpec(proto="http.rest", methods=("POST",), path="/widgets"),
                    ),
                    _op(
                        "list",
                        "list",
                        HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/widgets"),
                    ),
                ),
            ),
        ),
    )
    member = PathSpec(
        path="/widgets/{item_id}",
        tables=(
            TableSpec(
                name="Widget",
                resource="widget",
                model_ref="app.models:Widget",
                ops=(
                    _op(
                        "read",
                        "read",
                        HttpRestBindingSpec(
                            proto="http.rest",
                            methods=("GET",),
                            path="/widgets/{item_id}",
                        ),
                        arity="member",
                    ),
                    _op(
                        "delete",
                        "delete",
                        HttpRestBindingSpec(
                            proto="http.rest",
                            methods=("DELETE",),
                            path="/widgets/{item_id}",
                        ),
                        arity="member",
                    ),
                ),
            ),
        ),
    )
    return collection, member


def _shared_rpc_path() -> PathSpec:
    return PathSpec(
        path="/rpc",
        kind="jsonrpc",
        tables=(
            TableSpec(
                name="Widget",
                resource="widget",
                model_ref="app.models:Widget",
                ops=(
                    _op(
                        "create",
                        "create",
                        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create"),
                    ),
                    _op(
                        "list",
                        "list",
                        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.list"),
                    ),
                ),
            ),
            TableSpec(
                name="Account",
                resource="account",
                model_ref="app.models:Account",
                ops=(
                    _op(
                        "create",
                        "create",
                        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Account.create"),
                    ),
                    _op(
                        "list",
                        "list",
                        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Account.list"),
                    ),
                ),
            ),
        ),
    )


def _multisurface_paths() -> tuple[PathSpec, ...]:
    public_http = DocsProjectionSpec(name="public-http", include_protocols=("http.rest",))
    public_rpc = DocsProjectionSpec(name="public-rpc", include_protocols=("http.jsonrpc",))
    rest_collection, rest_member = _widget_rest_paths()
    return (
        rest_collection,
        rest_member,
        _shared_rpc_path(),
        PathSpec(
            path="/ws",
            kind="websocket",
            ops=(_op("socket_events", "custom", WsBindingSpec(proto="ws", path="/ws")),),
        ),
        PathSpec(
            path="/events",
            kind="sse",
            ops=(_op("event_stream", "tail", SseBindingSpec(proto="http.sse", path="/events")),),
        ),
        PathSpec(
            path="/transport",
            kind="webtransport",
            ops=(
                _op(
                    "transport",
                    "send_datagram",
                    WebTransportBindingSpec(path="/transport"),
                ),
            ),
        ),
        PathSpec(
            path="/openapi.json",
            kind="docs-payload",
            docs_payload=DocsPayloadSpec(kind="openapi", projection=public_http),
        ),
        PathSpec(
            path="/openrpc.json",
            kind="docs-payload",
            docs_payload=DocsPayloadSpec(kind="openrpc", projection=public_rpc),
        ),
        PathSpec(
            path="/docs",
            kind="docs-uix",
            docs_uix=DocsUixSpec(kind="swagger", payload_path="/openapi.json"),
        ),
        PathSpec(path="/static", kind="static", static={"directory": "public"}),
        PathSpec(path="/admin", kind="mount", mount=AppSpec(title="Admin")),
    )


def _multisurface_appspec() -> AppSpec:
    return AppSpec(
        title="Nested AppSpec Corpus",
        routers=(RouterSpec(name="api", prefix="/api", paths=_multisurface_paths()),),
    )


def test_nested_appspec_composition_is_address_first() -> None:
    app = _multisurface_appspec()
    router = app.routers[0]

    assert isinstance(app, AppSpec)
    assert isinstance(router, RouterSpec)
    assert {path.path for path in router.paths} >= {
        "/widgets",
        "/widgets/{item_id}",
        "/rpc",
        "/openapi.json",
        "/openrpc.json",
        "/docs",
        "/static",
        "/admin",
    }
    widget_path = next(path for path in router.paths if path.path == "/widgets")
    assert widget_path.tables[0] == TableSpec(
        name="Widget",
        resource="widget",
        model_ref="app.models:Widget",
        ops=widget_path.tables[0].ops,
    )


def test_docs_projection_selects_by_protocol_path_table_and_rpc_method() -> None:
    selected = DocsProjectionSpec(
        name="widget-rpc",
        include_protocols=("http.jsonrpc",),
        include_paths=("/rpc",),
        include_tables=("Widget",),
        rpc_methods=("Widget.create",),
    ).select(_multisurface_paths())

    assert len(selected) == 1
    assert selected[0].path == "/rpc"
    assert selected[0].table == "Widget"
    assert selected[0].op == "create"
    assert selected[0].rpc_methods == ("Widget.create",)


def test_openapi_and_openrpc_projections_are_disjoint_by_protocol() -> None:
    paths = _multisurface_paths()
    openapi = DocsProjectionSpec(name="openapi", include_protocols=("http.rest",))
    openrpc = DocsProjectionSpec(name="openrpc", include_protocols=("http.jsonrpc",))

    assert {item.path for item in openapi.select(paths)} == {
        "/widgets",
        "/widgets/{item_id}",
    }
    assert {item.path for item in openrpc.select(paths)} == {"/rpc"}
    assert all("http.jsonrpc" not in item.protocols for item in openapi.select(paths))
    assert all("http.rest" not in item.protocols for item in openrpc.select(paths))


def test_docs_payload_and_uix_paths_are_normal_pathspec_entries() -> None:
    paths = _multisurface_paths()
    payload_paths = {path.path: path.docs_payload for path in paths if path.kind == "docs-payload"}
    docs_path = next(path for path in paths if path.path == "/docs")

    assert isinstance(payload_paths["/openapi.json"], DocsPayloadSpec)
    assert payload_paths["/openapi.json"].projection.include_protocols == ("http.rest",)
    assert isinstance(payload_paths["/openrpc.json"], DocsPayloadSpec)
    assert payload_paths["/openrpc.json"].projection.include_protocols == ("http.jsonrpc",)
    assert isinstance(docs_path.docs_uix, DocsUixSpec)
    assert docs_path.docs_uix.payload_path == "/openapi.json"
    assert docs_path.docs_uix.projection is None


def test_docs_tree_validation_rejects_incidental_or_missing_docs_relationships() -> None:
    validate_docs_tree(_multisurface_paths())

    with pytest.raises(ValueError, match="requires docs_payload"):
        PathSpec(path="/openapi.json", kind="docs-payload")

    with pytest.raises(ValueError, match="must reference a docs-payload"):
        validate_docs_tree(
            (
                PathSpec(
                    path="/docs",
                    kind="docs-uix",
                    docs_uix=DocsUixSpec(kind="swagger", payload_path="/missing.json"),
                ),
            )
        )

    with pytest.raises(ValueError, match="must not include JSON-RPC"):
        DocsPayloadSpec(
            kind="openapi",
            projection=DocsProjectionSpec(name="bad", include_protocols=("http.jsonrpc",)),
        )


def test_shared_jsonrpc_dispatcher_preserves_table_groups_and_rest_alias_parity() -> None:
    rest_collection, rest_member = _widget_rest_paths()
    rpc_path = _shared_rpc_path()

    assert [path.path for path in (rest_collection, rest_member, rpc_path)] == [
        "/widgets",
        "/widgets/{item_id}",
        "/rpc",
    ]
    assert {rpc_path.binding_path(op.bindings[0]) for op in rpc_path.iter_ops()} == {"/rpc"}
    assert {
        table.name: {binding.rpc_method for op in table.ops for binding in op.bindings}
        for table in rpc_path.tables
    } == {
        "Widget": {"Widget.create", "Widget.list"},
        "Account": {"Account.create", "Account.list"},
    }
    assert {op.alias for op in rest_collection.tables[0].ops} == {
        op.alias for op in rpc_path.tables[0].ops
    }


def test_pathspec_rejects_concrete_model_classes_as_canonical_identity() -> None:
    class Widget:
        pass

    with pytest.raises(TypeError, match="concrete model classes"):
        PathSpec(path="/widgets", tables=(TableSpec(model=Widget),))

    accepted = PathSpec(
        path="/widgets",
        tables=(TableSpec(name="Widget", resource="widget", model_ref="app.models:Widget"),),
    )

    assert accepted.tables[0].model_ref == "app.models:Widget"
