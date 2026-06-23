from __future__ import annotations

from tigrbl_equivalence_contracts import (
    CERTIFIABLE_EQUIVALENCES,
    certify_all,
    equivalence_by_id,
    matrix_rows,
)


def test_every_declared_equivalence_certifies() -> None:
    results = certify_all()

    assert len(results) == len(CERTIFIABLE_EQUIVALENCES)
    assert all(result.certified for result in results)
    assert {result.equivalence_id for result in results} == {
        case.id for case in CERTIFIABLE_EQUIVALENCES
    }


def test_matrix_tracks_every_runtime_equivalence() -> None:
    rows = matrix_rows()

    assert {row["id"] for row in rows} == {case.id for case in CERTIFIABLE_EQUIVALENCES}
    assert all(row["tigrbl"] for row in rows)
    assert all(row["fastapi"] for row in rows)
    assert all(row["flask"] for row in rows)
    assert all(row["test"].endswith("test_certifiable_equivalences.py") for row in rows)


def test_app_http_health_runs_all_frameworks() -> None:
    result = equivalence_by_id("app.http-health").certify()

    assert result.status == "equivalent"
    assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
    assert result.evidence["observed"]["tigrbl"] == {
        "status_code": 200,
        "json": {"status": "ok"},
    }


def test_router_prefix_read_runs_all_frameworks() -> None:
    result = equivalence_by_id("router.prefix-read").certify()

    assert result.status == "analogous"
    assert result.evidence["observed"]["tigrbl"] == {
        "status_code": 200,
        "json": {"id": "item-1", "name": "Ada"},
    }


def test_table_equivalence_has_tigrbl_fastapi_flask_code() -> None:
    result = equivalence_by_id("table.resource-contract").certify()

    assert result.status == "analogous"
    assert result.evidence["observed"]["tigrbl"]["operations"] == (
        "create",
        "list",
        "read",
    )
    assert result.evidence["observed"]["tigrbl"]["bindings"] == (
        "http.rest",
        "http.jsonrpc",
    )
    assert result.evidence["code_refs"]["fastapi"].endswith("fastapi_impl.py")
    assert result.evidence["code_refs"]["flask"].endswith("flask_impl.py")


def test_websocket_equivalence_is_declared_for_all_frameworks() -> None:
    result = equivalence_by_id("websocket.echo-contract").certify()

    assert result.status == "projection-only"
    assert result.evidence["observed"]["tigrbl"]["path"] == "/ws/echo"
    assert result.evidence["observed"]["tigrbl"]["framing"] == "json"
    assert result.evidence["observed"]["tigrbl"]["subprotocols"] == ("json",)


def test_engine_equivalence_certifies_logical_identity_not_physical_sql_parity() -> None:
    result = equivalence_by_id("sql.logical-datatype-lowering").certify()

    assert result.status == "projection-only"
    assert result.evidence["observed"]["tigrbl"]["logical_fields"]["id"] == "uuid"
    assert result.evidence["observed"]["tigrbl"]["lowerings"]["sqlite"]["id"] == "TEXT"
    assert result.evidence["observed"]["tigrbl"]["lowerings"]["postgres"]["id"] == "UUID"
