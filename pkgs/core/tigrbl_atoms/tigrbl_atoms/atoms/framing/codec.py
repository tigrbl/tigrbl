from __future__ import annotations

import json
from typing import Any


def _loads(raw: bytes | bytearray | str, framing: str) -> Any:
    try:
        text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
        return json.loads(text)
    except Exception as exc:
        raise ValueError(f"invalid {framing} framing decode payload") from exc


def decode_frame(framing: str, payload: bytes | bytearray | str) -> Any:
    if framing == "json":
        return _loads(payload, framing)
    if framing == "jsonrpc":
        data = _loads(payload, framing)
        if (
            not isinstance(data, dict)
            or data.get("jsonrpc") != "2.0"
            or "method" not in data
        ):
            raise ValueError("invalid jsonrpc framing payload")
        return data
    if framing == "websocket.text":
        try:
            return (
                payload.decode("utf-8")
                if isinstance(payload, (bytes, bytearray))
                else payload
            )
        except UnicodeDecodeError as exc:
            raise ValueError("invalid websocket.text framing decode payload") from exc
    raise ValueError(f"unsupported framing decode kind: {framing}")


def encode_frame(framing: str, payload: Any) -> Any:
    if framing == "json":
        return json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if framing == "jsonrpc":
        body = dict(payload)
        body.setdefault("jsonrpc", "2.0")
        return json.dumps(body, separators=(",", ":")).encode("utf-8")
    if framing == "sse":
        lines: list[str] = []
        for key in ("event", "id", "retry", "data"):
            if key in payload:
                lines.append(f"{key}: {payload[key]}")
        return ("\n".join(lines) + "\n\n").encode("utf-8")
    if framing == "websocket.text":
        text = payload["text"] if isinstance(payload, dict) else str(payload)
        return {"type": "websocket.send", "text": text}
    raise ValueError(f"unsupported framing encode kind: {framing}")


__all__ = ["decode_frame", "encode_frame"]
