from __future__ import annotations

from dataclasses import replace

import pytest

from tigrbl import (
    JsonRpcOlapTable,
    JsonRpcOltpTable,
    JsonRpcTable,
    RestOlapTable,
    RestJsonRpcOlapTable,
    RestJsonRpcOltpTable,
    RestJsonRpcTable,
    RestOltpTable,
    RestTable,
    WebSocketJsonRpcTable,
    WebTransportBidiTable,
    WebTransportDatagramTable,
)
from tigrbl_core._spec import (
    HttpStreamBindingSpec,
    BytesFramingSpec,
    JsonFramingSpec,
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
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
    assert token.path == "/resttable"
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


def test_rest_jsonrpc_profile_lowers_to_ordered_dual_tokens() -> None:
    tokens = _tokens(RestJsonRpcTable)

    assert tuple((token.op_alias, token.binding_kind) for token in tokens[:4]) == (
        ("create", "http.rest"),
        ("create", "http.jsonrpc"),
        ("read", "http.rest"),
        ("read", "http.jsonrpc"),
    )
    assert {token.binding_kind for token in tokens} == {"http.rest", "http.jsonrpc"}
    assert {
        token.rpc_method
        for token in tokens
        if token.binding_kind == "http.jsonrpc"
    } == {
        f"RestJsonRpcTable.{alias}"
        for alias in ("create", "read", "update", "replace", "delete", "list", "clear")
    }


def test_rest_jsonrpc_oltp_and_olap_tokens_keep_semantic_targets() -> None:
    oltp_tokens = _tokens(RestJsonRpcOltpTable)
    olap_tokens = _tokens(RestJsonRpcOlapTable)

    assert tuple(token.binding_kind for token in oltp_tokens[:2]) == (
        "http.rest",
        "http.jsonrpc",
    )
    assert {token.op_target for token in oltp_tokens} == {
        "create",
        "read",
        "update",
        "replace",
        "merge",
        "delete",
        "list",
        "count",
        "exists",
    }
    assert {token.op_target for token in olap_tokens} == {
        "read",
        "list",
        "count",
        "exists",
        "aggregate",
        "group_by",
    }
    assert {token.binding_kind for token in olap_tokens} == {
        "http.rest",
        "http.jsonrpc",
    }


def test_oltp_and_olap_token_details_preserve_protocol_specific_selectors() -> None:
    rest_oltp = {token.op_alias: token for token in _tokens(RestOltpTable)}
    rest_olap = {token.op_alias: token for token in _tokens(RestOlapTable)}
    jsonrpc_oltp = {token.op_alias: token for token in _tokens(JsonRpcOltpTable)}
    jsonrpc_olap = {token.op_alias: token for token in _tokens(JsonRpcOlapTable)}

    assert rest_oltp["merge"].methods == ("PATCH",)
    assert rest_oltp["merge"].path == "/restoltptable/{item_id}"
    assert rest_olap["aggregate"].methods == ("POST",)
    assert rest_olap["aggregate"].path == "/restolaptable"
    assert jsonrpc_oltp["merge"].rpc_method == "JsonRpcOltpTable.merge"
    assert jsonrpc_oltp["merge"].framing == "jsonrpc"
    assert jsonrpc_olap["aggregate"].rpc_method == "JsonRpcOlapTable.aggregate"
    assert jsonrpc_olap["aggregate"].framing == "jsonrpc"


def test_dual_tokens_keep_independent_rest_path_and_jsonrpc_method() -> None:
    pairs = {}
    for token in _tokens(RestJsonRpcOltpTable):
        pairs.setdefault(token.op_alias, {})[token.binding_kind] = token

    merge = pairs["merge"]

    assert merge["http.rest"].path == "/restjsonrpcoltptable/{item_id}"
    assert merge["http.rest"].methods == ("PATCH",)
    assert merge["http.rest"].rpc_method is None
    assert merge["http.jsonrpc"].path == ""
    assert merge["http.jsonrpc"].methods == ()
    assert merge["http.jsonrpc"].rpc_method == "RestJsonRpcOltpTable.merge"


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
    assert tokens["list"].path == "/resttable"
    assert tokens["list"].framing == "json"


def test_jsonrpc_binding_tokens_include_method_and_framing() -> None:
    read = {token.op_alias: token for token in _tokens(JsonRpcTable)}["read"]

    assert read.binding_kind == "http.jsonrpc"
    assert read.rpc_method == "JsonRpcTable.read"
    assert read.framing == "jsonrpc"


def test_websocket_binding_tokens_include_framing_and_session_lanes() -> None:
    tokens = _tokens(WebSocketJsonRpcTable)

    assert {token.binding_kind for token in tokens} == {"ws"}
    assert {token.protocol_kind for token in tokens} == {"ws"}
    assert {token.framing for token in tokens} == {"jsonrpc"}
    assert {token.framing_kind for token in tokens} == {"jsonrpc"}
    assert {token.framing_spec for token in tokens} == {"JsonRpcFramingSpec"}
    assert {token.required_subprotocol for token in tokens} == {"jsonrpc"}
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


def test_webtransport_op_lane_binding_contract() -> None:
    profile = TableProfileSpec(
        kind="webtransport_ops",
        ops=(
            OpSpec(alias="create", target="create"),
            OpSpec(alias="tail", target="tail"),
            OpSpec(alias="append_chunk", target="append_chunk"),
            OpSpec(alias="send_datagram", target="send_datagram"),
            OpSpec(alias="open_unidi_stream", target="open_unidi_stream"),
        ),
    )

    lowered = lower_table_profile_bindings(WebTransportBidiTable, profile, tuple(profile.ops))
    by_target = {op.target: op.bindings[0] for op in lowered}

    assert (by_target["create"].lane, by_target["create"].inner_framing) == (
        "bidi_stream",
        JsonRpcFramingSpec(),
    )
    assert (by_target["tail"].lane, by_target["tail"].inner_framing) == (
        "unidi_server_stream",
        NdjsonFramingSpec(),
    )
    assert (
        by_target["append_chunk"].lane,
        by_target["append_chunk"].inner_framing,
    ) == ("unidi_client_stream", BytesFramingSpec())
    assert (
        by_target["send_datagram"].lane,
        by_target["send_datagram"].inner_framing,
    ) == ("datagram", JsonFramingSpec())
    assert (
        by_target["open_unidi_stream"].lane,
        by_target["open_unidi_stream"].inner_framing,
    ) == ("bidi_stream", JsonRpcFramingSpec())


def test_canonical_binding_token_typed_framing_fields() -> None:
    profile = TableProfileSpec(
        kind="tests.explicit-ws-jsonrpc",
        ops=(
            OpSpec(
                alias="create",
                target="create",
                bindings=(
                    WebTransportBindingSpec(
                        profile="bidi_stream",
                        inner_framing=JsonRpcFramingSpec(),
                    ),
                ),
            ),
        ),
        custom=True,
        namespace="tests",
    )
    op = tuple(profile.ops)[0]

    token = lower_binding_tokens_for_ops(WebTransportBidiTable, profile, (op,))[0]

    assert token.protocol_kind == "webtransport"
    assert token.framing == ""
    assert token.framing_kind == ""
    assert token.framing_spec == ""
    assert token.lane == "bidi_stream"
    assert token.inner_framing == "jsonrpc"


def test_binding_token_lowering_rejects_unsupported_transport_profile_pairs() -> None:
    profile = make_table_profile("stream", ())
    op = OpSpec(alias="create", target="create")

    with pytest.raises(TableProfileError, match="stream target"):
        lower_table_profile_bindings(RestTable, profile, (op,))


def test_binding_token_lowering_rejects_unsupported_framing_fallback() -> None:
    with pytest.raises(TypeError, match="FramingSpec"):
        WebTransportBindingSpec(profile="datagram", inner_framing="ndjson")


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


@pytest.mark.parametrize(
    "table",
    (RestJsonRpcTable, RestJsonRpcOltpTable, RestJsonRpcOlapTable),
)
def test_dual_binding_token_lowering_does_not_mutate_source_specs(table: type) -> None:
    before = tuple(table.TABLE_PROFILE.ops)
    _ = TableSpec.collect(table)
    after = tuple(table.TABLE_PROFILE.ops)

    assert before == after
    assert all(not op.bindings for op in table.TABLE_PROFILE.ops)
