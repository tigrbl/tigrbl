from __future__ import annotations

from tigrbl_equivalence_contracts import (
    CERTIFIABLE_EQUIVALENCES,
    certify_all,
    equivalence_by_id,
    matrix_rows,
)
from tigrbl_equivalence_contracts.runtime import (
    EXPECTED_WIDGET_CRUD_EVIDENCE,
    TABLE_CLASS_SURFACES,
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


def test_widget_rest_crud_equivalence_has_tigrbl_fastapi_flask_code() -> None:
    result = equivalence_by_id("rest-crud.widget").certify()

    assert result.status == "analogous"
    assert result.evidence["observed"]["tigrbl"] == EXPECTED_WIDGET_CRUD_EVIDENCE
    assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
    assert result.evidence["code_refs"] == {
        "tigrbl": "src/tigrbl_equivalence_contracts/frameworks/tigrbl_impl.py",
        "fastapi": "src/tigrbl_equivalence_contracts/frameworks/fastapi_impl.py",
        "flask": "src/tigrbl_equivalence_contracts/frameworks/flask_impl.py",
    }


def test_matrix_tracks_one_equivalence_per_concrete_tigrbl_table_class() -> None:
    rows = matrix_rows()
    table_rows = [row for row in rows if row["category"] == "table-class"]

    assert len(table_rows) == len(TABLE_CLASS_SURFACES)
    assert {row["id"] for row in table_rows} == {
        f"table-class.{surface['slug']}" for surface in TABLE_CLASS_SURFACES
    }
    assert all(row["status"] == "analogous" for row in table_rows)


def test_each_table_class_equivalence_certifies_expected_route_surface() -> None:
    for surface in TABLE_CLASS_SURFACES:
        result = equivalence_by_id(f"table-class.{surface['slug']}").certify()

        assert result.status == "analogous"
        assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
        assert result.evidence["observed"]["tigrbl"] == tuple(
            {"path": path, "methods": tuple(methods)}
            for path, methods in surface["routes"]
        )
