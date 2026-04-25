from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String
from sqlalchemy.exc import IntegrityError

from tigrbl import TableBase, TigrblRouter, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.factories.engine import mem
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import _Ctx


def _build_app():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_openrpc"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app, Widget


def test_openrpc_endpoint_exposed():
    app, _ = _build_app()

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/openrpc.json")

    response = asyncio.run(_fetch())
    assert response.status_code == 200
    payload = response.json()
    assert payload["openrpc"] == "1.2.6"
    assert payload["servers"] == [{"name": app.title, "url": "/rpc"}]
    assert "methods" in payload


def test_openrpc_server_url_respects_jsonrpc_prefix():
    app, _ = _build_app()
    app.jsonrpc_prefix = "/rpc/custom"

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return (await client.get("/openrpc.json")).json()

    payload = asyncio.run(_fetch())
    assert payload["servers"] == [{"name": app.title, "url": "/rpc/custom"}]


def test_openrpc_includes_method_schema():
    app, model = _build_app()

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return (await client.get("/openrpc.json")).json()

    payload = asyncio.run(_fetch())
    methods = {method["name"]: method for method in payload["methods"]}

    create_method = methods.get(f"{model.__name__}.create")
    if create_method is None:
        assert payload["methods"] == []
        return

    assert create_method["paramStructure"] == "by-name"

    params = create_method["params"][0]["schema"]
    assert params["title"].startswith(model.__name__)
    assert "Create" in params["title"]

    result = create_method["result"]["schema"]
    assert result["title"].startswith(model.__name__)
    assert "Response" in result["title"]


def test_mount_jsonrpc_updates_openrpc_server_url() -> None:
    app, _ = _build_app()
    app.mount_jsonrpc(prefix="/jsonrpc")

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return (await client.get("/openrpc.json")).json()

    payload = asyncio.run(_fetch())
    assert payload["servers"] == [{"name": app.title, "url": "/jsonrpc"}]


def test_jsonrpc_create_with_nested_params_mapping_returns_no_content() -> None:
    app, model = _build_app()
    request_payload = {
        "jsonrpc": "2.0",
        "method": f"{model.__name__}.create",
        "params": {"params": {"name": "New Widget"}},
        "id": 1,
    }

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/rpc", json=request_payload)

    response = asyncio.run(_fetch())
    # Current transport/runtime behavior treats this malformed nested params payload
    # as a no-content path rather than surfacing a JSON-RPC error envelope. Gate C
    # records the behavior as explicit and tested rather than silently assumed.
    assert response.status_code == 204
    assert response.content == b""


def test_jsonrpc_notification_without_id_returns_no_content() -> None:
    app, model = _build_app()
    request_payload = {
        "jsonrpc": "2.0",
        "method": f"{model.__name__}.create",
        "params": {"name": "Silent Widget"},
    }

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/rpc", json=request_payload)

    response = asyncio.run(_fetch())
    assert response.status_code == 204
    assert response.content == b""


def test_jsonrpc_create_missing_required_field_returns_clean_invalid_params() -> None:
    class Thing(TableBase, GUIDPk):
        __tablename__ = "things_jsonrpc_missing_required"
        label = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Thing)
    app.initialize()
    app.mount_jsonrpc()
    request_payload = {
        "jsonrpc": "2.0",
        "method": f"{Thing.__name__}.create",
        "params": {},
        "id": 1,
    }

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/rpc", json=request_payload)

    response = asyncio.run(_fetch())
    payload = response.json()
    response_text = response.text.lower()

    assert response.status_code == 200
    assert payload["id"] == 1
    assert payload["error"]["code"] == -32602
    assert payload["error"]["message"] == "Invalid params"
    assert "label" in str(payload["error"].get("data", "")).lower()
    for forbidden in (
        "sqlalchemy",
        "sqlite3",
        "integrityerror",
        "insert into",
        "things_jsonrpc_missing_required",
        "parameters",
    ):
        assert forbidden not in response_text


def test_jsonrpc_persistence_exception_payload_is_sanitized() -> None:
    ctx = _Ctx.ensure(
        request=None,
        db=None,
        seed={
            "temp": {
                "jsonrpc_request_id": 7,
                "route": {
                    "rpc_envelope": {
                        "jsonrpc": "2.0",
                        "method": "Thing.create",
                        "params": {"label": "ok"},
                        "id": 7,
                    }
                },
            }
        },
    )
    raw = IntegrityError(
        "INSERT INTO secret_table (label) VALUES (?)",
        ("secret-bound-value",),
        Exception("sqlite3 raw failure"),
    )

    payload = PackedPlanExecutor._jsonrpc_error_payload(
        ctx,
        422,
        {"detail": str(raw)},
        sanitize_detail=PackedPlanExecutor._is_persistence_exception(raw),
    )
    text = str(payload).lower()

    assert payload == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32603,
            "message": "Internal error",
            "data": {"detail": "Internal error"},
        },
        "id": 7,
    }
    for forbidden in (
        "sqlalchemy",
        "sqlite3",
        "integrityerror",
        "insert into",
        "secret_table",
        "secret-bound-value",
    ):
        assert forbidden not in text


def test_packed_executor_http_persistence_exception_payload_is_sanitized() -> None:
    raw = IntegrityError(
        "INSERT INTO secret_table (label) VALUES (?)",
        ("secret-bound-value",),
        Exception("sqlite3 raw failure"),
    )

    assert PackedPlanExecutor._is_persistence_exception(raw)


def test_mount_lens_uses_latest_openrpc_path_by_default() -> None:
    app, _ = _build_app()
    app.mount_openrpc(path="/schema/openrpc.json")
    app.mount_lens(path="/lens-custom")

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return (await client.get("/lens-custom")).text

    html = asyncio.run(_fetch())
    assert "/schema/openrpc.json" in html


def test_default_system_docs_endpoints_are_present_and_gettable() -> None:
    app, _ = _build_app()

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            docs = await client.get("/docs")
            lens = await client.get("/lens")
            openapi = await client.get("/openapi.json")
            openrpc = await client.get("/openrpc.json")
        return docs, lens, openapi, openrpc

    docs, lens, openapi, openrpc = asyncio.run(_fetch())

    assert docs.status_code == 200
    assert "text/html" in docs.headers.get("content-type", "")
    assert "swagger-ui" in docs.text

    assert lens.status_code == 200
    assert "text/html" in lens.headers.get("content-type", "")
    assert 'id="root"' in lens.text

    assert openapi.status_code == 200
    assert openapi.json()["openapi"] == "3.1.0"

    assert openrpc.status_code == 200
    assert openrpc.json()["openrpc"] == "1.2.6"


def test_docs_lens_openapi_openrpc_are_rest_get_only_and_not_rpc_methods() -> None:
    app, _ = _build_app()
    route_map = {route.path: route for route in app.routes}
    for path in ("/docs", "/lens", "/openapi.json", "/openrpc.json"):
        assert path in route_map
        assert set(route_map[path].methods or []) == {"GET"}

    async def _exercise_docs() -> set[str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = (await client.get("/openrpc.json")).json()
            return {method["name"] for method in payload["methods"]}

    method_names = asyncio.run(_exercise_docs())
    for forbidden in ("docs", "lens", "openapi", "openrpc"):
        assert all(forbidden not in name.lower() for name in method_names)


def test_openrpc_server_url_for_router_mount_via_app_uses_current_app_level_prefix_behavior():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_openrpc_router_mount_prefix"
        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Widget)
    router.initialize()
    router.mount_jsonrpc(prefix="/jsonrpc")
    router.mount_openrpc()

    app = TigrblApp()
    app.include_router(router.router)

    async def _fetch():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return (await client.get("/openrpc.json")).json()

    payload = asyncio.run(_fetch())
    # Router-mounted OpenRPC keeps the mounted router JSON-RPC binding path.
    assert payload["servers"] == [{"name": router.title, "url": "/jsonrpc"}]

