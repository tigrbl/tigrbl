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
    "multipart/form-data",
]


@dataclass(frozen=True, slots=True)
class FramingSpec(SerdeMixin):
    kind: Framing
    required_subprotocol: str | None = None


@dataclass(frozen=True, slots=True)
class JsonFramingSpec(FramingSpec):
    kind: Literal["json"] = "json"


@dataclass(frozen=True, slots=True)
class JsonRpcFramingSpec(FramingSpec):
    kind: Literal["jsonrpc"] = "jsonrpc"
    required_subprotocol: str | None = "jsonrpc"


@dataclass(frozen=True, slots=True)
class NdjsonFramingSpec(FramingSpec):
    kind: Literal["ndjson"] = "ndjson"
    required_subprotocol: str | None = "ndjson"


@dataclass(frozen=True, slots=True)
class SseFramingSpec(FramingSpec):
    kind: Literal["sse"] = "sse"


@dataclass(frozen=True, slots=True)
class StreamFramingSpec(FramingSpec):
    kind: Literal["stream"] = "stream"


@dataclass(frozen=True, slots=True)
class TextFramingSpec(FramingSpec):
    kind: Literal["text"] = "text"


@dataclass(frozen=True, slots=True)
class BytesFramingSpec(FramingSpec):
    kind: Literal["bytes"] = "bytes"


@dataclass(frozen=True, slots=True)
class BinaryFramingSpec(FramingSpec):
    kind: Literal["binary"] = "binary"


@dataclass(frozen=True, slots=True)
class WebTransportFramingSpec(FramingSpec):
    kind: Literal["webtransport"] = "webtransport"


@dataclass(frozen=True, slots=True)
class MultipartFormDataFramingSpec(FramingSpec):
    kind: Literal["multipart/form-data"] = "multipart/form-data"


FRAMING_SPEC_BY_KIND: dict[str, type[FramingSpec]] = {
    "json": JsonFramingSpec,
    "jsonrpc": JsonRpcFramingSpec,
    "ndjson": NdjsonFramingSpec,
    "sse": SseFramingSpec,
    "stream": StreamFramingSpec,
    "text": TextFramingSpec,
    "bytes": BytesFramingSpec,
    "binary": BinaryFramingSpec,
    "webtransport": WebTransportFramingSpec,
    "multipart/form-data": MultipartFormDataFramingSpec,
}


def normalize_framing_spec(
    framing: Framing | FramingSpec | str | None,
    *,
    default: Framing | str | None = None,
) -> FramingSpec:
    if isinstance(framing, FramingSpec):
        return framing
    selected = str(framing or default or "")
    cls = FRAMING_SPEC_BY_KIND.get(selected)
    if cls is None:
        raise ValueError(f"unsupported framing kind {selected!r}")
    return cls()


def framing_spec_name(framing: Framing | FramingSpec | str | None) -> str:
    if isinstance(framing, FramingSpec):
        return framing.__class__.__name__
    return FRAMING_SPEC_BY_KIND.get(str(framing or ""), FramingSpec).__name__
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
WebTransportStreamKind = Literal[
    "bidi_stream",
    "unidi_client_stream",
    "unidi_server_stream",
]

APP_LEVEL_FRAMING_SUPPORT: dict[str, tuple[str, ...]] = {
    "http.rest": ("json", "multipart/form-data"),
    "https.rest": ("json", "multipart/form-data"),
    "http.jsonrpc": ("jsonrpc",),
    "https.jsonrpc": ("jsonrpc",),
    "http.stream": (
        "stream",
        "bytes",
        "binary",
        "text",
        "json",
        "ndjson",
        "jsonrpc",
    ),
    "https.stream": (
        "stream",
        "bytes",
        "binary",
        "text",
        "json",
        "ndjson",
        "jsonrpc",
    ),
    "http.sse": ("sse",),
    "https.sse": ("sse",),
    "ws": ("text", "bytes", "binary", "json", "jsonrpc", "ndjson"),
    "wss": ("text", "bytes", "binary", "json", "jsonrpc", "ndjson"),
    "webtransport": ("webtransport",),
}

BINDING_PROFILE_EXCHANGE_SUPPORT: dict[str, tuple[str, ...]] = {
    "http.rest": ("request_response",),
    "https.rest": ("request_response",),
    "http.jsonrpc": ("request_response",),
    "https.jsonrpc": ("request_response",),
    "http.stream": ("server_stream", "client_stream"),
    "https.stream": ("server_stream", "client_stream"),
    "http.sse": ("server_stream",),
    "https.sse": ("server_stream",),
    "ws": ("bidirectional_stream",),
    "wss": ("bidirectional_stream",),
    "webtransport": ("bidirectional_stream", "client_stream", "server_stream"),
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
    "datagram": ("bytes", "binary", "text", "json", "jsonrpc"),
}

WEBTRANSPORT_LANE_EXCHANGES: dict[str, str] = {
    "session": "bidirectional_stream",
    "bidi_stream": "bidirectional_stream",
    "unidi_client_stream": "client_stream",
    "unidi_server_stream": "server_stream",
    "datagram": "bidirectional_stream",
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
    framing: Framing | FramingSpec | str | None,
    subprotocols: tuple[str, ...] = (),
) -> str:
    allowed = APP_LEVEL_FRAMING_SUPPORT.get(binding_kind)
    if allowed is None:
        raise ValueError(f"unsupported binding kind {binding_kind!r}")
    selected = normalize_framing_spec(framing, default=allowed[0]).kind
    if selected not in allowed:
        raise ValueError(
            f"unsupported app-level framing {selected!r} for binding {binding_kind!r}"
        )
    if selected in {"jsonrpc", "ndjson"} and binding_kind in {"ws", "wss"}:
        lowered = tuple(str(item).lower() for item in subprotocols)
        if lowered and selected not in lowered:
            raise ValueError(
                f"WebSocket {selected} framing conflicts with subprotocols; "
                f"expected '{selected}'."
            )
    if selected == "ndjson" and "jsonrpc" in binding_kind:
        raise ValueError("ndjson is not a JSON-RPC framing substitute")
    return selected


def derive_session_metadata_for_framing(
    *,
    binding_kind: str,
    framing: Framing | FramingSpec | str | None,
    subprotocols: tuple[str, ...] = (),
) -> dict[str, object]:
    spec = normalize_framing_spec(framing)
    lowered = tuple(str(item).lower() for item in subprotocols)
    metadata: dict[str, object] = {
        "framing_kind": spec.kind,
        "framing_spec": spec.__class__.__name__,
    }
    if binding_kind in {"ws", "wss"} and spec.required_subprotocol:
        if lowered and spec.required_subprotocol not in lowered:
            raise ValueError(
                f"WebSocket {spec.kind} framing conflicts with subprotocols; "
                f"expected '{spec.required_subprotocol}'."
            )
        metadata["required_subprotocol"] = spec.required_subprotocol
        metadata["subprotocols"] = lowered or (spec.required_subprotocol,)
    return metadata


def derive_websocket_subprotocols(
    *,
    framing: Framing | FramingSpec | str | None,
    subprotocols: tuple[str, ...] = (),
) -> tuple[str, ...]:
    metadata = derive_session_metadata_for_framing(
        binding_kind="ws",
        framing=framing,
        subprotocols=subprotocols,
    )
    fallback = tuple(str(item).lower() for item in subprotocols)
    return tuple(metadata.get("subprotocols", fallback))  # type: ignore[arg-type]


def derive_websocket_subprotocol_for_framing(
    framing: Framing | FramingSpec | str | None,
) -> str | None:
    selected = normalize_framing_spec(framing).kind
    if selected in {"jsonrpc", "ndjson"}:
        return selected
    return None


def validate_binding_profile_exchange(
    *,
    binding_kind: str,
    exchange: str | None,
) -> str:
    allowed = BINDING_PROFILE_EXCHANGE_SUPPORT.get(binding_kind)
    if allowed is None:
        raise ValueError(f"unsupported binding kind {binding_kind!r}")
    selected = normalize_exchange(exchange or allowed[0])
    if selected not in allowed:
        raise ValueError(
            f"unsupported exchange {selected!r} for binding {binding_kind!r}"
        )
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
    inner_framing: Framing | FramingSpec | str | None,
) -> str | None:
    selected_lane = webtransport_lane_for_profile(lane)
    if inner_framing is None:
        return None
    selected = normalize_framing_spec(inner_framing).kind
    allowed = WEBTRANSPORT_INNER_FRAMING_SUPPORT[selected_lane]
    if not allowed:
        raise ValueError("WebTransport session lane does not carry app-level framing")
    if selected not in allowed:
        raise ValueError(
            f"unsupported WebTransport inner framing {selected!r} for lane {selected_lane!r}"
        )
    return selected


def validate_webtransport_lane_exchange(*, lane: str, exchange: str | None) -> str:
    selected_lane = webtransport_lane_for_profile(lane)
    selected_exchange = normalize_exchange(exchange)
    expected = WEBTRANSPORT_LANE_EXCHANGES[selected_lane]
    if selected_exchange != expected:
        raise ValueError(
            f"invalid WebTransport exchange {selected_exchange!r} for lane "
            f"{selected_lane!r}; expected {expected!r}"
        )
    return selected_exchange


def _coerce_webtransport_stream_spec(
    value: "WebTransportStreamSpec | dict[str, Any]",
    *,
    default_name: str = "",
) -> "WebTransportStreamSpec":
    if isinstance(value, WebTransportStreamSpec):
        return value
    return WebTransportStreamSpec(
        name=str(value.get("name") or default_name),
        kind=value.get("kind", "bidi_stream"),  # type: ignore[arg-type]
        opens=value.get("opens"),  # type: ignore[arg-type]
        purpose=value.get("purpose"),  # type: ignore[arg-type]
        framing=value.get("framing"),
    )


def _coerce_webtransport_datagram_spec(
    value: "WebTransportDatagramSpec | dict[str, Any]",
) -> "WebTransportDatagramSpec":
    if isinstance(value, WebTransportDatagramSpec):
        return value
    return WebTransportDatagramSpec(
        name=str(value.get("name") or ""),
        purpose=value.get("purpose"),  # type: ignore[arg-type]
        framing=value.get("framing"),
    )


@dataclass(frozen=True, slots=True)
class HttpRestProtocolBindingSpec(SerdeMixin):
    path: str
    methods: tuple[str, ...] = ("GET",)
    framing: Framing | FramingSpec = "json"
    proto: Literal["http.rest", "https.rest"] = "http.rest"
    profile: Literal["rest"] = "rest"
    exchange: Exchange = "request_response"

    def __post_init__(self) -> None:
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "methods", tuple(str(method).upper() for method in self.methods))
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class HttpJsonRpcProtocolBindingSpec(SerdeMixin):
    method: str
    path: str = __JSONRPC_DEFAULT_ENDPOINT__
    framing: Framing | FramingSpec = "jsonrpc"
    proto: Literal["http.jsonrpc", "https.jsonrpc"] = "http.jsonrpc"
    profile: Literal["jsonrpc"] = "jsonrpc"
    exchange: Exchange = "request_response"

    def __post_init__(self) -> None:
        if not self.method:
            raise ValueError("HttpJsonRpcProtocolBindingSpec requires method")
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "method", str(self.method))
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class WebSocketProtocolBindingSpec(SerdeMixin):
    path: str
    framing: Framing | FramingSpec = "text"
    proto: Literal["ws", "wss"] = "ws"
    profile: Literal["websocket"] = "websocket"
    exchange: Exchange = "bidirectional_stream"

    def __post_init__(self) -> None:
        exchange = validate_binding_profile_exchange(
            binding_kind=self.proto,
            exchange=self.exchange,
        )
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "exchange", exchange)
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class WebTransportStreamSpec(SerdeMixin):
    name: str
    kind: WebTransportStreamKind
    framing: Framing | FramingSpec
    opens: Literal["first", "peer"] | None = None
    purpose: str | None = None

    def __post_init__(self) -> None:
        kind = str(self.kind)
        if kind not in {"bidi_stream", "unidi_client_stream", "unidi_server_stream"}:
            raise ValueError(f"unsupported WebTransport stream kind {kind!r}")
        framing = validate_webtransport_inner_framing(lane=kind, inner_framing=self.framing)
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "framing", framing)
        if self.purpose is not None:
            object.__setattr__(self, "purpose", str(self.purpose))


@dataclass(frozen=True, slots=True)
class WebTransportDatagramSpec(SerdeMixin):
    name: str
    framing: Framing | FramingSpec
    purpose: str | None = None

    def __post_init__(self) -> None:
        if not str(self.name):
            raise ValueError("WebTransport datagram specs require a name")
        framing = validate_webtransport_inner_framing(
            lane="datagram",
            inner_framing=self.framing,
        )
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "framing", framing)
        if self.purpose is not None:
            object.__setattr__(self, "purpose", str(self.purpose))


@dataclass(frozen=True, slots=True)
class WebTransportProtocolBindingSpec(SerdeMixin):
    path: str
    control_stream: WebTransportStreamSpec | dict[str, Any]
    streams: tuple[WebTransportStreamSpec | dict[str, Any], ...] = ()
    datagrams: tuple[WebTransportDatagramSpec | dict[str, Any], ...] = ()
    framing: Framing | FramingSpec = "webtransport"
    proto: Literal["webtransport"] = "webtransport"
    profile: Literal["webtransport"] = "webtransport"
    exchange: Exchange = "bidirectional_stream"

    def __post_init__(self) -> None:
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        validate_webtransport_lane_exchange(lane="session", exchange=self.exchange)
        control = _coerce_webtransport_stream_spec(
            self.control_stream,
            default_name="control",
        )
        if control.kind != "bidi_stream":
            raise ValueError("WebTransport control_stream must use bidi_stream")
        if control.opens != "first":
            raise ValueError("WebTransport control_stream must open first")
        streams = tuple(_coerce_webtransport_stream_spec(item) for item in self.streams)
        datagrams = tuple(_coerce_webtransport_datagram_spec(item) for item in self.datagrams)
        names = [item.name for item in streams] + [item.name for item in datagrams]
        if any(not name for name in names):
            raise ValueError("WebTransport stream and datagram specs require names")
        if len(set(names)) != len(names):
            raise ValueError("WebTransport lane names must be unique")
        object.__setattr__(self, "control_stream", control)
        object.__setattr__(self, "streams", streams)
        object.__setattr__(self, "datagrams", datagrams)
        object.__setattr__(self, "framing", framing)
        object.__setattr__(self, "exchange", "bidirectional_stream")


@dataclass(frozen=True, slots=True)
class HTTPBindingSpec(SerdeMixin):
    proto: Literal["http", "https"] = "http"
    profile: Literal["rest", "jsonrpc", "stream", "sse"] = "rest"
    path: str = "/"
    methods: tuple[str, ...] = ("GET",)
    rpc_method: str | None = None
    endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__
    exchange: Exchange | None = None
    framing: Framing | FramingSpec | None = None

    def __post_init__(self) -> None:
        default_exchange, default_framing = _PROFILE_DEFAULTS[self.profile]
        kind = binding_kind_for(proto=self.proto, profile=self.profile)
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(self.exchange or default_exchange),
        )
        framing = normalize_framing_spec(self.framing, default=default_framing).kind
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
    framing: Framing | FramingSpec = "text"

    def __post_init__(self) -> None:
        subprotocols = derive_websocket_subprotocols(
            framing=self.framing,
            subprotocols=self.subprotocols,
        )
        exchange = validate_binding_profile_exchange(
            binding_kind=self.proto,
            exchange=self.exchange,
        )
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
            subprotocols=subprotocols,
        )
        object.__setattr__(self, "subprotocols", subprotocols)
        object.__setattr__(self, "exchange", exchange)
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class HttpRestBindingSpec(SerdeMixin):
    proto: Literal["http.rest", "https.rest"]
    methods: tuple[str, ...]
    path: str
    profile: Literal["rest"] = "rest"
    exchange: Exchange = "request_response"
    framing: Framing | FramingSpec = "json"

    def __post_init__(self) -> None:
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class HttpJsonRpcBindingSpec(SerdeMixin):
    proto: Literal["http.jsonrpc", "https.jsonrpc"]
    rpc_method: str
    endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__
    profile: Literal["jsonrpc"] = "jsonrpc"
    exchange: Exchange = "request_response"
    framing: Framing | FramingSpec = "jsonrpc"

    def __post_init__(self) -> None:
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class HttpStreamBindingSpec(SerdeMixin):
    proto: Literal["http.stream", "https.stream"]
    path: str
    methods: tuple[str, ...] = ("GET",)
    profile: Literal["stream"] = "stream"
    exchange: Exchange = "server_stream"
    framing: Framing | FramingSpec = "stream"

    def __post_init__(self) -> None:
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class SseBindingSpec(SerdeMixin):
    proto: Literal["http.sse", "https.sse"] = "http.sse"
    path: str = "/"
    methods: tuple[str, ...] = ("GET",)
    profile: Literal["sse"] = "sse"
    exchange: Exchange = "server_stream"
    framing: Framing | FramingSpec = "sse"

    def __post_init__(self) -> None:
        validate_binding_profile_exchange(binding_kind=self.proto, exchange=self.exchange)
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        object.__setattr__(self, "framing", framing)


@dataclass(frozen=True, slots=True)
class WsBindingSpec(SerdeMixin):
    proto: Literal["ws", "wss"]
    path: str
    subprotocols: tuple[str, ...] = ()
    profile: Literal["websocket"] = "websocket"
    exchange: Exchange = "bidirectional_stream"
    framing: Framing | FramingSpec = "text"

    def __post_init__(self) -> None:
        subprotocols = derive_websocket_subprotocols(
            framing=self.framing,
            subprotocols=self.subprotocols,
        )
        exchange = validate_binding_profile_exchange(
            binding_kind=self.proto,
            exchange=self.exchange,
        )
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
            subprotocols=subprotocols,
        )
        object.__setattr__(self, "subprotocols", subprotocols)
        object.__setattr__(self, "exchange", exchange)
        object.__setattr__(self, "framing", framing)


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
    framing: Framing | FramingSpec = "webtransport"
    inner_framing: Framing | FramingSpec | None = None

    def __post_init__(self) -> None:
        framing = validate_app_framing_for_binding(
            binding_kind=self.proto,
            framing=self.framing,
        )
        profile_lane = webtransport_lane_for_profile(self.profile)
        lane = webtransport_lane_for_profile(self.lane or self.profile)
        if (
            self.lane is not None
            and self.profile not in {"webtransport", "session"}
            and lane != profile_lane
        ):
            raise ValueError(
                f"WebTransport lane {lane!r} conflicts with profile {self.profile!r}"
            )
        default_exchange, _default_framing = _PROFILE_DEFAULTS[lane]
        exchange = str(self.exchange or default_exchange)
        if self.exchange == "bidirectional_stream" and default_exchange != "bidirectional_stream":
            exchange = default_exchange
        exchange = validate_webtransport_lane_exchange(lane=lane, exchange=exchange)
        inner_framing = validate_webtransport_inner_framing(
            lane=lane,
            inner_framing=self.inner_framing,
        )
        object.__setattr__(self, "framing", framing)
        object.__setattr__(self, "lane", lane)
        object.__setattr__(self, "exchange", exchange)
        object.__setattr__(self, "inner_framing", inner_framing)


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


ProtocolBindingSpec = Union[
    HttpRestProtocolBindingSpec,
    HttpJsonRpcProtocolBindingSpec,
    WebSocketProtocolBindingSpec,
    WebTransportProtocolBindingSpec,
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
TransportBindingSpec = ProtocolBindingSpec


def canonical_binding_kind(binding: TransportBindingSpec | MappingLike) -> str:
    if isinstance(
        binding,
        (
            HttpRestProtocolBindingSpec,
            HttpJsonRpcProtocolBindingSpec,
            WebSocketProtocolBindingSpec,
            WebTransportProtocolBindingSpec,
        ),
    ):
        return str(binding.proto)
    if isinstance(binding, HTTPBindingSpec):
        return binding_kind_for(proto=binding.proto, profile=binding.profile)
    if isinstance(binding, WebSocketBindingSpec):
        return binding.proto
    if isinstance(binding, (HttpRestBindingSpec, HttpJsonRpcBindingSpec, HttpStreamBindingSpec, SseBindingSpec, WsBindingSpec, WebTransportBindingSpec)):
        return str(binding.proto)
    if isinstance(binding, dict):
        return _canonical_binding_kind_from_mapping(binding)
    return str(getattr(binding, "proto", ""))


def normalize_binding_spec(binding: TransportBindingSpec) -> HTTPBindingSpec | WebSocketBindingSpec | WebTransportBindingSpec | WebTransportProtocolBindingSpec | MessageBindingSpec | DatagramBindingSpec:
    if isinstance(binding, WebTransportProtocolBindingSpec):
        return binding
    if isinstance(binding, HttpRestProtocolBindingSpec):
        proto = "https" if binding.proto == "https.rest" else "http"
        return HTTPBindingSpec(
            proto=proto,
            profile="rest",
            path=binding.path,
            methods=binding.methods,
            exchange=binding.exchange,
            framing=binding.framing,
        )
    if isinstance(binding, HttpJsonRpcProtocolBindingSpec):
        proto = "https" if binding.proto == "https.jsonrpc" else "http"
        return HTTPBindingSpec(
            proto=proto,
            profile="jsonrpc",
            rpc_method=binding.method,
            endpoint=binding.path,
            exchange=binding.exchange,
            framing=binding.framing,
        )
    if isinstance(binding, WebSocketProtocolBindingSpec):
        return WebSocketBindingSpec(
            proto=binding.proto,
            path=binding.path,
            exchange=binding.exchange,
            framing=binding.framing,
        )
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
        "framing_kind": framing,
        "framing_spec": framing_spec_name(framing),
        "family": family,
        "subevents": _binding_subevents(family),
    }
    if isinstance(binding, WebTransportProtocolBindingSpec):
        control = binding.control_stream
        metadata["lane"] = "session"
        metadata["control_stream"] = {
            "name": control.name,
            "kind": control.kind,
            "opens": control.opens,
            "purpose": control.purpose,
            "framing": control.framing,
        }
        metadata["streams"] = tuple(
            {
                "name": stream.name,
                "kind": stream.kind,
                "purpose": stream.purpose,
                "framing": stream.framing,
            }
            for stream in binding.streams
        )
        metadata["datagrams"] = tuple(
            {
                "name": datagram.name,
                "purpose": datagram.purpose,
                "framing": datagram.framing,
            }
            for datagram in binding.datagrams
        )
    elif isinstance(binding, WebTransportBindingSpec):
        metadata["lane"] = binding.lane or webtransport_lane_for_profile(binding.profile)
        metadata["inner_framing"] = inner_framing
        if metadata["lane"] == "bidi_stream":
            metadata["direction"] = "bidirectional"
        elif metadata["lane"] == "unidi_client_stream":
            metadata["stream_initiator"] = "client"
            metadata["direction"] = "client_to_server"
        elif metadata["lane"] == "unidi_server_stream":
            metadata["stream_initiator"] = "server"
            metadata["direction"] = "server_to_client"
    elif family == "stream" and proto in {"http.stream", "https.stream"}:
        if exchange == "client_stream":
            metadata["carrier_kind"] = "http_request_body"
            metadata["stream_initiator"] = "client"
            metadata["direction"] = "client_to_server"
        elif exchange == "server_stream":
            metadata["carrier_kind"] = "http_response_body"
            metadata["stream_initiator"] = "server"
            metadata["direction"] = "server_to_client"
    if isinstance(binding, WebSocketProtocolBindingSpec):
        derived = derive_websocket_subprotocol_for_framing(binding.framing)
        if derived is not None:
            metadata["websocket_subprotocol"] = derived
    elif proto in {"ws", "wss"}:
        metadata.update(
            derive_session_metadata_for_framing(
                binding_kind=proto,
                framing=framing,
                subprotocols=tuple(getattr(binding, "subprotocols", ()) or ()),
            )
        )
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
    if isinstance(binding, HttpRestProtocolBindingSpec):
        return "request"
    if isinstance(binding, HttpJsonRpcProtocolBindingSpec):
        return "request"
    if isinstance(binding, WebSocketProtocolBindingSpec):
        return "message"
    if isinstance(binding, WebTransportProtocolBindingSpec):
        return "session"
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
    "BINDING_PROFILE_EXCHANGE_SUPPORT",
    "BindingProfile",
    "BinaryFramingSpec",
    "BytesFramingSpec",
    "DatagramBindingSpec",
    "Exchange",
    "FRAMING_SPEC_BY_KIND",
    "Framing",
    "FramingSpec",
    "HTTPBindingSpec",
    "HttpJsonRpcBindingSpec",
    "HttpJsonRpcProtocolBindingSpec",
    "HttpRestBindingSpec",
    "HttpRestProtocolBindingSpec",
    "HttpStreamBindingSpec",
    "JsonFramingSpec",
    "JsonRpcFramingSpec",
    "MessageBindingSpec",
    "MultipartFormDataFramingSpec",
    "NdjsonFramingSpec",
    "ProtocolBindingSpec",
    "SseBindingSpec",
    "SseFramingSpec",
    "StreamFramingSpec",
    "TextFramingSpec",
    "TransportBindingSpec",
    "WEBTRANSPORT_INNER_FRAMING_SUPPORT",
    "WEBTRANSPORT_LANE_EXCHANGES",
    "WEBTRANSPORT_NATIVE_LANES",
    "WebSocketBindingSpec",
    "WebTransportFramingSpec",
    "WebTransportBindingSpec",
    "WebSocketProtocolBindingSpec",
    "WebTransportDatagramSpec",
    "WebTransportLane",
    "WebTransportProtocolBindingSpec",
    "WebTransportStreamKind",
    "WebTransportStreamSpec",
    "WsBindingSpec",
    "binding_kind_for",
    "canonical_binding_kind",
    "compile_binding_event_key",
    "derive_session_metadata_for_framing",
    "derive_websocket_subprotocol_for_framing",
    "derive_websocket_subprotocols",
    "framing_spec_name",
    "matches_exchange_selector",
    "normalize_exchange",
    "normalize_binding_spec",
    "normalize_framing_spec",
    "project_binding_runtime_metadata",
    "resolve_rest_nested_prefix",
    "validate_app_framing_for_binding",
    "validate_binding_profile_exchange",
    "validate_webtransport_lane_exchange",
    "validate_webtransport_inner_framing",
    "webtransport_lane_for_profile",
    "webtransport_runtime_family",
]
