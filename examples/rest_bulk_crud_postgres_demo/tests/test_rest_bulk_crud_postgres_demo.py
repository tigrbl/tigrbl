from __future__ import annotations

import importlib.util
from pathlib import Path

from httpx import ASGITransport, AsyncClient
import pytest

from tigrbl.factories.engine import mem


DEMO_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _load_demo_module():
    spec = importlib.util.spec_from_file_location(
        "rest_bulk_crud_postgres_demo_app",
        DEMO_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_uses_postgres_runtime_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_demo_module()

    monkeypatch.delenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_DSN", raising=False)
    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_HOST", "db")
    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_PORT", "5544")
    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_USER", "demo_user")
    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_PASSWORD", "demo_pwd")
    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_DB", "demo_db")

    settings = module.postgres_runtime_settings()
    source = module.postgres_engine_source()
    summary = module.demo_connection_summary()

    assert settings["host"] == "db"
    assert settings["port"] == 5544
    assert settings["user"] == "demo_user"
    assert settings["db"] == "demo_db"
    assert source["kind"] == "postgres"
    assert source["host"] == "db"
    assert source["port"] == 5544
    assert source["user"] == "demo_user"
    assert source["db"] == "demo_db"
    assert summary == {
        "engine_kind": "postgres",
        "resource": "orders",
        "source": "mapping",
        "host": "db",
        "port": 5544,
        "user": "demo_user",
        "db": "demo_db",
    }


def test_demo_uses_dsn_override(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_demo_module()
    dsn = "postgresql+psycopg://demo:secret@postgres:5432/demo_db"

    monkeypatch.setenv("TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_DSN", dsn)

    assert module.postgres_engine_source() == dsn
    assert module.demo_connection_summary()["source"] == "dsn"


@pytest.mark.asyncio
async def test_demo_projects_rest_bulk_crud_routes_and_docs() -> None:
    module = _load_demo_module()
    app = module.build_app(engine_override=mem(async_=False))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        health = await client.get("/healthz")
        config = await client.get("/demo-config")
        openapi = await client.get("/openapi.json")
        openrpc = await client.get("/openrpc.json")
        lens = await client.get("/lens")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert config.status_code == 200
    assert config.json()["engine_kind"] == "postgres"
    assert config.json()["resource"] == "orders"

    assert openapi.status_code == 200
    payload = openapi.json()
    assert "/orders" in payload["paths"]
    assert "/orders/{item_id}" in payload["paths"]
    assert set(payload["paths"]["/orders"]) == {"get", "post", "patch", "put", "delete"}
    assert set(payload["paths"]["/orders/{item_id}"]) == {"get", "patch", "put", "delete"}
    assert openrpc.status_code == 404
    assert lens.status_code == 404


@pytest.mark.asyncio
async def test_demo_rest_bulk_crud_flow_with_engine_override() -> None:
    module = _load_demo_module()
    app = module.build_app(engine_override=mem(async_=False))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/orders",
            json=[
                {
                    "id": "ord-100",
                    "sku": "sku-100",
                    "quantity": 2,
                    "status": "pending",
                },
                {
                    "id": "ord-101",
                    "sku": "sku-101",
                    "quantity": 5,
                    "status": "pending",
                },
            ],
        )
        updated = await client.patch(
            "/orders",
            json=[
                {"id": "ord-100", "quantity": 3},
                {"id": "ord-101", "status": "allocated"},
            ],
        )
        replaced = await client.put(
            "/orders",
            json=[
                {
                    "id": "ord-100",
                    "sku": "sku-100-r",
                    "quantity": 7,
                    "status": "packed",
                },
                {
                    "id": "ord-101",
                    "sku": "sku-101-r",
                    "quantity": 8,
                    "status": "packed",
                },
            ],
        )
        listed = await client.get("/orders")
        read_one = await client.get("/orders/ord-100")
        deleted = await client.request(
            "DELETE",
            "/orders",
            json={"ids": ["ord-100"]},
        )
        remaining = await client.get("/orders")

    assert created.status_code == 201
    assert [row["id"] for row in created.json()] == ["ord-100", "ord-101"]

    assert updated.status_code == 200
    assert updated.json()[0]["quantity"] == 3
    assert updated.json()[1]["status"] == "allocated"

    assert replaced.status_code == 200
    assert replaced.json()[0]["sku"] == "sku-100-r"
    assert replaced.json()[1]["status"] == "packed"

    assert listed.status_code == 200
    assert len(listed.json()) == 2

    assert read_one.status_code == 200
    assert read_one.json() == {
        "id": "ord-100",
        "sku": "sku-100-r",
        "quantity": 7,
        "status": "packed",
    }

    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": 1}
    assert remaining.status_code == 200
    assert remaining.json() == [
        {
            "id": "ord-101",
            "sku": "sku-101-r",
            "quantity": 8,
            "status": "packed",
        }
    ]
