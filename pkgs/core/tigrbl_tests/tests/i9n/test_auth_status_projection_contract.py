from __future__ import annotations

from httpx import ASGITransport, Client
from sqlalchemy.orm import sessionmaker

from tigrbl import HTTPBearer, Request, TableBase, TigrblApp, TigrblRouter
from tigrbl import resolver as _resolver
from tigrbl._concrete._security.http_bearer import HTTPAuthorizationCredentials
from tigrbl.decorators.allow_anon import allow_anon
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.status import HTTPException
from tigrbl.security import Security
from tigrbl.types import AuthNProvider, Column, String, uuid4


class RequiredBearerAuth(AuthNProvider):
    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> dict:
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        return {"sub": "user"}


def _client_with_required_auth() -> Client:
    TableBase.metadata.clear()

    class Secret(TableBase, GUIDPk):
        __tablename__ = "auth_status_projection_secret"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=RequiredBearerAuth().get_principal)
    app.include_table(Secret)
    app.initialize()
    return Client(transport=ASGITransport(app=app), base_url="http://test")


def test_required_bearer_auth_projects_missing_and_wrong_credentials_statuses() -> None:
    client = _client_with_required_auth()
    try:
        assert client.get("/secret").status_code == 403
        assert client.get(
            "/secret", headers={"Authorization": "Bearer wrong"}
        ).status_code == 401
    finally:
        client.close()


def test_allow_anon_create_projects_rest_created_status_without_credentials() -> None:
    TableBase.metadata.clear()

    @allow_anon("create")
    class PublicItem(TableBase, GUIDPk):
        __tablename__ = "auth_status_projection_public_item"
        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(PublicItem)
    router.initialize()
    app = TigrblApp()
    app.include_router(router)
    app.initialize()

    provider = _resolver.resolve_provider()
    engine, _ = provider.ensure()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    client = Client(transport=ASGITransport(app=app), base_url="http://test")
    try:
        payload = {"id": str(uuid4()), "name": "public"}
        response = client.post("/publicitem", json=payload)

        assert response.status_code == 201
        with SessionLocal() as db:
            assert db.query(PublicItem).count() == 1
    finally:
        client.close()
