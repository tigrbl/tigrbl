from __future__ import annotations

import inspect

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl_core._spec import (
    AppSpec,
    DocsPayloadSpec,
    DocsProjectionSpec,
    DocsUixSpec,
    EngineSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
)
from tigrbl_concrete._concrete import engine_resolver as _resolver


class Widget(TableBase, GUIDPk):
    __tablename__ = "canonical_appspec_widgets"
    name = Column(String, nullable=False)


class Account(TableBase, GUIDPk):
    __tablename__ = "canonical_appspec_accounts"
    name = Column(String, nullable=False)


def _op(alias: str, target: str, *bindings: object, arity: str = "collection") -> OpSpec:
    return OpSpec(
        alias=alias,
        target=target,  # type: ignore[arg-type]
        arity=arity,  # type: ignore[arg-type]
        bindings=tuple(bindings),  # type: ignore[arg-type]
    )


def _spec() -> AppSpec:
    openapi_projection = DocsProjectionSpec(
        name="http-only",
        include_protocols=("http.rest",),
    )
    openrpc_projection = DocsProjectionSpec(
        name="rpc-only",
        include_protocols=("http.jsonrpc",),
        include_paths=("/rpc",),
    )
    return AppSpec(
        title="Canonical Runtime",
        engines=(
            EngineSpec(name="primary", kind="sqlite", memory=True),
            EngineSpec(name="audit", kind="sqlite", memory=True),
        ),
        engine_name="primary",
        routers=(
            RouterSpec(
                name="api",
                prefix="/api",
                engine_name="audit",
                paths=(
                    PathSpec(
                        path="/widgets",
                        kind="resource",
                        tables=(
                            TableSpec(
                                name="Widget",
                                resource="widget",
                                model_ref=f"{__name__}:Widget",
                                engine_name="primary",
                                ops=(
                                    _op(
                                        "create",
                                        "create",
                                        HttpRestBindingSpec(
                                            proto="http.rest",
                                            methods=("POST",),
                                            path="/widgets",
                                        ),
                                    ),
                                    _op(
                                        "list",
                                        "list",
                                        HttpRestBindingSpec(
                                            proto="http.rest",
                                            methods=("GET",),
                                            path="/widgets",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    PathSpec(
                        path="/widgets/{item_id}",
                        kind="resource",
                        tables=(
                            TableSpec(
                                name="Widget",
                                resource="widget",
                                model_ref=f"{__name__}:Widget",
                                ops=(
                                    _op(
                                        "read",
                                        "read",
                                        HttpRestBindingSpec(
                                            proto="http.rest",
                                            methods=("GET",),
                                            path="/widgets/{item_id}",
                                        ),
                                        arity="member",
                                    ),
                                ),
                            ),
                        ),
                    ),
                    PathSpec(
                        path="/rpc",
                        kind="jsonrpc",
                        tables=(
                            TableSpec(
                                name="Widget",
                                resource="widget",
                                model_ref=f"{__name__}:Widget",
                                engine_name="audit",
                                ops=(
                                    _op(
                                        "create",
                                        "create",
                                        HttpJsonRpcBindingSpec(
                                            proto="http.jsonrpc",
                                            rpc_method="Widget.create",
                                        ),
                                    ),
                                    _op(
                                        "list",
                                        "list",
                                        HttpJsonRpcBindingSpec(
                                            proto="http.jsonrpc",
                                            rpc_method="Widget.list",
                                        ),
                                    ),
                                ),
                            ),
                            TableSpec(
                                name="Account",
                                resource="account",
                                model_ref=f"{__name__}:Account",
                                ops=(
                                    _op(
                                        "create",
                                        "create",
                                        HttpJsonRpcBindingSpec(
                                            proto="http.jsonrpc",
                                            rpc_method="Account.create",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    PathSpec(
                        path="/openapi.json",
                        kind="docs-payload",
                        docs_payload=DocsPayloadSpec(
                            kind="openapi",
                            projection=openapi_projection,
                        ),
                    ),
                    PathSpec(
                        path="/openrpc.json",
                        kind="docs-payload",
                        docs_payload=DocsPayloadSpec(
                            kind="openrpc",
                            projection=openrpc_projection,
                        ),
                    ),
                    PathSpec(
                        path="/docs",
                        kind="docs-uix",
                        docs_uix=DocsUixSpec(kind="swagger", payload_path="/openapi.json"),
                    ),
                    PathSpec(
                        path="/lens",
                        kind="docs-uix",
                        docs_uix=DocsUixSpec(kind="lens", payload_path="/openrpc.json"),
                    ),
                    PathSpec(
                        path="/admin",
                        kind="mount",
                        mount=AppSpec(title="Admin Surface"),
                    ),
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_canonical_appspec_runtime_lowering_materializes_docs_routes_engines_and_mounts() -> None:
    app = TigrblApp.from_spec(_spec())
    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    assert _resolver.resolve_provider(engine_name="primary") is not None
    assert _resolver.resolve_provider(engine_name="audit") is not None

    attached_routers = list(app.routers.values() if isinstance(app.routers, dict) else app.routers)
    assert attached_routers
    assert _resolver.resolve_provider(router=attached_routers[0]) is not None

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        openapi = await client.get("/api/openapi.json")
        openrpc = await client.get("/api/openrpc.json")
        docs = await client.get("/api/docs")
        lens = await client.get("/api/lens")
        admin = await client.get("/api/admin")

    assert openapi.status_code == 200
    assert "/api/widgets" in openapi.json()["paths"]
    assert "/api/openrpc.json" not in openapi.json()["paths"]

    assert openrpc.status_code == 200
    assert openrpc.json()["servers"][0]["url"] == "/api/rpc"
    method_names = {item["name"] for item in openrpc.json()["methods"]}
    assert method_names >= {"Widget.create", "Widget.list"}
    assert "Widget.read" not in method_names

    assert docs.status_code == 200
    assert "/api/openapi.json" in docs.text
    assert lens.status_code == 200
    assert "/api/openrpc.json" in lens.text

    assert admin.status_code == 200
    assert admin.json()["ok"] is True
