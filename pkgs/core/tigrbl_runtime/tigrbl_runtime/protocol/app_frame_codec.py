from __future__ import annotations

from collections.abc import Iterator


HEADER_SIZE = 8
SUPPORTED_VERSION = 1
RESERVED_FLAG_MASK = 0x80
DEFAULT_MAX_PAYLOAD_SIZE = 16 * 1024 * 1024


def _as_bytes(payload: bytes | bytearray | memoryview) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, (bytearray, memoryview)):
        return bytes(payload)
    raise TypeError("payload must be bytes-like")


def encode_app_frame(
    *,
    version: int = SUPPORTED_VERSION,
    kind: int,
    flags: int = 0,
    payload: bytes | bytearray | memoryview = b"",
) -> bytes:
    if version != SUPPORTED_VERSION:
        raise ValueError(f"unsupported app frame version: {version}")
    if not 0 <= kind <= 0xFF:
        raise ValueError("app frame kind must fit in one byte")
    if not 0 <= flags <= 0x7F:
        raise ValueError("app frame flags include reserved bits")
    body = _as_bytes(payload)
    if len(body) > 0xFFFFFFFF:
        raise ValueError("app frame payload length exceeds wire limit")
    return bytes((version, kind, flags, 0)) + len(body).to_bytes(4, "big") + body


def decode_app_frame(
    frame: bytes | bytearray | memoryview,
    *,
    max_payload_size: int = DEFAULT_MAX_PAYLOAD_SIZE,
) -> dict[str, object]:
    raw = _as_bytes(frame)
    if len(raw) < HEADER_SIZE:
        raise ValueError("truncated app frame header")
    version, kind, flags, reserved = raw[:4]
    if version != SUPPORTED_VERSION:
        raise ValueError(f"unsupported app frame version: {version}")
    if flags & RESERVED_FLAG_MASK or reserved:
        raise ValueError("app frame reserved bits must be zero")
    length = int.from_bytes(raw[4:8], "big")
    if length > max_payload_size:
        raise ValueError("app frame size exceeds configured limit before allocation")
    end = HEADER_SIZE + length
    if len(raw) < end:
        raise ValueError("truncated app frame payload length")
    if len(raw) > end:
        raise ValueError("app frame contains trailing bytes")
    return {
        "version": version,
        "kind": kind,
        "flags": flags,
        "length": length,
        "payload": raw[HEADER_SIZE:end],
    }


def decode_app_frames(
    stream: bytes | bytearray | memoryview,
    *,
    max_payload_size: int = DEFAULT_MAX_PAYLOAD_SIZE,
) -> Iterator[dict[str, object]]:
    raw = _as_bytes(stream)
    offset = 0
    while offset < len(raw):
        if len(raw) - offset < HEADER_SIZE:
            raise ValueError("truncated app frame header")
        length = int.from_bytes(raw[offset + 4 : offset + 8], "big")
        end = offset + HEADER_SIZE + length
        if end > len(raw):
            raise ValueError("truncated app frame payload length")
        yield decode_app_frame(raw[offset:end], max_payload_size=max_payload_size)
        offset = end


class FrameStreamDecoder:
    def __init__(self, *, max_payload_size: int = DEFAULT_MAX_PAYLOAD_SIZE) -> None:
        self._buffer = bytearray()
        self._max_payload_size = max_payload_size

    def feed(self, chunk: bytes | bytearray | memoryview) -> Iterator[dict[str, object]]:
        self._buffer.extend(_as_bytes(chunk))
        while len(self._buffer) >= HEADER_SIZE:
            length = int.from_bytes(self._buffer[4:8], "big")
            if length > self._max_payload_size:
                raise ValueError("app frame size exceeds configured limit before allocation")
            end = HEADER_SIZE + length
            if len(self._buffer) < end:
                break
            frame = bytes(self._buffer[:end])
            del self._buffer[:end]
            yield decode_app_frame(frame, max_payload_size=self._max_payload_size)


__all__ = [
    "FrameStreamDecoder",
    "decode_app_frame",
    "decode_app_frames",
    "encode_app_frame",
]
