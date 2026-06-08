from __future__ import annotations

from dataclasses import replace

import pytest

from tigrbl import (
    JsonRpcTable,
    RestTable,
    WebSocketJsonRpcTable,
    WebTransportBidiTable,
    WebTransportDatagramTable,
)
from tigrbl_core._spec import (
    HttpStreamBindingSpec,
    OpSpec,
    TableProfileError,
    TableProfileSpec,
    TableSpec,
    WebTransportBindingSpec,
    lower_binding_tokens_for_ops,
    lower_table_profile_bindings,
)
from tigrbl_core._spec.table_profile_spec import make_table_profile


def _tokens(table: type):
    spec = TableSpec.collect(table)
    return lower_binding_tokens_for_ops(table, spec.table_profile, tuple(spec.ops))


def test_binding_tokens_have_canonical_shape() -> None:
    token = _tokens(RestTable)[0]

    assert token.source == "table_profile"
    assert token.profile == "rest"
    assert token.op_alias == "create"
    assert token.op_target == "create"
    assert token.binding_kind == "http.rest"
    assert token.path == "/create"
    assert token.methods == ("POST",)
    assert token.framing == "json"
    assert token.exchange == "request_response"


def test_table_profile_defaults_lower_to_ordered_binding_tokens() -> None:
    tokens = _tokens(JsonRpcTable)

    assert tuple(token.op_alias for token in tokens) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )
    assert {token.binding_kind for token in tokens} == {"http.jsonrpc"}
    assert tuple(token.rpc_method for token in tokens) == tuple(
        f"JsonRpcTable.{alias}" for alias in (
            "create",
            "read",
            "update",
            "replace",
            "delete",
            "list",
            "clear",
        )
    )


def test_opspec_binding_overrides_are_applied_before_defaults() -> None:
    explicit = HttpStreamBindingSpec(proto="http.stream", path="/explicit")

    class Explicit(RestTable):
        __abstract__ = True
        TABLE_PROFILE = TableProfileSpec(
            kind="explicit_override",
            ops=(OpSpec(alias="tail", target="tail", bindings=(explicit,)),),
            custom=True,
            namespace="tests",
        )

    spec = TableSpec.collect(Explicit)
    tokens = lower_binding_tokens_for_ops(Explicit, spec.table_profile, tuple(spec.ops))

    assert tuple(op.bindings for op in spec.ops) == ((explicit,),)
    assert tokens[0].source == "explicit"
    assert tokens[0].binding_kind == "http.stream"
    assert tokens[0].path == "/explicit"


def test_rest_binding_tokens_include_method_path_and_media_type() -> None:
    tokens = {token.op_alias: token for token in _tokens(RestTable)}

    assert tokens["create"].methods == ("POST",)
    assert tokens["read"].methods == ("GET",)
    assert tokens["update"].methods == ("PATCH",)
    assert tokens["replace"].methods == ("PUT",)
    assert tokens["delete"].methods == ("DELETE",)
    assert tokens["list"].path == "/list"
    assert tokens["list"].framing == "json"


def test_jsonrpc_binding_tokens_include_method_and_framing() -> None:
    read = {token.op_alias: token for token in _tokens(JsonRpcTable)}["read"]

    assert read.binding_kind == "http.jsonrpc"
    assert read.rpc_method == "JsonRpcTable.read"
    assert read.framing == "jsonrpc"


def test_websocket_binding_tokens_include_framing_and_session_lanes() -> None:
    tokens = _tokens(WebSocketJsonRpcTable)

    assert {token.binding_kind for token in tokens} == {"ws"}
    assert {token.framing for token in tokens} == {"jsonrpc"}
    assert {tuple(binding.subprotocols) for op in TableSpec.collect(WebSocketJsonRpcTable).ops for binding in op.bindings} == {
        ("jsonrpc",)
    }


def test_webtransport_binding_tokens_include_stream_and_datagram_lanes() -> None:
    stream_tokens = _tokens(WebTransportBidiTable)
    datagram_tokens = _tokens(WebTransportDatagramTable)

    assert {token.binding_kind for token in stream_tokens} == {"webtransport"}
    assert {token.lane for token in stream_tokens} == {"bidi_stream"}
    assert {token.lane for token in datagram_tokens} == {"datagram"}
    assert {token.op_target for token in datagram_tokens} == {"send_datagram"}


def test_binding_token_lowering_rejects_unsupported_transport_profile_pairs() -> None:
    profile = make_table_profile("stream", ())
    op = OpSpec(alias="create", target="create")

    with pytest.raises(TableProfileError, match="stream target"):
        lower_table_profile_bindings(RestTable, profile, (op,))


def test_binding_token_lowering_rejects_unsupported_framing_fallback() -> None:
    with pytest.raises(ValueError, match="inner framing"):
        WebTransportBindingSpec(profile="datagram", inner_framing="jsonrpc")


def test_binding_token_lowering_reports_source_precedence() -> None:
    default_token = _tokens(RestTable)[0]
    explicit_token = replace(default_token, source="explicit", precedence=0)

    assert explicit_token.precedence < default_token.precedence
    assert default_token.source == "table_profile"


def test_binding_token_lowering_output_is_deterministic() -> None:
    assert _tokens(WebTransportBidiTable) == _tokens(WebTransportBidiTable)


def test_binding_token_lowering_does_not_mutate_source_specs() -> None:
    before = tuple(RestTable.TABLE_PROFILE.ops)
    _ = TableSpec.collect(RestTable)
    after = tuple(RestTable.TABLE_PROFILE.ops)

    assert before == after
    assert all(not op.bindings for op in RestTable.TABLE_PROFILE.ops)
