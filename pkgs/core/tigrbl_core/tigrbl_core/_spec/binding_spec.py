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


TransportBindingSpec = Union[
    HttpRestBindingSpec,
    HttpJsonRpcBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WsBindingSpec,
    WebTransportBindingSpec,
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


__all__ = [
    "BindingSpec",
    "BindingRegistrySpec",
    "Exchange",
    "Framing",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "HttpStreamBindingSpec",
    "SseBindingSpec",
    "TransportBindingSpec",
    "WebTransportBindingSpec",
    "WsBindingSpec",
    "resolve_rest_nested_prefix",
]
