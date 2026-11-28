"""Request data must never become public API declarations or retained history."""

import httpx
import pytest
from tigrbl import TigrblApp


def test_openapi_ignores_legacy_request_observations():
    app = TigrblApp(mount_system=False)

    @app.get("/mailboxes/{mailbox_id}", operation_id="Mailbox.read")
    async def mailbox():
        return {"ok": True}

    before = app.openapi()
    app.openapi_schema = None
    app._seen_paths = {"/mailboxes/private-address"}
    assert app.openapi() == before


@pytest.mark.asyncio
@pytest.mark.parametrize("document_first", [True, False])
async def test_openapi_contains_only_declared_routes_after_parameterized_requests(document_first):
    app = TigrblApp(mount_system=False)

    @app.get("/tenants/{tenant_id}/mailboxes/{mailbox_id}", operation_id="Mailbox.read")
    async def mailbox():
        return {"ok": True}

    @app.get("/tenants/public/mailboxes/help", operation_id="Mailbox.help")
    async def help_page():
        return {"ok": True}

    app.mount_openapi(path="/schema.json")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        before = (await client.get("/schema.json")).json() if document_first else None
        for tenant in ("private-tenant-a", "private-tenant-b"):
            response = await client.get(f"/tenants/{tenant}/mailboxes/private-mailbox")
            assert response.status_code == 200, response.text
        document = (await client.get("/schema.json")).json()
        if before is not None:
            assert document == before
        assert set(document["paths"]) == {
            "/tenants/{tenant_id}/mailboxes/{mailbox_id}",
            "/tenants/public/mailboxes/help",
        }
        assert document["paths"]["/tenants/{tenant_id}/mailboxes/{mailbox_id}"]["get"]["operationId"] == "Mailbox.read"
        assert not hasattr(app, "_seen_paths")
