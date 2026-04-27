from __future__ import annotations

import pytest

from tigrbl_core._spec import binding_spec


def _normalize(exchange: str | None) -> str:
    normalizer = getattr(binding_spec, "normalize_exchange", None)
    if normalizer is None:
        pytest.xfail("binding exchange normalizer is not implemented")
    return normalizer(exchange)


def _project(binding: object) -> dict[str, object]:
    projector = getattr(binding_spec, "project_binding_runtime_metadata", None)
    if projector is None:
        pytest.xfail("binding runtime metadata projector is not implemented")
    return projector(binding)


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("request_response", "request_response"),
        ("server_stream", "server_stream"),
        ("client_stream", "client_stream"),
        ("bidirectional_stream", "bidirectional_stream"),
        ("bidirectional", "bidirectional_stream"),
        ("event_stream", "server_stream"),
    ),
)
def test_exchange_aliases_normalize_to_canonical_tokens(value: str, expected: str) -> None:
    assert _normalize(value) == expected


@pytest.mark.parametrize("value", ("", "streaming", "message", "datagram", "response_stream"))
def test_invalid_exchange_tokens_fail_closed(value: str) -> None:
    with pytest.raises(ValueError, match="exchange|canonical|invalid"):
        _normalize(value)


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


def test_sse_event_stream_compatibility_projects_to_server_stream() -> None:
    metadata = _project(
        binding_spec.SseBindingSpec(
            proto="http.sse",
            path="/items/events",
            exchange="event_stream",  # type: ignore[arg-type]
        )
    )

    assert metadata["exchange"] == "server_stream"
    assert metadata["framing"] == "sse"


def test_hook_selector_matching_uses_normalized_exchange_token() -> None:
    matcher = getattr(binding_spec, "matches_exchange_selector", None)
    if matcher is None:
        pytest.xfail("binding exchange selector matcher is not implemented")

    assert matcher(selector="server_stream", exchange="event_stream")
    assert matcher(selector="bidirectional_stream", exchange="bidirectional")
    assert not matcher(selector="request_response", exchange="server_stream")


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


def test_message_and_datagram_bindings_do_not_share_subevent_taxonomy() -> None:
    message_cls = getattr(binding_spec, "MessageBindingSpec", None)
    datagram_cls = getattr(binding_spec, "DatagramBindingSpec", None)
    if message_cls is None or datagram_cls is None:
        pytest.xfail("message/datagram binding families are not implemented")

    message = _project(message_cls(proto="internal.message", topic="inventory.changed"))
    datagram = _project(datagram_cls(proto="udp.datagram", endpoint="events"))

    message_subevents = set(message["subevents"])
    datagram_subevents = set(datagram["subevents"])

    assert message_subevents
    assert datagram_subevents
    assert message_subevents.isdisjoint(datagram_subevents)
    assert all(str(value).startswith("message.") for value in message_subevents)
    assert all(str(value).startswith("datagram.") for value in datagram_subevents)


def test_message_and_datagram_bindings_have_distinct_eventkey_families() -> None:
    compiler = getattr(binding_spec, "compile_binding_event_key", None)
    message_cls = getattr(binding_spec, "MessageBindingSpec", None)
    datagram_cls = getattr(binding_spec, "DatagramBindingSpec", None)
    if compiler is None or message_cls is None or datagram_cls is None:
        pytest.xfail("message/datagram EventKey family compilation is not implemented")

    message_key = compiler(message_cls(proto="internal.message", topic="inventory.changed"))
    datagram_key = compiler(datagram_cls(proto="udp.datagram", endpoint="events"))

    assert message_key.family == "message"
    assert datagram_key.family == "datagram"
    assert message_key.family_code != datagram_key.family_code


def test_message_and_datagram_exchange_overrides_fail_closed() -> None:
    message_cls = getattr(binding_spec, "MessageBindingSpec", None)
    datagram_cls = getattr(binding_spec, "DatagramBindingSpec", None)
    if message_cls is None or datagram_cls is None:
        pytest.xfail("message/datagram binding families are not implemented")

    with pytest.raises(ValueError, match="exchange|family|canonical|invalid"):
        _project(
            message_cls(
                proto="internal.message",
                topic="inventory.changed",
                exchange="server_stream",
            )
        )
    with pytest.raises(ValueError, match="exchange|family|canonical|invalid"):
        _project(
            datagram_cls(
                proto="udp.datagram",
                endpoint="events",
                exchange="request_response",
            )
        )


def test_binding_projection_rejects_noncanonical_exchange_overrides() -> None:
    with pytest.raises(ValueError, match="exchange|canonical|invalid"):
        _project(
            binding_spec.HttpRestBindingSpec(
                proto="http.rest",
                methods=("GET",),
                path="/items",
                exchange="message",  # type: ignore[arg-type]
            )
        )
