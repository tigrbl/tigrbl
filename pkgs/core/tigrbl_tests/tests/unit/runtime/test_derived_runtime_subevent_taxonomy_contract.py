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


@pytest.mark.parametrize(
    ("family", "expected"),
    (
        ("request", ("request.received", "request.body.received")),
        ("response", ("response.emit", "response.emit_complete")),
        ("session", ("session.open", "session.ready", "session.close")),
        ("message", ("message.received", "message.decoded", "message.emit", "message.emit_complete")),
        ("stream", ("stream.open", "stream.chunk.received", "stream.chunk.emit", "stream.close")),
        ("datagram", ("datagram.received", "datagram.emit", "datagram.emit_complete")),
    ),
)
def test_runtime_subevent_taxonomy_uses_qualified_family_specific_names(
    family: str,
    expected: tuple[str, ...],
) -> None:
    taxonomy = _require("tigrbl_kernel.subevent_taxonomy", "derive_runtime_subevents")

    result = taxonomy(family)

    assert result == expected
    assert all(item.startswith(f"{family}.") for item in result)


@pytest.mark.parametrize(
    ("binding", "expected_family"),
    (
        ("http.rest", "response"),
        ("http.jsonrpc", "response"),
        ("http.stream", "stream"),
        ("http.sse", "stream"),
        ("ws", "message"),
        ("webtransport.datagram", "datagram"),
    ),
)
def test_binding_kind_derives_runtime_subevent_family(
    binding: str,
    expected_family: str,
) -> None:
    derive = _require("tigrbl_kernel.subevent_taxonomy", "derive_binding_subevents")

    result = derive(binding)

    assert result["family"] == expected_family
    assert result["subevents"]


def test_coarse_channel_verbs_are_compatibility_aliases_not_primary_subevents() -> None:
    resolve_alias = _require("tigrbl_kernel.subevent_taxonomy", "resolve_channel_verb_alias")

    assert resolve_alias("receive", family="message") == "message.received"
    assert resolve_alias("emit", family="response") == "response.emit"
    assert resolve_alias("complete", family="datagram") == "datagram.emit_complete"


def test_taxonomy_rejects_ambiguous_unqualified_subevents() -> None:
    normalize = _require("tigrbl_kernel.subevent_taxonomy", "normalize_subevent")

    with pytest.raises(ValueError, match="subevent|qualified|ambiguous|family"):
        normalize("received")


def test_taxonomy_preserves_stable_order_without_duplicates() -> None:
    derive = _require("tigrbl_kernel.subevent_taxonomy", "derive_runtime_subevents")

    subevents = derive("message")

    assert subevents == tuple(dict.fromkeys(subevents))
    assert subevents.index("message.received") < subevents.index("message.emit")
    assert subevents.index("message.emit") < subevents.index("message.emit_complete")
