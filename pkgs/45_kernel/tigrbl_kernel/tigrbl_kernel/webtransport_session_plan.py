from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
import struct
import json
import inspect

from tigrbl_atoms.atoms.framing import WebTransportRecordDecoder


@dataclass(slots=True)
class WebTransportSessionPlan:
    """Session-scoped carrier plan for framed control records.

    The plan owns record decoder state across ASGI receive calls. One inbound
    carrier chunk may yield zero, one, or several operation-dispatch events;
    completing any one operation does not complete the bidirectional stream.
    """

    pending: deque[dict[str, Any]] = field(default_factory=deque)
    control_decoders: dict[str, WebTransportRecordDecoder] = field(
        default_factory=dict
    )

    def has_pending(self) -> bool:
        return bool(self.pending)

    def pop_pending(self) -> dict[str, Any]:
        return self.pending.popleft()

    def project_receive(self, message: Mapping[str, Any]) -> None:
        event = dict(message)
        if (
            event.get("type") != "webtransport.stream.receive"
            or str(event.get("stream_direction") or "bidi") != "bidi"
        ):
            self.pending.append(event)
            return
        data = event.get("data")
        if data is None:
            data = event.get("bytes")
        if not isinstance(data, (bytes, bytearray, memoryview)):
            self.pending.append(event)
            return
        raw = bytes(data)
        stream_id = str(event.get("stream_id"))
        decoder = self.control_decoders.get(stream_id)
        if decoder is None and raw.lstrip().startswith((b"{", b"[")):
            # Compatibility for unframed peers while declared framed bindings
            # migrate. New peers must use uint32 big-endian record boundaries.
            self.pending.append(event)
            return
        if decoder is None and len(raw) >= 4:
            declared_size = struct.unpack_from("!I", raw, 0)[0]
            if declared_size > 3 * 1024 * 1024:
                self.pending.append(event)
                return
        if decoder is None:
            decoder = WebTransportRecordDecoder()
            self.control_decoders[stream_id] = decoder
        more = event.get("more")
        records = decoder.feed(raw, final=more is False)
        if more is False:
            self.control_decoders.pop(stream_id, None)
        for record in records:
            projected = dict(event)
            projected.pop("bytes", None)
            projected["data"] = json.dumps(
                record, separators=(",", ":")
            ).encode("utf-8")
            projected["framing"] = "jsonrpc"
            self.pending.append(projected)

    def close(self) -> None:
        self.pending.clear()
        self.control_decoders.clear()

    async def cleanup(self, *callbacks: Any) -> None:
        self.close()
        for callback in callbacks:
            if not callable(callback):
                continue
            result = callback()
            if inspect.isawaitable(result):
                await result


__all__ = ["WebTransportSessionPlan"]
