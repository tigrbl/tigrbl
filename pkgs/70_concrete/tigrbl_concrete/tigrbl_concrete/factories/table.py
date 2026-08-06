from __future__ import annotations

from dataclasses import replace
from typing import Any, Sequence, Type

from tigrbl_concrete._concrete._table import Table
from tigrbl_core._spec.table_spec import TableSpec


def defineTableSpec(
    *,
    # engine binding
    engine: Any = None,
    # composition
    ops: Sequence[Any] = (),
    columns: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    # dependency stacks
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
) -> Type[TableSpec]:
    """
    Build a Table-spec class with class attributes only (no instances).
    Use directly in your ORM class MRO:

        class User(defineTableSpec(engine=..., ops=(...)), Base, Table):
            __tablename__ = "users"

    or pass it to `deriveTable(Model, ...)` to get a configured subclass.
    """
    attrs = {
        # top-level mirrors read by collectors
        "OPS": tuple(ops or ()),
        "COLUMNS": tuple(columns or ()),
        "SCHEMAS": tuple(schemas or ()),
        "HOOKS": tuple(hooks or ()),
        "SECURITY_DEPS": tuple(security_deps or ()),
        "DEPS": tuple(deps or ()),
    }

    # Engine binding is conventionally stored under table_config["engine"]
    # (and legacy "db" for backward compatibility) so collectors can find it.
    if engine is not None:
        attrs["table_config"] = {"engine": engine, "db": engine}

    return type("TableSpec", (TableSpec,), attrs)


def deriveTable(model: Type[Table], **kw: Any) -> Type[Table]:
    """Produce a concrete ORM subclass that inherits the spec."""
    Spec = defineTableSpec(**kw)
    name = f"{model.__name__}WithSpec"
    return type(name, (Spec, model), {})


def _merge_ops(existing: Sequence[Any], incoming: Sequence[Any]) -> tuple[Any, ...]:
    if not incoming:
        return tuple(existing)
    merged: dict[tuple[Any, Any], Any] = {}
    for operation in (*tuple(existing), *tuple(incoming)):
        alias = getattr(operation, "alias", None)
        target = getattr(operation, "target", None)
        key = (
            (alias, target)
            if alias is not None and target is not None
            else ("legacy", operation)
        )
        merged[key] = operation
    return tuple(merged.values())


def deriveTableSpec(
    model: Type[Table],
    *,
    ops: Sequence[Any] = (),
    columns: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
) -> TableSpec:
    """Derive a new specification without mutating the source table."""

    collected = TableSpec.collect(model)
    return replace(
        collected,
        ops=_merge_ops(tuple(collected.ops), tuple(ops)),
        columns=(*tuple(collected.columns), *tuple(columns)),
        schemas=(*tuple(collected.schemas), *tuple(schemas)),
        hooks=(*tuple(collected.hooks), *tuple(hooks)),
        security_deps=(*tuple(collected.security_deps), *tuple(security_deps)),
        deps=(*tuple(collected.deps), *tuple(deps)),
    )


def provideTableSpec(source: Type[Table] | TableSpec) -> TableSpec:
    """Normalize a concrete table or collected specification for consumers."""

    spec = source if isinstance(source, TableSpec) else deriveTableSpec(source)
    if not isinstance(spec, TableSpec):
        raise TypeError("table specification source must be a Table or TableSpec")
    if not isinstance(spec.model, type):
        raise TypeError("table specification requires a concrete model class")
    return spec


__all__ = ["defineTableSpec", "deriveTable", "deriveTableSpec", "provideTableSpec"]
