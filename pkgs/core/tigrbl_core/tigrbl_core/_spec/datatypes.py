from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from importlib import import_module
from typing import Any, Callable, Dict, Mapping, MutableMapping, Protocol, runtime_checkable

from .serde import SerdeMixin

CANONICAL_DATATYPES: tuple[str, ...] = (
    "string",
    "integer",
    "number",
    "decimal",
    "boolean",
    "bytes",
    "date",
    "datetime",
    "time",
    "duration",
    "json",
    "object",
    "array",
    "uuid",
    "ulid",
)

_LOGICAL_NAME_ALIASES = {
    "str": "string",
    "varchar": "string",
    "text": "string",
    "int": "integer",
    "bigint": "integer",
    "smallint": "integer",
    "float": "number",
    "double": "number",
    "real": "number",
    "numeric": "decimal",
    "bool": "boolean",
    "bytea": "bytes",
    "timestamp": "datetime",
    "dict": "object",
    "list": "array",
    "tuple": "array",
}

_ENGINE_FAMILY_MAPPINGS: dict[str, dict[str, str]] = {
    "sqlite": {
        "string": "TEXT",
        "integer": "INTEGER",
        "number": "REAL",
        "decimal": "NUMERIC",
        "boolean": "BOOLEAN",
        "bytes": "BLOB",
        "date": "DATE",
        "datetime": "DATETIME",
        "time": "TIME",
        "duration": "TEXT",
        "json": "JSON",
        "object": "JSON",
        "array": "JSON",
        "uuid": "TEXT",
        "ulid": "TEXT",
    },
    "postgres": {
        "string": "TEXT",
        "integer": "BIGINT",
        "number": "DOUBLE PRECISION",
        "decimal": "NUMERIC",
        "boolean": "BOOLEAN",
        "bytes": "BYTEA",
        "date": "DATE",
        "datetime": "TIMESTAMPTZ",
        "time": "TIME",
        "duration": "INTERVAL",
        "json": "JSONB",
        "object": "JSONB",
        "array": "JSONB",
        "uuid": "UUID",
        "ulid": "UUID",
    },
    "dataframe": {
        "string": "string",
        "integer": "int64",
        "number": "float64",
        "decimal": "object",
        "boolean": "bool",
        "bytes": "bytes",
        "date": "datetime64[ns]",
        "datetime": "datetime64[ns]",
        "time": "object",
        "duration": "timedelta64[ns]",
        "json": "object",
        "object": "object",
        "array": "object",
        "uuid": "string",
        "ulid": "string",
    },
    "file": {
        "string": "string",
        "integer": "integer",
        "number": "number",
        "decimal": "decimal",
        "boolean": "boolean",
        "bytes": "bytes",
        "date": "date",
        "datetime": "datetime",
        "time": "time",
        "duration": "duration",
        "json": "json",
        "object": "json",
        "array": "json",
        "uuid": "string",
        "ulid": "string",
    },
    "cache": {
        "string": "string",
        "integer": "string",
        "number": "string",
        "decimal": "string",
        "boolean": "string",
        "bytes": "bytes",
        "json": "json",
        "object": "json",
        "array": "json",
        "uuid": "string",
        "ulid": "string",
    },
}

_REFLECTION_HINTS: dict[str | None, dict[str, str]] = {
    None: {
        "varchar": "string",
        "text": "string",
        "string": "string",
        "integer": "integer",
        "int": "integer",
        "bigint": "integer",
        "float": "number",
        "double": "number",
        "numeric": "decimal",
        "decimal": "decimal",
        "boolean": "boolean",
        "bool": "boolean",
        "json": "json",
        "jsonb": "json",
        "uuid": "uuid",
        "bytea": "bytes",
        "blob": "bytes",
        "datetime": "datetime",
        "timestamp": "datetime",
        "date": "date",
        "time": "time",
        "interval": "duration",
    },
    "sqlite": {
        "text": "string",
        "integer": "integer",
        "real": "number",
        "numeric": "decimal",
        "blob": "bytes",
        "json": "json",
        "datetime": "datetime",
    },
    "postgres": {
        "text": "string",
        "bigint": "integer",
        "double precision": "number",
        "numeric": "decimal",
        "bytea": "bytes",
        "jsonb": "json",
        "uuid": "uuid",
        "timestamptz": "datetime",
        "interval": "duration",
    },
}


def _class_path(value: type[Any]) -> str:
    return f"{value.__module__}:{value.__qualname__}"


def _resolve_class(path: str) -> type[Any]:
    module_name, _, qualname = path.partition(":")
    if not module_name or not qualname:
        raise ValueError(f"Invalid adapter path: {path}")
    value: Any = import_module(module_name)
    for segment in qualname.split("."):
        value = getattr(value, segment)
    if not isinstance(value, type):
        raise TypeError(f"Adapter path does not resolve to a class: {path}")
    return value


@dataclass(frozen=True)
class StorageTypeRef(SerdeMixin):
    """Logical-to-physical storage type mapping."""

    physical_name: str
    engine_kind: str | None = None


@dataclass(frozen=True)
class DataTypeSpec(SerdeMixin):
    """Canonical logical datatype definition."""

    logical_name: str
    nullable: bool = False
    options: Dict[str, Any] = dc_field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized = _normalize_logical_name(self.logical_name)
        object.__setattr__(self, "logical_name", normalized)
        object.__setattr__(self, "options", dict(self.options))

    @classmethod
    def new(cls, logical_name: str, **options: Any) -> "DataTypeSpec":
        nullable = bool(options.pop("nullable", False))
        return cls(logical_name=logical_name, nullable=nullable, options=dict(options))


def _normalize_logical_name(value: str) -> str:
    normalized = str(value).strip().lower()
    if not normalized:
        return "object"
    return _LOGICAL_NAME_ALIASES.get(normalized, normalized)


def _logical_name_from_value(value: Any) -> str:
    if isinstance(value, DataTypeSpec):
        return value.logical_name
    if isinstance(value, str):
        return _normalize_logical_name(value)

    cls = value if isinstance(value, type) else value.__class__
    name = getattr(cls, "__name__", None)
    if name is None:
        return "object"
    return _normalize_logical_name(str(name))


def infer_datatype(
    *,
    field_py_type: Any = Any,
    storage_type: Any = None,
    nullable: bool | None = None,
    constraints: Mapping[str, Any] | None = None,
) -> DataTypeSpec:
    """Best-effort canonical datatype inference for legacy column specs."""

    constraints = dict(constraints or {})
    candidates = [storage_type, field_py_type]
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, DataTypeSpec):
            return candidate

        logical_name = _logical_name_from_value(candidate)
        options: dict[str, Any] = {}
        if "max_length" in constraints:
            options["max_length"] = constraints["max_length"]
        if logical_name in CANONICAL_DATATYPES:
            return DataTypeSpec(
                logical_name=logical_name,
                nullable=bool(nullable) if nullable is not None else False,
                options=options,
            )

    return DataTypeSpec(
        logical_name="object",
        nullable=bool(nullable) if nullable is not None else False,
        options=dict(constraints),
    )


@runtime_checkable
class TypeAdapter(Protocol):
    logical_name: str

    def normalize(self, spec: DataTypeSpec) -> DataTypeSpec: ...

    def encode(self, value: Any) -> Any: ...

    def decode(self, value: Any) -> Any: ...

    def to_json(self, value: Any) -> Any: ...

    def to_df(self, value: Any) -> Any: ...


class BaseTypeAdapter:
    """Minimal executable adapter contract for canonical datatypes."""

    logical_name = "object"

    def __init__(self, logical_name: str | None = None) -> None:
        if logical_name is not None:
            self.logical_name = _normalize_logical_name(logical_name)

    def normalize(self, spec: DataTypeSpec) -> DataTypeSpec:
        if spec.logical_name == self.logical_name:
            return spec
        return DataTypeSpec(
            logical_name=self.logical_name,
            nullable=spec.nullable,
            options=dict(spec.options),
        )

    def encode(self, value: Any) -> Any:
        return value

    def decode(self, value: Any) -> Any:
        return value

    def to_json(self, value: Any) -> Any:
        return value

    def to_df(self, value: Any) -> Any:
        return value


def _builtin_adapter_paths() -> dict[str, str]:
    base = f"{__name__}:BaseTypeAdapter"
    return {logical_name: base for logical_name in CANONICAL_DATATYPES}


class TypeRegistry(SerdeMixin):
    """Executable adapter registry with stable serde surface."""

    def __init__(
        self,
        adapters: MutableMapping[str, str] | None = None,
        *,
        include_builtins: bool = True,
    ) -> None:
        self.adapters: MutableMapping[str, str] = {}
        if include_builtins:
            self.adapters.update(_builtin_adapter_paths())
        if adapters:
            self.adapters.update(
                {_normalize_logical_name(name): path for name, path in dict(adapters).items()}
            )
        self._runtime_adapters: dict[str, TypeAdapter] = {}

    def to_dict(self) -> dict[str, Any]:
        return {"adapters": dict(self.adapters)}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TypeRegistry":
        adapters = payload.get("adapters")
        if not isinstance(adapters, dict):
            adapters = {}
        return cls(adapters=adapters, include_builtins=False)

    def register(self, adapter: TypeAdapter) -> None:
        logical_name = _normalize_logical_name(adapter.logical_name)
        self.adapters[logical_name] = _class_path(adapter.__class__)
        self._runtime_adapters[logical_name] = adapter

    def registered_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.adapters))

    def resolve(self, logical_name: str) -> TypeAdapter | None:
        normalized = _normalize_logical_name(logical_name)
        if normalized in self._runtime_adapters:
            return self._runtime_adapters[normalized]

        adapter_path = self.adapters.get(normalized)
        if adapter_path is None:
            return None
        adapter_cls = _resolve_class(adapter_path)
        try:
            adapter = adapter_cls(normalized)
        except TypeError:
            adapter = adapter_cls()
        if not isinstance(adapter, TypeAdapter):
            raise TypeError(f"Registered adapter does not implement TypeAdapter: {adapter_path}")
        self._runtime_adapters[normalized] = adapter
        return adapter

    def normalize(self, spec: DataTypeSpec) -> DataTypeSpec:
        adapter = self.resolve(spec.logical_name)
        return adapter.normalize(spec) if adapter is not None else spec

    def encode(self, logical_name: str, value: Any) -> Any:
        adapter = self.resolve(logical_name)
        return adapter.encode(value) if adapter is not None else value

    def decode(self, logical_name: str, value: Any) -> Any:
        adapter = self.resolve(logical_name)
        return adapter.decode(value) if adapter is not None else value


@runtime_checkable
class EngineTypeLowerer(Protocol):
    engine_kind: str

    def lower(self, datatype: DataTypeSpec) -> StorageTypeRef: ...


class StaticEngineLowerer:
    def __init__(self, engine_kind: str, mapping: Mapping[str, str]) -> None:
        self.engine_kind = engine_kind
        self._mapping = {_normalize_logical_name(k): v for k, v in mapping.items()}

    def lower(self, datatype: DataTypeSpec) -> StorageTypeRef:
        physical_name = self._mapping.get(datatype.logical_name)
        if physical_name is None:
            raise LookupError(
                f"engine '{self.engine_kind}' does not support logical datatype '{datatype.logical_name}'"
            )
        return StorageTypeRef(engine_kind=self.engine_kind, physical_name=physical_name)


class EngineRegistry:
    def __init__(self, include_builtins: bool = True) -> None:
        self._lowerers: dict[str, EngineTypeLowerer] = {}
        if include_builtins:
            for engine_kind, mapping in _ENGINE_FAMILY_MAPPINGS.items():
                self.register(StaticEngineLowerer(engine_kind, mapping))

    def register(self, lowerer: EngineTypeLowerer) -> None:
        self._lowerers[lowerer.engine_kind] = lowerer

    def get(self, engine_kind: str) -> EngineTypeLowerer | None:
        return self._lowerers.get(str(engine_kind).strip().lower())

    def known_engines(self) -> tuple[str, ...]:
        return tuple(sorted(self._lowerers))


class EngineDatatypeBridge:
    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or EngineRegistry()

    def lower(
        self,
        engine_kind: str,
        datatype: DataTypeSpec,
        *,
        strict: bool = False,
    ) -> StorageTypeRef:
        normalized_engine = str(engine_kind).strip().lower()
        lowerer = self.registry.get(normalized_engine)
        if lowerer is None:
            if strict:
                raise LookupError(f"no lowerer registered for engine '{normalized_engine}'")
            return StorageTypeRef(
                engine_kind=normalized_engine,
                physical_name=datatype.logical_name,
            )
        try:
            return lowerer.lower(datatype)
        except LookupError:
            if strict:
                raise
            return StorageTypeRef(
                engine_kind=normalized_engine,
                physical_name=datatype.logical_name,
            )


@dataclass(frozen=True)
class ReflectedDatatype(SerdeMixin):
    engine_kind: str
    physical_name: str
    logical_hint: str | None = None


class ReflectedTypeMapper:
    """Recover canonical datatypes from reflected engine metadata."""

    def _mapping_for_engine(self, engine_kind: str | None) -> dict[str, str]:
        normalized = engine_kind.lower() if isinstance(engine_kind, str) else None
        mapping = dict(_REFLECTION_HINTS.get(None, {}))
        mapping.update(_REFLECTION_HINTS.get(normalized, {}))
        return mapping

    def from_storage_ref(
        self,
        storage_ref: StorageTypeRef,
        *,
        mode: str = "best_effort",
        strict: bool = False,
    ) -> DataTypeSpec:
        mapping = self._mapping_for_engine(storage_ref.engine_kind)
        hint = mapping.get(storage_ref.physical_name.lower())
        if hint is None and strict:
            raise LookupError(
                f"no reflected datatype mapping for {storage_ref.engine_kind or 'unknown'}:{storage_ref.physical_name}"
            )
        options: dict[str, Any] = {}
        if mode == "metadata_preserving":
            options["reflected_physical_name"] = storage_ref.physical_name
            if storage_ref.engine_kind is not None:
                options["reflected_engine_kind"] = storage_ref.engine_kind
        if hint is None:
            options.setdefault("downgraded_from_physical_name", storage_ref.physical_name)
            return DataTypeSpec(logical_name="object", options=options)
        return DataTypeSpec(logical_name=hint, options=options)

    def reflect(
        self,
        *,
        engine_kind: str,
        physical_name: str,
        logical_hint: str | None = None,
        mode: str = "best_effort",
        strict: bool = False,
    ) -> DataTypeSpec:
        ref = StorageTypeRef(engine_kind=engine_kind, physical_name=physical_name)
        reflected = self.from_storage_ref(ref, mode=mode, strict=strict)
        if logical_hint is not None:
            return DataTypeSpec(
                logical_name=logical_hint,
                nullable=reflected.nullable,
                options=dict(reflected.options),
            )
        return reflected


__all__ = [
    "BaseTypeAdapter",
    "CANONICAL_DATATYPES",
    "DataTypeSpec",
    "EngineDatatypeBridge",
    "EngineRegistry",
    "EngineTypeLowerer",
    "ReflectedDatatype",
    "ReflectedTypeMapper",
    "StaticEngineLowerer",
    "StorageTypeRef",
    "TypeAdapter",
    "TypeRegistry",
    "infer_datatype",
]
