from __future__ import annotations

import pytest

from tigrbl import (
    BulkCrudTable,
    CrudTable,
    OlapTable,
    OltpTable,
    RealtimeTable,
    WebTransportDatagramTable,
)
from tigrbl_core._spec import OpSpec, TableProfileError, TableProfileSpec, TableSpec
from tigrbl_core._spec.table_profile_bindings import lower_table_profile_bindings
from tigrbl_core._spec.table_profile_spec import make_table_profile


def _targets(table: type) -> tuple[str, ...]:
    return tuple(op.target for op in TableSpec.collect(table).ops)


def test_abstract_crud_profile_selects_crud_ops_without_transport_bindings() -> None:
    spec = TableSpec.collect(CrudTable)

    assert _targets(CrudTable) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )
    assert all(not op.bindings for op in spec.ops)


def test_abstract_realtime_profile_selects_realtime_ops_without_transport_bindings() -> None:
    spec = TableSpec.collect(RealtimeTable)

    assert _targets(RealtimeTable) == ("publish", "subscribe", "tail")
    assert all(not op.bindings for op in spec.ops)


def test_bulk_crud_profile_selects_bulk_and_crud_ops() -> None:
    assert _targets(BulkCrudTable) == (
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


def test_oltp_profile_selects_transactional_query_and_merge_ops() -> None:
    assert _targets(OltpTable) == (
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


def test_olap_profile_selects_read_only_analytical_ops() -> None:
    assert _targets(OlapTable) == (
        "read",
        "list",
        "count",
        "exists",
        "aggregate",
        "group_by",
    )


def test_checkpoint_profile_selects_checkpoint_ops_only() -> None:
    profile = make_table_profile("tests.checkpoint", ("checkpoint",), custom=True, namespace="tests")

    assert tuple(op.target for op in profile.ops) == ("checkpoint",)


def test_abstract_profiles_do_not_emit_concrete_binding_tokens() -> None:
    assert all(not op.bindings for op in TableSpec.collect(CrudTable).ops)
    assert all(not op.bindings for op in TableSpec.collect(RealtimeTable).ops)


def test_olap_profile_rejects_mutation_ops() -> None:
    profile = TableProfileSpec(
        kind="olap",
        ops=(OpSpec(alias="create", target="create"),),
    )

    with pytest.raises(TableProfileError, match="REST target"):
        lower_table_profile_bindings(OlapTable, profile, tuple(profile.ops))


def test_datagram_profile_rejects_stream_and_session_ops() -> None:
    profile = TableProfileSpec(
        kind="webtransport_datagram",
        ops=(OpSpec(alias="tail", target="tail"),),
    )

    with pytest.raises(TableProfileError, match="WebTransport target"):
        lower_table_profile_bindings(WebTransportDatagramTable, profile, tuple(profile.ops))


def test_custom_ops_are_not_selected_by_profile_defaults() -> None:
    profile = TableProfileSpec(
        kind="tests.custom",
        ops=(OpSpec(alias="custom_action", target="custom"),),
        custom=True,
        namespace="tests",
    )

    lowered = lower_table_profile_bindings(CrudTable, profile, tuple(profile.ops))

    assert lowered[0].bindings == ()


def test_unknown_table_profile_fails_closed() -> None:
    profile = TableProfileSpec(
        kind="tests.unknown",
        ops=(OpSpec(alias="read", target="read"),),
    )

    with pytest.raises(TableProfileError, match="unsupported table profile"):
        lower_table_profile_bindings(CrudTable, profile, tuple(profile.ops))


def test_profile_operation_selection_is_deterministic() -> None:
    assert TableSpec.collect(BulkCrudTable).ops == TableSpec.collect(BulkCrudTable).ops
