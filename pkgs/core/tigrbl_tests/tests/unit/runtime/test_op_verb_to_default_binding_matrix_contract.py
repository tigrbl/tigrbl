from __future__ import annotations

import pytest

from tigrbl import (
    JsonRpcTable,
    RestJsonRpcOlapTable,
    RestJsonRpcTable,
    RestTable,
    SseTable,
    StreamTable,
    WebSocketJsonRpcTable,
    WebTransportBidiTable,
    WebTransportDatagramTable,
)
from tigrbl_core._spec import OpSpec, TableProfileError, TableProfileSpec, TableSpec
from tigrbl_core._spec.table_profile_bindings import lower_table_profile_bindings


def _bindings_by_target(table: type):
    return {
        op.target: tuple(type(binding).__name__ for binding in op.bindings)
        for op in TableSpec.collect(table).ops
    }


def test_create_read_update_delete_list_verbs_lower_to_rest_defaults() -> None:
    bindings = _bindings_by_target(RestTable)

    assert bindings["create"] == ("HttpRestBindingSpec",)
    assert bindings["read"] == ("HttpRestBindingSpec",)
    assert bindings["update"] == ("HttpRestBindingSpec",)
    assert bindings["delete"] == ("HttpRestBindingSpec",)
    assert bindings["list"] == ("HttpRestBindingSpec",)


def test_create_read_update_delete_list_verbs_lower_to_jsonrpc_defaults() -> None:
    bindings = _bindings_by_target(JsonRpcTable)

    assert set(bindings) >= {"create", "read", "update", "delete", "list"}
    assert set(bindings.values()) == {("HttpJsonRpcBindingSpec",)}


def test_create_read_update_delete_list_verbs_lower_to_rest_jsonrpc_defaults() -> None:
    bindings = _bindings_by_target(RestJsonRpcTable)

    assert bindings["create"] == ("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")
    assert bindings["read"] == ("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")
    assert bindings["update"] == ("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")
    assert bindings["delete"] == ("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")
    assert bindings["list"] == ("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")


def test_stream_verbs_lower_to_stream_compatible_defaults() -> None:
    bindings = _bindings_by_target(StreamTable)

    assert bindings == {
        "tail": ("HttpStreamBindingSpec",),
        "download": ("HttpStreamBindingSpec",),
    }


def test_sse_verbs_lower_to_sse_compatible_defaults() -> None:
    bindings = _bindings_by_target(SseTable)

    assert bindings == {
        "subscribe": ("SseBindingSpec",),
        "tail": ("SseBindingSpec",),
    }


def test_websocket_jsonrpc_verbs_require_jsonrpc_framing_defaults() -> None:
    for op in TableSpec.collect(WebSocketJsonRpcTable).ops:
        assert len(op.bindings) == 1
        binding = op.bindings[0]
        assert binding.framing == "jsonrpc"
        assert binding.subprotocols == ("jsonrpc",)


def test_webtransport_stream_verbs_lower_to_lane_compatible_defaults() -> None:
    for op in TableSpec.collect(WebTransportBidiTable).ops:
        assert len(op.bindings) == 1
        binding = op.bindings[0]
        assert binding.proto == "webtransport"
        assert binding.profile == "bidi_stream"
        assert binding.lane == "bidi_stream"
        assert binding.inner_framing is None


def test_webtransport_datagram_verbs_lower_to_datagram_only_defaults() -> None:
    spec = TableSpec.collect(WebTransportDatagramTable)

    assert tuple(op.target for op in spec.ops) == ("send_datagram",)
    binding = spec.ops[0].bindings[0]
    assert binding.proto == "webtransport"
    assert binding.profile == "datagram"
    assert binding.lane == "datagram"


def test_webtransport_ops_lower_to_op_specific_lanes() -> None:
    profile = TableProfileSpec(
        kind="webtransport_ops",
        ops=(
            OpSpec(alias="create", target="create"),
            OpSpec(alias="download", target="download"),
            OpSpec(alias="upload", target="upload"),
            OpSpec(alias="send_datagram", target="send_datagram"),
        ),
    )

    lowered = lower_table_profile_bindings(WebTransportBidiTable, profile, tuple(profile.ops))
    bindings = {op.target: op.bindings[0] for op in lowered}

    assert (bindings["create"].lane, bindings["create"].inner_framing) == (
        "bidi_stream",
        "jsonrpc",
    )
    assert (bindings["download"].lane, bindings["download"].inner_framing) == (
        "unidi_server_stream",
        "bytes",
    )
    assert (bindings["upload"].lane, bindings["upload"].inner_framing) == (
        "unidi_client_stream",
        "bytes",
    )
    assert (bindings["send_datagram"].lane, bindings["send_datagram"].inner_framing) == (
        "datagram",
        "json",
    )


def test_explicit_opspec_bindings_override_verb_defaults() -> None:
    explicit = TableSpec.collect(StreamTable).ops[0].bindings[0]

    profile = TableProfileSpec(
        kind="tests.explicit",
        ops=(OpSpec(alias="create", target="create", bindings=(explicit,)),),
        custom=True,
        namespace="tests",
    )
    lowered = lower_table_profile_bindings(
        RestTable,
        profile,
        tuple(profile.bind_table(RestTable).ops),
    )

    assert lowered[0].bindings == (explicit,)


def test_custom_verbs_do_not_receive_implicit_defaults() -> None:
    profile = TableProfileSpec(
        kind="tests.custom",
        ops=(OpSpec(alias="custom_action", target="custom"),),
        custom=True,
        namespace="tests",
    )

    lowered = lower_table_profile_bindings(
        RestTable,
        profile,
        tuple(profile.bind_table(RestTable).ops),
    )

    assert lowered[0].bindings == ()


def test_custom_verbs_do_not_receive_implicit_dual_defaults() -> None:
    profile = TableProfileSpec(
        kind="tests.custom",
        ops=(OpSpec(alias="custom_action", target="custom"),),
        custom=True,
        namespace="tests",
    )

    lowered = lower_table_profile_bindings(
        RestJsonRpcTable,
        profile,
        tuple(profile.bind_table(RestJsonRpcTable).ops),
    )

    assert lowered[0].bindings == ()


def test_olap_mutation_verb_defaults_fail_closed_for_http_profile_family() -> None:
    for kind, match in (
        ("rest_olap", "REST target"),
        ("jsonrpc_olap", "JSON-RPC target"),
        ("rest_jsonrpc_olap", "REST target"),
    ):
        profile = TableProfileSpec(
            kind=kind,
            ops=(OpSpec(alias="create", target="create"),),
        )

        with pytest.raises(TableProfileError, match=match):
            lower_table_profile_bindings(
                RestJsonRpcOlapTable,
                profile,
                tuple(profile.ops),
            )


def test_unknown_verb_default_binding_fails_closed() -> None:
    bad = OpSpec(alias="read", target="read")
    profile = TableProfileSpec(
        kind="tests.unknown",
        ops=(bad,),
        custom=False,
    )

    with pytest.raises(TableProfileError, match="unsupported table profile"):
        lower_table_profile_bindings(RestTable, profile, (bad,))


@pytest.mark.parametrize(
    ("kind", "target", "match"),
    (
        ("stream", "create", "stream target"),
        ("sse", "create", "SSE target"),
        ("websocket", "read", "WebSocket target"),
        ("webtransport_datagram", "tail", "WebTransport target"),
    ),
)
def test_incompatible_verb_profile_binding_fails_closed(
    kind: str,
    target: str,
    match: str,
) -> None:
    profile = TableProfileSpec(
        kind=kind,
        ops=(OpSpec(alias=str(target), target=target),),  # type: ignore[arg-type]
    )

    with pytest.raises(TableProfileError, match=match):
        lower_table_profile_bindings(RestTable, profile, tuple(profile.ops))


def test_default_binding_matrix_output_is_deterministic() -> None:
    assert TableSpec.collect(RestTable).ops == TableSpec.collect(RestTable).ops
