from __future__ import annotations

import pytest

from tigrbl_concrete._concrete._app import App
from tigrbl_concrete._concrete._route import ensure_route_ops_model
from tigrbl_core._spec import BinaryFramingSpec, WebTransportBindingSpec


@pytest.mark.parametrize(
    ("profile", "expected_exchange"),
    [
        ("bidi_stream", "bidirectional_stream"),
        ("unidi_client_stream", "client_stream"),
        ("unidi_server_stream", "server_stream"),
    ],
)
def test_webtransport_route_derives_exchange_from_binding(
    profile: str,
    expected_exchange: str,
) -> None:
    app = App(openapi_url=None, docs_url=None)

    async def endpoint() -> None:
        return None

    binding = WebTransportBindingSpec(
        path="/wt",
        profile=profile,
        inner_framing=BinaryFramingSpec(),
    )
    app.add_route(
        "/wt",
        endpoint,
        methods=("POST",),
        name=f"wt_{profile}",
        tigrbl_binding=binding,
    )

    model = ensure_route_ops_model(app)
    assert model is not None
    spec = model.ops.by_alias[f"wt_{profile}"][0]
    assert spec.exchange == expected_exchange


def test_explicit_webtransport_route_exchange_takes_precedence() -> None:
    app = App(openapi_url=None, docs_url=None)

    async def endpoint() -> None:
        return None

    binding = WebTransportBindingSpec(
        path="/wt",
        profile="bidi_stream",
        inner_framing=BinaryFramingSpec(),
    )
    app.add_route(
        "/wt",
        endpoint,
        methods=("POST",),
        name="wt_explicit",
        tigrbl_binding=binding,
        tigrbl_exchange="client_stream",
    )

    model = ensure_route_ops_model(app)
    assert model is not None
    assert model.ops.by_alias["wt_explicit"][0].exchange == "client_stream"
