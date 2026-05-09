from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Sequence

from .binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    TransportBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from .op_spec import OpSpec
from .serde import SerdeMixin
from .table_spec import TableSpec

PathKind = Literal[
    "resource",
    "jsonrpc",
    "websocket",
    "wss-jsonrpc",
    "sse",
    "webtransport",
    "docs-payload",
    "docs-uix",
    "static",
    "mount",
]


@dataclass
class PathSpec(SerdeMixin):
    """Canonical address node for path-owned AppSpec composition."""

    path: str
    kind: PathKind = "resource"
    name: str | None = None
    tables: Sequence[TableSpec] = field(default_factory=tuple)
    ops: Sequence[OpSpec] = field(default_factory=tuple)
    middlewares: Sequence[Any] = field(default_factory=tuple)
    docs_payload: Any | None = None
    docs_uix: Any | None = None
    static: Any | None = None
    mount: Any | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path.startswith("/"):
            raise ValueError("PathSpec.path must be an absolute path string.")
        self._validate_tables()
        self._validate_ops("PathSpec.ops", self.ops)
        for table in self.tables:
            self._validate_ops("TableSpec.ops", table.ops)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PathSpec":
        if "routes" in payload:
            raise ValueError("PathSpec does not accept 'routes'; use path-owned specs.")
        return super().from_dict(payload)

    def binding_path(self, binding: TransportBindingSpec) -> str:
        """Return the containing path for a binding, rejecting conflicting paths."""

        if isinstance(binding, HttpJsonRpcBindingSpec):
            if binding.endpoint not in {"", "default", self.path}:
                raise ValueError(
                    "HttpJsonRpcBindingSpec endpoint conflicts with containing PathSpec.path."
                )
            return self.path

        explicit_path = getattr(binding, "path", None)
        if explicit_path in {None, "", "/", self.path}:
            return self.path
        raise ValueError(
            f"{binding.__class__.__name__} path conflicts with containing PathSpec.path."
        )

    def iter_ops(self) -> tuple[OpSpec, ...]:
        table_ops = tuple(op for table in self.tables for op in table.ops)
        return (*tuple(self.ops), *table_ops)

    def _validate_tables(self) -> None:
        for table in self.tables:
            if isinstance(table, str):
                raise TypeError("PathSpec.tables entries must be TableSpec, not strings.")
            if not isinstance(table, TableSpec):
                raise TypeError(
                    f"PathSpec.tables entries must be TableSpec; got {type(table).__name__}."
                )
            if isinstance(table.model, type):
                raise TypeError(
                    "PathSpec canonical tables must use spec-native identity, not concrete model classes."
                )
            if table.model is not None and table.model_ref is None:
                raise TypeError(
                    "PathSpec canonical tables must use model_ref/name/resource identity."
                )

    @staticmethod
    def _validate_ops(field_name: str, ops: Sequence[Any]) -> None:
        for op in ops:
            if isinstance(op, str):
                raise TypeError(f"{field_name} entries must be OpSpec, not strings.")
            if not isinstance(op, OpSpec):
                raise TypeError(
                    f"{field_name} entries must be OpSpec; got {type(op).__name__}."
                )


def path_for_binding(path: PathSpec, binding: TransportBindingSpec) -> str:
    return path.binding_path(binding)


__all__ = ["PathKind", "PathSpec", "path_for_binding"]
