from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from tigrbl import Column, HTTPException, Op, Request, TableBase, TigrblApp, TigrblRouter, hook_ctx
from tigrbl.factories.engine import mem


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "composition", ["direct", "mounted", "mounted_after_warmup", "router_policy"]
)
async def test_app_auth_protects_bound_writes(composition: str) -> None:
    calls = []

    def operation_authorize(request: Request):
        calls.append("operation authorize")
        if request.state.user["sub"] == "operation-denied":
            raise HTTPException(status_code=403, detail="Operation denied")

    class Widget(TableBase):
        __tablename__ = f"mounted_auth_{uuid4().hex}"
        resource_name = "widget"
        if composition == "router_policy":
            __tigrbl_ops__ = (
                Op.make(alias="create", target="create", security_deps=(operation_authorize,)),
            )
        id = Column.make(
            storage=Column.S(primary_key=True),
            field=Column.F(py_type=str, required_in=("create",)),
            io=Column.IO(in_verbs=("create",), out_verbs=("list", "create")),
        )

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def count_write(cls, ctx):
            calls.append("write")

    async def authenticate(request: Request):
        calls.append("authenticate")
        principal = request.headers.get("x-test-principal")
        if principal is None:
            raise HTTPException(status_code=401, detail="Missing test identity")
        return {"sub": principal}

    def app_authorize(request, model, alias, payload, user):
        if alias == "create":
            calls.append("app authorize")
        return user is not None and user["sub"] != "app-denied"

    def router_authorize(request, model, alias, payload, user):
        if alias == "create":
            calls.append("router authorize")
        return user is not None and user["sub"] != "router-denied"

    app = TigrblApp(engine=mem(async_=False))
    if composition != "mounted_after_warmup":
        app.set_auth(authn=authenticate, authorize=app_authorize, allow_anon=False)
    path = "/widget"
    if composition == "direct":
        app.include_table(Widget)
    else:
        router = TigrblRouter(prefix="/api")
        if composition == "router_policy":
            router.set_auth(authn=authenticate, authorize=router_authorize, allow_anon=False)
        router.include_table(Widget)
        app.include_router(router)
        path = "/api/widget"
    await app.initialize()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        if composition == "mounted_after_warmup":
            assert (await client.get(path)).status_code == 200
            app.set_auth(authn=authenticate, authorize=app_authorize, allow_anon=False)

        missing = await client.post(path, json={"id": "missing"})
        assert missing.status_code == 401, missing.text
        assert calls == ["authenticate"]

        calls.clear()
        denied = await client.post(
            path, json={"id": "denied"}, headers={"x-test-principal": "app-denied"}
        )
        assert denied.status_code == 403, denied.text
        assert calls == ["authenticate", "app authorize"]

        calls.clear()
        if composition == "router_policy":
            denied = await client.post(
                path, json={"id": "router-denied"}, headers={"x-test-principal": "router-denied"}
            )
            assert denied.status_code == 403, denied.text
            assert calls == ["authenticate", "app authorize", "router authorize"]
            calls.clear()

        expected = ["authenticate", "app authorize"]
        if composition == "router_policy":
            expected.extend(("router authorize", "operation authorize"))
            denied = await client.post(
                path,
                json={"id": "operation-denied"},
                headers={"x-test-principal": "operation-denied"},
            )
            assert denied.status_code == 403, denied.text
            assert calls == expected
            calls.clear()

        created = await client.post(
            path, json={"id": "allowed"}, headers={"x-test-principal": "allowed"}
        )
        assert created.status_code == 201, created.text
        assert calls == [*expected, "write"]
        listed = await client.get(path, headers={"x-test-principal": "allowed"})
        assert [row["id"] for row in listed.json()] == ["allowed"]

        if composition in {"mounted", "router_policy"}:
            app.mount_jsonrpc()
            for principal, expected_calls in (
                (None, ["authenticate"]),
                ("app-denied", ["authenticate", "app authorize"]),
                ("allowed", [*expected, "write"]),
            ):
                calls.clear()
                headers = {"x-test-principal": principal} if principal else {}
                response = await client.post(
                    "/rpc",
                    json={
                        "jsonrpc": "2.0",
                        "method": "Widget.create",
                        "params": {"id": "rpc"},
                        "id": 1,
                    },
                    headers=headers,
                )
                assert calls == expected_calls, response.text
                assert ("result" in response.json()) == (principal == "allowed"), response.text


@pytest.mark.asyncio
async def test_mount_policy_is_local_to_the_app_with_a_shared_model() -> None:
    class SharedWidget(TableBase):
        __tablename__ = "mounted_auth_shared_widget"
        resource_name = "shared"
        id = Column.make(
            storage=Column.S(primary_key=True),
            field=Column.F(py_type=int),
            io=Column.IO(out_verbs=("list",)),
        )

    async def require_identity(request: Request):
        if request.headers.get("x-test-principal") != "allowed":
            raise HTTPException(status_code=401, detail="Missing test identity")
        return {"sub": "allowed"}

    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=require_identity)
    protected = app
    app = TigrblApp(engine=mem(async_=False))
    public = app
    for app in (protected, public):
        router = TigrblRouter(prefix="/api")
        router.include_table(SharedWidget)
        app.include_router(router)
        await app.initialize()

    for app, expected in ((public, 200), (protected, 401), (public, 200)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/shared")
            assert response.status_code == expected, response.text
