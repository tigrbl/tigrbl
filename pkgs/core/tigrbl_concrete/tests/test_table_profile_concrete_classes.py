from __future__ import annotations

from tigrbl_concrete._concrete import (
    BulkCrudTable,
    CrudTable,
    JsonRpcTable,
    OlapTable,
    OltpTable,
    RealtimeTable,
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
from tigrbl_core._spec.table_spec import TableSpec
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
    assert "bulk_create" in _targets(BulkCrudTable)
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
