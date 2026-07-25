from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from jsonschema import Draft202012Validator

from tigrbl import TigrblApp
from tigrbl._spec import F, IO, S
from tigrbl.factories import acol
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.system.docs import build_openapi, build_openrpc_spec
from tigrbl.types import Mapped, String


def _build_app() -> tuple[TigrblApp, type[TableBase]]:
    TableBase.metadata.clear()

    class RuntimeWidget(TableBase, GUIDPk):
        __tablename__ = "runtime_openapi_openrpc_result_parity"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, required_in=("create",)),
            io=IO(
                in_verbs=("create",),
                out_verbs=("create", "read", "list"),
            ),
        )

        __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}

    app = TigrblApp(engine=mem())
    app.include_table(RuntimeWidget, prefix="")
    app.mount_jsonrpc()
    return app, RuntimeWidget


def _openapi_operation(
    document: dict[str, Any],
    alias: str,
) -> tuple[str, str, dict[str, Any]]:
    for path, path_item in document["paths"].items():
        for method, operation in path_item.items():
            if operation.get("operationId", "").endswith(f".{alias}"):
                return path, method, operation
    raise AssertionError(f"OpenAPI operation {alias!r} was not found")


def _openrpc_method(
    document: dict[str, Any],
    model: type[TableBase],
    alias: str,
) -> dict[str, Any]:
    name = f"{model.__name__}.{alias}"
    return next(method for method in document["methods"] if method["name"] == name)


def _validate(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
) -> None:
    def normalize_refs(node: Any) -> Any:
        if isinstance(node, dict):
            normalized = {
                key: normalize_refs(nested)
                for key, nested in node.items()
            }
            ref = normalized.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                normalized["$ref"] = ref.replace(
                    "#/components/schemas/",
                    "#/$defs/",
                )
            return normalized
        if isinstance(node, list):
            return [normalize_refs(nested) for nested in node]
        return node

    standalone = normalize_refs(deepcopy(schema))
    standalone["$defs"] = normalize_refs(
        deepcopy(document["components"]["schemas"])
    )
    Draft202012Validator(standalone).validate(value)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_and_jsonrpc_list_values_validate_against_both_documents() -> None:
    app, model = _build_app()
    await app.initialize()

    openapi_document = build_openapi(app)
    openrpc_document = build_openrpc_spec(app)
    create_path, create_method, _ = _openapi_operation(openapi_document, "create")
    list_path, list_method, list_operation = _openapi_operation(
        openapi_document,
        "list",
    )
    assert create_method == "post"
    assert list_method == "get"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for name in ("first", "second"):
            response = await client.post(create_path, json={"name": name})
            assert response.status_code == 201

        rest_response = await client.get(list_path)
        assert rest_response.status_code == 200
        rest_value = rest_response.json()

        rpc_response = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": "list-runtime-widgets",
                "method": f"{model.__name__}.list",
                "params": {},
            },
        )
        assert rpc_response.status_code == 200
        rpc_payload = rpc_response.json()
        assert "error" not in rpc_payload
        rpc_value = rpc_payload["result"]

    openapi_schema = list_operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    openrpc_schema = _openrpc_method(
        openrpc_document,
        model,
        "list",
    )["result"]["schema"]

    assert openapi_schema["type"] == openrpc_schema["type"] == "array"
    _validate(rest_value, openapi_schema, openapi_document)
    _validate(rpc_value, openrpc_schema, openrpc_document)
    assert {row["name"] for row in rest_value} == {"first", "second"}
    assert {row["name"] for row in rpc_value} == {"first", "second"}
