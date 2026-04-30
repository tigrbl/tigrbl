from __future__ import annotations

import json
from pathlib import Path

from httpx import ASGITransport, Client

from tigrbl import HTTPBearer, TableBase, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.security import Security
from tigrbl.types import Column, String


ROOT = Path(__file__).resolve().parents[5]


def test_oidc_discovery_docs_are_explicitly_descoped_in_operator_docs() -> None:
    docs_ui = (ROOT / "docs/developer/operator/docs-ui.md").read_text(encoding="utf-8")
    operator_surfaces = (ROOT / "docs/developer/OPERATOR_SURFACES.md").read_text(
        encoding="utf-8"
    )
    current_target = (ROOT / "docs/conformance/CURRENT_TARGET.md").read_text(
        encoding="utf-8"
    )

    for text in (docs_ui, operator_surfaces, current_target):
        assert "OIDC discovery/docs surface" in text
    assert "de-scoped from the current cycle" in docs_ui


def test_oidc_discovery_routes_are_not_mounted_by_default() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.initialize()

    client = Client(transport=ASGITransport(app=app), base_url="http://test")
    try:
        for path in (
            "/.well-known/openid-configuration",
            "/system/.well-known/openid-configuration",
            "/openid-configuration",
            "/jwks.json",
            "/system/jwks.json",
        ):
            assert client.get(path).status_code == 404, path
    finally:
        client.close()


def test_oidc_descope_does_not_remove_openapi_security_projection() -> None:
    TableBase.metadata.clear()

    class OidcDescopeSecurityWidget(TableBase, GUIDPk):
        __tablename__ = "operator_oidc_descope_security_widget"
        name = Column(String, nullable=False)

    async def authn(creds=Security(HTTPBearer())):
        return {"sub": creds.credentials}

    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=authn, allow_anon=False)
    app.include_table(OidcDescopeSecurityWidget)
    app.initialize()

    client = Client(transport=ASGITransport(app=app), base_url="http://test")
    try:
        spec = client.get("/openapi.json").json()
        operation = spec["paths"]["/oidcdescopesecuritywidget"]["get"]

        assert operation["security"] == [{"HTTPBearer": []}]
        assert spec["components"]["securitySchemes"]["HTTPBearer"] == {
            "type": "http",
            "scheme": "bearer",
        }
    finally:
        client.close()


def test_oidc_descoped_feature_is_not_marked_implemented_without_route_evidence() -> None:
    registry = json.loads((ROOT / ".ssot/registry.json").read_text(encoding="utf-8"))
    feature = next(
        row
        for row in registry["features"]
        if row["id"] == "feat:operator-oidc-discovery-docs-descoped-001"
    )

    assert feature["implementation_status"] == "partial"
    assert "OIDC discovery and docs surface out of bounds" in feature["title"]
