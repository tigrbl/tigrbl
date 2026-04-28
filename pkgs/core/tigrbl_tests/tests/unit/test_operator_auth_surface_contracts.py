from __future__ import annotations

from httpx import ASGITransport, Client
import pytest

from tigrbl import HTTPBearer, Request, TableBase, TigrblApp
from tigrbl._concrete._security.http_bearer import HTTPAuthorizationCredentials
from tigrbl.decorators.allow_anon import allow_anon
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.status import HTTPException
from tigrbl.security import Security
from tigrbl.types import AuthNProvider, Column, String


class RequiredBearerAuth(AuthNProvider):
    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> dict[str, str]:
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        return {"sub": "operator"}


def _build_auth_app(*, authorize=None) -> Client:
    TableBase.metadata.clear()

    @allow_anon("list")
    class OperatorAuthWidget(TableBase, GUIDPk):
        __tablename__ = "operator_auth_surface_widget"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(
        authn=RequiredBearerAuth().get_principal,
        authorize=authorize,
        allow_anon=False,
    )
    app.include_table(OperatorAuthWidget)
    app.initialize()
    return Client(transport=ASGITransport(app=app), base_url="http://test")


def test_operator_auth_surface_is_dependency_based_and_projects_openapi_security() -> None:
    client = _build_auth_app()
    try:
        spec = client.get("/openapi.json").json()
        path = spec["paths"]["/operatorauthwidget"]

        assert path["get"].get("security") in (None, [])
        assert path["get"]["x-tigrbl-auth"] == {
            "policy": "public-by-default",
            "public": True,
            "security": [],
        }
        assert path["post"]["security"] == [{"HTTPBearer": []}]
        assert path["post"]["x-tigrbl-auth"] == {
            "policy": "protected",
            "public": False,
            "security": [{"HTTPBearer": []}],
        }
        assert spec["components"]["securitySchemes"]["HTTPBearer"] == {
            "type": "http",
            "scheme": "bearer",
        }
    finally:
        client.close()


def test_operator_auth_surface_allow_anon_does_not_unprotect_other_ops() -> None:
    client = _build_auth_app()
    try:
        assert client.get("/operatorauthwidget").status_code == 200
        assert client.post("/operatorauthwidget", json={"name": "blocked"}).status_code == 403
        assert (
            client.post(
                "/operatorauthwidget",
                json={"name": "created"},
                headers={"Authorization": "Bearer secret"},
            ).status_code
            == 201
        )
    finally:
        client.close()


@pytest.mark.xfail(
    reason=(
        "feat:operator-auth-dependency-hook-surface-001 is partial; "
        "authorize hook rejection currently projects as 400 instead of 403."
    ),
)
def test_operator_auth_surface_authorize_hook_can_reject_requests() -> None:
    def deny_create(_request, _model, alias, _payload, _user):
        return alias != "create"

    client = _build_auth_app(authorize=deny_create)
    try:
        response = client.post(
            "/operatorauthwidget",
            json={"name": "denied"},
            headers={"Authorization": "Bearer secret"},
        )

        assert response.status_code == 403
        assert "traceback" not in response.text.lower()
    finally:
        client.close()


def test_operator_auth_surface_does_not_advertise_generic_auth_middleware() -> None:
    catalog = "docs/developer/operator/middleware-catalog.md"
    text = __import__("pathlib").Path(catalog).read_text(encoding="utf-8")

    assert "dependency/hook-based only" in text
    assert "monolithic generic auth middleware" in text
    assert "generic auth middleware abstraction" in text


def test_generated_crud_openapi_declares_public_default_without_authn() -> None:
    TableBase.metadata.clear()

    class PublicWidget(TableBase, GUIDPk):
        __tablename__ = "operator_public_default_widget"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(PublicWidget)
    app.initialize()
    client = Client(transport=ASGITransport(app=app), base_url="http://test")

    try:
        spec = client.get("/openapi.json").json()
        operations = spec["paths"]["/publicwidget"]

        assert operations["get"].get("security") in (None, [])
        assert operations["get"]["x-tigrbl-auth"] == {
            "policy": "public-by-default",
            "public": True,
            "security": [],
        }
        assert operations["post"].get("security") in (None, [])
        assert operations["post"]["x-tigrbl-auth"] == {
            "policy": "public-by-default",
            "public": True,
            "security": [],
        }
    finally:
        client.close()
