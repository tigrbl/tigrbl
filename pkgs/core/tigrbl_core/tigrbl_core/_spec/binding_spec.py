from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Type, Union

from ..config.constants import (
    TIGRBL_NESTED_PATHS_ATTR,
    __JSONRPC_DEFAULT_ENDPOINT__,
)
from .serde import SerdeMixin

Exchange = Literal[
    "request_response",
    "server_stream",
    "event_stream",
    "client_stream",
    "bidirectional",
    "bidirectional_stream",
    "fire_and_forget",
]
Framing = Literal["json", "jsonrpc", "sse", "stream", "text", "bytes", "webtransport"]


@dataclass(frozen=True, slots=True)
class HttpRestBindingSpec(SerdeMixin):
    proto: Literal["http.rest", "https.rest"]
    methods: tuple[str, ...]
    path: str
    exchange: Exchange = "request_response"
    framing: Framing = "json"


@dataclass(frozen=True, slots=True)
class HttpJsonRpcBindingSpec(SerdeMixin):
    proto: Literal["http.jsonrpc", "https.jsonrpc"]
    rpc_method: str
    endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__
    exchange: Exchange = "request_response"
    framing: Framing = "jsonrpc"


@dataclass(frozen=True, slots=True)
class HttpStreamBindingSpec(SerdeMixin):
    proto: Literal["http.stream", "https.stream"]
    path: str
    methods: tuple[str, ...] = ("GET",)
    exchange: Exchange = "server_stream"
    framing: Framing = "stream"


@dataclass(frozen=True, slots=True)
class SseBindingSpec(SerdeMixin):
    proto: Literal["http.sse", "https.sse"] = "http.sse"
    path: str = "/"
    methods: tuple[str, ...] = ("GET",)
    exchange: Exchange = "server_stream"
    framing: Framing = "sse"


@dataclass(frozen=True, slots=True)
class WsBindingSpec(SerdeMixin):
    proto: Literal["ws", "wss"]
    path: str
    subprotocols: tuple[str, ...] = ()
    exchange: Exchange = "bidirectional_stream"
    framing: Framing = "text"


@dataclass(frozen=True, slots=True)
class WebTransportBindingSpec(SerdeMixin):
    proto: Literal["webtransport"] = "webtransport"
    path: str = "/"
    exchange: Exchange = "bidirectional_stream"
    framing: Framing = "webtransport"


@dataclass(frozen=True, slots=True)
class MessageBindingSpec(SerdeMixin):
    proto: str
    topic: str
    exchange: Exchange = "fire_and_forget"
    framing: Framing = "bytes"


@dataclass(frozen=True, slots=True)
class DatagramBindingSpec(SerdeMixin):
    proto: str
    endpoint: str
    exchange: Exchange = "fire_and_forget"
    framing: Framing = "bytes"


TransportBindingSpec = Union[
    HttpRestBindingSpec,
    HttpJsonRpcBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WsBindingSpec,
    WebTransportBindingSpec,
    MessageBindingSpec,
    DatagramBindingSpec,
]


@dataclass(frozen=True, slots=True)
class BindingSpec(SerdeMixin):
    """Named binding declaration used for registry composition."""

    name: str
    spec: TransportBindingSpec


@dataclass(slots=True)
class BindingRegistrySpec(SerdeMixin):
    """Simple in-memory registry for named transport bindings."""

    _bindings: dict[str, BindingSpec] = field(default_factory=dict)

    def register(self, binding: BindingSpec) -> None:
        self._bindings[binding.name] = binding

    def get(self, name: str) -> Optional[BindingSpec]:
        return self._bindings.get(name)

    def values(self) -> tuple[BindingSpec, ...]:
        return tuple(self._bindings.values())


def resolve_rest_nested_prefix(model: Type) -> Optional[str]:
    """Return the configured nested REST prefix for ``model`` if present."""

    cb = getattr(model, TIGRBL_NESTED_PATHS_ATTR, None)
    if callable(cb):
        return cb()
    return getattr(model, "_nested_path", None)


_EXCHANGE_ALIASES = {
    "bidirectional": "bidirectional_stream",
    "event_stream": "server_stream",
}
_CANONICAL_EXCHANGES = {
    "request_response",
    "server_stream",
    "client_stream",
    "bidirectional_stream",
    "fire_and_forget",
}


@dataclass(frozen=True, slots=True)
class BindingEventKey:
    family: str
    family_code: int


def normalize_exchange(exchange: str | None) -> str:
    token = str(exchange or "")
    normalized = _EXCHANGE_ALIASES.get(token, token)
    if normalized not in _CANONICAL_EXCHANGES:
        raise ValueError(f"invalid exchange token {exchange!r}; expected canonical exchange")
    return normalized


def matches_exchange_selector(*, selector: str, exchange: str | None) -> bool:
    return normalize_exchange(selector) == normalize_exchange(exchange)


def project_binding_runtime_metadata(binding: TransportBindingSpec) -> dict[str, object]:
    proto = str(getattr(binding, "proto", ""))
    exchange = normalize_exchange(getattr(binding, "exchange", None))
    framing = str(getattr(binding, "framing", ""))
    family = _binding_family(binding)
    _validate_binding_exchange(family, exchange)
    return {
        "proto": proto,
        "exchange": exchange,
        "framing": framing,
        "family": family,
        "subevents": _binding_subevents(family),
    }


def compile_binding_event_key(binding: TransportBindingSpec) -> BindingEventKey:
    family = str(project_binding_runtime_metadata(binding)["family"])
    codes = {
        "request_response": 10,
        "rpc": 11,
        "stream": 20,
        "event_stream": 21,
        "socket": 30,
        "transport": 31,
        "message": 40,
        "datagram": 41,
    }
    return BindingEventKey(family=family, family_code=codes[family])


def _binding_family(binding: TransportBindingSpec) -> str:
    if isinstance(binding, HttpJsonRpcBindingSpec):
        return "rpc"
    if isinstance(binding, HttpStreamBindingSpec):
        return "stream"
    if isinstance(binding, SseBindingSpec):
        return "event_stream"
    if isinstance(binding, WsBindingSpec):
        return "socket"
    if isinstance(binding, WebTransportBindingSpec):
        return "transport"
    if isinstance(binding, MessageBindingSpec):
        return "message"
    if isinstance(binding, DatagramBindingSpec):
        return "datagram"
    return "request_response"


def _binding_subevents(family: str) -> tuple[str, ...]:
    subevents = {
        "request_response": ("request.received", "response.sent"),
        "rpc": ("rpc.request", "rpc.response"),
        "stream": ("stream.open", "stream.message", "stream.close"),
        "event_stream": ("event_stream.open", "event_stream.event", "event_stream.close"),
        "socket": ("socket.open", "socket.message", "socket.close"),
        "transport": ("transport.open", "transport.datagram", "transport.close"),
        "message": ("message.received", "message.processed"),
        "datagram": ("datagram.received", "datagram.ack"),
    }
    return subevents[family]


def _validate_binding_exchange(family: str, exchange: str) -> None:
    allowed = {
        "request_response": {"request_response"},
        "rpc": {"request_response"},
        "stream": {"server_stream"},
        "event_stream": {"server_stream"},
        "socket": {"bidirectional_stream"},
        "transport": {"bidirectional_stream"},
        "message": {"fire_and_forget"},
        "datagram": {"fire_and_forget"},
    }
    if exchange not in allowed[family]:
        raise ValueError(
            f"invalid exchange {exchange!r} for binding family {family!r}; "
            "expected canonical family exchange"
        )


__all__ = [
    "BindingSpec",
    "BindingRegistrySpec",
    "BindingEventKey",
    "DatagramBindingSpec",
    "Exchange",
    "Framing",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "HttpStreamBindingSpec",
    "MessageBindingSpec",
    "SseBindingSpec",
    "TransportBindingSpec",
    "WebTransportBindingSpec",
    "WsBindingSpec",
    "compile_binding_event_key",
    "matches_exchange_selector",
    "normalize_exchange",
    "project_binding_runtime_metadata",
    "resolve_rest_nested_prefix",
]
