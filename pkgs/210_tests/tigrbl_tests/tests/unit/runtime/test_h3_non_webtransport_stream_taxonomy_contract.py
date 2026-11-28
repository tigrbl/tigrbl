from __future__ import annotations

import pytest

from tigrbl_kernel.protocol_streams import classify_plain_h3_stream


def test_plain_h3_request_push_and_control_streams_have_distinct_taxonomy() -> None:
    request = classify_plain_h3_stream(stream_type="h3_request_stream")
    push = classify_plain_h3_stream(stream_type="h3_push_stream")
    control = classify_plain_h3_stream(stream_type="qpack_encoder_stream")

    assert request["stream_initiator"] == "client"
    assert request["direction"] == "bidirectional"
    assert request["app_payload"] is True
    assert push["stream_initiator"] == "server"
    assert push["direction"] == "server_to_client"
    assert push["response_only"] is True
    assert control["family"] == "control"
    assert control["app_payload"] is False


def test_plain_h3_does_not_import_webtransport_extension_semantics() -> None:
    with pytest.raises(ValueError, match="extension context"):
        classify_plain_h3_stream(stream_type="server_bidi_stream", initiator="server")

    with pytest.raises(ValueError, match="WebTransport"):
        classify_plain_h3_stream(
            stream_type="server_bidi_stream",
            initiator="server",
            extension_context="webtransport",
        )

    extension = classify_plain_h3_stream(
        stream_type="server_bidi_stream",
        initiator="server",
        extension_context="connect",
    )

    assert extension["extension_context"] == "connect"
    assert extension["stream_initiator"] == "server"
    assert extension["exchange"] == "bidirectional_stream"
