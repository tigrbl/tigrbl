from __future__ import annotations

from httpx import ASGITransport, AsyncClient
import pytest

from tigrbl import Request, TigrblApp
from tigrbl.system import build_healthz_uix, build_lens, build_swagger, mount_healthz_uix


def _request(path: str = "/docs") -> Request:
    return Request(
        method="GET",
        path=path,
        headers={},
        query={},
        path_params={},
        body=b"",
    )


@pytest.mark.unit
def test_build_lens_helper_returns_openrpc_uix_html() -> None:
    app = TigrblApp()

    html = build_lens(app, _request("/lens"), spec_path="/openrpc.json")

    assert "<!doctype html>" in html.lower()
    assert "@tigrbljs/tigrbl-lens" in html
    assert "EmbeddedLens" in html
    assert "/openrpc.json" in html
    assert 'id="root"' in html


@pytest.mark.unit
def test_openapi_and_healthz_uix_build_helpers_return_html() -> None:
    app = TigrblApp()

    openapi_html = build_swagger(app, _request("/docs"))
    healthz_html = build_healthz_uix(
        app,
        _request("/healthz"),
        healthz_path="/system/healthz",
    )

    assert "swagger-ui" in openapi_html
    assert "/openapi.json" in openapi_html
    assert "<title>TigrblApp health</title>" in healthz_html
    assert 'fetch("/system/healthz"' in healthz_html
    assert 'id="payload"' in healthz_html


@pytest.mark.asyncio
async def test_default_uix_routes_are_human_viewable_get_surfaces() -> None:
    app = TigrblApp()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        docs = await client.get("/docs")
        lens = await client.get("/lens")
        healthz_uix = await client.get("/healthz")
        healthz_json = await client.get("/system/healthz")

    assert docs.status_code == 200
    assert "text/html" in docs.headers.get("content-type", "")
    assert "swagger-ui" in docs.text

    assert lens.status_code == 200
    assert "text/html" in lens.headers.get("content-type", "")
    assert "@tigrbljs/tigrbl-lens" in lens.text
    assert "/openrpc.json" in lens.text

    assert healthz_uix.status_code == 200
    assert "text/html" in healthz_uix.headers.get("content-type", "")
    assert 'fetch("/system/healthz"' in healthz_uix.text
    assert 'id="payload"' in healthz_uix.text

    assert healthz_json.status_code == 200
    assert healthz_json.json() == {"ok": True}


@pytest.mark.asyncio
async def test_custom_healthz_uix_route_can_target_custom_health_payload() -> None:
    app = TigrblApp(mount_system=False)
    app.attach_diagnostics(prefix="/internal")
    mount_healthz_uix(app, path="/status", healthz_path="/internal/healthz")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        status = await client.get("/status")
        health = await client.get("/internal/healthz")

    assert status.status_code == 200
    assert 'fetch("/internal/healthz"' in status.text
    assert health.status_code == 200
    assert health.json() == {"ok": True}


@pytest.mark.unit
def test_uix_routes_are_not_projected_as_rpc_methods_or_openapi_operations() -> None:
    app = TigrblApp()

    route_map = {route.path: route for route in app.routes}
    for path in ("/docs", "/lens", "/healthz"):
        assert path in route_map
        assert set(route_map[path].methods or []) == {"GET"}
        assert route_map[path].include_in_schema is False
        assert route_map[path].inherit_owner_dependencies is False

    openrpc_methods = {method["name"] for method in app.openrpc()["methods"]}
    for forbidden in ("docs", "lens", "healthz", "openapi"):
        assert all(forbidden not in name.lower() for name in openrpc_methods)
