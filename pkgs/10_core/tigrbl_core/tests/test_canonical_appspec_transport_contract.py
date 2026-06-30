from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    AppSpec,
    DocsProjectionSpec,
    EngineSpec,
    HttpJsonRpcBindingSpec,
    HttpStreamBindingSpec,
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
    WsBindingSpec,
    resolve_engine_name,
    validate_path_binding,
)


def _op(alias: str, *bindings: object, engine_name: str | None = None) -> OpSpec:
    return OpSpec(
        alias=alias,
        target="custom",
        bindings=tuple(bindings),
        engine_name=engine_name,
    )


def test_appspec_engine_inventory_requires_unique_engine_names() -> None:
    primary = EngineSpec(kind="sqlite", memory=True, name="primary")
    audit = EngineSpec(kind="sqlite", memory=True, name="audit")

    spec = AppSpec(engines=(primary, audit), engine_name="primary")

    assert spec.engines == (primary, audit)
    assert resolve_engine_name(spec) == "primary"

    with pytest.raises(ValueError, match="Duplicate EngineSpec.name"):
        AppSpec(engines=(primary, EngineSpec(kind="sqlite", memory=True, name="primary")))

    with pytest.raises(ValueError, match="must declare EngineSpec.name"):
        AppSpec(engines=(EngineSpec(kind="sqlite", memory=True),))


def test_engine_name_binding_uses_nearest_scope_precedence() -> None:
    primary = EngineSpec(kind="sqlite", memory=True, name="primary")
    reporting = EngineSpec(kind="postgres", name="reporting")
    op = _op("rotate", engine_name="reporting")
    table = TableSpec(name="keys", engine_name="primary", ops=(op,))
    router = RouterSpec(name="admin", engine_name="primary")
    spec = AppSpec(engines=(primary, reporting), engine_name="primary")

    assert resolve_engine_name(spec, router=router, table=table, op=op) == "reporting"
    assert resolve_engine_name(spec, router=router, table=table) == "primary"

    with pytest.raises(ValueError, match="unknown engine name"):
        AppSpec(engines=(primary,), routers=(RouterSpec(name="bad", engine_name="missing"),))


def test_pathspec_rejects_engine_ownership() -> None:
    with pytest.raises(ValueError, match="does not own engines"):
        PathSpec.from_dict({"path": "/widgets", "engine_name": "primary"})

    with pytest.raises(ValueError, match="does not own engines"):
        PathSpec.from_dict({"path": "/widgets", "engine": "sqlite://:memory:"})


def test_transport_path_kinds_converge_with_bindings() -> None:
    stream = PathSpec(path="/widgets/tail", kind="stream")
    validate_path_binding(
        stream,
        HttpStreamBindingSpec(proto="http.stream", path="/widgets/tail"),
    )

    rpc = PathSpec(path="/rpc", kind="jsonrpc")
    validate_path_binding(
        rpc,
        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create", endpoint="/rpc"),
    )

    socket_rpc = PathSpec(path="/ws/rpc", kind="ws-jsonrpc")
    validate_path_binding(
        socket_rpc,
        WsBindingSpec(proto="ws", path="/ws/rpc", framing=JsonRpcFramingSpec(), subprotocols=("jsonrpc",)),
    )
    secure_socket_rpc = PathSpec(path="/wss/rpc", kind="wss-jsonrpc")
    validate_path_binding(
        secure_socket_rpc,
        WsBindingSpec(
            proto="wss",
            path="/wss/rpc",
            framing=JsonRpcFramingSpec(),
            subprotocols=("jsonrpc",),
        ),
    )

    with pytest.raises(ValueError, match="requires PathSpec.kind"):
        validate_path_binding(
            PathSpec(path="/ws/rpc", kind="websocket"),
            WsBindingSpec(proto="ws", path="/ws/rpc", framing=JsonRpcFramingSpec(), subprotocols=("jsonrpc",)),
        )


def test_websocket_jsonrpc_and_ndjson_subprotocols_are_required() -> None:
    binding = WsBindingSpec(
        proto="wss",
        path="/wss/rpc",
        framing=JsonRpcFramingSpec(),
        subprotocols=("JSONRPC",),
    )

    assert binding.subprotocols == ("jsonrpc",)

    implicit = WsBindingSpec(proto="ws", path="/ws/rpc", framing=JsonRpcFramingSpec())

    assert implicit.subprotocols == ("jsonrpc",)

    with pytest.raises(ValueError, match="conflicts with subprotocols"):
        WsBindingSpec(
            proto="ws",
            path="/ws/rpc",
            framing=JsonRpcFramingSpec(),
            subprotocols=("v2",),
        )

    derived = WsBindingSpec(proto="ws", path="/ws/ndjson", framing=NdjsonFramingSpec())

    assert derived.subprotocols == ("ndjson",)

    validate_path_binding(
        PathSpec(path="/ws/ndjson", kind="ws-ndjson"),
        WsBindingSpec(
            proto="ws",
            path="/ws/ndjson",
            framing=NdjsonFramingSpec(),
            subprotocols=("ndjson",),
        ),
    )
    validate_path_binding(
        PathSpec(path="/wss/ndjson", kind="wss-ndjson"),
        WsBindingSpec(
            proto="wss",
            path="/wss/ndjson",
            framing=NdjsonFramingSpec(),
            subprotocols=("ndjson",),
        ),
    )


def test_docs_projection_selects_transport_metadata_explicitly() -> None:
    path = PathSpec(
        path="/ws/rpc",
        kind="ws-jsonrpc",
        ops=(
            _op(
                "events",
                WsBindingSpec(
                    proto="ws",
                    path="/ws/rpc",
                    framing=JsonRpcFramingSpec(),
                    subprotocols=("jsonrpc",),
                ),
            ),
        ),
    )
    projection = DocsProjectionSpec(
        name="websocket-rpc",
        include_protocols=("ws",),
        include_path_kinds=("ws-jsonrpc",),
        include_framings=("jsonrpc",),
        include_subprotocols=("jsonrpc",),
    )

    selected = projection.select((path,))

    assert len(selected) == 1
    assert selected[0].path == "/ws/rpc"
    assert selected[0].path_kind == "ws-jsonrpc"
    assert selected[0].protocols == ("ws",)
    assert selected[0].framings == ("jsonrpc",)
    assert selected[0].subprotocols == ("jsonrpc",)
