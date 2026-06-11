from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Literal, Mapping, Sequence, get_args

from .binding_spec import BindingSpec, TransportBindingSpec
from .op_spec import OpSpec, TargetOp
from .serde import SerdeMixin

TableProfileRole = Literal["abstract", "concrete"]
DocsExposure = Literal["none", "declared", "default"]
RuntimeExposure = Literal["none", "declared", "default"]
TableProfileBindingFamily = Literal[
    "http.rest",
    "http.jsonrpc",
    "http.stream",
    "http.sse",
    "ws",
    "webtransport",
]


@dataclass(frozen=True, slots=True)
class BuiltinTableProfile:
    """Authoritative builtin table profile taxonomy row."""

    kind: str
    role: TableProfileRole
    targets: tuple[TargetOp, ...]
    binding_families: tuple[TableProfileBindingFamily, ...] = ()
    docs_exposure: DocsExposure = "none"
    runtime_exposure: RuntimeExposure = "none"
    public_class_names: tuple[str, ...] = ()


_CRUD_TARGETS: tuple[TargetOp, ...] = (
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
)
_OLTP_TARGETS: tuple[TargetOp, ...] = (
    "create",
    "read",
    "update",
    "replace",
    "merge",
    "delete",
    "list",
    "count",
    "exists",
)
_OLAP_TARGETS: tuple[TargetOp, ...] = (
    "read",
    "list",
    "count",
    "exists",
    "aggregate",
    "group_by",
)

BUILTIN_TABLE_PROFILE_DEFINITIONS: Mapping[str, BuiltinTableProfile] = {
    row.kind: row
    for row in (
        BuiltinTableProfile(
            "plain", "concrete", _CRUD_TARGETS, public_class_names=("TableBase",)
        ),
        BuiltinTableProfile(
            "crud",
            "abstract",
            _CRUD_TARGETS,
            public_class_names=("CrudTableBase", "CrudTable"),
        ),
        BuiltinTableProfile(
            "realtime",
            "abstract",
            ("publish", "subscribe", "tail"),
            public_class_names=("RealtimeTableBase", "RealtimeTable"),
        ),
        BuiltinTableProfile(
            "rest",
            "concrete",
            _CRUD_TARGETS,
            ("http.rest",),
            "default",
            "default",
            ("RestTable",),
        ),
        BuiltinTableProfile(
            "jsonrpc",
            "concrete",
            _CRUD_TARGETS,
            ("http.jsonrpc",),
            "default",
            "default",
            ("JsonRpcTable",),
        ),
        BuiltinTableProfile(
            "rest_jsonrpc",
            "concrete",
            _CRUD_TARGETS,
            ("http.rest", "http.jsonrpc"),
            "default",
            "default",
            ("RestJsonRpcTable",),
        ),
        BuiltinTableProfile(
            "bulk_crud",
            "concrete",
            (
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
            ),
            ("http.rest",),
            "default",
            "default",
            ("BulkCrudTable",),
        ),
        BuiltinTableProfile(
            "oltp", "concrete", _OLTP_TARGETS, ("http.rest",), "default", "default"
        ),
        BuiltinTableProfile(
            "olap", "concrete", _OLAP_TARGETS, ("http.rest",), "default", "default"
        ),
        BuiltinTableProfile(
            "rest_oltp",
            "concrete",
            _OLTP_TARGETS,
            ("http.rest",),
            "default",
            "default",
            ("RestOltpTable", "OltpTable"),
        ),
        BuiltinTableProfile(
            "jsonrpc_oltp",
            "concrete",
            _OLTP_TARGETS,
            ("http.jsonrpc",),
            "default",
            "default",
            ("JsonRpcOltpTable",),
        ),
        BuiltinTableProfile(
            "rest_jsonrpc_oltp",
            "concrete",
            _OLTP_TARGETS,
            ("http.rest", "http.jsonrpc"),
            "default",
            "default",
            ("RestJsonRpcOltpTable",),
        ),
        BuiltinTableProfile(
            "rest_olap",
            "concrete",
            _OLAP_TARGETS,
            ("http.rest",),
            "default",
            "default",
            ("RestOlapTable", "OlapTable"),
        ),
        BuiltinTableProfile(
            "jsonrpc_olap",
            "concrete",
            _OLAP_TARGETS,
            ("http.jsonrpc",),
            "default",
            "default",
            ("JsonRpcOlapTable",),
        ),
        BuiltinTableProfile(
            "rest_jsonrpc_olap",
            "concrete",
            _OLAP_TARGETS,
            ("http.rest", "http.jsonrpc"),
            "default",
            "default",
            ("RestJsonRpcOlapTable",),
        ),
        BuiltinTableProfile(
            "stream",
            "concrete",
            ("tail", "download"),
            ("http.stream",),
            "default",
            "default",
            ("StreamTable",),
        ),
        BuiltinTableProfile(
            "sse",
            "concrete",
            ("subscribe", "tail"),
            ("http.sse",),
            "default",
            "default",
            ("SseTable",),
        ),
        BuiltinTableProfile(
            "event_stream",
            "concrete",
            ("subscribe", "tail"),
            ("http.sse",),
            "default",
            "default",
            ("EventStreamTable",),
        ),
        BuiltinTableProfile(
            "websocket",
            "concrete",
            ("publish", "subscribe"),
            ("ws",),
            "default",
            "default",
            ("WebSocketTable",),
        ),
        BuiltinTableProfile(
            "websocket_jsonrpc",
            "concrete",
            ("create", "read", "update", "replace", "delete", "list"),
            ("ws",),
            "default",
            "default",
            ("WebSocketJsonRpcTable",),
        ),
        BuiltinTableProfile(
            "webtransport",
            "concrete",
            ("publish", "subscribe", "tail"),
            ("webtransport",),
            "default",
            "default",
            ("WebTransportTable",),
        ),
        BuiltinTableProfile(
            "webtransport_bidi",
            "concrete",
            ("publish", "subscribe", "tail"),
            ("webtransport",),
            "default",
            "default",
            ("WebTransportBidiTable",),
        ),
        BuiltinTableProfile(
            "webtransport_client_stream",
            "concrete",
            ("upload", "append_chunk"),
            ("webtransport",),
            "default",
            "default",
            ("WebTransportClientStreamTable",),
        ),
        BuiltinTableProfile(
            "webtransport_server_stream",
            "concrete",
            ("download", "tail"),
            ("webtransport",),
            "default",
            "default",
            ("WebTransportServerStreamTable",),
        ),
        BuiltinTableProfile(
            "webtransport_datagram",
            "concrete",
            ("send_datagram",),
            ("webtransport",),
            "default",
            "default",
            ("WebTransportDatagramTable",),
        ),
    )
}

BUILTIN_TABLE_PROFILE_KINDS: frozenset[str] = frozenset(
    BUILTIN_TABLE_PROFILE_DEFINITIONS
)

_VALID_ROLES = {"abstract", "concrete"}
_VALID_DOCS_EXPOSURE = {"none", "declared", "default"}
_VALID_RUNTIME_EXPOSURE = {"none", "declared", "default"}
_TRANSPORT_BINDING_TYPES = get_args(TransportBindingSpec)

_COLLECTION_TARGETS = {
    "create",
    "list",
    "clear",
    "count",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "aggregate",
    "group_by",
    "publish",
    "subscribe",
    "tail",
    "upload",
    "download",
    "append_chunk",
    "send_datagram",
    "checkpoint",
}


class TableProfileError(ValueError):
    """Raised when a table profile declaration is malformed or ambiguous."""


@dataclass(frozen=True, slots=True)
class TableProfileSpec(SerdeMixin):
    """Complete table-level default operation and exposure policy."""

    kind: str = "plain"
    role: TableProfileRole = "concrete"
    ops: Sequence[OpSpec] = field(default_factory=tuple)
    default_bindings: Sequence[BindingSpec | TransportBindingSpec] = field(
        default_factory=tuple
    )
    docs_exposure: DocsExposure = "none"
    runtime_exposure: RuntimeExposure = "none"
    custom: bool = False
    namespace: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind:
            raise TableProfileError("TableProfileSpec.kind must be a non-empty string")
        if self.role not in _VALID_ROLES:
            raise TableProfileError(f"invalid table profile role {self.role!r}")
        if self.docs_exposure not in _VALID_DOCS_EXPOSURE:
            raise TableProfileError(
                f"invalid table profile docs_exposure {self.docs_exposure!r}"
            )
        if self.runtime_exposure not in _VALID_RUNTIME_EXPOSURE:
            raise TableProfileError(
                f"invalid table profile runtime_exposure {self.runtime_exposure!r}"
            )
        if self.custom:
            if self.kind in BUILTIN_TABLE_PROFILE_KINDS:
                raise TableProfileError(
                    f"custom table profile cannot use reserved kind {self.kind!r}"
                )
            if not isinstance(self.namespace, str) or not self.namespace:
                raise TableProfileError("custom table profiles require a namespace")
        elif self.namespace is not None:
            raise TableProfileError("built-in table profiles cannot declare namespace")

        ops = tuple(self.ops or ())
        for op in ops:
            if not isinstance(op, OpSpec):
                raise TableProfileError(
                    "TableProfileSpec.ops entries must be OpSpec instances"
                )
        object.__setattr__(self, "ops", ops)

        bindings = tuple(self.default_bindings or ())
        for binding in bindings:
            if not isinstance(binding, (BindingSpec, *_TRANSPORT_BINDING_TYPES)):
                raise TableProfileError(
                    "TableProfileSpec.default_bindings entries must be binding specs"
                )
        if self.role == "abstract" and bindings:
            raise TableProfileError(
                "abstract table profiles cannot declare default network bindings"
            )
        object.__setattr__(self, "default_bindings", bindings)

        builtin = BUILTIN_TABLE_PROFILE_DEFINITIONS.get(self.kind)
        if builtin is not None and self.role != builtin.role:
            raise TableProfileError(
                f"built-in table profile {self.kind!r} requires role {builtin.role!r}"
            )

    def bind_table(self, table: type) -> "TableProfileSpec":
        return replace(
            self,
            ops=tuple(
                op if getattr(op, "table", None) is table else replace(op, table=table)
                for op in self.ops
            ),
        )


def make_profile_op(
    target: TargetOp,
    *,
    alias: str | None = None,
    bindings: Sequence[Any] = (),
    exchange: Any = "request_response",
) -> OpSpec:
    selected_alias = alias or str(target)
    return OpSpec(
        alias=selected_alias,
        target=target,
        arity="collection" if target in _COLLECTION_TARGETS else "member",
        bindings=tuple(bindings or ()),
        exchange=exchange,
        persist="default",
        handler=None,
        request_model=None,
        response_model=None,
        hooks=(),
        status_code=None,
        extra={},
    )


def make_table_profile(
    kind: str,
    targets: Sequence[TargetOp],
    *,
    role: TableProfileRole = "concrete",
    default_bindings: Sequence[BindingSpec | TransportBindingSpec] = (),
    docs_exposure: DocsExposure = "none",
    runtime_exposure: RuntimeExposure = "none",
    custom: bool = False,
    namespace: str | None = None,
) -> TableProfileSpec:
    return TableProfileSpec(
        kind=kind,
        role=role,
        ops=tuple(make_profile_op(target) for target in targets),
        default_bindings=tuple(default_bindings or ()),
        docs_exposure=docs_exposure,
        runtime_exposure=runtime_exposure,
        custom=custom,
        namespace=namespace,
    )


def make_builtin_table_profile(kind: str) -> TableProfileSpec:
    try:
        row = BUILTIN_TABLE_PROFILE_DEFINITIONS[kind]
    except KeyError as exc:
        raise TableProfileError(
            f"unknown built-in table profile kind {kind!r}"
        ) from exc
    return make_table_profile(
        row.kind,
        row.targets,
        role=row.role,
        docs_exposure=row.docs_exposure,
        runtime_exposure=row.runtime_exposure,
    )


def get_builtin_table_profile_definition(kind: str) -> BuiltinTableProfile:
    try:
        return BUILTIN_TABLE_PROFILE_DEFINITIONS[kind]
    except KeyError as exc:
        raise TableProfileError(
            f"unknown built-in table profile kind {kind!r}"
        ) from exc


def iter_builtin_table_profile_definitions() -> tuple[BuiltinTableProfile, ...]:
    return tuple(BUILTIN_TABLE_PROFILE_DEFINITIONS.values())


_BUILTIN_TABLE_PROFILES: dict[str, TableProfileSpec] = {
    kind: make_builtin_table_profile(kind) for kind in BUILTIN_TABLE_PROFILE_DEFINITIONS
}

PLAIN_TABLE_PROFILE = _BUILTIN_TABLE_PROFILES["plain"]
CRUD_TABLE_PROFILE = _BUILTIN_TABLE_PROFILES["crud"]
REALTIME_TABLE_PROFILE = _BUILTIN_TABLE_PROFILES["realtime"]


_REGISTRY: dict[str, TableProfileSpec] = dict(_BUILTIN_TABLE_PROFILES)


def register_table_profile(profile: TableProfileSpec) -> TableProfileSpec:
    normalized = coerce_table_profile(profile)
    existing = _REGISTRY.get(normalized.kind)
    if existing is not None:
        raise TableProfileError(
            f"table profile kind {normalized.kind!r} is already registered"
        )
    if normalized.kind in BUILTIN_TABLE_PROFILE_KINDS and normalized.custom:
        raise TableProfileError(
            f"custom table profile cannot replace built-in kind {normalized.kind!r}"
        )
    _REGISTRY[normalized.kind] = normalized
    return normalized


def get_table_profile(kind: str) -> TableProfileSpec:
    try:
        return _REGISTRY[kind]
    except KeyError as exc:
        raise TableProfileError(f"unknown table profile kind {kind!r}") from exc


def coerce_table_profile(value: Any) -> TableProfileSpec:
    if isinstance(value, TableProfileSpec):
        return value
    if isinstance(value, str):
        return get_table_profile(value)
    if isinstance(value, Mapping):
        return TableProfileSpec.from_dict(dict(value))
    raise TableProfileError(
        "TABLE_PROFILE must be a TableProfileSpec, registered profile kind, or mapping"
    )


__all__ = [
    "BUILTIN_TABLE_PROFILE_KINDS",
    "BUILTIN_TABLE_PROFILE_DEFINITIONS",
    "BuiltinTableProfile",
    "CRUD_TABLE_PROFILE",
    "DocsExposure",
    "PLAIN_TABLE_PROFILE",
    "REALTIME_TABLE_PROFILE",
    "RuntimeExposure",
    "TableProfileBindingFamily",
    "TableProfileError",
    "TableProfileRole",
    "TableProfileSpec",
    "coerce_table_profile",
    "get_builtin_table_profile_definition",
    "get_table_profile",
    "iter_builtin_table_profile_definitions",
    "make_profile_op",
    "make_builtin_table_profile",
    "make_table_profile",
    "register_table_profile",
]
