from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any, Callable, Dict, Mapping, MutableMapping, Protocol, runtime_checkable

from .serde import SerdeMixin


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

    @classmethod
    def new(cls, logical_name: str, **options: Any) -> "DataTypeSpec":
        nullable = bool(options.pop("nullable", False))
        return cls(logical_name=logical_name, nullable=nullable, options=dict(options))


def _logical_name_from_value(value: Any) -> str:
    if isinstance(value, DataTypeSpec):
        return value.logical_name
    if isinstance(value, str):
        return value
    name = getattr(value, "__name__", None)
    if name is None:
        return "object"
    return str(name).lower()


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

        normalized = {
            "str": "string",
            "string": "string",
            "varchar": "string",
            "text": "string",
            "int": "integer",
            "integer": "integer",
            "bigint": "integer",
            "smallint": "integer",
            "float": "number",
            "double": "number",
            "real": "number",
            "number": "number",
            "numeric": "decimal",
            "decimal": "decimal",
            "bool": "boolean",
            "boolean": "boolean",
            "bytes": "bytes",
            "bytea": "bytes",
            "date": "date",
            "datetime": "datetime",
            "timestamp": "datetime",
            "time": "time",
            "timedelta": "duration",
            "dict": "object",
            "object": "object",
            "json": "json",
            "list": "array",
            "tuple": "array",
            "uuid": "uuid",
            "ulid": "ulid",
        }.get(logical_name, None)
        if normalized is not None:
            return DataTypeSpec(
                logical_name=normalized,
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


@dataclass
class TypeRegistry(SerdeMixin):
    adapters: MutableMapping[str, str] = dc_field(default_factory=dict)

    def register(self, adapter: TypeAdapter) -> None:
        self.adapters[adapter.logical_name] = (
            f"{adapter.__class__.__module__}:{adapter.__class__.__qualname__}"
        )

    def registered_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.adapters))

    def normalize(self, spec: DataTypeSpec, factories: Mapping[str, Callable[[], TypeAdapter]] | None = None) -> DataTypeSpec:
        logical_name = spec.logical_name
        if factories and logical_name in factories:
            return factories[logical_name]().normalize(spec)
        return spec


@runtime_checkable
class EngineTypeLowerer(Protocol):
    engine_kind: str

    def lower(self, datatype: DataTypeSpec) -> StorageTypeRef: ...


class EngineRegistry:
    def __init__(self) -> None:
        self._lowerers: dict[str, EngineTypeLowerer] = {}

    def register(self, lowerer: EngineTypeLowerer) -> None:
        self._lowerers[lowerer.engine_kind] = lowerer

    def get(self, engine_kind: str) -> EngineTypeLowerer | None:
        return self._lowerers.get(engine_kind)

    def known_engines(self) -> tuple[str, ...]:
        return tuple(sorted(self._lowerers))


class EngineDatatypeBridge:
    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or EngineRegistry()

    def lower(self, engine_kind: str, datatype: DataTypeSpec) -> StorageTypeRef:
        lowerer = self.registry.get(engine_kind)
        if lowerer is None:
            return StorageTypeRef(
                engine_kind=engine_kind,
                physical_name=datatype.logical_name,
            )
        return lowerer.lower(datatype)


@dataclass(frozen=True)
class ReflectedDatatype(SerdeMixin):
    engine_kind: str
    physical_name: str
    logical_hint: str | None = None


class ReflectedTypeMapper:
    """Recover canonical datatypes from reflected engine metadata."""

    _DEFAULT_HINTS = {
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
    }

    def from_storage_ref(
        self,
        storage_ref: StorageTypeRef,
        *,
        mode: str = "best_effort",
    ) -> DataTypeSpec:
        hint = self._DEFAULT_HINTS.get(storage_ref.physical_name.lower(), "object")
        options = {}
        if mode == "metadata_preserving":
            options["reflected_physical_name"] = storage_ref.physical_name
            if storage_ref.engine_kind is not None:
                options["reflected_engine_kind"] = storage_ref.engine_kind
        return DataTypeSpec(logical_name=hint, options=options)

    def reflect(
        self,
        *,
        engine_kind: str,
        physical_name: str,
        logical_hint: str | None = None,
        mode: str = "best_effort",
    ) -> DataTypeSpec:
        ref = StorageTypeRef(engine_kind=engine_kind, physical_name=physical_name)
        reflected = self.from_storage_ref(ref, mode=mode)
        if logical_hint is not None:
            return DataTypeSpec(
                logical_name=logical_hint,
                nullable=reflected.nullable,
                options=dict(reflected.options),
            )
        return reflected


__all__ = [
    "BaseTypeAdapter",
    "DataTypeSpec",
    "EngineDatatypeBridge",
    "EngineRegistry",
    "EngineTypeLowerer",
    "ReflectedDatatype",
    "ReflectedTypeMapper",
    "StorageTypeRef",
    "TypeAdapter",
    "TypeRegistry",
    "infer_datatype",
]
