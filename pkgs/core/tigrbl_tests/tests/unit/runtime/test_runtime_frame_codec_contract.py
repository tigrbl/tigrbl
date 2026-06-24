from __future__ import annotations

import json

import pytest

from tigrbl_atoms.atoms.framing import app_frame
from tigrbl_atoms.atoms.framing.codec import (
    FRAME_CODECS,
    FrameCodec,
    decode_frame,
    decode_webtransport_inner_frame,
    encode_frame,
    encode_webtransport_inner_frame,
    get_frame_codec,
    supported_frame_codecs,
)
from tigrbl_core._spec.binding_spec import (
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    WebSocketBindingSpec,
    WsBindingSpec,
    derive_session_metadata_for_framing,
    validate_app_framing_for_binding,
    validate_webtransport_inner_framing,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload


def test_atom_frame_codec_registry_static_t0() -> None:
    assert callable(encode_frame)
    assert callable(decode_frame)
    assert callable(app_frame.encode_app_frame)
    assert callable(app_frame.decode_app_frame)
    assert isinstance(get_frame_codec("json"), FrameCodec)
    assert tuple(FRAME_CODECS) == supported_frame_codecs()


def test_runtime_frame_codec_registry_lookup_t1() -> None:
    expected = {
        "json",
        "jsonrpc",
        "ndjson",
        "text",
        "bytes",
        "binary",
        "stream",
        "sse",
        "multipart/form-data",
        "websocket.text",
        "websocket.json",
        "websocket.jsonrpc",
        "websocket.ndjson",
        "websocket.bytes",
        "websocket.binary",
    }

    assert set(supported_frame_codecs()) == expected
    assert get_frame_codec("sse").supports_encode is True
    assert get_frame_codec("sse").supports_decode is False
    with pytest.raises(ValueError, match="unsupported framing kind: yaml"):
        get_frame_codec("yaml")


def test_runtime_frame_envelope_schema_static_t0() -> None:
    frame = app_frame.encode_app_frame(kind=7, flags=1, payload=b"abc")

    assert frame[:4] == bytes((app_frame.SUPPORTED_VERSION, 7, 1, 0))
    assert int.from_bytes(frame[4:8], "big") == 3
    assert app_frame.decode_app_frame(frame) == {
        "version": app_frame.SUPPORTED_VERSION,
        "kind": 7,
        "flags": 1,
        "length": 3,
        "payload": b"abc",
    }


def test_framing_support_matrix_codec_coverage_t0() -> None:
    assert validate_app_framing_for_binding(binding_kind="http.rest", framing="json") == "json"
    assert (
        validate_app_framing_for_binding(
            binding_kind="http.jsonrpc",
            framing=JsonRpcFramingSpec(),
        )
        == "jsonrpc"
    )
    assert validate_app_framing_for_binding(binding_kind="http.sse", framing="sse") == "sse"
    assert validate_app_framing_for_binding(binding_kind="ws", framing="text") == "text"


def test_jsonrpc_ndjson_distinction_static_t0() -> None:
    with pytest.raises(ValueError, match="ndjson"):
        validate_app_framing_for_binding(
            binding_kind="http.jsonrpc",
            framing="ndjson",
        )


def test_webtransport_inner_codec_legality_static_t0() -> None:
    assert validate_webtransport_inner_framing(lane="bidi_stream", inner_framing="json") == "json"
    assert validate_webtransport_inner_framing(lane="datagram", inner_framing=None) is None
    with pytest.raises(ValueError, match="session lane"):
        validate_webtransport_inner_framing(lane="session", inner_framing="json")


def test_runtime_json_codec_roundtrip_t1() -> None:
    payload = {"ok": True, "count": 2}

    assert decode_frame("json", encode_frame("json", payload)) == payload


def test_runtime_jsonrpc_codec_strict_validation_t1() -> None:
    encoded = encode_frame("jsonrpc", {"method": "items.list", "params": {}})

    assert decode_frame("jsonrpc", encoded)["jsonrpc"] == "2.0"
    assert decode_frame(
        "jsonrpc",
        encode_frame("jsonrpc", {"id": 1, "result": {"ok": True}}),
    ) == {"id": 1, "result": {"ok": True}, "jsonrpc": "2.0"}
    assert decode_frame(
        "jsonrpc",
        encode_frame(
            "jsonrpc",
            [
                {"method": "items.list", "id": 1},
                {"id": 1, "result": []},
            ],
        ),
    ) == [
        {"method": "items.list", "id": 1, "jsonrpc": "2.0"},
        {"id": 1, "result": [], "jsonrpc": "2.0"},
    ]
    with pytest.raises(ValueError, match="invalid jsonrpc"):
        decode_frame("jsonrpc", json.dumps({"method": "items.list"}).encode("utf-8"))


def test_runtime_ndjson_codec_record_boundary_t1() -> None:
    records = [{"a": 1}, {"a": 2}]

    encoded = encode_frame("ndjson", records)

    assert encoded == b'{"a":1}\n{"a":2}\n'
    assert decode_frame("ndjson", encoded) == records


def test_runtime_text_bytes_binary_codec_t1() -> None:
    assert encode_frame("text", "hello") == b"hello"
    assert decode_frame("text", b"hello") == "hello"
    for framing in ("bytes", "binary", "stream"):
        assert encode_frame(framing, b"\x00raw") == b"\x00raw"
        assert decode_frame(framing, bytearray(b"\x00raw")) == b"\x00raw"
    assert decode_frame("websocket.text", b"hello") == "hello"
    with pytest.raises(ValueError, match="invalid websocket.text"):
        decode_frame("websocket.text", b"\xff")


def test_runtime_sse_codec_event_format_t1() -> None:
    assert encode_frame(
        "sse",
        {"event": "ready", "id": "1", "data": "ok"},
    ) == b"event: ready\nid: 1\ndata: ok\n\n"
    with pytest.raises(ValueError, match="unsupported framing decode kind: sse"):
        decode_frame("sse", b"data: ok\n\n")


def test_runtime_multipart_form_data_codec_roundtrip_t1() -> None:
    encoded = encode_frame(
        "multipart/form-data",
        {
            "boundary": "tigrbl-boundary",
            "parts": [
                {"name": "title", "content": "hello"},
                {
                    "name": "upload",
                    "filename": "hello.txt",
                    "headers": {"content-type": "text/plain"},
                    "content": b"file bytes",
                },
            ],
        },
    )

    assert encoded["content_type"] == "multipart/form-data; boundary=tigrbl-boundary"
    assert b"--tigrbl-boundary\r\n" in encoded["body"]

    decoded = decode_frame("multipart/form-data", encoded)

    assert decoded["boundary"] == "tigrbl-boundary"
    assert decoded["parts"][0]["name"] == "title"
    assert decoded["parts"][0]["content"] == b"hello"
    assert decoded["parts"][1]["name"] == "upload"
    assert decoded["parts"][1]["filename"] == "hello.txt"
    assert decoded["parts"][1]["headers"]["content-type"] == "text/plain"
    assert decoded["parts"][1]["content"] == b"file bytes"


def test_runtime_multipart_form_data_codec_rejects_malformed_payload_t1() -> None:
    bad_cases = (
        lambda: encode_frame("multipart/form-data", {"boundary": "bad boundary", "parts": []}),
        lambda: encode_frame("multipart/form-data", {"boundary": "ok", "parts": []}),
        lambda: encode_frame(
            "multipart/form-data",
            {"boundary": "ok", "parts": [{"content": b"missing name"}]},
        ),
        lambda: decode_frame(
            "multipart/form-data",
            {"content_type": "multipart/form-data; boundary=ok", "body": b"not multipart"},
        ),
    )

    for case in bad_cases:
        with pytest.raises(ValueError, match="multipart/form-data"):
            case()


def test_runtime_websocket_text_codec_adapter_t1() -> None:
    assert encode_frame("websocket.text", {"text": "pong"}) == {
        "type": "websocket.send",
        "text": "pong",
    }


def test_runtime_websocket_frame_codec_adapters_t1() -> None:
    json_message = encode_frame("websocket.json", {"ok": True})
    assert json_message == {"type": "websocket.send", "text": '{"ok":true}'}
    assert decode_frame("websocket.json", json_message) == {"ok": True}

    rpc_message = encode_frame("websocket.jsonrpc", {"method": "ping", "id": 1})
    assert rpc_message == {
        "type": "websocket.send",
        "text": '{"method":"ping","id":1,"jsonrpc":"2.0"}',
    }
    assert decode_frame("websocket.jsonrpc", rpc_message)["method"] == "ping"

    ndjson_message = encode_frame("websocket.ndjson", [{"a": 1}, {"a": 2}])
    assert ndjson_message == {
        "type": "websocket.send",
        "text": '{"a":1}\n{"a":2}\n',
    }
    assert decode_frame("websocket.ndjson", ndjson_message) == [{"a": 1}, {"a": 2}]

    raw = b"\x00\xff"
    assert encode_frame("websocket.bytes", raw) == {
        "type": "websocket.send",
        "bytes": raw,
    }
    assert decode_frame(
        "websocket.binary",
        {"type": "websocket.receive", "bytes": raw},
    ) == raw


def test_webtransport_inner_codec_dispatch_t1() -> None:
    projection = validate_webtransport_event_payload(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"stream_id": "s1", "stream_direction": "bidi", "framing": "json"},
    )

    assert projection == {
        "family": "stream",
        "lane": "bidi_stream",
        "exchange": "bidirectional_stream",
        "stream_direction": "bidi",
        "direction": "bidirectional",
        "stream_initiator": "client",
    }
    encoded = encode_webtransport_inner_frame(
        lane="bidi_stream",
        framing="json",
        payload={"ok": True},
    )
    assert decode_webtransport_inner_frame(
        lane="bidi_stream",
        framing="json",
        payload=encoded,
    ) == {"ok": True}
    assert (
        encode_webtransport_inner_frame(
            lane="datagram",
            framing="bytes",
            payload=b"raw",
        )
        == b"raw"
    )


def test_binding_policy_to_codec_runtime_integration_t2() -> None:
    binding = WsBindingSpec(proto="ws", path="/rpc", framing=JsonRpcFramingSpec())

    assert binding.framing == "jsonrpc"
    assert binding.subprotocols == ("jsonrpc",)
    assert decode_frame("jsonrpc", encode_frame("jsonrpc", {"method": "ping"}))[
        "method"
    ] == "ping"


def test_framing_negative_corpus_runtime_t2() -> None:
    bad_cases = (
        lambda: decode_frame("json", b"{"),
        lambda: decode_frame("jsonrpc", b'{"jsonrpc":"2.0"}'),
        lambda: decode_frame("jsonrpc", b'{"jsonrpc":"2.0","id":1}'),
        lambda: decode_frame(
            "jsonrpc",
            b'{"jsonrpc":"2.0","id":1,"error":{"code":"bad","message":"x"}}',
        ),
        lambda: decode_frame("ndjson", b'{"ok":true}\n\n'),
        lambda: encode_frame("ndjson", {"not": "a record sequence"}),
        lambda: encode_frame("yaml", {}),
        lambda: app_frame.decode_app_frame(b"\x01"),
        lambda: app_frame.decode_app_frame(bytes((1, 1, 0x80, 0)) + (0).to_bytes(4, "big")),
    )

    for case in bad_cases:
        with pytest.raises(ValueError):
            case()


def test_websocket_jsonrpc_subprotocol_codec_t2() -> None:
    ndjson = WsBindingSpec(proto="ws", path="/events", framing=NdjsonFramingSpec())
    assert ndjson.framing == "ndjson"
    assert ndjson.subprotocols == ("ndjson",)
    assert decode_frame(
        "websocket.ndjson",
        encode_frame("websocket.ndjson", [{"event": "ready"}]),
    ) == [{"event": "ready"}]

    assert WsBindingSpec(proto="ws", path="/rpc", framing="jsonrpc").subprotocols == (
        "jsonrpc",
    )


def test_jsonrpc_framing_derives_websocket_subprotocol() -> None:
    binding = WebSocketBindingSpec(
        proto="wss",
        path="/rpc",
        framing=JsonRpcFramingSpec(),
    )

    assert binding.framing == "jsonrpc"
    assert binding.subprotocols == ("jsonrpc",)
    assert derive_session_metadata_for_framing(
        binding_kind="wss",
        framing=JsonRpcFramingSpec(),
    ) == {
        "framing_kind": "jsonrpc",
        "framing_spec": "JsonRpcFramingSpec",
        "required_subprotocol": "jsonrpc",
        "subprotocols": ("jsonrpc",),
    }


def test_jsonrpc_subprotocol_conflict_fails_closed() -> None:
    with pytest.raises(ValueError, match="conflicts with subprotocols"):
        WebSocketBindingSpec(
            proto="ws",
            path="/rpc",
            framing=JsonRpcFramingSpec(),
            subprotocols=("graphql-ws",),
        )


def test_runtime_websocket_frame_codec_adapters_t2() -> None:
    bad_cases = (
        lambda: decode_frame("websocket.text", b"\xff"),
        lambda: decode_frame("websocket.json", {"type": "websocket.receive", "text": "not-json"}),
        lambda: decode_frame("websocket.ndjson", b'{"ok":true}\n\n'),
        lambda: decode_frame("websocket.jsonrpc", b'{"jsonrpc":"2.0","id":1}'),
        lambda: encode_frame("websocket.bytes", "not-bytes"),
        lambda: decode_frame("websocket.binary", {"type": "websocket.receive", "text": "wrong-slot"}),
    )

    for case in bad_cases:
        with pytest.raises(ValueError):
            case()


def test_webtransport_stream_inner_codec_runtime_t2() -> None:
    assert (
        validate_webtransport_event_payload(
            event="webtransport.stream.send",
            channel="send",
            payload={"stream_id": "s1", "stream_direction": "server_to_client", "framing": "json"},
        )["lane"]
        == "unidi_server_stream"
    )
    encoded = encode_webtransport_inner_frame(
        lane="unidi_server_stream",
        framing="ndjson",
        payload=[{"chunk": 1}, {"chunk": 2}],
    )
    assert decode_webtransport_inner_frame(
        lane="unidi_server_stream",
        framing="ndjson",
        payload=encoded,
    ) == [{"chunk": 1}, {"chunk": 2}]


def test_webtransport_datagram_inner_codec_runtime_t2() -> None:
    with pytest.raises(ValueError, match="unsupported WebTransport inner framing"):
        validate_webtransport_event_payload(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"datagram_id": "d1", "framing": "jsonrpc"},
        )
    with pytest.raises(ValueError, match="unsupported WebTransport inner framing"):
        encode_webtransport_inner_frame(
            lane="datagram",
            framing="ndjson",
            payload=[{"bad": True}],
        )
    with pytest.raises(ValueError, match="session lane"):
        decode_webtransport_inner_frame(
            lane="session",
            framing="json",
            payload=b'{"bad":true}',
        )


def test_transport_demo_frame_codec_matrix_t2() -> None:
    frames = (
        encode_frame("json", {"transport": "http"}),
        encode_frame("jsonrpc", {"method": "rpc.call"}),
        encode_frame("ndjson", [{"transport": "stream"}]),
        encode_frame("sse", {"data": "event"}),
        encode_frame("websocket.text", "socket"),
        encode_frame("websocket.json", {"socket": "json"}),
        encode_frame("websocket.ndjson", [{"socket": "ndjson"}]),
    )

    assert frames[0] == b'{"transport":"http"}'
    assert frames[1] == b'{"method":"rpc.call","jsonrpc":"2.0"}'
    assert frames[2] == b'{"transport":"stream"}\n'
    assert frames[3] == b"data: event\n\n"
    assert frames[4] == {"type": "websocket.send", "text": "socket"}
    assert frames[5] == {"type": "websocket.send", "text": '{"socket":"json"}'}
    assert frames[6] == {
        "type": "websocket.send",
        "text": '{"socket":"ndjson"}\n',
    }


def test_codec_errors_map_to_runtime_fail_closed_t2() -> None:
    decoder = app_frame.FrameStreamDecoder(max_payload_size=1)
    oversized = app_frame.encode_app_frame(kind=1, payload=b"xx")

    with pytest.raises(ValueError, match="configured limit"):
        list(decoder.feed(oversized))
