from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Literal, Sequence

from .binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    TransportBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    canonical_binding_kind,
)
from .op_spec import OpSpec, TargetOp
from .table_profile_spec import TableProfileError, TableProfileSpec

BindingSource = Literal["explicit", "table_profile"]

_NO_DEFAULT_BINDING_PROFILES = {"plain", "crud", "realtime"}
_REST_PROFILES = {"rest", "bulk_crud", "oltp", "olap"}
_JSONRPC_PROFILES = {"jsonrpc"}
_STREAM_PROFILES = {"stream"}
_SSE_PROFILES = {"sse", "event_stream"}
_WEBSOCKET_PROFILES = {"websocket"}
_WEBSOCKET_JSONRPC_PROFILES = {"websocket_jsonrpc"}
_WEBTRANSPORT_PROFILE_LANES = {
    "webtransport": "session",
    "webtransport_bidi": "bidi_stream",
    "webtransport_client_stream": "unidi_client_stream",
    "webtransport_server_stream": "unidi_server_stream",
    "webtransport_datagram": "datagram",
}

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
_REST_PROFILE_TARGETS = {
    "rest": set(_REST_METHODS),
    "bulk_crud": {
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_delete",
    },
    "oltp": {"create", "read", "update", "replace", "merge", "delete", "list", "count", "exists"},
    "olap": {"read", "list", "count", "exists", "aggregate", "group_by"},
}


@dataclass(frozen=True, slots=True)
class BindingToken:
    """Deterministic projection record for a concrete op binding."""

    source: BindingSource
    profile: str
    op_alias: str
    op_target: str
    binding_kind: str
    path: str = ""
    methods: tuple[str, ...] = ()
    rpc_method: str | None = None
    framing: str = ""
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
                if dict(getattr(op, "extra", {}) or {}).get(
                    "__tigrbl_binding_source__"
                )
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
    if kind in _STREAM_PROFILES:
        return (_stream_binding(table=table, profile=profile, op=op),)
    if kind in _SSE_PROFILES:
        return (_sse_binding(table=table, profile=profile, op=op),)
    if kind in _WEBSOCKET_PROFILES:
        return (_websocket_binding(table=table, profile=profile, op=op, jsonrpc=False),)
    if kind in _WEBSOCKET_JSONRPC_PROFILES:
        return (_websocket_binding(table=table, profile=profile, op=op, jsonrpc=True),)
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


def _rest_binding(*, table: type, profile: TableProfileSpec, op: OpSpec) -> LoweredBinding:
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


def _stream_binding(*, table: type, profile: TableProfileSpec, op: OpSpec) -> LoweredBinding:
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


def _sse_binding(*, table: type, profile: TableProfileSpec, op: OpSpec) -> LoweredBinding:
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
        framing="jsonrpc" if jsonrpc else "text",
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


def _token_from_binding(
    *,
    source: BindingSource,
    profile: str,
    op: OpSpec,
    binding: TransportBindingSpec,
    precedence: int,
) -> BindingToken:
    return BindingToken(
        source=source,
        profile=profile,
        op_alias=str(op.alias),
        op_target=str(op.target),
        binding_kind=canonical_binding_kind(binding),
        path=str(getattr(binding, "path", "") or ""),
        methods=tuple(str(method).upper() for method in getattr(binding, "methods", ()) or ()),
        rpc_method=getattr(binding, "rpc_method", None),
        framing=str(getattr(binding, "framing", "") or ""),
        exchange=str(getattr(binding, "exchange", "") or ""),
        lane=getattr(binding, "lane", None),
        inner_framing=getattr(binding, "inner_framing", None),
        precedence=precedence,
    )


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
