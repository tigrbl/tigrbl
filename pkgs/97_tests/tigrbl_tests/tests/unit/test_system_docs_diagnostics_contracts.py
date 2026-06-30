from __future__ import annotations

import asyncio
from types import SimpleNamespace

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import Column, String

from tigrbl import (
    HTTPBearer,
    Request,
    Router,
    TigrblApp,
    build_hooks,
    build_rest,
    build_schemas,
)
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.security import Security
from tigrbl._spec import OpSpec
from tigrbl.system import (
    build_json_schema_bundle,
    build_openapi,
    build_openrpc_spec,
    build_swagger,
)
from tigrbl.system.diagnostics import (
    build_healthz_endpoint,
    build_hookz_endpoint,
    build_kernelz_endpoint,
    build_methodz_endpoint,
    mount_diagnostics,
)


class SystemDocsWidget(TableBase, GUIDPk):
    __tablename__ = "system_docs_widgets"

    name = Column(String, nullable=False)


class SystemDocsSecureWidget(TableBase, GUIDPk):
    __tablename__ = "system_docs_secure_widgets"
    __tigrbl_allow_anon__ = ["list"]

    name = Column(String, nullable=False)


def _bearer_auth(cred=Security(HTTPBearer())):
    return cred


def _build_app() -> TigrblApp:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(SystemDocsWidget)
    app.initialize()
    app.mount_jsonrpc()
    return app


@pytest.mark.unit
def test_system_build_helpers_expose_docs_schema_and_runtime_surfaces() -> None:
    app = _build_app()
    request = Request(
        method="GET",
        path="/docs",
        headers={},
        query={},
        path_params={},
        body=b"",
    )

    openapi_doc = build_openapi(app)
    openrpc_doc = build_openrpc_spec(app)
    schema_bundle = build_json_schema_bundle(app)
    swagger_html = build_swagger(app, request)

    assert openapi_doc["openapi"] == "3.1.0"
    assert openapi_doc["jsonSchemaDialect"] == "https://json-schema.org/draft/2020-12/schema"
    assert openapi_doc["components"]["schemas"]
    assert any(
        operation.get("requestBody") or operation.get("parameters")
        for path_item in openapi_doc["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict)
    )
    assert openrpc_doc["openrpc"] == "1.2.6"
    assert openrpc_doc["methods"]
    assert schema_bundle["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema_bundle["$defs"]
    assert "swagger-ui" in swagger_html


@pytest.mark.asyncio
async def test_system_docs_mount_openapi_openrpc_and_swagger_get_surfaces() -> None:
    app = _build_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        openapi_response = await client.get("/openapi.json")
        openrpc_response = await client.get("/openrpc.json")
        docs_response = await client.get("/docs")

    assert openapi_response.status_code == 200
    assert openapi_response.json()["openapi"] == "3.1.0"
    assert openrpc_response.status_code == 200
    assert openrpc_response.json()["openrpc"] == "1.2.6"
    assert docs_response.status_code == 200
    assert "swagger-ui" in docs_response.text


@pytest.mark.unit
def test_mounted_docs_without_canonical_projection_keep_default_surface() -> None:
    app = _build_app()

    openapi_doc = build_openapi(app, docs_path="/openapi.json")
    openrpc_doc = build_openrpc_spec(app, docs_path="/openrpc.json")

    assert "/systemdocswidget" in openapi_doc["paths"]
    assert "/systemdocswidget/{item_id}" in openapi_doc["paths"]
    assert "SystemDocsWidget.list" in {method["name"] for method in openrpc_doc["methods"]}


@pytest.mark.asyncio
async def test_diagnostics_mount_uses_system_prefix_and_stable_healthz_payload() -> None:
    app = TigrblApp(mount_system=False)
    app.include_router(mount_diagnostics(SimpleNamespace(tables={})), prefix="/internal")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        mounted = await client.get("/internal/healthz")
        default = await client.get("/system/healthz")

    assert mounted.status_code == 200
    assert mounted.json() == {"ok": True}
    assert default.status_code == 404


@pytest.mark.asyncio
async def test_diagnostics_mount_exposes_methodz_and_kernelz_only_under_prefix() -> None:
    app = TigrblApp(mount_system=False)
    app.include_table(SystemDocsWidget)
    app.include_router(mount_diagnostics(app), prefix="/internal")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        methodz = await client.get("/internal/methodz")
        kernelz = await client.get("/internal/kernelz")
        default_methodz = await client.get("/system/methodz")
        default_kernelz = await client.get("/system/kernelz")

    assert methodz.status_code == 200
    assert kernelz.status_code == 200
    assert default_methodz.status_code == 404
    assert default_kernelz.status_code == 404


@pytest.mark.asyncio
async def test_diagnostics_endpoint_builders_project_operations_hooks_and_kernel() -> None:
    app = _build_app()

    healthz = build_healthz_endpoint(None)
    methodz = build_methodz_endpoint(app)
    hookz = build_hookz_endpoint(app)
    kernelz = build_kernelz_endpoint(app)

    request = Request(
        method="GET",
        path="/healthz",
        headers={},
        query={},
        path_params={},
        body=b"",
    )

    health_payload = await healthz(request)
    method_payload = await methodz()
    hook_payload = await hookz()
    kernel_payload = await kernelz()

    assert health_payload == {"ok": True}
    assert any(
        entry["model"] == "SystemDocsWidget" and entry["alias"] == "create"
        for entry in method_payload["methods"]
    )
    assert "SystemDocsWidget" in hook_payload
    assert "SystemDocsWidget" in kernel_payload


@pytest.mark.asyncio
async def test_methodz_payload_is_stable_sorted_and_filters_non_rpc_ops() -> None:
    class MethodzPayloadWidget(TableBase, GUIDPk):
        __tablename__ = "system_docs_methodz_payload_widgets"
        __tigrbl_ops__ = (
            OpSpec(alias="z_hidden", target="custom", expose_rpc=False),
            OpSpec(alias="alpha_visible", target="custom"),
        )

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    app.include_table(MethodzPayloadWidget)

    methodz = build_methodz_endpoint(app)
    first = await methodz()
    second = await methodz()

    assert first is second
    entries = first["methods"]
    aliases = [entry["alias"] for entry in entries if entry["model"] == "MethodzPayloadWidget"]

    assert aliases == sorted(aliases)
    assert "alpha_visible" in aliases
    assert "z_hidden" not in aliases

    visible = next(
        entry
        for entry in entries
        if entry["model"] == "MethodzPayloadWidget" and entry["alias"] == "alpha_visible"
    )
    assert set(visible) == {
        "method",
        "model",
        "alias",
        "target",
        "arity",
        "persist",
        "request_model",
        "response_model",
        "routes",
        "rpc",
        "tags",
    }
    assert visible["method"] == "MethodzPayloadWidget.alpha_visible"
    assert visible["target"] == "custom"
    assert visible["rpc"] is True
    assert first["MethodzPayloadWidget"] == [
        entry for entry in entries if entry["model"] == "MethodzPayloadWidget"
    ]


@pytest.mark.asyncio
async def test_kernelz_payload_is_stable_and_projects_kernel_phase_labels() -> None:
    app = _build_app()
    kernelz = build_kernelz_endpoint(app)

    first = await kernelz()
    second = await kernelz()

    assert first == second
    assert "SystemDocsWidget" in first
    assert "create" in first["SystemDocsWidget"]
    create_labels = first["SystemDocsWidget"]["create"]

    assert create_labels
    assert all(isinstance(label, str) and label for label in create_labels)
    assert any(label.startswith("START_TX:") for label in create_labels)
    assert any(label.startswith("HANDLER:") for label in create_labels)
    assert any(label.startswith("TX_COMMIT:") for label in create_labels)


@pytest.mark.unit
def test_root_build_helpers_materialize_schema_hook_and_rest_surfaces() -> None:
    class RootHelperWidget(TableBase, GUIDPk):
        __tablename__ = "system_docs_root_helper_widgets"

        name = Column(String, nullable=False)

    app = TigrblApp(mount_system=False)
    specs = app.include_table(RootHelperWidget, mount_router=False)[0].ops.all

    build_schemas(RootHelperWidget, specs)
    build_hooks(RootHelperWidget, specs)
    build_rest(RootHelperWidget, specs)

    assert getattr(RootHelperWidget, "schemas").create.in_ is not None
    assert getattr(RootHelperWidget, "hooks").create is not None
    assert getattr(RootHelperWidget, "rest").router is not None


@pytest.mark.unit
def test_api_level_auth_survives_include_router_openapi_projection() -> None:
    app = TigrblApp(mount_system=False)
    app.set_auth(authn=_bearer_auth, allow_anon=False)
    app.include_table(SystemDocsSecureWidget)

    root = Router()
    root.include_router(app.router)
    schema = build_openapi(root)

    paths = {
        route.name: route.path_template
        for route in app.routers["SystemDocsSecureWidget"].routes
    }
    list_sec = schema["paths"][paths["SystemDocsSecureWidget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["SystemDocsSecureWidget.read"]]["get"].get("security")

    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
