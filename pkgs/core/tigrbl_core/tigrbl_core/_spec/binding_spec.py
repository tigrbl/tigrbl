from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Type, Union

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
Framing = Literal[
    "json",
    "jsonrpc",
    "ndjson",
    "sse",
    "stream",
    "text",
    "binary",
    "bytes",
    "webtransport",
]
BindingProfile = Literal[
    "rest",
    "jsonrpc",
    "stream",
    "sse",
    "websocket",
    "webtransport",
    "session",
    "bidi_stream",
    "unidi_client_stream",
    "unidi_server_stream",
    "message",
    "datagram",
]
WebTransportLane = Literal[
    "session",
    "bidi_stream",
    "unidi_client_stream",
    "unidi_server_stream",
    "datagram",
]

APP_LEVEL_FRAMING_SUPPORT: dict[str, tuple[str, ...]] = {
    "http.rest": ("json",),
    "https.rest": ("json",),
    "http.jsonrpc": ("jsonrpc",),
    "https.jsonrpc": ("jsonrpc",),
    "http.stream": ("stream", "bytes", "binary", "text", "json", "ndjson"),
    "https.stream": ("stream", "bytes", "binary", "text", "json", "ndjson"),
    "http.sse": ("sse",),
    "https.sse": ("sse",),
    "ws": ("text", "bytes", "binary", "json", "jsonrpc"),
    "wss": ("text", "bytes", "binary", "json", "jsonrpc"),
    "webtransport": ("webtransport",),
}

WEBTRANSPORT_NATIVE_LANES: tuple[str, ...] = (
    "session",
    "bidi_stream",
    "unidi_client_stream",
    "unidi_server_stream",
    "datagram",
)

WEBTRANSPORT_INNER_FRAMING_SUPPORT: dict[str, tuple[str, ...]] = {
    "session": (),
    "bidi_stream": ("bytes", "binary", "text", "json", "jsonrpc", "ndjson"),
    "unidi_client_stream": ("bytes", "binary", "text", "json", "jsonrpc", "ndjson"),
    "unidi_server_stream": ("bytes", "binary", "text", "json", "jsonrpc", "ndjson"),
    "datagram": ("bytes", "binary", "text", "json"),
}

_PROFILE_DEFAULTS: dict[str, tuple[str, str]] = {
    "rest": ("request_response", "json"),
    "jsonrpc": ("request_response", "jsonrpc"),
    "stream": ("server_stream", "stream"),
    "sse": ("server_stream", "sse"),
    "websocket": ("bidirectional_stream", "text"),
    "webtransport": ("bidirectional_stream", "webtransport"),
    "session": ("bidirectional_stream", "webtransport"),
    "bidi_stream": ("bidirectional_stream", "webtransport"),
    "unidi_client_stream": ("client_stream", "webtransport"),
    "unidi_server_stream": ("server_stream", "webtransport"),
    "datagram": ("bidirectional_stream", "webtransport"),
}

_PROFILE_BINDING_KIND: dict[tuple[str, str], str] = {
    ("http", "rest"): "http.rest",
    ("https", "rest"): "https.rest",
    ("http", "jsonrpc"): "http.jsonrpc",
    ("https", "jsonrpc"): "https.jsonrpc",
    ("http", "stream"): "http.stream",
    ("https", "stream"): "https.stream",
    ("http", "sse"): "http.sse",
    ("https", "sse"): "https.sse",
    ("ws", "websocket"): "ws",
    ("wss", "websocket"): "wss",
    ("webtransport", "webtransport"): "webtransport",
    ("webtransport", "session"): "webtransport",
    ("webtransport", "bidi_stream"): "webtransport",
    ("webtransport", "unidi_client_stream"): "webtransport",
    ("webtransport", "unidi_server_stream"): "webtransport",
    ("webtransport", "datagram"): "webtransport",
}


def binding_kind_for(*, proto: str, profile: str) -> str:
    try:
        return _PROFILE_BINDING_KIND[(proto, profile)]
    except KeyError as exc:
        raise ValueError(f"unsupported binding profile {profile!r} for proto {proto!r}") from exc


def validate_app_framing_for_binding(
    *,
    binding_kind: str,
    framing: str | None,
    subprotocols: tuple[str, ...] = (),
) -> str:
    selected = str(framing or APP_LEVEL_FRAMING_SUPPORT[binding_kind][0])
    allowed = APP_LEVEL_FRAMING_SUPPORT.get(binding_kind)
    if allowed is None:
        raise ValueError(f"unsupported binding kind {binding_kind!r}")
    if selected not in allowed:
        raise ValueError(
            f"unsupported app-level framing {selected!r} for binding {binding_kind!r}"
        )
    if selected == "jsonrpc" and binding_kind in {"ws", "wss"}:
        lowered = tuple(str(item).lower() for item in subprotocols)
        if "jsonrpc" not in lowered:
            raise ValueError(
                "WebSocket jsonrpc framing requires subprotocols to include 'jsonrpc'."
            )
    if selected == "ndjson" and "jsonrpc" in binding_kind:
        raise ValueError("ndjson is not a JSON-RPC framing substitute")
    return selected


def webtransport_lane_for_profile(profile: str | None) -> str:
    selected = str(profile or "webtransport")
    if selected == "webtransport":
        return "session"
    if selected == "message":
        raise ValueError("WebTransport does not support a native message lane")
    if selected not in WEBTRANSPORT_NATIVE_LANES:
        raise ValueError(f"unsupported WebTransport lane {selected!r}")
    return selected


def webtransport_runtime_family(lane: str) -> str:
    selected = webtransport_lane_for_profile(lane)
    if selected == "session":
        return "session"
    if selected == "datagram":
        return "datagram"
    return "stream"


def validate_webtransport_inner_framing(
    *,
    lane: str,
    inner_framing: str | None,
) -> str | None:
    selected_lane = webtransport_lane_for_profile(lane)
    if inner_framing is None:
        return None
    selected = str(inner_framing)
    allowed = WEBTRANSPORT_INNER_FRAMING_SUPPORT[selected_lane]
    if not allowed:
        raise ValueError("WebTransport session lane does not carry app-level framing")
    if selected not in allowed:
        raise ValueError(
            f"unsupported WebTransport inner framing {selected!r} for lane {selected_lane!r}"
        )
    return selected


@dataclass(frozen=True, slots=True)
class HTTPBindingSpec(SerdeMixin):
    proto: Literal["http", "https"] = "http"
    profile: Literal["rest", "jsonrpc", "stream", "sse"] = "rest"
    path: str = "/"
    methods: tuple[str, ...] = ("GET",)
    rpc_method: str | None = None
    endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__
    exchange: Exchange | None = None
    framing: Framing | None = None

    def __post_init__(self) -> None:
        default_exchange, default_framing = _PROFILE_DEFAULTS[self.profile]
        exchange = str(self.exchange or default_exchange)
        framing = str(self.framing or default_framing)
        kind = binding_kind_for(proto=self.proto, profile=self.profile)
        validate_app_framing_for_binding(binding_kind=kind, framing=framing)
        if self.profile == "jsonrpc" and not self.rpc_method:
            raise ValueError("HTTPBindingSpec profile='jsonrpc' requires rpc_method")
        object.__setattr__(self, "exchange", exchange)
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class WebSocketBindingSpec(SerdeMixin):
    proto: Literal["ws", "wss"] = "ws"
    profile: Literal["websocket"] = "websocket"
    path: str = "/"
    subprotocols: tuple[str, ...] = ()
    exchange: Exchange = "bidirectional_stream"
    framing: Framing = "text"

    def __post_init__(self) -> None:
        subprotocols = tuple(str(item).lower() for item in self.subprotocols)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
            subprotocols=subprotocols,
        )
        object.__setattr__(self, "subprotocols", subprotocols)
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class HttpRestBindingSpec(SerdeMixin):
    proto: Literal["http.rest", "https.rest"]
    methods: tuple[str, ...]
    path: str
    profile: Literal["rest"] = "rest"
    exchange: Exchange = "request_response"
    framing: Framing = "json"

    def __post_init__(self) -> None:
        validate_app_framing_for_binding(binding_kind=self.proto, framing=self.framing)


@dataclass(frozen=True, slots=True)
class HttpJsonRpcBindingSpec(SerdeMixin):
    proto: Literal["http.jsonrpc", "https.jsonrpc"]
    rpc_method: str
    endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__
    profile: Literal["jsonrpc"] = "jsonrpc"
    exchange: Exchange = "request_response"
    framing: Framing = "jsonrpc"

    def __post_init__(self) -> None:
        validate_app_framing_for_binding(binding_kind=self.proto, framing=self.framing)


@dataclass(frozen=True, slots=True)
class HttpStreamBindingSpec(SerdeMixin):
    proto: Literal["http.stream", "https.stream"]
    path: str
    methods: tuple[str, ...] = ("GET",)
    profile: Literal["stream"] = "stream"
    exchange: Exchange = "server_stream"
    framing: Framing = "stream"

    def __post_init__(self) -> None:
        validate_app_framing_for_binding(binding_kind=self.proto, framing=self.framing)


@dataclass(frozen=True, slots=True)
class SseBindingSpec(SerdeMixin):
    proto: Literal["http.sse", "https.sse"] = "http.sse"
    path: str = "/"
    methods: tuple[str, ...] = ("GET",)
    profile: Literal["sse"] = "sse"
    exchange: Exchange = "server_stream"
    framing: Framing = "sse"

    def __post_init__(self) -> None:
        validate_app_framing_for_binding(binding_kind=self.proto, framing=self.framing)


@dataclass(frozen=True, slots=True)
class WsBindingSpec(SerdeMixin):
    proto: Literal["ws", "wss"]
    path: str
    subprotocols: tuple[str, ...] = ()
    profile: Literal["websocket"] = "websocket"
    exchange: Exchange = "bidirectional_stream"
    framing: Framing = "text"

    def __post_init__(self) -> None:
        subprotocols = tuple(str(item).lower() for item in self.subprotocols)
        if self.framing == "jsonrpc" and not subprotocols:
            subprotocols = ("jsonrpc",)
        validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
            subprotocols=subprotocols,
        )
        object.__setattr__(self, "subprotocols", subprotocols)


@dataclass(frozen=True, slots=True)
class WebTransportBindingSpec(SerdeMixin):
    proto: Literal["webtransport"] = "webtransport"
    path: str = "/"
    profile: Literal[
        "webtransport",
        "session",
        "bidi_stream",
        "unidi_client_stream",
        "unidi_server_stream",
        "datagram",
    ] = "webtransport"
    lane: WebTransportLane | None = None
    exchange: Exchange = "bidirectional_stream"
    framing: Framing = "webtransport"
    inner_framing: Framing | None = None

    def __post_init__(self) -> None:
        validate_app_framing_for_binding(binding_kind=self.proto, framing=self.framing)
        lane = webtransport_lane_for_profile(self.lane or self.profile)
        default_exchange, _default_framing = _PROFILE_DEFAULTS[lane]
        exchange = str(self.exchange or default_exchange)
        if self.exchange == "bidirectional_stream" and default_exchange != "bidirectional_stream":
            exchange = default_exchange
        validate_webtransport_inner_framing(
            lane=lane,
            inner_framing=self.inner_framing,
        )
        object.__setattr__(self, "lane", lane)
        object.__setattr__(self, "exchange", exchange)


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
    HTTPBindingSpec,
    WebSocketBindingSpec,
    HttpRestBindingSpec,
    HttpJsonRpcBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WsBindingSpec,
    WebTransportBindingSpec,
    MessageBindingSpec,
    DatagramBindingSpec,
]


def canonical_binding_kind(binding: TransportBindingSpec | MappingLike) -> str:
    if isinstance(binding, HTTPBindingSpec):
        return binding_kind_for(proto=binding.proto, profile=binding.profile)
    if isinstance(binding, WebSocketBindingSpec):
        return binding.proto
    if isinstance(binding, (HttpRestBindingSpec, HttpJsonRpcBindingSpec, HttpStreamBindingSpec, SseBindingSpec, WsBindingSpec, WebTransportBindingSpec)):
        return str(binding.proto)
    if isinstance(binding, dict):
        return _canonical_binding_kind_from_mapping(binding)
    return str(getattr(binding, "proto", ""))


def normalize_binding_spec(binding: TransportBindingSpec) -> HTTPBindingSpec | WebSocketBindingSpec | WebTransportBindingSpec | MessageBindingSpec | DatagramBindingSpec:
    if isinstance(binding, (HTTPBindingSpec, WebSocketBindingSpec, WebTransportBindingSpec, MessageBindingSpec, DatagramBindingSpec)):
        return binding
    if isinstance(binding, HttpRestBindingSpec):
        proto = "https" if binding.proto == "https.rest" else "http"
        return HTTPBindingSpec(proto=proto, profile="rest", path=binding.path, methods=binding.methods, exchange=binding.exchange, framing=binding.framing)
    if isinstance(binding, HttpJsonRpcBindingSpec):
        proto = "https" if binding.proto == "https.jsonrpc" else "http"
        return HTTPBindingSpec(proto=proto, profile="jsonrpc", rpc_method=binding.rpc_method, endpoint=binding.endpoint, exchange=binding.exchange, framing=binding.framing)
    if isinstance(binding, HttpStreamBindingSpec):
        proto = "https" if binding.proto == "https.stream" else "http"
        return HTTPBindingSpec(proto=proto, profile="stream", path=binding.path, methods=binding.methods, exchange=binding.exchange, framing=binding.framing)
    if isinstance(binding, SseBindingSpec):
        proto = "https" if binding.proto == "https.sse" else "http"
        return HTTPBindingSpec(proto=proto, profile="sse", path=binding.path, methods=binding.methods, exchange=binding.exchange, framing=binding.framing)
    if isinstance(binding, WsBindingSpec):
        return WebSocketBindingSpec(proto=binding.proto, path=binding.path, subprotocols=binding.subprotocols, exchange=binding.exchange, framing=binding.framing)
    raise TypeError(f"unsupported binding spec {type(binding)!r}")


MappingLike = dict[str, Any]


def _canonical_binding_kind_from_mapping(binding: MappingLike) -> str:
    kind = binding.get("kind") or binding.get("proto")
    profile = binding.get("profile")
    if kind in {"http", "https", "ws", "wss", "webtransport"} and profile:
        return binding_kind_for(proto=str(kind), profile=str(profile))
    if kind == "websocket":
        return str(binding.get("proto") or "ws")
    if kind == "http.rest":
        return "http.rest"
    if kind == "https.rest":
        return "https.rest"
    if kind == "http.jsonrpc":
        return "http.jsonrpc"
    if kind == "https.jsonrpc":
        return "https.jsonrpc"
    if kind == "http.stream":
        return "http.stream"
    if kind == "https.stream":
        return "https.stream"
    if kind == "http.sse":
        return "http.sse"
    if kind == "https.sse":
        return "https.sse"
    if kind in {"ws", "wss", "webtransport"}:
        return str(kind)
    return str(kind or "")


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
    proto = canonical_binding_kind(binding)
    exchange = normalize_exchange(getattr(binding, "exchange", None))
    framing = str(getattr(binding, "framing", ""))
    inner_framing = getattr(binding, "inner_framing", None)
    family = _binding_family(binding)
    _validate_binding_exchange(family, exchange)
    metadata: dict[str, object] = {
        "proto": proto,
        "exchange": exchange,
        "framing": framing,
        "family": family,
        "subevents": _binding_subevents(family),
    }
    if isinstance(binding, WebTransportBindingSpec):
        metadata["lane"] = binding.lane or webtransport_lane_for_profile(binding.profile)
        metadata["inner_framing"] = inner_framing
    return metadata


def compile_binding_event_key(binding: TransportBindingSpec) -> BindingEventKey:
    family = str(project_binding_runtime_metadata(binding)["family"])
    codes = {
        "request": 10,
        "request_response": 10,
        "rpc": 10,
        "stream": 20,
        "event_stream": 20,
        "session": 30,
        "transport": 30,
        "message": 40,
        "socket": 40,
        "datagram": 50,
    }
    return BindingEventKey(family=family, family_code=codes[family])


def _binding_family(binding: TransportBindingSpec) -> str:
    if isinstance(binding, HTTPBindingSpec):
        if binding.profile == "stream":
            return "stream"
        if binding.profile == "sse":
            return "stream"
        return "request"
    if isinstance(binding, WebSocketBindingSpec):
        return "message"
    if isinstance(binding, HttpRestBindingSpec):
        return "request"
    if isinstance(binding, HttpJsonRpcBindingSpec):
        return "request"
    if isinstance(binding, HttpStreamBindingSpec):
        return "stream"
    if isinstance(binding, SseBindingSpec):
        return "stream"
    if isinstance(binding, WsBindingSpec):
        return "message"
    if isinstance(binding, WebTransportBindingSpec):
        return webtransport_runtime_family(binding.lane or binding.profile)
    if isinstance(binding, MessageBindingSpec):
        return "message"
    if isinstance(binding, DatagramBindingSpec):
        return "datagram"
    return "request_response"


def _binding_subevents(family: str) -> tuple[str, ...]:
    subevents = {
        "request": ("request.received", "response.emit"),
        "request_response": ("request.received", "response.sent"),
        "rpc": ("rpc.request", "rpc.response"),
        "stream": ("stream.open", "stream.message", "stream.close"),
        "event_stream": ("event_stream.open", "event_stream.event", "event_stream.close"),
        "session": ("session.open", "session.close"),
        "socket": ("socket.open", "socket.message", "socket.close"),
        "transport": ("transport.open", "transport.datagram", "transport.close"),
        "message": ("message.received", "message.processed"),
        "datagram": ("datagram.received", "datagram.ack"),
    }
    return subevents[family]


def _validate_binding_exchange(family: str, exchange: str) -> None:
    allowed = {
        "request": {"request_response"},
        "request_response": {"request_response"},
        "rpc": {"request_response"},
        "stream": {"server_stream", "client_stream", "bidirectional_stream"},
        "event_stream": {"server_stream"},
        "socket": {"bidirectional_stream"},
        "session": {"bidirectional_stream"},
        "transport": {"bidirectional_stream"},
        "message": {"fire_and_forget", "bidirectional_stream"},
        "datagram": {"fire_and_forget", "bidirectional_stream"},
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
    "APP_LEVEL_FRAMING_SUPPORT",
    "BindingProfile",
    "DatagramBindingSpec",
    "Exchange",
    "Framing",
    "HTTPBindingSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "HttpStreamBindingSpec",
    "MessageBindingSpec",
    "SseBindingSpec",
    "TransportBindingSpec",
    "WEBTRANSPORT_INNER_FRAMING_SUPPORT",
    "WEBTRANSPORT_NATIVE_LANES",
    "WebSocketBindingSpec",
    "WebTransportBindingSpec",
    "WebTransportLane",
    "WsBindingSpec",
    "binding_kind_for",
    "canonical_binding_kind",
    "compile_binding_event_key",
    "matches_exchange_selector",
    "normalize_exchange",
    "normalize_binding_spec",
    "project_binding_runtime_metadata",
    "resolve_rest_nested_prefix",
    "validate_app_framing_for_binding",
    "validate_webtransport_inner_framing",
    "webtransport_lane_for_profile",
    "webtransport_runtime_family",
]
