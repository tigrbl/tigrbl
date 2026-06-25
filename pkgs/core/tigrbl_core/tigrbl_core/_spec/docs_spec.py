from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence

from .binding_spec import FramingSpec, HttpJsonRpcBindingSpec
from .path_spec import PathSpec
from .serde import SerdeMixin

DocsPayloadKind = Literal["openapi", "openrpc", "jsonschema"]
DocsUixKind = Literal["swagger", "redoc", "scalar", "lens", "custom"]


@dataclass(frozen=True)
class DocsProjectionSelection(SerdeMixin):
    path: str
    table: str | None = None
    op: str = ""
    protocols: tuple[str, ...] = ()
    path_kind: str = "resource"
    framings: tuple[str, ...] = ()
    subprotocols: tuple[str, ...] = ()
    rpc_methods: tuple[str, ...] = ()


@dataclass
class DocsProjectionSpec(SerdeMixin):
    """Documentation inclusion policy, separate from docs payload/UIX paths."""

    name: str
    include_protocols: Sequence[str] = field(default_factory=tuple)
    exclude_protocols: Sequence[str] = field(default_factory=tuple)
    include_paths: Sequence[str] = field(default_factory=tuple)
    exclude_paths: Sequence[str] = field(default_factory=tuple)
    include_path_kinds: Sequence[str] = field(default_factory=tuple)
    include_tables: Sequence[str] = field(default_factory=tuple)
    include_ops: Sequence[str] = field(default_factory=tuple)
    include_tags: Sequence[str] = field(default_factory=tuple)
    include_framings: Sequence[str] = field(default_factory=tuple)
    include_subprotocols: Sequence[str] = field(default_factory=tuple)
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
                    selection = self._select_op(path, table_name, op)
                    if selection is not None:
                        selections.append(selection)
            for op in path.ops:
                selection = self._select_op(path, None, op)
                if selection is not None:
                    selections.append(selection)
        return tuple(selections)

    def selected_paths(self, paths: Sequence[PathSpec]) -> tuple[str, ...]:
        return tuple(path.path for path in paths if self._path_allowed(path))

    def validate_for_payload_kind(self, kind: DocsPayloadKind) -> None:
        protocols = set(self.include_protocols)
        if kind == "openapi" and any(protocol.endswith(".jsonrpc") for protocol in protocols):
            raise ValueError("OpenAPI docs projection must not include JSON-RPC protocols.")
        if kind == "openrpc" and protocols and "http.jsonrpc" not in protocols and "https.jsonrpc" not in protocols:
            raise ValueError("OpenRPC docs projection must include a JSON-RPC protocol.")
        if str(kind) == "asyncapi":
            raise ValueError("AsyncAPI docs payloads are not supported.")

    def _path_allowed(self, path: PathSpec) -> bool:
        if path.path in set(self.exclude_paths):
            return False
        if self.include_path_kinds and path.kind not in set(self.include_path_kinds):
            return False
        return not self.include_paths or path.path in set(self.include_paths)

    def _select_op(
        self, path: PathSpec, table_name: str | None, op: object
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
        framings = tuple(_framing_kind(getattr(binding, "framing", None)) for binding in bindings)
        subprotocols = tuple(
            item
            for binding in bindings
            for item in tuple(getattr(binding, "subprotocols", ()) or ())
        )

        include_protocols = set(self.include_protocols)
        exclude_protocols = set(self.exclude_protocols)
        if include_protocols and include_protocols.isdisjoint(protocols):
            return None
        if exclude_protocols and not exclude_protocols.isdisjoint(protocols):
            return None
        if self.include_framings and set(self.include_framings).isdisjoint(framings):
            return None
        if self.include_subprotocols and set(self.include_subprotocols).isdisjoint(subprotocols):
            return None

        rpc_methods = tuple(
            binding.rpc_method
            for binding in bindings
            if isinstance(binding, HttpJsonRpcBindingSpec)
        )
        if self.rpc_methods and set(self.rpc_methods).isdisjoint(rpc_methods):
            return None

        return DocsProjectionSelection(
            path=path.path,
            path_kind=path.kind,
            table=table_name,
            op=alias,
            protocols=protocols,
            framings=framings,
            subprotocols=subprotocols,
            rpc_methods=rpc_methods,
        )


@dataclass
class DocsPayloadSpec(SerdeMixin):
    kind: DocsPayloadKind
    projection: DocsProjectionSpec
    media_type: str = "application/json"

    def __post_init__(self) -> None:
        if not isinstance(self.projection, DocsProjectionSpec):
            raise TypeError("DocsPayloadSpec.projection must be a DocsProjectionSpec.")
        self.projection.validate_for_payload_kind(self.kind)


@dataclass
class DocsUixSpec(SerdeMixin):
    kind: DocsUixKind
    payload_path: str | None = None
    projection: DocsProjectionSpec | None = None

    def __post_init__(self) -> None:
        if self.payload_path is not None and not self.payload_path.startswith("/"):
            raise ValueError("DocsUixSpec.payload_path must be an absolute path when provided.")
        if self.projection is not None and not isinstance(self.projection, DocsProjectionSpec):
            raise TypeError("DocsUixSpec.projection must be a DocsProjectionSpec when provided.")


def _table_name(table: object) -> str:
    model_ref = getattr(table, "model_ref", None)
    if isinstance(model_ref, str) and model_ref:
        return model_ref.rsplit(":", 1)[-1].rsplit(".", 1)[-1]
    model = getattr(table, "model", None)
    if isinstance(model, str) and model:
        return model.rsplit(":", 1)[-1].rsplit(".", 1)[-1]
    return getattr(table, "name", None) or "table"


def _framing_kind(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, FramingSpec):
        return value.kind
    return str(value)


def validate_docs_tree(paths: Sequence[PathSpec]) -> None:
    by_path = {path.path: path for path in paths}
    for path in paths:
        if path.kind == "docs-payload":
            validate_docs_payload_path(path)
        if path.kind == "docs-uix":
            validate_docs_uix_path(path, by_path)


def validate_docs_payload_path(path: PathSpec) -> None:
    if not isinstance(path.docs_payload, DocsPayloadSpec):
        raise TypeError("docs-payload PathSpec entries must carry DocsPayloadSpec.")
    selected = path.docs_payload.projection.select(())
    if selected:
        raise ValueError("Docs payload projection validation must not depend on incidental docs path exposure.")


def validate_docs_uix_path(path: PathSpec, paths_by_path: dict[str, PathSpec]) -> None:
    if not isinstance(path.docs_uix, DocsUixSpec):
        raise TypeError("docs-uix PathSpec entries must carry DocsUixSpec.")
    payload_path = path.docs_uix.payload_path
    if payload_path is None:
        return
    target = paths_by_path.get(payload_path)
    if target is None or target.kind != "docs-payload":
        raise ValueError("DocsUixSpec.payload_path must reference a docs-payload PathSpec.")


__all__ = [
    "DocsPayloadKind",
    "DocsPayloadSpec",
    "DocsProjectionSelection",
    "DocsProjectionSpec",
    "DocsUixKind",
    "DocsUixSpec",
    "validate_docs_payload_path",
    "validate_docs_tree",
    "validate_docs_uix_path",
]
