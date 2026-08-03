from __future__ import annotations

import json
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


DEFAULT_MAX_RECORD_BYTES = 3 * 1024 * 1024
_LENGTH = struct.Struct("!I")


def encode_jsonrpc_record(payload: Mapping[str, Any]) -> bytes:
    body = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
    if len(body) > DEFAULT_MAX_RECORD_BYTES:
        raise ValueError("WebTransport control record exceeds maximum size")
    return _LENGTH.pack(len(body)) + body


def decode_jsonrpc_records(
    payload: bytes,
    *,
    max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
) -> tuple[list[dict[str, Any]], bytes]:
    records: list[dict[str, Any]] = []
    offset = 0
    while len(payload) - offset >= _LENGTH.size:
        size = _LENGTH.unpack_from(payload, offset)[0]
        if size > max_record_bytes:
            raise ValueError("WebTransport control record exceeds maximum size")
        end = offset + _LENGTH.size + size
        if end > len(payload):
            break
        value = json.loads(payload[offset + _LENGTH.size : end].decode("utf-8"))
        if not isinstance(value, dict) or value.get("jsonrpc") != "2.0":
            raise ValueError("WebTransport control record must contain JSON-RPC 2.0")
        records.append(value)
        offset = end
    return records, payload[offset:]


@dataclass(slots=True)
class WebTransportRecordDecoder:
    max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES
    remainder: bytes = b""

    def feed(self, payload: bytes, *, final: bool = False) -> list[dict[str, Any]]:
        records, self.remainder = decode_jsonrpc_records(
            self.remainder + bytes(payload),
            max_record_bytes=self.max_record_bytes,
        )
        if final and self.remainder:
            self.remainder = b""
            raise ValueError("incomplete WebTransport control record")
        return records


__all__ = [
    "DEFAULT_MAX_RECORD_BYTES",
    "WebTransportRecordDecoder",
    "decode_jsonrpc_records",
    "encode_jsonrpc_record",
]
