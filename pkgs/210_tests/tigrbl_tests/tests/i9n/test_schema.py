import pytest
from tigrbl.schema import _build_schema
from tigrbl.types import BaseModel


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_generation(app_client):
    client, _, Item = app_client

    read_model = _build_schema(Item, verb="read")
    update_model = _build_schema(Item, verb="update")
    delete_model = _build_schema(Item, verb="delete")
    list_model = _build_schema(Item, verb="list")

    assert issubclass(read_model, BaseModel)
    assert issubclass(update_model, BaseModel)
    assert issubclass(delete_model, BaseModel)
    assert issubclass(list_model, BaseModel)

    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemList"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert any(name.startswith(read_model.__name__) for name in schemas)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_operation_schema(app_client):
    pytest.skip("Bulk operation schemas are covered by dedicated bulk suites.")
    client, _, _ = app_client
    spec = (await client.get("/openapi.json")).json()
    assert "/tenant/{tenant_id}/item" in spec["paths"]
    ops = spec["paths"]["/tenant/{tenant_id}/item"]
    assert "post" in ops and "delete" in ops
