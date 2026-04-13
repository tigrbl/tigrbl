from __future__ import annotations

import asyncio
import json
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from sqlalchemy import Column, String

from tigrbl import APIKey, HTTPBasic, HTTPBearer, MutualTLS, OAuth2, OpenIdConnect, TigrblApp, TigrblRouter
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.security import Security

SNAPSHOT_DIR = (
    Path(__file__).resolve().parents[5]
    / "docs"
    / "conformance"
    / "audit"
    / "2026"
    / "phase5-oas-jsonschema-jsonrpc-openrpc-closure"
    / "snapshots"
)
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
EXPECTED_SECURITY_SCHEMES = {
    "ApiKeyAuth",
    "BasicAuth",
    "BearerAuth",
    "MutualTLSAuth",
    "OAuth2Auth",
    "OpenIdAuth",
}


def _basic_dep(cred=Security(HTTPBasic(scheme_name="BasicAuth"))):
    return cred


def _bearer_dep(cred=Security(HTTPBearer(scheme_name="BearerAuth"))):
    return cred


def _api_key_dep(cred=Security(APIKey(scheme_name="ApiKeyAuth", name="X-API-Key"))):
    return cred


def _oauth2_dep(
    cred=Security(
        OAuth2(
            scheme_name="OAuth2Auth",
            flows={"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
        )
    ),
):
    return cred


def _openid_dep(
    cred=Security(
        OpenIdConnect(
            scheme_name="OpenIdAuth",
            openid_connect_url="https://issuer.example/.well-known/openid-configuration",
        )
    ),
):
    return cred


def _mtls_dep(cred=Security(MutualTLS(scheme_name="MutualTLSAuth"))):
    return cred


class Phase5CreateWidget(BaseModel):
    name: str


class Phase5WidgetOut(BaseModel):
    id: str
    name: str


class Phase5BasicDocsTable(TableBase, GUIDPk):
    __tablename__ = "phase5_basic_docs_table"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias="read", target="read", secdeps=(_basic_dep,)),)


class Phase5BearerDocsTable(TableBase, GUIDPk):
    __tablename__ = "phase5_bearer_docs_table"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias="read", target="read", secdeps=(_bearer_dep,)),)


class Phase5RouterDocsTable(TableBase, GUIDPk):
    __tablename__ = "phase5_router_docs_table"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias="read", target="read", secdeps=(_api_key_dep,)),)


class Phase5TableDocsTable(TableBase, GUIDPk):
    __tablename__ = "phase5_table_docs_table"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(
            alias="read",
            target="read",
            secdeps=(_oauth2_dep, _openid_dep, _mtls_dep),
        ),
    )


def _build_app() -> TigrblApp:
    router = TigrblRouter(title="Phase 5 Router", version="5.0.0", engine=mem(async_=False))

    @router.post(
        "/widgets/{widget_id}",
        tags=["widgets"],
        summary="Create widget",
        description="Create or update a widget",
        request_model=Phase5CreateWidget,
        response_model=Phase5WidgetOut,
        path_param_schemas={"widget_id": {"type": "string"}},
        query_param_schemas={"verbose": {"type": "boolean", "required": False}},
    )
    def create(widget_id: str):
        return {"id": widget_id, "name": widget_id}

    router.include_table(Phase5BasicDocsTable)
    router.include_table(Phase5RouterDocsTable)
    router.include_table(Phase5TableDocsTable)

    app = TigrblApp(title="Phase 5 API", version="5.0.0", engine=mem(async_=False))
    app.include_table(Phase5BearerDocsTable)
    app.include_router(router)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()
    return app


def _load_json_snapshot(name: str) -> dict[str, object]:
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def test_phase5_generated_specs_and_snapshot_artifacts_cover_required_contracts() -> None:
    app = _build_app()

    async def _fetch() -> tuple[dict[str, object], dict[str, object], str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            openapi_doc = (await client.get("/openapi.json")).json()
            openrpc_doc = (await client.get("/openrpc.json")).json()
            swagger_html = (await client.get("/docs")).text
            lens_html = (await client.get("/lens")).text
        return openapi_doc, openrpc_doc, swagger_html, lens_html

    openapi_doc, openrpc_doc, swagger_html, lens_html = asyncio.run(_fetch())

    snapshot_openapi = _load_json_snapshot("openapi_snapshot.json")
    snapshot_openrpc = _load_json_snapshot("openrpc_snapshot.json")
    snapshot_swagger = (SNAPSHOT_DIR / "swagger_snapshot.html").read_text(encoding="utf-8")
    snapshot_lens = (SNAPSHOT_DIR / "lens_snapshot.html").read_text(encoding="utf-8")

    assert openapi_doc["openapi"] == "3.1.0"
    assert openapi_doc["jsonSchemaDialect"] == JSON_SCHEMA_DIALECT
    assert set(openapi_doc["components"]["securitySchemes"]) == EXPECTED_SECURITY_SCHEMES
    assert "Phase5CreateWidget" in openapi_doc["components"]["schemas"]
    assert "Phase5WidgetOut" in openapi_doc["components"]["schemas"]

    widget_post = openapi_doc["paths"]["/widgets/{widget_id}"]["post"]
    assert widget_post["summary"] == "Create widget"
    assert widget_post["description"] == "Create or update a widget"
    assert widget_post["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/Phase5CreateWidget"
    }
    assert widget_post["responses"]["201"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/Phase5WidgetOut"
    }
    assert widget_post["parameters"] == [
        {"name": "widget_id", "in": "path", "required": True, "schema": {"type": "string"}},
        {"name": "verbose", "in": "query", "required": False, "schema": {"type": "boolean"}},
    ]

    assert openapi_doc["paths"]["/phase5basicdocstable/{item_id}"]["get"]["security"] == [{"BasicAuth": []}]
    assert openapi_doc["paths"]["/phase5bearerdocstable/{item_id}"]["get"]["security"] == [{"BearerAuth": []}]
    assert openapi_doc["paths"]["/phase5routerdocstable/{item_id}"]["get"]["security"] == [{"ApiKeyAuth": []}]
    assert openapi_doc["paths"]["/phase5tabledocstable/{item_id}"]["get"]["security"] == [
        {"OAuth2Auth": []},
        {"OpenIdAuth": []},
        {"MutualTLSAuth": []},
    ]

    assert snapshot_openapi["openapi"] == openapi_doc["openapi"]
    assert snapshot_openapi["jsonSchemaDialect"] == openapi_doc["jsonSchemaDialect"]
    assert set(snapshot_openapi["components"]["securitySchemes"]) == EXPECTED_SECURITY_SCHEMES
    assert snapshot_openapi["paths"]["/widgets/{widget_id}"]["post"]["parameters"] == widget_post["parameters"]

    assert openrpc_doc["openrpc"] == "1.2.6"
    assert set(openrpc_doc["components"]["securitySchemes"]) == EXPECTED_SECURITY_SCHEMES
    methods_by_name = {method["name"]: method for method in openrpc_doc["methods"]}
    assert methods_by_name["Phase5BasicDocsTable.read"]["security"] == [{"BasicAuth": []}]
    assert methods_by_name["Phase5BearerDocsTable.read"]["security"] == [{"BearerAuth": []}]
    assert methods_by_name["Phase5RouterDocsTable.read"]["security"] == [{"ApiKeyAuth": []}]
    assert methods_by_name["Phase5TableDocsTable.read"]["security"] == [
        {"OAuth2Auth": []},
        {"OpenIdAuth": []},
        {"MutualTLSAuth": []},
    ]
    assert len(methods_by_name) == 28
    assert "create" not in methods_by_name

    snapshot_methods_by_name = {method["name"]: method for method in snapshot_openrpc["methods"]}
    assert snapshot_openrpc["openrpc"] == openrpc_doc["openrpc"]
    assert set(snapshot_openrpc["components"]["securitySchemes"]) == EXPECTED_SECURITY_SCHEMES
    assert set(snapshot_methods_by_name) == set(methods_by_name)
    assert snapshot_methods_by_name["Phase5BasicDocsTable.read"]["security"] == methods_by_name["Phase5BasicDocsTable.read"]["security"]
    assert snapshot_methods_by_name["Phase5TableDocsTable.read"]["security"] == methods_by_name["Phase5TableDocsTable.read"]["security"]

    assert "swagger-ui" in swagger_html.lower()
    assert "swagger-ui" in snapshot_swagger.lower()
    assert "phase 5 api" in swagger_html.lower()
    assert "phase 5 api" in snapshot_swagger.lower()

    assert "lens" in lens_html.lower()
    assert "openrpc" in lens_html.lower()
    assert "lens" in snapshot_lens.lower()
    assert "openrpc" in snapshot_lens.lower()
