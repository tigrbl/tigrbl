from __future__ import annotations

from tigrbl_equivalence_contracts import CERTIFIABLE_EQUIVALENCES, certify_all, equivalence_by_id, matrix_rows
from tigrbl_equivalence_contracts.equivalences.rest_crud_widget.runtime import EXPECTED_WIDGET_CRUD_EVIDENCE

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


def test_widget_rest_crud_equivalence_has_tigrbl_fastapi_flask_code() -> None:
    result = equivalence_by_id("rest-crud.widget").certify()
    assert result.status == "analogous"
    assert result.evidence["observed"]["tigrbl"] == EXPECTED_WIDGET_CRUD_EVIDENCE
    assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
    assert result.evidence["code_refs"] == {
        "tigrbl": "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/tigrbl_impl.py",
        "fastapi": "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/fastapi_impl.py",
        "flask": "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/flask_impl.py",
    }


def test_matrix_tracks_one_equivalence_per_concrete_tigrbl_table_class() -> None:
    assert len(TABLE_CLASS_IDS) == 23
    assert len(set(TABLE_CLASS_IDS)) == len(TABLE_CLASS_IDS)


def test_each_table_class_equivalence_certifies_expected_route_surface() -> None:
    for equivalence_id in TABLE_CLASS_IDS:
        result = equivalence_by_id(equivalence_id).certify()
        assert result.status == "analogous"
        assert set(result.evidence["observed"]) == {"tigrbl", "fastapi", "flask"}
        assert result.evidence["observed"]["tigrbl"]
