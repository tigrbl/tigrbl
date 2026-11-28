from __future__ import annotations

import importlib

import pytest

from tigrbl_concrete._concrete import CORSMiddleware, Middleware
from tigrbl_concrete._decorators.middlewares import middleware, middlewares


def test_concrete_package_exports_only_the_governed_builtin_middleware_names() -> None:
    concrete = importlib.import_module("tigrbl_concrete._concrete")
    middleware_exports = sorted(name for name in concrete.__all__ if "Middleware" in name)

    assert middleware_exports == ["CORSMiddleware", "Middleware"]


def test_middleware_decorator_records_declared_class_and_options() -> None:
    config = middleware(CORSMiddleware, allow_origins=("https://example.com",), allow_credentials=True)

    assert config.cls is CORSMiddleware
    assert config.kwargs == {
        "allow_origins": ("https://example.com",),
        "allow_credentials": True,
    }


def test_middlewares_decorator_attaches_a_closed_tuple_to_the_target_class() -> None:
    cors_config = middleware(CORSMiddleware, allow_origin="https://example.com")

    @middlewares(cors_config)
    class AppConfig:
        pass

    assert AppConfig.MIDDLEWARES == (cors_config,)


def test_cors_middleware_resolves_allowed_and_rejected_origins() -> None:
    cors = CORSMiddleware(
        lambda scope, receive, send: None,
        allow_origins=("https://allowed.example",),
        allow_credentials=True,
    )

    allowed = dict(cors._cors_headers({"origin": "https://allowed.example"}))
    rejected = dict(cors._cors_headers({"origin": "https://blocked.example"}))

    assert allowed["access-control-allow-origin"] == "https://allowed.example"
    assert allowed["access-control-allow-credentials"] == "true"
    assert rejected["access-control-allow-origin"] == "null"


def test_generic_middleware_base_rejects_invalid_invocation_shape() -> None:
    wrapped = Middleware(lambda scope, receive, send: None)

    with pytest.raises(TypeError, match="Invalid middleware invocation"):
        wrapped("unexpected")
