from __future__ import annotations

import pytest

from tigrbl import (
    CrudTable,
    EventStreamTable,
    JsonRpcBulkCrudTable,
    JsonRpcOlapTable,
    JsonRpcOltpTable,
    JsonRpcTable,
    OlapTable,
    OltpTable,
    RestJsonRpcOlapTable,
    RestJsonRpcOltpTable,
    RestJsonRpcTable,
    RestBulkCrudTable,
    RestOlapTable,
    RestOltpTable,
    RestTable,
    RealtimeTable,
    SseTable,
    StreamTable,
    WebSocketJsonRpcTable,
    WebTransportBidiTable,
    WebTransportClientStreamTable,
    WebTransportDatagramTable,
    WebTransportServerStreamTable,
    WebTransportTable,
)
from tigrbl_core._spec import OpSpec, TableProfileError, TableProfileSpec, TableSpec
from tigrbl_core._spec.table_profile_bindings import lower_binding_tokens_for_ops


def _spec(table: type):
    return TableSpec.collect(table)


def _binding_names(table: type) -> tuple[str, ...]:
    return tuple(
        type(binding).__name__
        for op in _spec(table).ops
        for binding in tuple(op.bindings or ())
    )


def test_crudtable_abstract_selects_ops_without_bindings() -> None:
    spec = _spec(CrudTable)

    assert spec.table_profile.role == "abstract"
    assert tuple(op.target for op in spec.ops) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )
    assert all(not op.bindings for op in spec.ops)


def test_realtimetable_abstract_selects_ops_without_bindings() -> None:
    spec = _spec(RealtimeTable)

    assert spec.table_profile.role == "abstract"
    assert tuple(op.target for op in spec.ops) == ("publish", "subscribe", "tail")
    assert all(not op.bindings for op in spec.ops)


def test_resttable_lowers_to_http_rest_bindings() -> None:
    assert set(_binding_names(RestTable)) == {"HttpRestBindingSpec"}


def test_jsonrpctable_lowers_to_http_jsonrpc_bindings() -> None:
    assert set(_binding_names(JsonRpcTable)) == {"HttpJsonRpcBindingSpec"}


def test_rest_jsonrpc_table_lowers_to_both_http_binding_families() -> None:
    for op in _spec(RestJsonRpcTable).ops:
        assert tuple(type(binding).__name__ for binding in op.bindings) == (
            "HttpRestBindingSpec",
            "HttpJsonRpcBindingSpec",
        )


def test_bulk_crud_protocol_table_profiles_lower_to_selected_http_families() -> None:
    expected_targets = (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_delete",
    )

    assert tuple(op.target for op in _spec(RestBulkCrudTable).ops) == expected_targets
    assert tuple(op.target for op in _spec(JsonRpcBulkCrudTable).ops) == expected_targets
    assert set(_binding_names(RestBulkCrudTable)) == {"HttpRestBindingSpec"}
    assert set(_binding_names(JsonRpcBulkCrudTable)) == {"HttpJsonRpcBindingSpec"}


def test_oltp_protocol_table_profiles_lower_to_selected_http_families() -> None:
    expected_targets = (
        "create",
        "read",
        "update",
        "replace",
        "merge",
        "delete",
        "list",
        "count",
        "exists",
    )

    assert tuple(op.target for op in _spec(RestOltpTable).ops) == expected_targets
    assert tuple(op.target for op in _spec(JsonRpcOltpTable).ops) == expected_targets
    assert tuple(op.target for op in _spec(RestJsonRpcOltpTable).ops) == expected_targets
    assert set(_binding_names(RestOltpTable)) == {"HttpRestBindingSpec"}
    assert set(_binding_names(JsonRpcOltpTable)) == {"HttpJsonRpcBindingSpec"}
    assert {
        tuple(type(binding).__name__ for binding in op.bindings)
        for op in _spec(RestJsonRpcOltpTable).ops
    } == {("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")}


def test_olap_protocol_table_profiles_lower_to_selected_http_families() -> None:
    expected_targets = ("read", "list", "count", "exists", "aggregate", "group_by")

    assert tuple(op.target for op in _spec(RestOlapTable).ops) == expected_targets
    assert tuple(op.target for op in _spec(JsonRpcOlapTable).ops) == expected_targets
    assert tuple(op.target for op in _spec(RestJsonRpcOlapTable).ops) == expected_targets
    assert set(_binding_names(RestOlapTable)) == {"HttpRestBindingSpec"}
    assert set(_binding_names(JsonRpcOlapTable)) == {"HttpJsonRpcBindingSpec"}
    assert {
        tuple(type(binding).__name__ for binding in op.bindings)
        for op in _spec(RestJsonRpcOlapTable).ops
    } == {("HttpRestBindingSpec", "HttpJsonRpcBindingSpec")}


def test_legacy_oltp_and_olap_names_are_rest_basis_compatibility_profiles() -> None:
    assert OltpTable.TABLE_PROFILE.kind == "rest_oltp"
    assert OlapTable.TABLE_PROFILE.kind == "rest_olap"
    assert tuple(op.target for op in _spec(OltpTable).ops) == tuple(
        op.target for op in _spec(RestOltpTable).ops
    )
    assert tuple(op.target for op in _spec(OlapTable).ops) == tuple(
        op.target for op in _spec(RestOlapTable).ops
    )
    assert set(_binding_names(OltpTable)) == {"HttpRestBindingSpec"}
    assert set(_binding_names(OlapTable)) == {"HttpRestBindingSpec"}


def test_streamtable_op_binding_compatibility() -> None:
    assert tuple(op.target for op in _spec(StreamTable).ops) == ("tail", "download")
    assert set(_binding_names(StreamTable)) == {"HttpStreamBindingSpec"}


def test_ssetable_op_binding_compatibility() -> None:
    assert tuple(op.target for op in _spec(SseTable).ops) == ("subscribe", "tail")
    assert set(_binding_names(SseTable)) == {"SseBindingSpec"}
    assert set(_binding_names(EventStreamTable)) == {"SseBindingSpec"}


def test_websocket_jsonrpc_table_requires_subprotocol() -> None:
    for op in _spec(WebSocketJsonRpcTable).ops:
        binding = op.bindings[0]
        assert binding.framing == "jsonrpc"
        assert binding.subprotocols == ("jsonrpc",)


def test_webtransport_session_table_selects_session_compatible_ops() -> None:
    spec = _spec(WebTransportTable)

    assert tuple(op.target for op in spec.ops) == ("publish", "subscribe", "tail")
    assert {op.bindings[0].lane for op in spec.ops} == {"session"}


def test_webtransport_bidi_table_selects_stream_compatible_ops() -> None:
    spec = _spec(WebTransportBidiTable)

    assert tuple(op.target for op in spec.ops) == ("publish", "subscribe", "tail")
    assert {op.bindings[0].lane for op in spec.ops} == {"bidi_stream"}


def test_webtransport_client_stream_table_selects_upload_ops() -> None:
    spec = _spec(WebTransportClientStreamTable)

    assert tuple(op.target for op in spec.ops) == ("upload", "append_chunk")
    assert {op.bindings[0].lane for op in spec.ops} == {"unidi_client_stream"}


def test_webtransport_server_stream_table_selects_download_ops() -> None:
    spec = _spec(WebTransportServerStreamTable)

    assert tuple(op.target for op in spec.ops) == ("download", "tail")
    assert {op.bindings[0].lane for op in spec.ops} == {"unidi_server_stream"}


def test_webtransport_datagram_table_selects_send_datagram_only() -> None:
    spec = _spec(WebTransportDatagramTable)

    assert tuple(op.target for op in spec.ops) == ("send_datagram",)
    assert spec.ops[0].bindings[0].lane == "datagram"


def test_binding_token_lowering_is_deterministic() -> None:
    first = lower_binding_tokens_for_ops(
        RestTable,
        _spec(RestTable).table_profile,
        tuple(_spec(RestTable).ops),
    )
    second = lower_binding_tokens_for_ops(
        RestTable,
        _spec(RestTable).table_profile,
        tuple(_spec(RestTable).ops),
    )

    assert first == second


def test_explicit_opspec_bindings_override_table_defaults() -> None:
    explicit = _spec(StreamTable).ops[0].bindings[0]

    class Explicit(RestTable):
        __abstract__ = True
        TABLE_PROFILE = TableProfileSpec(
            kind="tests.explicit-table",
            ops=(OpSpec(alias="tail", target="tail", bindings=(explicit,)),),
            custom=True,
            namespace="tests",
        )

    assert _spec(Explicit).ops[0].bindings == (explicit,)


def test_explicit_opspec_bindings_suppress_both_dual_profile_defaults() -> None:
    explicit = _spec(StreamTable).ops[0].bindings[0]

    class Explicit(RestJsonRpcTable):
        __abstract__ = True
        TABLE_PROFILE = TableProfileSpec(
            kind="rest_jsonrpc",
            ops=(
                OpSpec(alias="read", target="read", bindings=(explicit,)),
                OpSpec(alias="list", target="list"),
            ),
        )

    spec = _spec(Explicit)

    assert tuple(type(binding).__name__ for binding in spec.ops[0].bindings) == (
        "HttpStreamBindingSpec",
    )
    assert tuple(type(binding).__name__ for binding in spec.ops[1].bindings) == (
        "HttpRestBindingSpec",
        "HttpJsonRpcBindingSpec",
    )


def test_docs_exposure_does_not_imply_network_mount() -> None:
    profile = TableProfileSpec(
        kind="tests.docs-only",
        ops=(OpSpec(alias="read", target="read"),),
        docs_exposure="default",
        runtime_exposure="none",
        custom=True,
        namespace="tests",
    )

    class DocsOnly(RestTable):
        __abstract__ = True
        TABLE_PROFILE = profile

    assert _spec(DocsOnly).table_profile.docs_exposure == "default"
    assert _spec(DocsOnly).ops[0].bindings == ()


def test_network_exposure_does_not_imply_docs_exposure() -> None:
    assert _spec(StreamTable).table_profile.runtime_exposure == "default"
    assert _spec(StreamTable).table_profile.docs_exposure == "default"
    assert set(_binding_names(StreamTable)) == {"HttpStreamBindingSpec"}


def test_asgi_transport_is_not_table_class() -> None:
    assert not hasattr(WebTransportTable, "scope")
    assert not hasattr(WebTransportTable, "receive")
    assert not hasattr(WebTransportTable, "send")


def test_custom_op_remains_explicit_only() -> None:
    profile = TableProfileSpec(
        kind="tests.custom-table",
        ops=(OpSpec(alias="custom_action", target="custom"),),
        custom=True,
        namespace="tests",
    )

    class Custom(RestTable):
        __abstract__ = True
        TABLE_PROFILE = profile

    assert _spec(Custom).ops[0].bindings == ()


def test_checkpoint_profile_policy_is_enforced() -> None:
    profile = TableProfileSpec(
        kind="stream",
        ops=(OpSpec(alias="checkpoint", target="checkpoint"),),
    )

    with pytest.raises(TableProfileError, match="stream target"):
        _spec(type("BadStream", (StreamTable,), {"__abstract__": True, "TABLE_PROFILE": profile}))
