from __future__ import annotations

import pytest
from httpx import ASGITransport, Client

from tigrbl import TigrblApp, TigrblRouter
from tigrbl.factories.engine import mem
from tigrbl.system import (
    WellKnownResource,
    mount_well_known,
    normalize_well_known_name,
    well_known_path,
)


OIDC_DISCOVERY_PAYLOAD = {
    "issuer": "https://issuer.example",
    "jwks_uri": "https://issuer.example/.well-known/jwks.json",
    "authorization_endpoint": "https://issuer.example/oauth2/authorize",
    "token_endpoint": "https://issuer.example/oauth2/token",
}


def _client(app: TigrblApp) -> Client:
    return Client(transport=ASGITransport(app=app), base_url="http://test")


def test_well_known_uris_are_not_mounted_by_default() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.initialize()

    client = _client(app)
    try:
        for path in (
            "/.well-known/openid-configuration",
            "/.well-known/jwks.json",
            "/system/.well-known/openid-configuration",
            "/openid-configuration",
            "/jwks.json",
        ):
            assert client.get(path).status_code == 404, path
    finally:
        client.close()


def test_mount_well_known_publishes_explicit_root_resource() -> None:
    app = TigrblApp(engine=mem(async_=False))

    mounted = mount_well_known(
        app,
        {
            "openid-configuration": OIDC_DISCOVERY_PAYLOAD,
        },
    )

    assert mounted == ("/.well-known/openid-configuration",)
    assert app._well_known_mounts == list(mounted)

    client = _client(app)
    try:
        response = client.get("/.well-known/openid-configuration")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert response.json() == OIDC_DISCOVERY_PAYLOAD
        assert client.get("/system/.well-known/openid-configuration").status_code == 404
    finally:
        client.close()


def test_app_and_included_router_can_both_mount_well_known_resources() -> None:
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    router = TigrblRouter(engine=mem(async_=False))

    app_mounted = app.mount_well_known(
        [
            WellKnownResource(
                name="/.well-known/openid-configuration",
                payload=OIDC_DISCOVERY_PAYLOAD,
                headers={"cache-control": "public, max-age=300"},
            )
        ]
    )
    router_mounted = router.mount_well_known({"jwks.json": {"keys": []}})
    app.include_router(router)

    assert app_mounted == ("/.well-known/openid-configuration",)
    assert router_mounted == ("/.well-known/jwks.json",)

    client = _client(app)
    try:
        discovery = client.get("/.well-known/openid-configuration")
        jwks = client.get("/.well-known/jwks.json")

        assert discovery.status_code == 200
        assert discovery.json() == OIDC_DISCOVERY_PAYLOAD
        assert discovery.headers["cache-control"] == "public, max-age=300"
        assert jwks.status_code == 200
        assert jwks.json() == {"keys": []}
        assert client.get("/system/.well-known/openid-configuration").status_code == 404
        assert client.get("/system/.well-known/jwks.json").status_code == 404
    finally:
        client.close()


def test_router_method_mounts_well_known_resource_when_router_is_included() -> None:
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    router = TigrblRouter(engine=mem(async_=False))

    mounted = router.mount_well_known(
        [
            {
                "name": "jwks.json",
                "payload": {"keys": []},
            }
        ],
    )
    app.include_router(router)

    assert mounted == ("/.well-known/jwks.json",)

    client = _client(app)
    try:
        response = client.get("/.well-known/jwks.json")
        assert response.status_code == 200
        assert response.json() == {"keys": []}
    finally:
        client.close()


@pytest.mark.parametrize(
    "name",
    [
        "",
        "/openid-configuration",
        "../openid-configuration",
        "openid-configuration/../jwks.json",
        "openid-configuration?x=1",
        "openid-configuration#fragment",
    ],
)
def test_well_known_name_validation_rejects_ambiguous_or_unsafe_names(
    name: str,
) -> None:
    with pytest.raises(ValueError):
        normalize_well_known_name(name)


def test_well_known_path_normalization_accepts_relative_and_canonical_names() -> None:
    assert well_known_path("openid-configuration") == (
        "/.well-known/openid-configuration"
    )
    assert well_known_path("/.well-known/jwks.json") == "/.well-known/jwks.json"
    assert well_known_path("oauth-authorization-server") == (
        "/.well-known/oauth-authorization-server"
    )
