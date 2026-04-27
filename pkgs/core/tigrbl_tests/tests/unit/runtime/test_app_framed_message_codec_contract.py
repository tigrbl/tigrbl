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


def test_app_framed_codec_round_trips_header_flags_length_and_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    frame = encode(version=1, kind=3, flags=0, payload=b"hello")
    decoded = decode(frame)

    assert decoded["version"] == 1
    assert decoded["kind"] == 3
    assert decoded["flags"] == 0
    assert decoded["length"] == 5
    assert decoded["payload"] == b"hello"


@pytest.mark.parametrize("flags", (0x00, 0x01, 0x02, 0x03, 0x7F))
def test_app_framed_codec_round_trips_supported_flag_combinations(flags: int) -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    frame = encode(version=1, kind=4, flags=flags, payload=b"payload")

    assert decode(frame)["flags"] == flags


def test_app_framed_codec_round_trips_zero_length_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    decoded = decode(encode(version=1, kind=1, flags=0, payload=b""))

    assert decoded["length"] == 0
    assert decoded["payload"] == b""


def test_app_framed_codec_decodes_multiple_stream_frames_in_order() -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decode_many = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frames")

    raw = encode(version=1, kind=1, flags=0, payload=b"a") + encode(
        version=1, kind=2, flags=0, payload=b"bb"
    )
    frames = list(decode_many(raw))

    assert [frame["kind"] for frame in frames] == [1, 2]
    assert [frame["payload"] for frame in frames] == [b"a", b"bb"]


def test_app_framed_codec_buffers_partial_stream_frame_until_complete() -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decoder = _require("tigrbl_runtime.protocol.app_frame_codec", "FrameStreamDecoder")

    raw = encode(version=1, kind=1, flags=0, payload=b"chunk")
    stream = decoder()

    assert list(stream.feed(raw[:4])) == []
    assert list(stream.feed(raw[4:])) == [
        {"version": 1, "kind": 1, "flags": 0, "length": 5, "payload": b"chunk"}
    ]


@pytest.mark.parametrize(
    "raw",
    (
        b"\x01\x01\x00\x00\x00\x00\x00\x05a",
        b"\xff\x01\x00\x00\x00\x00\x00\x01a",
        b"\x01\x01\x80\x00\x00\x00\x00\x01a",
    ),
)
def test_app_framed_codec_rejects_truncated_unsupported_or_reserved_frames(raw: bytes) -> None:
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    with pytest.raises(ValueError, match="frame|version|reserved|truncated|length"):
        decode(raw)


def test_app_framed_codec_rejects_oversized_frames_before_payload_allocation() -> None:
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    header_only = b"\x01\x01\x00\x00\xff\xff\xff\xff"
    with pytest.raises(ValueError, match="frame|size|limit|allocation"):
        decode(header_only, max_payload_size=1024)


def test_app_framed_codec_accepts_frame_at_exact_max_payload_boundary() -> None:
    encode = _require("tigrbl_runtime.protocol.app_frame_codec", "encode_app_frame")
    decode = _require("tigrbl_runtime.protocol.app_frame_codec", "decode_app_frame")

    frame = encode(version=1, kind=1, flags=0, payload=b"x" * 1024)

    assert decode(frame, max_payload_size=1024)["length"] == 1024
