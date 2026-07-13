from __future__ import annotations

import os
from typing import Any

from tigrbl import RestBulkCrudTable, TigrblApp
from tigrbl.factories.engine import engine as build_engine
from tigrbl.factories.engine import pgs
from tigrbl.types import Column, Integer, String


ENV_PREFIX = "TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO"
RESOURCE_NAME = "orders"


class DemoOrder(RestBulkCrudTable):
    __tablename__ = "demo_orders"
    __allow_unmapped__ = True
    resource_name = RESOURCE_NAME

    id = Column(String(64), primary_key=True)
    sku = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)


def postgres_runtime_settings() -> dict[str, Any]:
    dsn = os.environ.get(f"{ENV_PREFIX}_DSN", "").strip()
    return {
        "dsn": dsn,
        "host": os.environ.get(f"{ENV_PREFIX}_HOST", "127.0.0.1"),
        "port": int(os.environ.get(f"{ENV_PREFIX}_PORT", "5432")),
        "user": os.environ.get(f"{ENV_PREFIX}_USER", "tigrbl"),
        "password": os.environ.get(f"{ENV_PREFIX}_PASSWORD", "tigrbl"),
        "db": os.environ.get(f"{ENV_PREFIX}_DB", "tigrbl_rest_bulk_crud_demo"),
    }


def postgres_engine_source() -> str | dict[str, Any]:
    settings = postgres_runtime_settings()
    if settings["dsn"]:
        return settings["dsn"]
    return pgs(
        host=settings["host"],
        port=settings["port"],
        user=settings["user"],
        pwd=settings["password"],
        name=settings["db"],
    )


def demo_connection_summary() -> dict[str, Any]:
    settings = postgres_runtime_settings()
    return {
        "engine_kind": "postgres",
        "resource": RESOURCE_NAME,
        "source": "dsn" if settings["dsn"] else "mapping",
        "host": settings["host"],
        "port": settings["port"],
        "user": settings["user"],
        "db": settings["db"],
    }


def build_app(*, engine_override: Any | None = None) -> TigrblApp:
    engine_source = engine_override if engine_override is not None else postgres_engine_source()
    app = TigrblApp(
        title="Tigrbl RestBulkCrudTable PostgreSQL Demo",
        version="0.1.0",
        description=(
            "Repo-owned RestBulkCrudTable demo that defaults to a PostgreSQL "
            "backend and exposes collection-level bulk CRUD plus member CRUD."
        ),
        engine=build_engine(engine_source),
        mount_system=False,
    )
    app.include_table(DemoOrder)
    app.initialize()
    app.mount_openapi(path="/openapi.json")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/demo-config")
    def demo_config() -> dict[str, Any]:
        return demo_connection_summary()

    return app
