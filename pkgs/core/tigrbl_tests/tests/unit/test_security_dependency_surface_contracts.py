from __future__ import annotations

import base64
import asyncio
from types import SimpleNamespace

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import Column, String

from tigrbl import (
    HTTPBasic,
    MutualTLS,
    OAuth2,
    OpenIdConnect,
    TigrblApp,
)
from tigrbl._spec import OpSpec
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.security import Security
from tigrbl_base._base._security_base import OpenAPISecurityDependency


def _basic_dep(
    cred=Security(
        HTTPBasic(
            scheme_name="BasicAuth",
            realm="operators",
            description="HTTP Basic operator credential",
        )
    ),
):
    return cred


def _oauth2_dep(
    cred=Security(
        OAuth2(
            scheme_name="OAuth2Auth",
            flows={"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
            scopes=("jobs:read",),
            description="OAuth2 client credential flow",
        )
    ),
):
    return cred


def _openid_dep(
    cred=Security(
        OpenIdConnect(
            scheme_name="OpenIdAuth",
            openid_connect_url="https://issuer.example/.well-known/openid-configuration",
            description="OpenID Connect discovery",
        )
    ),
):
    return cred


def _mtls_dep(
    cred=Security(
        MutualTLS(
            scheme_name="MutualTLSAuth",
            description="Mutual TLS client certificate",
        )
    ),
):
    return cred


class SecurityDependencyTable(TableBase, GUIDPk):
    __tablename__ = "security_dependency_surface_contracts"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(
            alias="read",
            target="read",
            secdeps=(_basic_dep, _oauth2_dep, _openid_dep, _mtls_dep),
        ),
    )


@pytest.mark.unit
def test_security_dependency_classes_are_first_class_openapi_dependencies() -> None:
    basic = HTTPBasic(scheme_name="BasicAuth", realm="operators")
    oauth2 = OAuth2(
        scheme_name="OAuth2Auth",
        flows={"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
        scopes=("jobs:read",),
    )
    openid = OpenIdConnect(
        scheme_name="OpenIdAuth",
        openid_connect_url="https://issuer.example/.well-known/openid-configuration",
    )
    mtls = MutualTLS(scheme_name="MutualTLSAuth")

    for dependency in (basic, oauth2, openid, mtls):
        assert isinstance(dependency, OpenAPISecurityDependency)
        assert dependency.openapi_security_requirement() == {
            dependency.scheme_name: list(getattr(dependency, "_scopes", []))
        }

    assert basic.openapi_security_scheme() == {"type": "http", "scheme": "basic"}
    assert oauth2.openapi_security_scheme() == {
        "type": "oauth2",
        "flows": {"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
    }
    assert oauth2.openapi_security_requirement() == {"OAuth2Auth": ["jobs:read"]}
    assert openid.openapi_security_scheme() == {
        "type": "openIdConnect",
        "openIdConnectUrl": "https://issuer.example/.well-known/openid-configuration",
    }
    assert mtls.openapi_security_scheme() == {"type": "mutualTLS"}


@pytest.mark.unit
def test_http_basic_dependency_decodes_credentials_and_fails_closed() -> None:
    dependency = HTTPBasic(auto_error=False)
    token = base64.b64encode(b"alice:secret").decode("ascii")

    credentials = dependency(
        SimpleNamespace(headers={"authorization": f"Basic {token}"})
    )

    assert credentials is not None
    assert credentials.username == "alice"
    assert credentials.password == "secret"
    assert dependency(SimpleNamespace(headers={})) is None
    assert dependency(SimpleNamespace(headers={"authorization": "Bearer token"})) is None


@pytest.mark.unit
def test_security_dependencies_project_to_openapi_and_openrpc() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(SecurityDependencyTable)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()

    async def _fetch() -> tuple[dict[str, object], dict[str, object]]:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            openapi = (await client.get("/openapi.json")).json()
            openrpc = (await client.get("/openrpc.json")).json()
        return openapi, openrpc

    openapi, openrpc = asyncio.run(_fetch())
    expected_schemes = {
        "BasicAuth": {
            "type": "http",
            "scheme": "basic",
            "description": "HTTP Basic operator credential",
        },
        "OAuth2Auth": {
            "type": "oauth2",
            "flows": {"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
            "description": "OAuth2 client credential flow",
        },
        "OpenIdAuth": {
            "type": "openIdConnect",
            "openIdConnectUrl": "https://issuer.example/.well-known/openid-configuration",
            "description": "OpenID Connect discovery",
        },
        "MutualTLSAuth": {
            "type": "mutualTLS",
            "description": "Mutual TLS client certificate",
        },
    }
    expected_security = [
        {"BasicAuth": []},
        {"OAuth2Auth": ["jobs:read"]},
        {"OpenIdAuth": []},
        {"MutualTLSAuth": []},
    ]

    assert openapi["components"]["securitySchemes"] == expected_schemes
    assert openrpc["components"]["securitySchemes"] == expected_schemes

    openapi_security = [
        security
        for path_item in openapi["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict)
        for security in operation.get("security", [])
    ]
    assert expected_security == openapi_security

    method_map = {method["name"]: method for method in openrpc["methods"]}
    assert method_map["SecurityDependencyTable.read"]["security"] == expected_security
