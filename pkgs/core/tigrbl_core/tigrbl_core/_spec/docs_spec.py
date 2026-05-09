from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence

from .binding_spec import HttpJsonRpcBindingSpec
from .path_spec import PathSpec
from .serde import SerdeMixin

DocsPayloadKind = Literal["openapi", "openrpc", "asyncapi", "jsonschema"]
DocsUixKind = Literal["swagger", "redoc", "scalar", "lens", "custom"]


@dataclass(frozen=True)
class DocsProjectionSelection(SerdeMixin):
    path: str
    table: str | None
    op: str
    protocols: tuple[str, ...]
    rpc_methods: tuple[str, ...] = ()


@dataclass
class DocsProjectionSpec(SerdeMixin):
    """Documentation inclusion policy, separate from docs payload/UIX paths."""

    name: str
    include_protocols: Sequence[str] = field(default_factory=tuple)
    exclude_protocols: Sequence[str] = field(default_factory=tuple)
    include_paths: Sequence[str] = field(default_factory=tuple)
    exclude_paths: Sequence[str] = field(default_factory=tuple)
    include_tables: Sequence[str] = field(default_factory=tuple)
    include_ops: Sequence[str] = field(default_factory=tuple)
    include_tags: Sequence[str] = field(default_factory=tuple)
    visibility: Sequence[str] = field(default_factory=tuple)
    rpc_methods: Sequence[str] = field(default_factory=tuple)

    def select(self, paths: Sequence[PathSpec]) -> tuple[DocsProjectionSelection, ...]:
        selections: list[DocsProjectionSelection] = []
        for path in paths:
            if not self._path_allowed(path):
                continue
            for table in path.tables:
                table_name = _table_name(table)
                if self.include_tables and table_name not in self.include_tables:
                    continue
                for op in table.ops:
                    selection = self._select_op(path.path, table_name, op)
                    if selection is not None:
                        selections.append(selection)
            for op in path.ops:
                selection = self._select_op(path.path, None, op)
                if selection is not None:
                    selections.append(selection)
        return tuple(selections)

    def selected_paths(self, paths: Sequence[PathSpec]) -> tuple[str, ...]:
        return tuple(path.path for path in paths if self._path_allowed(path))

    def _path_allowed(self, path: PathSpec) -> bool:
        if path.path in set(self.exclude_paths):
            return False
        return not self.include_paths or path.path in set(self.include_paths)

    def _select_op(
        self, path: str, table_name: str | None, op: object
    ) -> DocsProjectionSelection | None:
        alias = str(getattr(op, "alias", ""))
        if self.include_ops and alias not in set(self.include_ops):
            return None

        tags = set(getattr(op, "tags", ()) or ())
        if self.include_tags and tags.isdisjoint(set(self.include_tags)):
            return None

        bindings = tuple(getattr(op, "bindings", ()) or ())
        protocols = tuple(str(getattr(binding, "proto", "")) for binding in bindings)
        if not protocols:
            return None

        include_protocols = set(self.include_protocols)
        exclude_protocols = set(self.exclude_protocols)
        if include_protocols and include_protocols.isdisjoint(protocols):
            return None
        if exclude_protocols and not exclude_protocols.isdisjoint(protocols):
            return None

        rpc_methods = tuple(
            binding.rpc_method
            for binding in bindings
            if isinstance(binding, HttpJsonRpcBindingSpec)
        )
        if self.rpc_methods and set(self.rpc_methods).isdisjoint(rpc_methods):
            return None

        return DocsProjectionSelection(
            path=path,
            table=table_name,
            op=alias,
            protocols=protocols,
            rpc_methods=rpc_methods,
        )


@dataclass
class DocsPayloadSpec(SerdeMixin):
    kind: DocsPayloadKind
    projection: DocsProjectionSpec
    media_type: str = "application/json"


@dataclass
class DocsUixSpec(SerdeMixin):
    kind: DocsUixKind
    payload_path: str | None = None
    projection: DocsProjectionSpec | None = None


def _table_name(table: object) -> str:
    model_ref = getattr(table, "model_ref", None)
    if isinstance(model_ref, str) and model_ref:
        return model_ref.rsplit(":", 1)[-1].rsplit(".", 1)[-1]
    model = getattr(table, "model", None)
    if isinstance(model, str) and model:
        return model.rsplit(":", 1)[-1].rsplit(".", 1)[-1]
    return getattr(table, "name", None) or "table"


__all__ = [
    "DocsPayloadKind",
    "DocsPayloadSpec",
    "DocsProjectionSelection",
    "DocsProjectionSpec",
    "DocsUixKind",
    "DocsUixSpec",
]
