from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp
from tigrbl_core.config.constants import (
    DEFAULT_ROOT_RESPONSE,
    TIGRBL_DEFAULT_ROOT_ALIAS,
)


def _route_aliases(app: TigrblApp) -> set[str]:
    route_model = app.tables["__tigrbl_route_ops__"]
    return {
        str(getattr(item, "alias", ""))
        for item in tuple(getattr(getattr(route_model, "ops", None), "all", ()) or ())
    }


@pytest.mark.asyncio
async def test_default_root_endpoint_is_available_on_tigrbl_app() -> None:
    app = TigrblApp(mount_system=False)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == dict(DEFAULT_ROOT_RESPONSE)
    assert TIGRBL_DEFAULT_ROOT_ALIAS in _route_aliases(app)


@pytest.mark.asyncio
async def test_explicit_get_root_overrides_default_endpoint() -> None:
    app = TigrblApp(mount_system=False)

    @app.get("/")
    async def root() -> dict[str, object]:
        return {"custom": True, "ok": False}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"custom": True, "ok": False}
    assert TIGRBL_DEFAULT_ROOT_ALIAS not in _route_aliases(app)
