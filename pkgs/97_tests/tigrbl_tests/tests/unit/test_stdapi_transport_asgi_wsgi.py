from __future__ import annotations

import pytest
from tigrbl import Request
from tigrbl import Router
from tigrbl import TigrblApp


@pytest.mark.asyncio()
async def test_asgi_http_scope_dispatches_with_query_and_body() -> None:
    app = TigrblApp()

    @app.post("/echo")
    async def echo(request: Request) -> dict[str, object]:
        return {
            "method": request.method,
            "query": request.query,
            "body": request.body.decode("utf-8"),
        }

    messages: list[dict[str, object]] = []

    request_messages = iter(
        [
            {
                "type": "http.request",
                "body": b'{"hello":"world"}',
                "more_body": False,
            }
        ]
    )

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await app(
        {
            "type": "http",
            "method": "POST",
            "path": "/echo",
            "query_string": b"x=1&x=2",
            "headers": [(b"content-type", b"application/json")],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    assert messages[0]["status"] == 200
    assert messages[1]["type"] == "http.response.body"
    assert (
        messages[1]["body"]
        == b'{"method":"POST","query":{"x":["1","2"]},"body":"{\\"hello\\":\\"world\\"}"}'
    )


@pytest.mark.asyncio()
async def test_asgi_204_response_omits_body_and_content_length() -> None:
    app = TigrblApp()

    @app.delete("/items/{item_id}", status_code=204)
    def delete_item(item_id: str) -> None:
        assert item_id == "1"
        return None

    messages: list[dict[str, object]] = []

    request_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await app(
        {
            "type": "http",
            "method": "DELETE",
            "path": "/items/1",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    assert messages[0]["status"] == 204
    assert (b"content-length", b"0") not in messages[0]["headers"]
    assert messages[1] == {
        "type": "http.response.body",
        "body": b"",
        "more_body": False,
    }


@pytest.mark.asyncio()
async def test_asgi_head_response_strips_body_and_entity_headers() -> None:
    app = TigrblApp()

    @app.get("/items")
    def list_items() -> dict[str, str]:
        return {"ok": "yes"}

    messages: list[dict[str, object]] = []

    request_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await app(
        {
            "type": "http",
            "method": "HEAD",
            "path": "/items",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    start_headers = dict(messages[0]["headers"])
    assert b"content-length" not in start_headers
    assert b"content-type" not in start_headers
    assert b"transfer-encoding" not in start_headers
    assert messages[1] == {
        "type": "http.response.body",
        "body": b"",
        "more_body": False,
    }


def test_router_is_not_a_transport_entrypoint_and_private_adapters_are_absent() -> None:
    router = Router()

    assert not hasattr(router, "_asgi_app")
    assert not hasattr(router, "_wsgi_app")

    with pytest.raises(TypeError, match="Router is no longer a transport entrypoint"):
        router("not-a-scope")
