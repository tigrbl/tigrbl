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
    ("binding", "expected"),
    (
        (
            {"kind": "http.rest", "methods": ("GET",), "path": "/items"},
            {
                "exchange": "request_response",
                "family": "response",
                "framing": "json",
                "subevents": ("request.received", "response.emit", "response.emit_complete"),
            },
        ),
        (
            {"kind": "http.jsonrpc", "rpc_method": "Item.read", "endpoint": "/rpc"},
            {
                "exchange": "request_response",
                "family": "response",
                "framing": "jsonrpc",
                "subevents": ("request.received", "response.emit", "response.emit_complete"),
            },
        ),
        (
            {"kind": "http.stream", "path": "/items/stream"},
            {
                "exchange": "server_stream",
                "family": "stream",
                "framing": "stream",
                "subevents": ("stream.open", "stream.chunk.emit", "stream.emit_complete", "stream.close"),
            },
        ),
        (
            {"kind": "http.sse", "path": "/events"},
            {
                "exchange": "server_stream",
                "family": "stream",
                "framing": "sse",
                "subevents": ("stream.open", "message.emit", "message.emit_complete", "stream.close"),
            },
        ),
        (
            {"kind": "ws", "path": "/socket", "framing": "text"},
            {
                "exchange": "bidirectional_stream",
                "family": "message",
                "framing": "text",
                "subevents": ("session.open", "message.received", "message.emit", "message.emit_complete", "session.close"),
            },
        ),
        (
            {"kind": "webtransport", "path": "/transport"},
            {
                "exchange": "bidirectional_stream",
                "family": "session",
                "framing": "webtransport",
                "subevents": ("session.open", "stream.received", "datagram.received", "session.close"),
            },
        ),
    ),
)
def test_bindingspec_projects_canonical_event_metadata(
    binding: dict[str, object],
    expected: dict[str, object],
) -> None:
    project = _require("tigrbl_kernel.binding_events", "project_binding_event_schema")

    metadata = project(binding)

    for key, value in expected.items():
        assert metadata[key] == value
    assert isinstance(metadata["channel_requirements"], tuple)
    assert metadata["loop_shape"] in {"request_response", "owner_loop", "dispatch_loop", "producer_loop"}


def test_declared_semantic_subevents_remain_distinct_from_transport_defaults() -> None:
    project = _require("tigrbl_kernel.binding_events", "project_binding_event_schema")

    metadata = project(
        {
            "kind": "ws",
            "path": "/socket",
            "declared_subevents": ("domain.order.accepted",),
        }
    )

    assert metadata["transport_subevents"]
    assert metadata["declared_subevents"] == ("domain.order.accepted",)
    assert "domain.order.accepted" not in metadata["transport_subevents"]


def test_bindingspec_event_schema_roundtrips_as_plain_data() -> None:
    project = _require("tigrbl_kernel.binding_events", "project_binding_event_schema")
    encode = _require("tigrbl_kernel.binding_events", "encode_binding_event_schema")
    decode = _require("tigrbl_kernel.binding_events", "decode_binding_event_schema")

    metadata = project({"kind": "http.sse", "path": "/events"})
    encoded = encode(metadata)

    assert isinstance(encoded, dict)
    assert decode(encoded) == metadata


@pytest.mark.parametrize(
    "binding",
    (
        {"kind": "http.rest", "path": "/items", "exchange": "bidirectional_stream"},
        {"kind": "http.sse", "path": "/events", "framing": "jsonrpc"},
        {"kind": "ws", "path": "/socket", "subevents": ("response.emit",)},
        {"kind": "webtransport", "path": "/transport", "family": "response"},
    ),
)
def test_invalid_or_contradictory_binding_event_metadata_fails_closed(
    binding: dict[str, object],
) -> None:
    project = _require("tigrbl_kernel.binding_events", "project_binding_event_schema")

    with pytest.raises(ValueError, match="binding|event|subevent|exchange|family|framing"):
        project(binding)
