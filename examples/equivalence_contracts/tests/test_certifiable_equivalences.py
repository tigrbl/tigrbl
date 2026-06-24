from __future__ import annotations

from tigrbl_equivalence_contracts import CERTIFIABLE_EQUIVALENCES, certify_all, equivalence_by_id, matrix_rows
from tigrbl_equivalence_contracts.equivalences.json_rpc_bulk_crud_table.runtime import (
    EXPECTED_JSONRPC_BULK_EVIDENCE,
)
from tigrbl_equivalence_contracts.equivalences.json_rpc_olap_table.runtime import (
    EXPECTED_JSONRPC_OLAP_EVIDENCE,
)
from tigrbl_equivalence_contracts.equivalences.json_rpc_oltp_table.runtime import (
    EXPECTED_JSONRPC_OLTP_EVIDENCE,
)
from tigrbl_equivalence_contracts.equivalences.rest_json_rpc_table.runtime import (
    EXPECTED_EVIDENCE as EXPECTED_REST_JSONRPC_EVIDENCE,
)
from tigrbl_equivalence_contracts.equivalences.rest_table.runtime import EXPECTED_WIDGET_CRUD_EVIDENCE

TABLE_CLASS_IDS = tuple(row["id"] for row in matrix_rows() if row["category"] == "table-class")


def test_every_declared_equivalence_certifies() -> None:
    results = certify_all()
    assert len(results) == len(CERTIFIABLE_EQUIVALENCES)
    assert all(result.certified for result in results)
    assert {result.equivalence_id for result in results} == {case.id for case in CERTIFIABLE_EQUIVALENCES}


def test_matrix_tracks_every_runtime_equivalence() -> None:
    rows = matrix_rows()
    assert {row["id"] for row in rows} == {case.id for case in CERTIFIABLE_EQUIVALENCES}
    assert all(row["tigrbl"] for row in rows)
    assert all(row["fastapi"] for row in rows)
    assert all(row["flask"] for row in rows)
    assert all(row["test"].endswith("test_certifiable_equivalences.py") for row in rows)


def test_rest_table_equivalence_has_tigrbl_fastapi_flask_widget_crud_code() -> None:
    result = equivalence_by_id("table-class.rest-table").certify()
    assert result.status == "analogous"
    assert result.evidence["observed"]["tigrbl"] == EXPECTED_WIDGET_CRUD_EVIDENCE
    assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
    assert result.evidence["code_refs"] == {
        "tigrbl": "src/tigrbl_equivalence_contracts/equivalences/rest_table/tigrbl_impl.py",
        "fastapi": "src/tigrbl_equivalence_contracts/equivalences/rest_table/fastapi_impl.py",
        "flask": "src/tigrbl_equivalence_contracts/equivalences/rest_table/flask_impl.py",
    }


def test_json_rpc_table_equivalence_uses_http_jsonrpc_envelopes() -> None:
    result = equivalence_by_id("table-class.json-rpc-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed[0]["step"] == "create"
        assert observed[0]["envelope"]["jsonrpc"] == "2.0"
        assert observed[0]["envelope"]["result"] == {
            "id": "widget-1",
            "name": "First",
        }
        assert observed[2]["step"] == "list_created"
        assert observed[2]["envelope"]["result"] == [
            {"id": "widget-1", "name": "First"}
        ]


def test_rest_json_rpc_table_equivalence_uses_rest_routes_and_jsonrpc_envelopes() -> None:
    result = equivalence_by_id("table-class.rest-json-rpc-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == EXPECTED_REST_JSONRPC_EVIDENCE
        assert set(observed) == {"rest_routes", "jsonrpc"}
        assert observed["jsonrpc"][0]["envelope"]["jsonrpc"] == "2.0"


def test_json_rpc_bulk_crud_table_equivalence_uses_bulk_jsonrpc_envelopes() -> None:
    result = equivalence_by_id("table-class.json-rpc-bulk-crud-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == EXPECTED_JSONRPC_BULK_EVIDENCE
        assert {step["step"] for step in observed} == {
            "bulk_create",
            "bulk_update",
            "bulk_replace",
            "list_replaced",
            "bulk_delete",
            "list_deleted",
        }


def test_json_rpc_oltp_table_equivalence_uses_oltp_jsonrpc_envelopes() -> None:
    result = equivalence_by_id("table-class.json-rpc-oltp-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == EXPECTED_JSONRPC_OLTP_EVIDENCE
        assert observed[1]["envelope"]["result"] == {"count": 1}
        assert observed[2]["envelope"]["result"] == {"exists": True}


def test_json_rpc_olap_table_equivalence_uses_read_only_olap_jsonrpc_envelopes() -> None:
    result = equivalence_by_id("table-class.json-rpc-olap-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == EXPECTED_JSONRPC_OLAP_EVIDENCE
        assert observed[3]["envelope"]["result"] == {
            "field": "name",
            "op": "sum",
            "value": 0,
            "count": 0,
        }


def test_websocket_table_equivalence_uses_real_websocket_exchange() -> None:
    result = equivalence_by_id("table-class.web-socket-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == (
            {
                "step": "message_exchange",
                "path": "/widgetwebsockettable",
                "sent": "ping",
                "received": "widget:ping",
            },
        )


def test_websocket_jsonrpc_table_equivalence_uses_jsonrpc_subprotocol() -> None:
    result = equivalence_by_id("table-class.web-socket-json-rpc-table").certify()

    assert result.status == "analogous"
    for observed in result.evidence["observed"].values():
        assert observed == (
            {
                "step": "jsonrpc_message_exchange",
                "path": "/widgetwebsocketjsonrpctable",
                "subprotocol": "jsonrpc",
                "sent_method": "WidgetWebSocketJsonRpcTable.echo",
                "envelope": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"message": "widget:ping"},
                },
            },
        )


def test_matrix_tracks_one_equivalence_per_concrete_tigrbl_table_class() -> None:
    assert len(TABLE_CLASS_IDS) == 24
    assert len(set(TABLE_CLASS_IDS)) == len(TABLE_CLASS_IDS)


def test_each_table_class_equivalence_certifies_expected_route_surface() -> None:
    for equivalence_id in TABLE_CLASS_IDS:
        result = equivalence_by_id(equivalence_id).certify()
        assert result.status == "analogous"
        assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
        assert result.evidence["observed"]["tigrbl"]
