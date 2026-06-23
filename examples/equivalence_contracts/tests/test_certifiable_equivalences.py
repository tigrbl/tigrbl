from __future__ import annotations

from tigrbl_equivalence_contracts import (
    CERTIFIABLE_EQUIVALENCES,
    certify_all,
    equivalence_by_id,
)


def test_every_declared_equivalence_certifies() -> None:
    results = certify_all()

    assert len(results) == len(CERTIFIABLE_EQUIVALENCES)
    assert all(result.certified for result in results)
    assert {result.equivalence_id for result in results} == {
        case.id for case in CERTIFIABLE_EQUIVALENCES
    }


def test_transport_read_equivalence_ignores_transport_envelope_fields() -> None:
    result = equivalence_by_id("transport.rest-jsonrpc-websocket-read").certify()

    assert result.status == "equivalent"
    assert result.evidence["transport_count"] == 3
    assert result.evidence["normalized_result"] == {
        "diagnostics": {"classification": "ok"},
        "effects": ("read:item-1",),
        "value": {"id": "item-1", "name": "Ada"},
    }


def test_stream_equivalence_preserves_ordering_and_completion() -> None:
    result = equivalence_by_id("transport.stream-sse-webtransport-tail").certify()

    assert result.status == "equivalent"
    assert result.evidence["families"] == ("stream",)
    assert result.evidence["normalized_result"]["ordering"] == "ordered"
    assert result.evidence["normalized_result"]["completion"] == "complete"


def test_router_equivalence_is_projection_not_authority_equivalence() -> None:
    result = equivalence_by_id("router.fastapi-flask-tigrbl-prefix").certify()

    assert result.status == "analogous"
    assert result.evidence["projection"] == {
        "path": "/v1/items/{item_id}",
        "methods": ("GET",),
        "endpoint": "Item.read",
    }
    assert result.evidence["authorities"]["tigrbl.router"] == "operation binding"
    assert result.evidence["authorities"]["fastapi.apirouter"] == "path operation"


def test_table_equivalence_keeps_tigrbl_table_authority_explicit() -> None:
    result = equivalence_by_id("table.fastapi-flask-tigrbl-resource").certify()

    assert result.status == "analogous"
    assert result.evidence["profile"] == "rest_jsonrpc"
    assert result.evidence["projection"]["operations"] == ("create", "list", "read")
    assert result.evidence["binding_families"] == ("http.rest", "http.jsonrpc")
    assert result.evidence["authorities"]["tigrbl.table-profile"] == "TableProfileSpec"


def test_engine_equivalence_certifies_logical_identity_not_physical_sql_parity() -> None:
    result = equivalence_by_id("engine.logical-datatype-lowering").certify()

    assert result.status == "projection-only"
    assert result.evidence["lowerings"]["uuid"] == {
        "sqlite": "TEXT",
        "postgres": "UUID",
    }
    assert result.evidence["lowerings"]["json"] == {
        "sqlite": "JSON",
        "postgres": "JSONB",
    }
