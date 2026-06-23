"""Contract row for Widget REST CRUD."""

from __future__ import annotations

from tigrbl_equivalence_contracts.contracts import CertifiableEquivalence, _impl, _lazy_attr

from .runtime import assert_equivalence


CONTRACT = CertifiableEquivalence(
    id="rest-crud.widget",
    category="rest-crud",
    intent="Author REST CRUD for a Widget resource with id and name columns.",
    status="analogous",
    claim="Tigrbl RestTable, FastAPI routes, and Flask routes can expose the same Widget REST CRUD surface.",
    source_documents=("docs/developer/AUTHORING_EQUIVALENCE.md", "docs/developer/ROUTER_TABLE_EQUIVALENCE.md"),
    implementations=(
        _impl("tigrbl", "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/tigrbl_impl.py", _lazy_attr("equivalences.rest_crud_widget.tigrbl_impl", "app"), "asgi", assert_equivalence, (), lambda result: result),
        _impl("fastapi", "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/fastapi_impl.py", _lazy_attr("equivalences.rest_crud_widget.fastapi_impl", "app"), "asgi", assert_equivalence, (), lambda result: result),
        _impl("flask", "src/tigrbl_equivalence_contracts/equivalences/rest_crud_widget/flask_impl.py", _lazy_attr("equivalences.rest_crud_widget.flask_impl", "app"), "wsgi", assert_equivalence, (), lambda result: result),
    ),
)
