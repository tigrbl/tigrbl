from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    BytesFramingSpec,
    HttpJsonRpcProtocolBindingSpec,
    HttpRestProtocolBindingSpec,
    JsonFramingSpec,
    JsonRpcFramingSpec,
    OpSpec,
    TableSpec,
    WebSocketProtocolBindingSpec,
    WebTransportProtocolBindingSpec,
    project_binding_runtime_metadata,
)


def _widget_ops() -> tuple[OpSpec, ...]:
    return (
        OpSpec(
            alias="create",
            target="create",
            bindings=(
                HttpRestProtocolBindingSpec(
                    path="/widgets",
                    methods=("POST",),
                    framing=JsonFramingSpec(),
                ),
                HttpJsonRpcProtocolBindingSpec(
                    path="/rpc",
                    method="Widget.create",
                    framing=JsonRpcFramingSpec(),
                ),
                WebSocketProtocolBindingSpec(
                    path="/ws/widgets",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="read",
            target="read",
            bindings=(
                HttpRestProtocolBindingSpec(
                    path="/widgets/{id}",
                    methods=("GET",),
                    framing=JsonFramingSpec(),
                ),
                HttpJsonRpcProtocolBindingSpec(
                    path="/rpc",
                    method="Widget.read",
                    framing=JsonRpcFramingSpec(),
                ),
                WebSocketProtocolBindingSpec(
                    path="/ws/widgets",
                    framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="subscribe",
            target="subscribe",
            bindings=(
                WebTransportProtocolBindingSpec(
                    path="/wt/widgets",
                    control_stream={
                        "kind": "bidi_stream",
                        "opens": "first",
                        "purpose": "session_control",
                        "framing": JsonRpcFramingSpec(),
                    },
                    streams=(
                        {
                            "name": "commands",
                            "kind": "bidi_stream",
                            "purpose": "jsonrpc_commands",
                            "framing": JsonRpcFramingSpec(),
                        },
                        {
                            "name": "events",
                            "kind": "unidi_server_stream",
                            "purpose": "subscription_events",
                            "framing": JsonRpcFramingSpec(),
                        },
                        {
                            "name": "uploads",
                            "kind": "unidi_client_stream",
                            "purpose": "client_upload_commands",
                            "framing": JsonRpcFramingSpec(),
                        },
                    ),
                    datagrams=(
                        {
                            "name": "acks",
                            "purpose": "low_latency_jsonrpc_ack",
                            "framing": JsonRpcFramingSpec(),
                        },
                    ),
                ),
            ),
        ),
    )


def test_protocol_binding_appspec_schema_authors_path_not_endpoint_or_subprotocols() -> None:
    create = _widget_ops()[0]
    rest, rpc, ws = create.bindings

    assert isinstance(rest, HttpRestProtocolBindingSpec)
    assert rest.path == "/widgets"
    assert rest.methods == ("POST",)
    assert isinstance(rest.framing, JsonFramingSpec)
    assert not hasattr(rest, "endpoint")
    assert not hasattr(rest, "rpc_method")

    assert isinstance(rpc, HttpJsonRpcProtocolBindingSpec)
    assert rpc.path == "/rpc"
    assert rpc.method == "Widget.create"
    assert isinstance(rpc.framing, JsonRpcFramingSpec)
    assert not hasattr(rpc, "endpoint")
    assert not hasattr(rpc, "rpc_method")

    assert isinstance(ws, WebSocketProtocolBindingSpec)
    assert ws.path == "/ws/widgets"
    assert isinstance(ws.framing, JsonRpcFramingSpec)
    assert not hasattr(ws, "subprotocols")


def test_webtransport_protocol_binding_schema_declares_named_jsonrpc_lanes() -> None:
    binding = _widget_ops()[2].bindings[0]

    assert isinstance(binding, WebTransportProtocolBindingSpec)
    assert binding.path == "/wt/widgets"
    assert binding.control_stream is not None
    assert binding.control_stream.kind == "bidi_stream"
    assert binding.control_stream.opens == "first"
    assert binding.control_stream.purpose == "session_control"
    assert isinstance(binding.control_stream.framing, JsonRpcFramingSpec)
    assert tuple(stream.name for stream in binding.streams) == (
        "commands",
        "events",
        "uploads",
    )
    assert {stream.kind for stream in binding.streams} == {
        "bidi_stream",
        "unidi_server_stream",
        "unidi_client_stream",
    }
    assert {type(stream.framing) for stream in binding.streams} == {JsonRpcFramingSpec}
    assert tuple(datagram.name for datagram in binding.datagrams) == ("acks",)
    assert isinstance(binding.datagrams[0].framing, JsonRpcFramingSpec)


def test_protocol_binding_runtime_metadata_derives_not_authors_session_labels() -> None:
    create = _widget_ops()[0]
    _rest, rpc, ws = create.bindings
    wt = _widget_ops()[2].bindings[0]

    rpc_metadata = project_binding_runtime_metadata(rpc)
    ws_metadata = project_binding_runtime_metadata(ws)
    wt_metadata = project_binding_runtime_metadata(wt)

    assert rpc_metadata["proto"] == "http.jsonrpc"
    assert rpc_metadata["framing"] == "jsonrpc"
    assert "endpoint" not in rpc_metadata

    assert ws_metadata["websocket_subprotocol"] == "jsonrpc"
    assert "required_subprotocol" not in ws_metadata
    assert "subprotocols" not in ws_metadata

    assert wt_metadata["control_stream"]["framing"] == "jsonrpc"
    assert {row["framing"] for row in wt_metadata["streams"]} == {"jsonrpc"}
    assert wt_metadata["datagrams"][0]["framing"] == "jsonrpc"
    assert "inner_framing_spec" not in wt_metadata


def test_webtransport_protocol_binding_allows_lane_ops_without_control_stream() -> None:
    binding = WebTransportProtocolBindingSpec(
        path="/wt/widgets",
        streams=(
            {
                "name": "events",
                "kind": "unidi_server_stream",
                "framing": JsonRpcFramingSpec(),
            },
        ),
        datagrams=(
            {
                "name": "acks",
                "framing": BytesFramingSpec(),
            },
        ),
    )

    metadata = project_binding_runtime_metadata(binding)

    assert binding.control_stream is None
    assert "control_stream" not in metadata
    assert metadata["streams"][0]["framing"] == "jsonrpc"
    assert metadata["datagrams"][0]["framing"] == "bytes"


def test_protocol_binding_schema_negative_corpus_fails_closed() -> None:
    with pytest.raises(TypeError):
        HttpJsonRpcProtocolBindingSpec(  # type: ignore[call-arg]
            endpoint="/rpc",
            method="Widget.create",
        )
    with pytest.raises(TypeError):
        WebSocketProtocolBindingSpec(  # type: ignore[call-arg]
            path="/ws/widgets",
            framing=JsonRpcFramingSpec(),
            subprotocols=("jsonrpc",),
        )
    with pytest.raises(TypeError, match="FramingSpec"):
        HttpRestProtocolBindingSpec(
            path="/widgets",
            methods=("GET",),
            framing="json",  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="unique"):
        WebTransportProtocolBindingSpec(
            path="/wt/widgets",
            control_stream={
                "kind": "bidi_stream",
                "opens": "first",
                "framing": JsonRpcFramingSpec(),
            },
            streams=(
                {
                    "name": "events",
                    "kind": "unidi_server_stream",
                    "framing": JsonRpcFramingSpec(),
                },
            ),
            datagrams=(
                {
                    "name": "events",
                    "framing": BytesFramingSpec(),
                },
            ),
        )


def test_table_spec_accepts_multiple_protocol_bindings_on_multiple_ops() -> None:
    class Widget:
        OPS = _widget_ops()

    spec = TableSpec.collect(Widget)

    assert tuple(op.alias for op in spec.ops) == ("create", "read", "subscribe")
    assert tuple(len(op.bindings) for op in spec.ops) == (3, 3, 1)
