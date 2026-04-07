from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Sequence

OpChannelKind = Literal["http", "websocket", "sse", "stream", "webtransport"]
OpChannelFamily = Literal["request", "response", "stream", "socket", "session"]
OpChannelSubevent = Literal[
    "connect",
    "receive",
    "emit",
    "complete",
    "disconnect",
]


@dataclass(slots=True)
class OpChannel:
    """Runtime transport descriptor shared across Python and Rust surfaces."""

    kind: OpChannelKind
    family: OpChannelFamily
    exchange: str
    protocol: str
    path: str
    method: str | None = None
    selector: str | None = None
    framing: str | None = None
    subevents: tuple[OpChannelSubevent, ...] = ()
    headers: Mapping[str, str] = field(default_factory=dict)
    query: Mapping[str, Sequence[str]] = field(default_factory=dict)
    path_params: Mapping[str, str] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    send: Callable[[Any], Any] | None = None
    receive: Callable[[], Any] | None = None


__all__ = [
    "OpChannel",
    "OpChannelFamily",
    "OpChannelKind",
    "OpChannelSubevent",
]
