from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from tigrbl import HttpRestBindingSpec, Request, RestRequestJson, TigrblApp, post
from tests.conftest import _build_router
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String
from tigrbl_core._spec.binding_spec import TextFramingSpec
from tigrbl_examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


def test_strict_rest_binding_policy_round_trip():
    @post("/decorated", request_json={"shape": "object"})
    def decorated(cls, ctx):
        return ctx.get("payload")

    (declared_binding,) = decorated.__func__.__tigrbl_op_spec__.bindings
    assert declared_binding.request_json == RestRequestJson("object", 422)
    assert HttpRestBindingSpec.from_json(declared_binding.to_json()) == declared_binding
    with pytest.raises(ValueError):
        HttpRestBindingSpec(
            proto="http.rest",
            path="/incompatible",
            methods=("POST",),
            framing=TextFramingSpec(),
            request_json=RestRequestJson("object"),
        )


@pytest.mark.parametrize(
    "kwargs", [{"shape": "scalar"}, {"shape": "object", "wrong_shape_status": 415}]
)
def test_invalid_strict_rest_policy(kwargs):
    with pytest.raises(ValueError):
        RestRequestJson(**kwargs)


def binding(path, shape="object", status=422, method="POST"):
    return HttpRestBindingSpec(
        proto="http.rest",
        path=path,
        methods=(method,),
        request_json=RestRequestJson(shape, status),
    )


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/strict", "/strict/{mailbox}"])
@pytest.mark.parametrize("wrong_shape_status", [400, 422])
async def test_strict_rest_request_errors(path, wrong_shape_status):
    app = TigrblApp()
    calls = []

    @app.post(path, tigrbl_binding=binding(path, status=wrong_shape_status))
    async def strict(request: Request):
        payload = await request.json()
        calls.append(payload)
        return payload

    app.initialize()
    url = path.replace("{mailbox}", "inbox") + "?fallback=true"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://test"
    ) as client:
        for body, media_type, status, detail in [
            (b"{}", "text/plain", 415, "Expected Content-Type application/json."),
            (b"{}", None, 415, "Expected Content-Type application/json."),
            (
                b"{}",
                "application/notjson",
                415,
                "Expected Content-Type application/json.",
            ),
            (b"{", "application/json", 400, "Malformed JSON request body."),
            (b'{"value":NaN}', "application/json", 400, "Malformed JSON request body."),
            (
                b'{"value":"\xff"}',
                "application/json",
                400,
                "Malformed JSON request body.",
            ),
            *[
                (
                    body,
                    "application/json",
                    wrong_shape_status,
                    "Expected a JSON object.",
                )
                for body in (b"[]", b"1", b'"scalar"', b"null")
            ],
        ]:
            headers = {"Content-Type": media_type} if media_type else {}
            response = await client.post(url, content=body, headers=headers)
            assert response.status_code == status, response.text
            assert response.json() == {"detail": detail}
        assert calls == []

        response = await client.post(
            url,
            content=b'{"value":1}',
            headers={"Content-Type": "Application/JSON; charset=utf-8"},
        )
        assert response.status_code == 200, response.text
        assert response.json() == {"value": 1}
        assert calls == [{"value": 1}]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bodyless_and_legacy_rest_routes():
    app = TigrblApp()

    @app.get("/bodyless", tigrbl_binding=binding("/bodyless", method="GET"))
    async def bodyless():
        return {"ok": True}

    @app.post("/legacy")
    async def legacy(request: Request):
        return await request.json()

    app.initialize()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/bodyless")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        response = await client.post(
            "/legacy", content=b'{"value":1}', headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 200
        assert response.json() == {"value": 1}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_strict_bulk_rest_request(sync_db_session):
    class StrictWidget(TableBase, GUIDPk, BulkCapable):
        __tablename__ = "strict_json_widgets"
        name = Column(String, nullable=False)

    router = _build_router(
        StrictWidget,
        [
            OpSpec(
                alias="bulk_create",
                target="bulk_create",
                bindings=(binding("/strict-bulk", "array", 400),),
            )
        ],
    )
    _, get_db = sync_db_session
    app = TigrblApp(get_db=get_db)
    app.include_router(router)
    app.initialize()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/strict-bulk", json={"name": "one"})
        assert response.status_code == 400, response.text
        assert response.json() == {"detail": "Expected a JSON array."}

        response = await client.post("/strict-bulk", json=[{}])
        assert response.status_code == 422, response.text

        response = await client.post(
            "/strict-bulk", json=[{"name": "one"}, {"name": "two"}]
        )
        assert response.is_success, response.text
        assert [row["name"] for row in response.json()] == ["one", "two"]


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/wire", "/wire/{mailbox}"])
async def test_strict_rest_chunked_http_recovery(path):
    app = TigrblApp()
    calls = []

    @app.post(path, tigrbl_binding=binding(path))
    async def strict(request: Request):
        payload = await request.json()
        calls.append(payload)
        return payload

    async def chunks(*pieces):
        for piece in pieces:
            yield piece

    app.initialize()
    base_url, server, task = await start_uvicorn(app, port=pick_unique_port())
    try:
        async with AsyncClient(base_url=base_url, timeout=5) as client:
            url = path.replace("{mailbox}", "inbox") + "?fallback=true"
            for pieces, content_type, status in (
                ((b"{", b"x"), "text/plain", 415),
                ((b"{", b"x"), "application/json", 400),
                ((b"n", b"ull"), "application/json", 422),
            ):
                response = await client.post(
                    url, content=chunks(*pieces), headers={"Content-Type": content_type}
                )
                assert response.request.headers["transfer-encoding"] == "chunked"
                assert response.http_version == "HTTP/1.1"
                assert response.status_code == status, response.text
            assert calls == []
            response = await client.post(
                url,
                content=chunks(b'{"name":"caf\xc3', b'\xa9"}'),
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            assert response.status_code == 200, response.text
            assert response.json() == {"name": "café"}
            assert calls == [{"name": "café"}]
    finally:
        await stop_uvicorn(server, task)
