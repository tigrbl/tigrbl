from __future__ import annotations

import importlib
from typing import Any

import pytest

import tigrbl
from tigrbl import CORSMiddleware, Middleware, TigrblApp, middleware, middlewares
from tigrbl.middlewares.compose import apply_middlewares
from tigrbl_base._base._middleware_base import MiddlewareBase
from tigrbl_core._spec.middleware_spec import (
    ASGIApp,
    ASGIReceive,
    ASGISend,
    MiddlewareSpec,
    WSGIStartResponse,
)


async def _receive_once(body: bytes = b"payload") -> dict[str, Any]:
    return {"type": "http.request", "body": body, "more_body": False}


async def _http_echo_app(scope: dict[str, Any], receive: ASGIReceive, send: ASGISend) -> None:
    message = await receive()
    await send(
        {
            "type": "http.response.start",
            "status": 202,
            "headers": [(b"x-downstream", b"1")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": message.get("body", b""),
            "more_body": False,
        }
    )


async def _capture_asgi(app: ASGIApp, *, body: bytes = b"payload") -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return await _receive_once(body)

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    if callable(app):
        await app({"type": "http", "method": "POST", "path": "/items", "headers": []}, receive, send)
    else:
        await app.asgi({"type": "http", "method": "POST", "path": "/items", "headers": []}, receive, send)
    return sent


def test_middlewarespec_protocol_exports_asgi_wsgi_contract_types() -> None:
    wrapped = Middleware(_http_echo_app, marker="value")

    assert MiddlewareSpec.__name__ == "MiddlewareSpec"
    assert callable(wrapped.asgi)
    assert callable(wrapped.wsgi)
    assert wrapped.kwargs == {"marker": "value"}
    assert ASGIReceive.__name__ == "Callable"
    assert ASGISend.__name__ == "Callable"
    assert WSGIStartResponse.__name__ == "Callable"

    with pytest.raises(TypeError, match="Invalid middleware invocation"):
        wrapped("invalid")


@pytest.mark.asyncio
async def test_middleware_extension_surface_can_mutate_http_response() -> None:
    class HeaderMiddleware(MiddlewareBase):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["x-extension"] = "seen"
            response.body += b":middleware"
            return response

    sent = await _capture_asgi(HeaderMiddleware(_http_echo_app), body=b"core")
    start = next(message for message in sent if message["type"] == "http.response.start")
    body = next(message for message in sent if message["type"] == "http.response.body")

    assert start["status"] == 202
    assert (b"x-extension", b"seen") in start["headers"]
    assert body["body"] == b"core:middleware"


@pytest.mark.asyncio
async def test_middleware_protocol_composition_wraps_in_declared_order() -> None:
    events: list[str] = []

    def make_middleware(label: str):
        class TracingMiddleware(Middleware):
            async def asgi(self, scope, receive, send):
                events.append(f"{label}:before")
                await self.app(scope, receive, send)
                events.append(f"{label}:after")

            def wsgi(self, environ, start_response):
                events.append(f"{label}:wsgi-before")
                result = self.app(environ, start_response)
                events.append(f"{label}:wsgi-after")
                return result

        return TracingMiddleware

    wrapped_asgi = apply_middlewares(
        _http_echo_app,
        [(make_middleware("outer"), {}), (make_middleware("inner"), {})],
    )
    await _capture_asgi(wrapped_asgi)

    assert events == ["outer:before", "inner:before", "inner:after", "outer:after"]

    events.clear()

    def wsgi_app(_environ, start_response):
        start_response("200 OK", [])
        return [b"ok"]

    wrapped_wsgi = apply_middlewares(
        wsgi_app,
        [(make_middleware("outer"), {}), (make_middleware("inner"), {})],
    )
    assert wrapped_wsgi({}, lambda _status, _headers: None) == [b"ok"]
    assert events == [
        "outer:wsgi-before",
        "inner:wsgi-before",
        "inner:wsgi-after",
        "outer:wsgi-after",
    ]


def test_middleware_builtin_catalog_is_bounded_to_middleware_and_cors() -> None:
    concrete = importlib.import_module("tigrbl_concrete._concrete")
    middleware_exports = sorted(name for name in concrete.__all__ if "Middleware" in name)

    assert middleware_exports == ["CORSMiddleware", "Middleware"]

    cors = CORSMiddleware(
        _http_echo_app,
        allow_origins=("https://allowed.example",),
        allow_credentials=True,
        allow_methods=("GET", "POST"),
        allow_headers="*",
    )

    allowed = dict(
        cors._cors_headers(
            {
                "origin": "https://allowed.example",
                "access-control-request-headers": "authorization,content-type",
            }
        )
    )
    rejected = dict(cors._cors_headers({"origin": "https://blocked.example"}))

    assert allowed["access-control-allow-origin"] == "https://allowed.example"
    assert allowed["access-control-allow-credentials"] == "true"
    assert allowed["access-control-allow-methods"] == "GET,POST"
    assert allowed["access-control-allow-headers"] == "authorization,content-type"
    assert rejected["access-control-allow-origin"] == "null"


def test_middleware_auth_separation_keeps_auth_out_of_middleware_catalog() -> None:
    concrete = importlib.import_module("tigrbl_concrete._concrete")
    middleware_exports = [name for name in concrete.__all__ if "Middleware" in name]
    auth_middleware_exports = [name for name in middleware_exports if "Auth" in name]

    app = TigrblApp(mount_system=False)
    app.set_auth(authn=lambda: {"sub": "user"}, allow_anon=False)

    assert auth_middleware_exports == []
    assert getattr(app, "_authn") is not None
    assert not hasattr(app, "AuthMiddleware")


def test_middleware_public_projection_exposes_concrete_and_declarative_surfaces() -> None:
    config = middleware(CORSMiddleware, allow_origin="https://example.com")

    @middlewares(config)
    class AppConfig:
        pass

    assert tigrbl.Middleware is Middleware
    assert tigrbl.CORSMiddleware is CORSMiddleware
    assert tigrbl.middleware is middleware
    assert callable(middlewares)
    assert "middlewares" in tigrbl.__all__
    assert config.cls is CORSMiddleware
    assert config.kwargs == {"allow_origin": "https://example.com"}
    assert AppConfig.MIDDLEWARES == (config,)
