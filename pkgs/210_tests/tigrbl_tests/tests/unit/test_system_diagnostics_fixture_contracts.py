from __future__ import annotations

import json

from httpx import ASGITransport, AsyncClient
import pytest

from tigrbl.system.diagnostics import (
    build_healthz_endpoint,
    build_hookz_endpoint,
    build_kernelz_endpoint,
    build_methodz_endpoint,
)
from tigrbl_tests.tests.fixtures.system_diagnostics import (
    build_system_diagnostics_fixture,
)


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_endpoint_builders() -> None:
    fixture = build_system_diagnostics_fixture()

    healthz = build_healthz_endpoint(None)
    methodz = build_methodz_endpoint(fixture.app)
    hookz = build_hookz_endpoint(fixture.app)
    kernelz = build_kernelz_endpoint(fixture.app)

    async def _collect():
        return (
            await healthz(fixture.request()),
            await methodz(),
            await hookz(),
            await kernelz(),
        )

    import asyncio

    health_payload, method_payload, hook_payload, kernel_payload = asyncio.run(_collect())

    assert health_payload == fixture.expected_healthz_payload
    assert any(
        entry["model"] == "SystemDiagnosticsFixtureWidget"
        and entry["alias"] == "create"
        for entry in method_payload["methods"]
    )
    assert "SystemDiagnosticsFixtureWidget" in hook_payload
    assert "SystemDiagnosticsFixtureWidget" in kernel_payload


@pytest.mark.asyncio
async def test_system_diagnostics_fixture_verifies_mount_paths() -> None:
    fixture = build_system_diagnostics_fixture()

    async with AsyncClient(
        transport=ASGITransport(app=fixture.app),
        base_url="http://test",
    ) as client:
        mounted = await client.get(fixture.healthz_path)
        absent_default = await client.get(fixture.absent_default_path)

    assert mounted.status_code == 200
    assert mounted.json() == fixture.expected_healthz_payload
    assert absent_default.status_code == 404


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_warning_vocabulary() -> None:
    fixture = build_system_diagnostics_fixture()
    healthz = build_healthz_endpoint(None)

    async def _collect():
        return await healthz(fixture.unavailable_db_request())

    import asyncio

    response = asyncio.run(_collect())
    payload = json.loads(response.body.decode("utf-8"))

    assert response.status_code == 200
    assert payload["ok"] is False
    assert payload["warning"] in fixture.warning_vocabulary
    assert payload["warning"] == "db-unavailable"


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_no_db_warning_modes() -> None:
    fixture = build_system_diagnostics_fixture()
    healthz = build_healthz_endpoint(None)

    async def _collect():
        return (
            await healthz(fixture.request()),
            await healthz(fixture.no_db_warning_request()),
        )

    import asyncio

    ignored, warned = asyncio.run(_collect())

    assert ignored == {"ok": True}
    assert warned == {"ok": True, "warning": "db-not-configured"}
    assert warned["warning"] in fixture.warning_vocabulary


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_one_db_attached() -> None:
    fixture = build_system_diagnostics_fixture()
    healthz = build_healthz_endpoint(None)

    async def _collect():
        return await healthz(fixture.available_db_request())

    import asyncio

    assert asyncio.run(_collect()) == {"ok": True}


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_multi_db_summary() -> None:
    fixture = build_system_diagnostics_fixture()
    healthz = build_healthz_endpoint(None)

    async def _collect():
        return await healthz(fixture.multi_db_request())

    import asyncio

    payload = asyncio.run(_collect())

    assert payload["ok"] is False
    assert payload["warning"] == "db-unavailable"
    assert payload["dbs"] == {"ok": 2, "total": 3, "failed": 1}
    assert "databases" not in payload


@pytest.mark.unit
def test_system_diagnostics_fixture_verifies_multi_db_full_details() -> None:
    fixture = build_system_diagnostics_fixture()
    healthz = build_healthz_endpoint(None)

    async def _collect():
        return await healthz(fixture.multi_db_request(detail="all"))

    import asyncio

    payload = asyncio.run(_collect())

    assert payload["dbs"] == {"ok": 2, "total": 3, "failed": 1}
    assert payload["databases"] == [
        {"name": "primary", "ok": True},
        {"name": "analytics", "ok": True},
        {
            "name": "archive",
            "ok": False,
            "warning": "db-unavailable",
            "error": "fixture database unavailable",
        },
    ]
