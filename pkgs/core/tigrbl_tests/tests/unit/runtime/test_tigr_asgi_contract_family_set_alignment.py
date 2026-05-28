from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_runtime_taxonomy_uses_governed_tigr_asgi_contract_family_set() -> None:
    derive = _require("tigrbl_kernel.subevent_taxonomy", "derive_runtime_subevents")

    actual = {"request", "session", "message", "stream", "datagram"}
    observed = {family for family in actual if derive(family)}

    assert observed == actual


@pytest.mark.parametrize(
    ("binding", "expected_family"),
    (
        ("http.rest", "request"),
        ("http.jsonrpc", "request"),
        ("http.stream", "stream"),
        ("http.sse", "stream"),
        ("ws", "message"),
        ("webtransport", "session"),
        ("webtransport.bidi_stream", "stream"),
        ("webtransport.unidi_client_stream", "stream"),
        ("webtransport.unidi_server_stream", "stream"),
        ("webtransport.datagram", "datagram"),
    ),
)
def test_binding_kinds_project_only_governed_runtime_families(
    binding: str,
    expected_family: str,
) -> None:
    derive = _require("tigrbl_kernel.subevent_taxonomy", "derive_binding_subevents")

    result = derive(binding)

    assert result["family"] == expected_family
    assert result["family"] in {"request", "session", "message", "stream", "datagram"}
