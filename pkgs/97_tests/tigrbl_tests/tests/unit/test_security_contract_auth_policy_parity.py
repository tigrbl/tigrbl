from __future__ import annotations

from httpx import ASGITransport, Client
from sqlalchemy import Column, String

from tigrbl import HTTPBearer, TableBase, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.security import Security


def _authn(cred=Security(HTTPBearer())):
    return {"sub": cred.credentials}


def _build_app(*, protected: bool) -> TigrblApp:
    TableBase.metadata.clear()

    class Tenant(TableBase, GUIDPk):
        __tablename__ = (
            "security_contract_protected_tenants"
            if protected
            else "security_contract_public_tenants"
        )

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    if protected:
        app.set_auth(authn=_authn, allow_anon=False)
    app.include_table(Tenant)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()
    return app


def _client(app: TigrblApp) -> Client:
    return Client(transport=ASGITransport(app=app), base_url="http://test")


def test_openapi_generated_crud_declares_public_default_auth_surface() -> None:
    app = _build_app(protected=False)

    with _client(app) as client:
        openapi = client.get("/openapi.json").json()

    operation = openapi["paths"]["/tenant"]["get"]

    assert operation.get("security") in (None, [])
    assert operation["x-tigrbl-auth"] == {
        "policy": "public-by-default",
        "public": True,
        "security": [],
    }
    assert "securitySchemes" not in openapi.get("components", {})


def test_openrpc_generated_methods_declare_public_default_auth_surface() -> None:
    app = _build_app(protected=False)

    with _client(app) as client:
        openrpc = client.get("/openrpc.json").json()

    method = {entry["name"]: entry for entry in openrpc["methods"]}["Tenant.list"]

    assert method.get("security") in (None, [])
    assert method["x-tigrbl-auth"] == {
        "policy": "public-by-default",
        "public": True,
        "security": [],
    }
    assert openrpc["components"]["securitySchemes"] == {}


def test_rest_generated_read_matches_auth_policy() -> None:
    public_app = _build_app(protected=False)
    protected_app = _build_app(protected=True)

    with _client(public_app) as client:
        public_response = client.get("/tenant")
        public_openapi = client.get("/openapi.json").json()

    with _client(protected_app) as client:
        protected_response = client.get("/tenant")
        protected_openapi = client.get("/openapi.json").json()

    public_operation = public_openapi["paths"]["/tenant"]["get"]
    protected_operation = protected_openapi["paths"]["/tenant"]["get"]

    assert public_response.status_code == 200
    assert public_operation["x-tigrbl-auth"]["policy"] == "public-by-default"
    assert public_operation.get("security") in (None, [])

    assert protected_response.status_code in {401, 403}
    assert protected_operation["x-tigrbl-auth"] == {
        "policy": "protected",
        "public": False,
        "security": [{"HTTPBearer": []}],
    }
    assert protected_operation["security"] == [{"HTTPBearer": []}]
    assert protected_openapi["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }


def test_jsonrpc_generated_read_matches_auth_policy() -> None:
    public_app = _build_app(protected=False)
    protected_app = _build_app(protected=True)
    payload = {"jsonrpc": "2.0", "method": "Tenant.list", "params": {}, "id": 1}

    with _client(public_app) as client:
        public_response = client.post("/rpc", json=payload)
        public_openrpc = client.get("/openrpc.json").json()

    with _client(protected_app) as client:
        protected_response = client.post("/rpc", json=payload)
        protected_openrpc = client.get("/openrpc.json").json()

    public_method = {
        entry["name"]: entry for entry in public_openrpc["methods"]
    }["Tenant.list"]
    protected_method = {
        entry["name"]: entry for entry in protected_openrpc["methods"]
    }["Tenant.list"]

    assert public_response.status_code == 200
    assert public_response.json()["result"] == []
    assert public_method["x-tigrbl-auth"]["policy"] == "public-by-default"
    assert public_method.get("security") in (None, [])

    protected_payload = protected_response.json()
    assert protected_response.status_code == 200
    assert "result" not in protected_payload
    assert protected_payload["error"]["message"] in {
        "Insufficient permissions",
        "Unauthorized",
    }
    assert protected_method["x-tigrbl-auth"] == {
        "policy": "protected",
        "public": False,
        "security": [{"HTTPBearer": []}],
    }
    assert protected_method["security"] == [{"HTTPBearer": []}]
    assert protected_openrpc["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
