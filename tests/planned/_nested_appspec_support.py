from __future__ import annotations

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
)


def op(alias: str, target: str, *bindings: object, arity: str = "collection") -> OpSpec:
    return OpSpec(
        alias=alias,
        target=target,  # type: ignore[arg-type]
        arity=arity,  # type: ignore[arg-type]
        bindings=tuple(bindings),  # type: ignore[arg-type]
    )


def widget_rest_paths() -> tuple[PathSpec, PathSpec]:
    collection = PathSpec(
        path="/widgets",
        tables=(
            TableSpec(
                name="Widget",
                resource="widget",
                model_ref="app.models:Widget",
                ops=(
                    op(
                        "create",
                        "create",
                        HttpRestBindingSpec(
                            proto="http.rest", methods=("POST",), path="/widgets"
                        ),
                    ),
                    op(
                        "list",
                        "list",
                        HttpRestBindingSpec(
                            proto="http.rest", methods=("GET",), path="/widgets"
                        ),
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
                    op(
                        "read",
                        "read",
                        HttpRestBindingSpec(
                            proto="http.rest",
                            methods=("GET",),
                            path="/widgets/{item_id}",
                        ),
                        arity="member",
                    ),
                    op(
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


def shared_rpc_path() -> PathSpec:
    return PathSpec(
        path="/rpc",
        kind="jsonrpc",
        tables=(
            TableSpec(
                name="Widget",
                resource="widget",
                model_ref="app.models:Widget",
                ops=(
                    op(
                        "create",
                        "create",
                        HttpJsonRpcBindingSpec(
                            proto="http.jsonrpc", rpc_method="Widget.create"
                        ),
                    ),
                    op(
                        "list",
                        "list",
                        HttpJsonRpcBindingSpec(
                            proto="http.jsonrpc", rpc_method="Widget.list"
                        ),
                    ),
                ),
            ),
            TableSpec(
                name="Account",
                resource="account",
                model_ref="app.models:Account",
                ops=(
                    op(
                        "create",
                        "create",
                        HttpJsonRpcBindingSpec(
                            proto="http.jsonrpc", rpc_method="Account.create"
                        ),
                    ),
                    op(
                        "list",
                        "list",
                        HttpJsonRpcBindingSpec(
                            proto="http.jsonrpc", rpc_method="Account.list"
                        ),
                    ),
                ),
            ),
        ),
    )


def multisurface_paths() -> tuple[PathSpec, ...]:
    public_http = DocsProjectionSpec(
        name="public-http",
        include_protocols=("http.rest",),
    )
    public_rpc = DocsProjectionSpec(
        name="public-rpc",
        include_protocols=("http.jsonrpc",),
    )
    rest_collection, rest_member = widget_rest_paths()
    rpc = shared_rpc_path()
    return (
        rest_collection,
        rest_member,
        rpc,
        PathSpec(
            path="/ws",
            kind="websocket",
            ops=(op("socket_events", "custom", WsBindingSpec(proto="ws", path="/ws")),),
        ),
        PathSpec(
            path="/events",
            kind="sse",
            ops=(
                op(
                    "event_stream",
                    "tail",
                    SseBindingSpec(proto="http.sse", path="/events"),
                ),
            ),
        ),
        PathSpec(
            path="/transport",
            kind="webtransport",
            ops=(
                op(
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


def multisurface_appspec() -> AppSpec:
    return AppSpec(
        title="Nested AppSpec Corpus",
        routers=(
            RouterSpec(
                name="api",
                prefix="/api",
                paths=multisurface_paths(),
                middlewares=("authn", "audit"),
            ),
        ),
    )
