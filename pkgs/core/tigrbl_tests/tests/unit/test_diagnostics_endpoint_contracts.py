from __future__ import annotations

from httpx import ASGITransport, AsyncClient
import pytest
from types import SimpleNamespace

from tigrbl import TigrblApp
from tigrbl.system.diagnostics import mount_diagnostics


class HealthyDB:
    def execute(self, statement):
        assert str(statement) == "SELECT 1"
        return 1


def _get_db():
    return HealthyDB()


def _mount_app(prefix: str = "/system", *, get_db=None) -> TigrblApp:
    app = TigrblApp(mount_system=False)
    router = SimpleNamespace(tables={})
    app.include_router(mount_diagnostics(router, get_db=get_db), prefix=prefix)
    return app


@pytest.mark.asyncio
async def test_healthz_payload_is_stable_when_dependency_is_available() -> None:
    app = _mount_app(get_db=_get_db)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/system/healthz")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_diagnostics_mount_uses_configured_system_prefix_only() -> None:
    app = _mount_app(prefix="/internal", get_db=_get_db)

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
@pytest.mark.xfail(
    reason=(
        "feat:diagnostics-absence-warning-suppression-001 is partial; "
        "missing optional integrations still emit no-db today."
    ),
)
async def test_absent_optional_db_does_not_emit_ungoverned_warning() -> None:
    app = _mount_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/system/healthz")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_healthz_payload_does_not_leak_runtime_debug_state() -> None:
    app = _mount_app(get_db=_get_db)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/system/healthz")

    payload = response.json()
    serialized = response.text
    assert set(payload) == {"ok"}
    assert "HealthyDB" not in serialized
    assert "object at 0x" not in serialized
    assert "traceback" not in serialized.lower()
