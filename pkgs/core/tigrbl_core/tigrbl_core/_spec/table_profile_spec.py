from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Literal, Mapping, Sequence

from .binding_spec import BindingSpec
from .op_spec import OpSpec, TargetOp
from .serde import SerdeMixin

TableProfileRole = Literal["abstract", "concrete"]
DocsExposure = Literal["none", "declared", "default"]
RuntimeExposure = Literal["none", "declared", "default"]

BUILTIN_TABLE_PROFILE_KINDS: frozenset[str] = frozenset(
    {
        "plain",
        "crud",
        "realtime",
        "rest",
        "jsonrpc",
        "rest_jsonrpc",
        "bulk_crud",
        "oltp",
        "olap",
        "rest_oltp",
        "jsonrpc_oltp",
        "rest_jsonrpc_oltp",
        "rest_olap",
        "jsonrpc_olap",
        "rest_jsonrpc_olap",
        "stream",
        "sse",
        "event_stream",
        "websocket",
        "websocket_jsonrpc",
        "webtransport",
        "webtransport_bidi",
        "webtransport_client_stream",
        "webtransport_server_stream",
        "webtransport_datagram",
    }
)

_VALID_ROLES = {"abstract", "concrete"}
_VALID_DOCS_EXPOSURE = {"none", "declared", "default"}
_VALID_RUNTIME_EXPOSURE = {"none", "declared", "default"}

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
    default_bindings: Sequence[BindingSpec] = field(default_factory=tuple)
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
            if not isinstance(binding, BindingSpec):
                raise TableProfileError(
                    "TableProfileSpec.default_bindings entries must be BindingSpec instances"
                )
        object.__setattr__(self, "default_bindings", bindings)

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
    default_bindings: Sequence[BindingSpec] = (),
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


PLAIN_TABLE_PROFILE = make_table_profile(
    "plain",
    ("create", "read", "update", "replace", "delete", "list", "clear"),
)
CRUD_TABLE_PROFILE = make_table_profile(
    "crud",
    ("create", "read", "update", "replace", "delete", "list", "clear"),
    role="abstract",
)
REALTIME_TABLE_PROFILE = make_table_profile(
    "realtime",
    ("publish", "subscribe", "tail"),
    role="abstract",
)


_REGISTRY: dict[str, TableProfileSpec] = {
    PLAIN_TABLE_PROFILE.kind: PLAIN_TABLE_PROFILE,
    CRUD_TABLE_PROFILE.kind: CRUD_TABLE_PROFILE,
    REALTIME_TABLE_PROFILE.kind: REALTIME_TABLE_PROFILE,
}


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
    "CRUD_TABLE_PROFILE",
    "DocsExposure",
    "PLAIN_TABLE_PROFILE",
    "REALTIME_TABLE_PROFILE",
    "RuntimeExposure",
    "TableProfileError",
    "TableProfileRole",
    "TableProfileSpec",
    "coerce_table_profile",
    "get_table_profile",
    "make_profile_op",
    "make_table_profile",
    "register_table_profile",
]
