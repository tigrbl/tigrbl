from __future__ import annotations

import pytest

from tigrbl import (
    JsonRpcTable,
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
