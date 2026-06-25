from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Literal, Sequence

from .binding_spec import (
    BytesFramingSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    JsonFramingSpec,
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    SseBindingSpec,
    TextFramingSpec,
    TransportBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    canonical_binding_kind,
    derive_session_metadata_for_framing,
    framing_kind,
    framing_spec_name,
)
from .op_spec import OpSpec, TargetOp
from .table_profile_spec import (
    BUILTIN_TABLE_PROFILE_DEFINITIONS,
    TableProfileError,
    TableProfileSpec,
)

BindingSource = Literal["explicit", "table_profile"]

_NO_DEFAULT_BINDING_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if not row.binding_families
}
_REST_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if row.binding_families == ("http.rest",)
}
_JSONRPC_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if row.binding_families == ("http.jsonrpc",)
}
_REST_JSONRPC_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if row.binding_families == ("http.rest", "http.jsonrpc")
}
_STREAM_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if row.binding_families == ("http.stream",)
}
_SSE_PROFILES = {
    kind
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if row.binding_families == ("http.sse",)
}
_WEBSOCKET_PROFILES = {"websocket"}
_WEBSOCKET_JSONRPC_PROFILES = {"websocket_jsonrpc"}
_WEBTRANSPORT_PROFILE_LANES = {
    "webtransport": "session",
    "webtransport_bidi": "bidi_stream",
    "webtransport_client_stream": "unidi_client_stream",
    "webtransport_server_stream": "unidi_server_stream",
    "webtransport_datagram": "datagram",
}
_WEBTRANSPORT_OP_LANE_PROFILES = {"webtransport_ops"}

_REST_METHODS: dict[str, tuple[str, ...]] = {
    "create": ("POST",),
    "read": ("GET",),
    "update": ("PATCH",),
    "replace": ("PUT",),
    "merge": ("PATCH",),
    "delete": ("DELETE",),
    "list": ("GET",),
    "clear": ("DELETE",),
    "count": ("GET",),
    "exists": ("GET",),
    "bulk_create": ("POST",),
    "bulk_update": ("PATCH",),
    "bulk_replace": ("PUT",),
    "bulk_merge": ("PATCH",),
    "bulk_delete": ("DELETE",),
    "aggregate": ("GET",),
    "group_by": ("GET",),
    "checkpoint": ("POST",),
}
_STREAM_TARGETS = {"tail", "download"}
_SSE_TARGETS = {"subscribe", "tail"}
_WEBSOCKET_TARGETS = {"publish", "subscribe"}
_WEBSOCKET_JSONRPC_TARGETS = {
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
}
_WEBTRANSPORT_LANE_TARGETS = {
    "session": {"publish", "subscribe", "tail"},
    "bidi_stream": {"publish", "subscribe", "tail"},
    "unidi_client_stream": {"upload", "append_chunk"},
    "unidi_server_stream": {"download", "tail"},
    "datagram": {"send_datagram"},
}
_WEBTRANSPORT_OP_LANE_DEFAULTS: dict[str, tuple[str, str | None]] = {
    "create": ("bidi_stream", "jsonrpc"),
    "read": ("bidi_stream", "jsonrpc"),
    "update": ("bidi_stream", "jsonrpc"),
    "replace": ("bidi_stream", "jsonrpc"),
    "merge": ("bidi_stream", "jsonrpc"),
    "delete": ("bidi_stream", "jsonrpc"),
    "list": ("bidi_stream", "jsonrpc"),
    "clear": ("bidi_stream", "jsonrpc"),
    "count": ("bidi_stream", "jsonrpc"),
    "exists": ("bidi_stream", "jsonrpc"),
    "bulk_create": ("bidi_stream", "jsonrpc"),
    "bulk_update": ("bidi_stream", "jsonrpc"),
    "bulk_replace": ("bidi_stream", "jsonrpc"),
    "bulk_merge": ("bidi_stream", "jsonrpc"),
    "bulk_delete": ("bidi_stream", "jsonrpc"),
    "aggregate": ("bidi_stream", "jsonrpc"),
    "group_by": ("bidi_stream", "jsonrpc"),
    "publish": ("bidi_stream", "jsonrpc"),
    "subscribe": ("unidi_server_stream", "ndjson"),
    "tail": ("unidi_server_stream", "ndjson"),
    "download": ("unidi_server_stream", "bytes"),
    "upload": ("unidi_client_stream", "bytes"),
    "append_chunk": ("unidi_client_stream", "bytes"),
    "send_datagram": ("datagram", "json"),
    "checkpoint": ("bidi_stream", "jsonrpc"),
}
_REST_PROFILE_TARGETS = {
    kind: set(row.targets)
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if "http.rest" in row.binding_families
}
_JSONRPC_PROFILE_TARGETS = {
    kind: set(row.targets)
    for kind, row in BUILTIN_TABLE_PROFILE_DEFINITIONS.items()
    if "http.jsonrpc" in row.binding_families
}


@dataclass(frozen=True, slots=True)
class BindingToken:
    """Deterministic projection record for a concrete op binding."""

    source: BindingSource
    profile: str
    op_alias: str
    op_target: str
    binding_kind: str
    protocol_kind: str = ""
    path: str = ""
    methods: tuple[str, ...] = ()
    rpc_method: str | None = None
    framing: str = ""
    framing_kind: str = ""
    framing_spec: str = ""
    required_subprotocol: str | None = None
    exchange: str = ""
    lane: str | None = None
    inner_framing: str | None = None
    precedence: int = 0


@dataclass(frozen=True, slots=True)
class LoweredBinding:
    token: BindingToken
    binding: TransportBindingSpec


def lower_table_profile_bindings(
    table: type,
    profile: TableProfileSpec,
    ops: Sequence[OpSpec],
) -> tuple[OpSpec, ...]:
    """Return ops with profile-specific default bindings applied."""

    return tuple(
        _lower_op_with_profile_defaults(table=table, profile=profile, op=op)
        for op in ops
    )


def lower_binding_tokens_for_ops(
    table: type,
    profile: TableProfileSpec,
    ops: Sequence[OpSpec],
) -> tuple[BindingToken, ...]:
    """Return deterministic tokens for explicit or profile-derived bindings."""

    out: list[BindingToken] = []
    for op in ops:
        explicit = tuple(getattr(op, "bindings", ()) or ())
        if explicit:
            source: BindingSource = (
                "table_profile"
                if dict(getattr(op, "extra", {}) or {}).get("__tigrbl_binding_source__")
                == "table_profile"
                else "explicit"
            )
            out.extend(
                _tokens_for_bindings(
                    source=source,
                    profile=profile,
                    op=op,
                    bindings=explicit,
                )
            )
            continue
        lowered = lower_default_bindings_for_op(table=table, profile=profile, op=op)
        out.extend(item.token for item in lowered)
    return tuple(out)


def lower_default_bindings_for_op(
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
) -> tuple[LoweredBinding, ...]:
    if _is_custom_or_unknown(op):
        return ()

    kind = profile.kind
    if kind in _NO_DEFAULT_BINDING_PROFILES or profile.role == "abstract":
        return ()
    if kind in _REST_PROFILES:
        return (_rest_binding(table=table, profile=profile, op=op),)
    if kind in _JSONRPC_PROFILES:
        return (_jsonrpc_binding(table=table, profile=profile, op=op),)
    if kind in _REST_JSONRPC_PROFILES:
        return (
            _rest_binding(table=table, profile=profile, op=op),
            _jsonrpc_binding(table=table, profile=profile, op=op),
        )
    if kind in _STREAM_PROFILES:
        return (_stream_binding(table=table, profile=profile, op=op),)
    if kind in _SSE_PROFILES:
        return (_sse_binding(table=table, profile=profile, op=op),)
    if kind in _WEBSOCKET_PROFILES:
        return (_websocket_binding(table=table, profile=profile, op=op, jsonrpc=False),)
    if kind in _WEBSOCKET_JSONRPC_PROFILES:
        return (_websocket_binding(table=table, profile=profile, op=op, jsonrpc=True),)
    if kind in _WEBTRANSPORT_OP_LANE_PROFILES:
        return (_webtransport_op_lane_binding(table=table, profile=profile, op=op),)
    if kind in _WEBTRANSPORT_PROFILE_LANES:
        return (_webtransport_binding(table=table, profile=profile, op=op),)
    if profile.custom:
        return ()
    raise TableProfileError(f"unsupported table profile default binding kind {kind!r}")


def _lower_op_with_profile_defaults(
    *,
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
) -> OpSpec:
    if tuple(getattr(op, "bindings", ()) or ()):
        return op
    lowered = lower_default_bindings_for_op(table=table, profile=profile, op=op)
    if not lowered:
        return replace(op, expose_routes=False, expose_rpc=False)
    return replace(
        op,
        bindings=tuple(item.binding for item in lowered),
        expose_routes=False,
        expose_rpc=False,
        extra={
            **dict(getattr(op, "extra", {}) or {}),
            "__tigrbl_binding_source__": "table_profile",
        },
    )


def _tokens_for_bindings(
    *,
    source: BindingSource,
    profile: TableProfileSpec,
    op: OpSpec,
    bindings: Iterable[TransportBindingSpec],
) -> tuple[BindingToken, ...]:
    return tuple(
        _token_from_binding(
            source=source,
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=0 if source == "explicit" else 1,
        )
        for binding in bindings
    )


def _rest_binding(
    *, table: type, profile: TableProfileSpec, op: OpSpec
) -> LoweredBinding:
    allowed = _REST_PROFILE_TARGETS.get(profile.kind, set(_REST_METHODS))
    if op.target not in allowed:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support REST target {op.target!r}"
        )
    if op.target not in _REST_METHODS:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support default REST binding for target {op.target!r}"
        )
    binding = HttpRestBindingSpec(
        proto="http.rest",
        methods=tuple(op.http_methods or _REST_METHODS[str(op.target)]),
        path=_path_for_op(op),
    )
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _jsonrpc_binding(
    *,
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
) -> LoweredBinding:
    allowed = _JSONRPC_PROFILE_TARGETS.get(profile.kind, set(_REST_METHODS))
    if op.target not in allowed:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support JSON-RPC target {op.target!r}"
        )
    if op.target not in _REST_METHODS:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support default JSON-RPC binding for target {op.target!r}"
        )
    binding = HttpJsonRpcBindingSpec(
        proto="http.jsonrpc",
        rpc_method=f"{table.__name__}.{op.alias}",
    )
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _stream_binding(
    *, table: type, profile: TableProfileSpec, op: OpSpec
) -> LoweredBinding:
    if op.target not in _STREAM_TARGETS:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support stream target {op.target!r}"
        )
    binding = HttpStreamBindingSpec(proto="http.stream", path=_path_for_op(op))
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _sse_binding(
    *, table: type, profile: TableProfileSpec, op: OpSpec
) -> LoweredBinding:
    if op.target not in _SSE_TARGETS:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support SSE target {op.target!r}"
        )
    binding = SseBindingSpec(proto="http.sse", path=_path_for_op(op))
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _websocket_binding(
    *,
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
    jsonrpc: bool,
) -> LoweredBinding:
    allowed = _WEBSOCKET_JSONRPC_TARGETS if jsonrpc else _WEBSOCKET_TARGETS
    if op.target not in allowed:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support WebSocket target {op.target!r}"
        )
    binding = WsBindingSpec(
        proto="ws",
        path=_path_for_op(op, prefix="/ws"),
        framing=JsonRpcFramingSpec() if jsonrpc else TextFramingSpec(),
        subprotocols=("jsonrpc",) if jsonrpc else (),
    )
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _webtransport_binding(
    *,
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
) -> LoweredBinding:
    lane = _WEBTRANSPORT_PROFILE_LANES[profile.kind]
    if op.target not in _WEBTRANSPORT_LANE_TARGETS[lane]:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support WebTransport target {op.target!r}"
        )
    binding = WebTransportBindingSpec(
        path=_path_for_op(op, prefix="/wt"),
        profile="webtransport" if lane == "session" else lane,
    )
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _webtransport_op_lane_binding(
    *,
    table: type,
    profile: TableProfileSpec,
    op: OpSpec,
) -> LoweredBinding:
    try:
        lane, inner_framing = _WEBTRANSPORT_OP_LANE_DEFAULTS[str(op.target)]
    except KeyError as exc:
        raise TableProfileError(
            f"profile {profile.kind!r} does not support WebTransport target {op.target!r}"
        ) from exc
    binding = WebTransportBindingSpec(
        path=_path_for_op(op, prefix="/wt"),
        profile=lane,
        inner_framing=_table_profile_framing_spec(inner_framing),
    )
    return LoweredBinding(
        token=_token_from_binding(
            source="table_profile",
            profile=profile.kind,
            op=op,
            binding=binding,
            precedence=1,
        ),
        binding=binding,
    )


def _token_from_binding(
    *,
    source: BindingSource,
    profile: str,
    op: OpSpec,
    binding: TransportBindingSpec,
    precedence: int,
) -> BindingToken:
    binding_kind = canonical_binding_kind(binding)
    framing_obj = getattr(binding, "framing", None)
    framing = framing_kind(framing_obj)
    session_metadata = {}
    if framing:
        session_metadata = derive_session_metadata_for_framing(
            binding_kind=binding_kind,
            framing=framing_obj,
            subprotocols=tuple(getattr(binding, "subprotocols", ()) or ()),
        )
    inner_framing = getattr(binding, "inner_framing", None)
    return BindingToken(
        source=source,
        profile=profile,
        op_alias=str(op.alias),
        op_target=str(op.target),
        binding_kind=binding_kind,
        protocol_kind=binding_kind,
        path=str(getattr(binding, "path", "") or ""),
        methods=tuple(
            str(method).upper() for method in getattr(binding, "methods", ()) or ()
        ),
        rpc_method=getattr(binding, "rpc_method", None),
        framing=framing,
        framing_kind=framing,
        framing_spec=framing_spec_name(framing_obj),
        required_subprotocol=session_metadata.get("required_subprotocol"),  # type: ignore[arg-type]
        exchange=str(getattr(binding, "exchange", "") or ""),
        lane=getattr(binding, "lane", None),
        inner_framing=framing_kind(inner_framing),
        precedence=precedence,
    )


def _table_profile_framing_spec(kind: str | None):
    if kind is None:
        return None
    if kind == "json":
        return JsonFramingSpec()
    if kind == "jsonrpc":
        return JsonRpcFramingSpec()
    if kind == "ndjson":
        return NdjsonFramingSpec()
    if kind == "bytes":
        return BytesFramingSpec()
    raise TableProfileError(f"unsupported table profile framing {kind!r}")


def _path_for_op(op: OpSpec, *, prefix: str = "") -> str:
    suffix = getattr(op, "path_suffix", None)
    if suffix:
        path = str(suffix)
    else:
        path = f"/{op.alias}"
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{prefix}{path}" if prefix else path


def _is_custom_or_unknown(op: OpSpec) -> bool:
    return str(op.target) == "custom" or str(op.target) not in TargetOp.__args__  # type: ignore[attr-defined]


__all__ = [
    "BindingToken",
    "LoweredBinding",
    "lower_binding_tokens_for_ops",
    "lower_default_bindings_for_op",
    "lower_table_profile_bindings",
]
