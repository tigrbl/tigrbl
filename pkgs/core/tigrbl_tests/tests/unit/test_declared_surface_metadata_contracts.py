from __future__ import annotations

from httpx import ASGITransport, Client

import pytest

from tigrbl_tests.tests.unit.test_declared_surface_docs import _build_app


def test_openapi_declared_surface_binding_proto_is_emitted() -> None:
    app, _ = _build_app()

    with Client(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    surface = payload["paths"]["/widget/events"]["get"]["x-tigrbl-surface"]
    assert surface["binding"]["proto"] == "http.stream"
    assert surface["binding"]["framing"] == "stream"
    assert surface["binding"]["family"] == "stream"


def test_openrpc_declared_surface_binding_proto_is_emitted() -> None:
    app, model = _build_app()

    with Client(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    methods = {method["name"]: method for method in payload["methods"]}
    surface = methods[f"{model.__name__}.socket_rpc"]["x-tigrbl-surface"]
    assert any(
        binding["proto"] == "ws"
        and binding["framing"] == "jsonrpc"
        and binding["family"] == "socket"
        for binding in surface["bindings"]
    )


def test_openapi_omits_optional_surface_metadata_when_not_declared() -> None:
    app, _ = _build_app()

    with Client(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    surface = payload["paths"]["/widget"]["post"]["x-tigrbl-surface"]
    assert "exchange" not in surface
    assert "txScope" not in surface
    assert "subevents" not in surface


def test_openapi_declared_optional_surface_metadata_is_exact() -> None:
    app, _ = _build_app()

    with Client(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    surface = payload["paths"]["/widget/events"]["get"]["x-tigrbl-surface"]
    assert surface["exchange"] == "server_stream"
    assert surface["txScope"] == "read_only"
    assert surface["subevents"] == ["chunk"]
