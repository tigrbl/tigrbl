import hashlib
import hmac
import inspect

import httpx
import pytest

from tigrbl import (
    DefineWebhook,
    HTTPException,
    Request,
    TigrblApp,
    WebhookSpec,
    webhook_ctx,
)
from tigrbl_core._spec import AppSpec, RouterSpec


@pytest.mark.asyncio
@pytest.mark.parametrize("form", ["spec", "factory", "decorator"])
async def test_mounted_webhook_authenticates_original_body_and_acknowledges_once(
    form, tmp_path, request
):
    import sqlite3

    inbox = sqlite3.connect(tmp_path / "inbox.db")
    request.addfinalizer(inbox.close)
    inbox.execute("CREATE TABLE inbox (id TEXT PRIMARY KEY)")

    def received():
        return {row[0] for row in inbox.execute("SELECT id FROM inbox")}

    body = b'{ "id": "evt-1" }'
    signature = hmac.new(b"test", body, hashlib.sha256).hexdigest()

    def authenticate(request: Request):
        if not hmac.compare_digest(
            request.headers.get("x-signature", ""),
            hmac.new(b"test", request.body, hashlib.sha256).hexdigest(),
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
        return True

    async def receive(ctx):
        event = ctx["payload"]
        with inbox:
            inserted = inbox.execute(
                "INSERT OR IGNORE INTO inbox VALUES (?)", (event["id"],)
            )
            if event["id"] == "fail":
                # Leave the transaction by error before it can commit.
                raise HTTPException(status_code=503, detail="Could not accept event")
        return {"duplicate": inserted.rowcount == 0}

    args = dict(
        path="/hooks",
        provider="billing",
        event_type="paid",
        security_deps=(authenticate,),
    )
    if form == "spec":
        router = RouterSpec(webhooks=(WebhookSpec(handler=receive, **args),))
        app = TigrblApp.from_spec(AppSpec(routers=(router,)))
    elif form == "factory":
        router = RouterSpec(paths=(DefineWebhook(handler=receive, **args),))
        app = TigrblApp.from_spec(AppSpec(routers=(router,)))
    else:
        app = TigrblApp()
        app.include_webhook(webhook_ctx(**args)(receive))
    init = app.initialize()
    if inspect.isawaitable(init):
        await init

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://test"
    ) as client:
        invalid = await client.post(
            "/hooks", content=body, headers={"content-type": "application/json"}
        )
        assert invalid.status_code in {401, 403}, invalid.text
        assert received() == set()
        headers = {"content-type": "application/json", "x-signature": signature}
        first = await client.post("/hooks", content=body, headers=headers)
        second = await client.post("/hooks", content=body, headers=headers)
        assert (first.status_code, second.status_code) == (202, 202), (
            first.text,
            second.text,
        )
        assert first.json() == {"duplicate": False}
        assert second.json() == {"duplicate": True}
        assert received() == {"evt-1"}
        failed = b'{"id":"fail"}'
        headers["x-signature"] = hmac.new(b"test", failed, hashlib.sha256).hexdigest()
        failure = await client.post("/hooks", content=failed, headers=headers)
        assert failure.status_code == 503, failure.text
        assert received() == {"evt-1"}
