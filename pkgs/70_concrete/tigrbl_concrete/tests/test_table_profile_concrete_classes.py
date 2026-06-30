from __future__ import annotations

from tigrbl_concrete._concrete import (
    BulkCrudTable,
    CrudTable,
    JsonRpcBulkCrudTable,
    JsonRpcTable,
    OlapTable,
    OltpTable,
    RealtimeTable,
    RestBulkCrudTable,
    RestTable,
    SseTable,
    StreamTable,
    Table,
    WebSocketJsonRpcTable,
    WebSocketTable,
    WebTransportBidiTable,
    WebTransportClientStreamTable,
    WebTransportDatagramTable,
    WebTransportServerStreamTable,
    WebTransportTable,
)
import tigrbl_concrete._concrete as concrete
from tigrbl_core._spec.table_spec import TableSpec
from tigrbl_core._spec.table_profile_spec import (
    get_builtin_table_profile_definition,
    iter_builtin_table_profile_definitions,
)
from tigrbl_base._base import CrudTableBase, RealtimeTableBase, TableBase


def _targets(table: type) -> tuple[str, ...]:
    return tuple(op.target for op in TableSpec.collect(table).ops)


def test_concrete_profile_classes_keep_table_behavior_and_base_lineage() -> None:
    assert issubclass(CrudTable, Table)
    assert issubclass(CrudTable, CrudTableBase)
    assert issubclass(RealtimeTable, Table)
    assert issubclass(RealtimeTable, RealtimeTableBase)
    assert issubclass(RestTable, TableBase)


def test_rest_and_jsonrpc_profiles_collect_complete_crud_ops() -> None:
    assert RestTable.TABLE_PROFILE.kind == "rest"
    assert JsonRpcTable.TABLE_PROFILE.kind == "jsonrpc"
    assert _targets(RestTable) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )


def test_concrete_query_profiles_collect_expected_ops() -> None:
    assert BulkCrudTable is RestBulkCrudTable
    assert "bulk_create" in _targets(RestBulkCrudTable)
    assert _targets(JsonRpcBulkCrudTable) == _targets(RestBulkCrudTable)
    assert "merge" in _targets(OltpTable)
    assert _targets(OlapTable) == (
        "read",
        "list",
        "count",
        "exists",
        "aggregate",
        "group_by",
    )


def test_realtime_profiles_collect_expected_ops() -> None:
    assert _targets(StreamTable) == ("tail", "download")
    assert _targets(SseTable) == ("subscribe", "tail")
    assert _targets(WebSocketTable) == ("publish", "subscribe")
    assert _targets(WebSocketJsonRpcTable) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
    )


def test_webtransport_lane_profiles_collect_expected_ops() -> None:
    assert _targets(WebTransportTable) == ("publish", "subscribe", "tail")
    assert _targets(WebTransportBidiTable) == ("publish", "subscribe", "tail")
    assert _targets(WebTransportClientStreamTable) == ("upload", "append_chunk")
    assert _targets(WebTransportServerStreamTable) == ("download", "tail")
    assert _targets(WebTransportDatagramTable) == ("send_datagram",)


def test_builtin_table_profile_taxonomy_matches_exported_classes() -> None:
    checked: set[str] = set()
    for row in iter_builtin_table_profile_definitions():
        for class_name in row.public_class_names:
            if not hasattr(concrete, class_name):
                continue
            table = getattr(concrete, class_name)
            spec = TableSpec.collect(table)

            assert table.TABLE_PROFILE.kind == row.kind
            assert spec.table_profile.role == row.role
            assert spec.table_profile.docs_exposure == row.docs_exposure
            assert spec.table_profile.runtime_exposure == row.runtime_exposure
            assert tuple(op.target for op in spec.ops) == row.targets
            checked.add(class_name)

    assert checked == {
        "CrudTable",
        "EventStreamTable",
        "JsonRpcBulkCrudTable",
        "JsonRpcOlapTable",
        "JsonRpcOltpTable",
        "JsonRpcTable",
        "OlapTable",
        "OltpTable",
        "RealtimeTable",
        "RestBulkCrudTable",
        "RestJsonRpcOlapTable",
        "RestJsonRpcOltpTable",
        "RestJsonRpcTable",
        "RestOlapTable",
        "RestOltpTable",
        "RestTable",
        "SseTable",
        "StreamTable",
        "WebSocketJsonRpcTable",
        "WebSocketTable",
        "WebTransportBidiTable",
        "WebTransportClientStreamTable",
        "WebTransportDatagramTable",
        "WebTransportServerStreamTable",
        "WebTransportTable",
    }


def test_compatibility_oltp_and_olap_taxonomy_rows_are_rest_basis() -> None:
    assert get_builtin_table_profile_definition("rest_oltp").public_class_names == (
        "RestOltpTable",
        "OltpTable",
    )
    assert get_builtin_table_profile_definition("rest_olap").public_class_names == (
        "RestOlapTable",
        "OlapTable",
    )
