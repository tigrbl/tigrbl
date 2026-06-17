from __future__ import annotations

import pytest

from tigrbl_kernel.protocol_streams import validate_protocol_stream_shape


def test_h11_request_and_response_body_streams_are_directional_not_bidi() -> None:
    upload = validate_protocol_stream_shape(
        protocol="h11",
        carrier_kind="http_body",
        exchange="client_stream",
    )
    download = validate_protocol_stream_shape(
        protocol="h11",
        carrier_kind="http_body",
        exchange="server_stream",
    )

    assert upload["stream_initiator"] == "client"
    assert upload["direction"] == "client_to_server"
    assert upload["carrier_kind"] == "http_request_body"
    assert download["stream_initiator"] == "server"
    assert download["direction"] == "server_to_client"
    with pytest.raises(ValueError, match="h11"):
        validate_protocol_stream_shape(
            protocol="h11",
            carrier_kind="http_body",
            exchange="bidirectional_stream",
        )


def test_h2_request_streams_are_client_initiated_and_push_is_response_only() -> None:
    request = validate_protocol_stream_shape(
        protocol="h2",
        carrier_kind="h2_request_stream",
        exchange="client_stream",
    )
    push = validate_protocol_stream_shape(
        protocol="h2",
        carrier_kind="h2_push_stream",
        exchange="server_stream",
    )

    assert request["stream_initiator"] == "client"
    assert request["direction"] == "client_to_server"
    assert push["stream_initiator"] == "server"
    assert push["response_only"] is True
    with pytest.raises(ValueError, match="extension context"):
        validate_protocol_stream_shape(
            protocol="h2",
            carrier_kind="h2_request_stream",
            exchange="bidirectional_stream",
        )
    with pytest.raises(ValueError, match="response-only"):
        validate_protocol_stream_shape(
            protocol="h2",
            carrier_kind="h2_push_stream",
            exchange="bidirectional_stream",
        )


def test_plain_h3_server_initiated_bidi_fails_without_non_wt_extension() -> None:
    request = validate_protocol_stream_shape(
        protocol="h3",
        carrier_kind="h3_request_stream",
        exchange="request_response",
    )

    assert request["stream_initiator"] == "client"
    assert request["direction"] == "bidirectional"
    with pytest.raises(ValueError, match="server-initiated bidirectional"):
        validate_protocol_stream_shape(
            protocol="h3",
            carrier_kind="server_bidi_stream",
            exchange="bidirectional_stream",
            stream_initiator="server",
        )
    with pytest.raises(ValueError, match="WebTransport"):
        validate_protocol_stream_shape(
            protocol="h3",
            carrier_kind="server_bidi_stream",
            exchange="bidirectional_stream",
            stream_initiator="server",
            extension_context="webtransport",
        )


def test_webtransport_bidi_streams_require_and_preserve_initiator() -> None:
    client_bidi = validate_protocol_stream_shape(
        protocol="webtransport",
        carrier_kind="bidi_stream",
        exchange="bidirectional_stream",
        stream_initiator="client",
    )
    server_bidi = validate_protocol_stream_shape(
        protocol="webtransport",
        carrier_kind="bidi_stream",
        exchange="bidirectional_stream",
        stream_initiator="server",
    )

    assert client_bidi["stream_initiator"] == "client"
    assert server_bidi["stream_initiator"] == "server"
    assert client_bidi["direction"] == server_bidi["direction"] == "bidirectional"
    with pytest.raises(ValueError, match="stream_initiator"):
        validate_protocol_stream_shape(
            protocol="webtransport",
            carrier_kind="bidi_stream",
            exchange="bidirectional_stream",
        )
