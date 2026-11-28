from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    JsonRpcFramingSpec,
    TextFramingSpec,
    PathSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    validate_path_binding,
)


VALID_PATHKIND_BINDINGS = (
    (
        "resource",
        HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"),
    ),
    (
        "resource",
        HttpRestBindingSpec(proto="https.rest", methods=("GET",), path="/items"),
    ),
    (
        "jsonrpc",
        HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Item.list"),
    ),
    (
        "jsonrpc",
        HttpJsonRpcBindingSpec(proto="https.jsonrpc", rpc_method="Item.list"),
    ),
    (
        "stream",
        HttpStreamBindingSpec(proto="http.stream", path="/items"),
    ),
    (
        "stream",
        HttpStreamBindingSpec(proto="https.stream", path="/items"),
    ),
    ("sse", SseBindingSpec(proto="http.sse", path="/items")),
    ("sse", SseBindingSpec(proto="https.sse", path="/items")),
    (
        "ws-jsonrpc",
        WsBindingSpec(
            proto="ws",
            path="/items",
            framing=JsonRpcFramingSpec(),
            subprotocols=("jsonrpc",),
        ),
    ),
    (
        "wss-jsonrpc",
        WsBindingSpec(
            proto="wss",
            path="/items",
            framing=JsonRpcFramingSpec(),
            subprotocols=("jsonrpc",),
        ),
    ),
    ("websocket", WsBindingSpec(proto="ws", path="/items", framing=TextFramingSpec())),
    ("websocket", WsBindingSpec(proto="wss", path="/items", framing=TextFramingSpec())),
    ("webtransport", WebTransportBindingSpec(path="/items")),
)


@pytest.mark.parametrize(("kind", "binding"), VALID_PATHKIND_BINDINGS)
def test_valid_pathkind_binding_matrix(kind: str, binding: object) -> None:
    validate_path_binding(PathSpec(path="/items", kind=kind), binding)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kind", "binding", "expected"),
    (
        (
            "stream",
            HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"),
            "resource",
        ),
        (
            "resource",
            HttpStreamBindingSpec(proto="http.stream", path="/items"),
            "stream",
        ),
        (
            "jsonrpc",
            WsBindingSpec(proto="ws", path="/items", framing=JsonRpcFramingSpec()),
            "ws-jsonrpc",
        ),
        (
            "ws-jsonrpc",
            WsBindingSpec(proto="wss", path="/items", framing=JsonRpcFramingSpec()),
            "wss-jsonrpc",
        ),
        ("websocket", SseBindingSpec(proto="http.sse", path="/items"), "sse"),
        ("webtransport", WsBindingSpec(proto="ws", path="/items"), "websocket"),
    ),
)
def test_invalid_pathkind_binding_matrix_fails_closed(
    kind: str,
    binding: object,
    expected: str,
) -> None:
    with pytest.raises(ValueError, match=expected):
        validate_path_binding(PathSpec(path="/items", kind=kind), binding)  # type: ignore[arg-type]


def test_pathkind_validation_never_silently_downgrades_secure_socket() -> None:
    path = PathSpec(path="/items", kind="ws-jsonrpc")
    binding = WsBindingSpec(proto="wss", path="/items", framing=JsonRpcFramingSpec())

    with pytest.raises(ValueError, match="wss-jsonrpc"):
        validate_path_binding(path, binding)
