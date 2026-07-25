from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from tigrbl import TigrblApp, op_ctx
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.system.docs import build_openapi, build_openrpc_spec
from tigrbl.system.docs.openapi.helpers import (
    _schema_from_operation_result as facade_result_schema,
)
from tigrbl.system.docs.openapi.schema import openapi as facade_openapi
from tigrbl.system.docs.openrpc import build_openrpc_spec as facade_openrpc
from tigrbl.types import Column, String
from tigrbl_concrete.system.docs.openapi.helpers import (
    _schema_from_operation_result as concrete_result_schema,
)
from tigrbl_concrete.system.docs.openapi.schema import openapi as concrete_openapi
from tigrbl_concrete.system.docs.openrpc import (
    build_openrpc_spec as concrete_openrpc,
)


class DecisionResult(BaseModel):
    accepted: bool


def _build_app() -> tuple[TigrblApp, type[TableBase]]:
    TableBase.metadata.clear()

    class Catalog(TableBase, GUIDPk):
        __tablename__ = "catalog_openapi_operation_results"
        name = Column(String)

        @op_ctx(
            alias="cards",
            target="custom",
            arity="collection",
            persist="skip",
        )
        def cards(cls, ctx) -> list[dict[str, int]]:
            return [{"count": 1}]

        @op_ctx(
            alias="decision",
            target="custom",
            arity="collection",
            response_schema=DecisionResult,
            persist="skip",
        )
        def decision(cls, ctx) -> list[dict[str, int]]:
            return [{"count": 1}]

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Catalog, prefix="")
    app.initialize()
    app.mount_jsonrpc()
    return app, Catalog


def _openapi_schema(document: dict[str, Any], alias: str) -> dict[str, Any]:
    for path_item in document["paths"].values():
        for operation in path_item.values():
            if operation.get("operationId", "").endswith(f".{alias}"):
                response = operation["responses"]["200"]
                return response["content"]["application/json"]["schema"]
    raise AssertionError(f"OpenAPI operation {alias!r} was not found")


def _openrpc_schema(
    document: dict[str, Any],
    model: type[TableBase],
    alias: str,
) -> dict[str, Any]:
    name = f"{model.__name__}.{alias}"
    method = next(method for method in document["methods"] if method["name"] == name)
    return method["result"]["schema"]


def _resolve_root(
    schema: dict[str, Any],
    document: dict[str, Any],
) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str):
        return schema
    name = ref.rsplit("/", maxsplit=1)[-1]
    return document["components"]["schemas"][name]


def _assert_component_refs_resolve(document: dict[str, Any]) -> None:
    components = document["components"]["schemas"]

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            ref = value.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                assert ref.rsplit("/", maxsplit=1)[-1] in components
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(document)


def test_public_docs_facade_delegates_to_canonical_concrete_builders() -> None:
    assert facade_openapi is concrete_openapi
    assert facade_openrpc is concrete_openrpc
    assert facade_result_schema is concrete_result_schema


def test_public_openapi_and_openrpc_publish_complete_result_shapes() -> None:
    app, model = _build_app()

    openapi_document = build_openapi(app)
    openrpc_document = build_openrpc_spec(app)

    list_openapi = _openapi_schema(openapi_document, "list")
    list_openrpc = _openrpc_schema(openrpc_document, model, "list")
    assert list_openapi["type"] == list_openrpc["type"] == "array"
    assert list_openapi["items"] == list_openrpc["items"]

    cards_openapi = _openapi_schema(openapi_document, "cards")
    cards_openrpc = _openrpc_schema(openrpc_document, model, "cards")
    assert cards_openapi == cards_openrpc
    assert cards_openapi["type"] == "array"
    assert cards_openapi["items"]["type"] == "object"

    decision_openapi = _resolve_root(
        _openapi_schema(openapi_document, "decision"),
        openapi_document,
    )
    decision_openrpc = _resolve_root(
        _openrpc_schema(openrpc_document, model, "decision"),
        openrpc_document,
    )
    assert decision_openapi["type"] == decision_openrpc["type"] == "object"
    assert set(decision_openapi["properties"]) == {"accepted"}
    assert set(decision_openrpc["properties"]) == {"accepted"}

    _assert_component_refs_resolve(openapi_document)
    _assert_component_refs_resolve(openrpc_document)
