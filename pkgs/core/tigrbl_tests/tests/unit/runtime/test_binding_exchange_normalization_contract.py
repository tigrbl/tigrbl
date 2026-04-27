from __future__ import annotations

import pytest

from tigrbl_core._spec import binding_spec


def _project(binding: object) -> dict[str, object]:
    projector = getattr(binding_spec, "project_binding_runtime_metadata", None)
    if projector is None:
        pytest.xfail("binding runtime metadata projector is not implemented")
    return projector(binding)


def test_transport_bindings_project_canonical_exchange_family_and_subevents() -> None:
    cases = (
        (
            binding_spec.HttpRestBindingSpec(
                proto="http.rest", methods=("GET",), path="/items"
            ),
            {
                "proto": "http.rest",
                "exchange": "request_response",
                "framing": "json",
                "family": "request_response",
            },
        ),
        (
            binding_spec.HttpJsonRpcBindingSpec(
                proto="http.jsonrpc", rpc_method="items.list"
            ),
            {
                "proto": "http.jsonrpc",
                "exchange": "request_response",
                "framing": "jsonrpc",
                "family": "rpc",
            },
        ),
        (
            binding_spec.HttpStreamBindingSpec(proto="http.stream", path="/items/stream"),
            {
                "proto": "http.stream",
                "exchange": "server_stream",
                "framing": "stream",
                "family": "stream",
            },
        ),
        (
            binding_spec.SseBindingSpec(path="/items/events"),
            {
                "proto": "http.sse",
                "exchange": "server_stream",
                "framing": "sse",
                "family": "event_stream",
            },
        ),
        (
            binding_spec.WsBindingSpec(proto="ws", path="/items/socket"),
            {
                "proto": "ws",
                "exchange": "bidirectional_stream",
                "framing": "text",
                "family": "socket",
            },
        ),
        (
            binding_spec.WebTransportBindingSpec(path="/items/transport"),
            {
                "proto": "webtransport",
                "exchange": "bidirectional_stream",
                "framing": "webtransport",
                "family": "transport",
            },
        ),
    )

    for binding, expected in cases:
        metadata = _project(binding)
        for key, value in expected.items():
            assert metadata[key] == value
        assert isinstance(metadata["subevents"], tuple)
        assert metadata["subevents"]


def test_message_and_datagram_bindings_project_distinct_runtime_families() -> None:
    message_cls = getattr(binding_spec, "MessageBindingSpec", None)
    datagram_cls = getattr(binding_spec, "DatagramBindingSpec", None)
    if message_cls is None or datagram_cls is None:
        pytest.xfail("message/datagram binding families are not implemented")

    message = _project(message_cls(proto="internal.message", topic="inventory.changed"))
    datagram = _project(datagram_cls(proto="udp.datagram", endpoint="events"))

    assert message["family"] == "message"
    assert message["exchange"] in {"fire_and_forget", "message"}
    assert "message.received" in message["subevents"]

    assert datagram["family"] == "datagram"
    assert datagram["exchange"] in {"fire_and_forget", "datagram"}
    assert "datagram.received" in datagram["subevents"]
